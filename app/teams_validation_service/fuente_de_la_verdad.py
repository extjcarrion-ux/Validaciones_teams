#app/teams_validation_service/fuente_de_la_verdad.py
import json
import copy
import warnings
import pandas as pd
from pathlib import Path
from typing import Tuple, Optional
from google.cloud.bigquery.exceptions import BigQueryError
from app.bigQuery.client.client import BigQueryClient
from config.config import settings
from config.log_config import logger
from app.utills.utills import (generar_request_id
                               ,reprocess
                               ,read_sql_file
                               ,read_json_file)

################ config #################
pd.set_option('display.max_rows', 5)
warnings.simplefilter("ignore", UserWarning)
#########################################

class ListaUsuarios:
  """
    Servicio encargado de:

    - Ejecutar consultas en BigQuery
    - Procesar resultados agrupados por manager
    - Generar mensajes en formato Adaptive Card (JSON)
    - Aplicar lógica de reprocesamiento
    - Exportar resultados a archivos CSV y Excel

    Este flujo está diseñado para validar equipos y enviar información
    estructurada a sistemas externos como Microsoft Teams.
  """
  def __init__(self,name_file:Optional[str] = None, project_id=settings.project_prod) -> None:
       """
        Inicializa la clase ListaUsuarios.
        Args:
            name_file (Optional[str]): Nombre del archivo de salida (sin extensión).
            project_id (str): ID del proyecto en BigQuery.
        """
       self.name_file   = str(name_file)
       self.dir_path    = Path(settings.path_output)
       self.path_file   = Path(settings.path_output,self.name_file)
       self.project_id  = project_id
       self.client      = BigQueryClient().ambientProd()

  #################################################################
  def exec_query(self,reprocesar:bool = True,sql_file:Optional[Path] = None
                 ,json_template:Path = Path("data/")
                 ) -> tuple[bool,str,pd.DataFrame]:
    """
        Ejecuta una query en BigQuery, procesa los resultados y genera mensajes por manager.
        Flujo:
            1. Lee el archivo SQL
            2. Ejecuta la consulta en BigQuery
            3. Agrupa resultados por manager
            4. Construye mensajes (Adaptive Cards)
            5. Genera request_id por destinatario
            6. (Opcional) Aplica reprocesamiento
            7. Exporta resultados a archivos

        Args:
            reprocesar (bool):
                - True: Filtra y reprocesa registros ya enviados
                - False: Envía todos los registros sin validación

            sql_file (Optional[Path]):
                Ruta del archivo SQL a ejecutar.

            json_template (Path):
                Ruta del archivo JSON que actúa como template para los mensajes.

        Returns:
            Tuple[bool, str, pd.DataFrame]:
                - success (bool): Estado de ejecución
                - message (str): Mensaje descriptivo
                - df_mensajes (pd.DataFrame): DataFrame con los mensajes generados

        Raises:
            BigQueryError: Error durante la ejecución de la query
            Exception: Error inesperado en el proceso
        """
    logger.info(
            "Iniciando exec_query | reprocesar=%s | proyecto=%s",
            reprocesar,
            self.project_id)

    success,message,df_mensajes   = True,"OK",pd.DataFrame()
    try:
      msn,query = read_sql_file(sql_file)

      if msn == False:
          logger.error("Error al leer el archivo SQL: %s", query[1])
          return False, f"Error al leer el archivo SQL: {query[1]}", pd.DataFrame()

      ### Ejecuta la consulta
      logger.info("Ejecutando query en BigQuery")
      query_job = self.client.query(query)
  
      ### Recupera los resultados de la consulta y conviértelos en un DataFrame de Pandas
      df_main = query_job.result().to_dataframe()
      logger.info("Query ejecutada correctamente | filas=%d", len(df_main))
      ### Agrupar por manager
      mensajes = []

      ########################################
      for manager, group in df_main.groupby("manager_corp_email_clear"):
          manager_email = manager
          manager_name = group["manager_name"].iloc[0]

          ########################################################
          # Clonar template para no pisarlo
          json_template_data = read_json_file(json_template)
          card = copy.deepcopy(json_template_data["data"])
            # Generar team members (simplificado)
          team_members = [
                {
                    "title": f'{row["emp_name"]} ({row["emp_corp_email_clear"]})',
                    "value": row["emp_corp_email_clear"]
                }
                for _, row in group.iterrows()
            ]

            # 🔹 Reemplazar dinámicamente el contenido
          for element in card["body"]:
                if element["type"] == "TextBlock" and "Validación de equipo" in element.get("text", ""):
                    element["text"] = f"Validación de equipo - {manager_email}"

                elif element["type"] == "Input.ChoiceSet":
                    element["choices"] = team_members

            # Resultado final
          adaptive_card_dict = card

          mensajes.append({
              "destinatario": manager,
              "mensaje": adaptive_card_dict
          })
          ########################################################

      ########################################
      for m in mensajes:
          m["mensaje"] = json.dumps(m["mensaje"], ensure_ascii=False, indent=4)

      ##### Crear el DataFrame auxiliar
      df_mensajes = pd.DataFrame(mensajes)
      ############## genera id ################      
      df_mensajes["request_id"] = df_mensajes["destinatario"].apply(generar_request_id)

      ############## pruebas ################      
      if reprocesar:
                logger.info("Iniciando reprocesamiento de request_id")
                df_mensajes = reprocess(df_mensajes)

      ######################################
      success,message = self._download_Data(df_mensajes)
      logger.info(
                "Proceso finalizado | success=%s | registros=%d",
                success,
                len(df_mensajes)
            )

    except BigQueryError:
      logger.exception("Error BigQuery durante exec_query",sql_file)
      return False, "BigQueryError", pd.DataFrame()

    except Exception:
      logger.exception("Error inesperado durante exec_query",sql_file)
      return False, "Exception", pd.DataFrame()

    return success,message,df_mensajes

  #################################################################
  def _download_Data(self, data: pd.DataFrame) -> Tuple[bool, str]:
    """
        Guarda el DataFrame en archivos CSV y Excel.
        Args:
            data (pd.DataFrame): DataFrame a exportar.

        Returns:
            Tuple[bool, str]:
                - success (bool): Estado de la operación
                - message (str): Mensaje descriptivo
        """
    success: bool = True
    message: str = "OK"

    try:
      if self.path_file is None:
            output_path = self.dir_path / "output"
      else:
            output_path = self.path_file

      logger.info("Guardando archivos de salida en %s", output_path)
      data.to_csv(f"{output_path}.csv", index=False, sep=";", encoding="utf-8")
      data.to_excel(f"{output_path}.xlsx", index=False) 

      logger.info("Archivos guardados correctamente")

    except Exception:
        logger.exception("Error al guardar archivos de salida")
        return False, "Exception"

    return success, message

