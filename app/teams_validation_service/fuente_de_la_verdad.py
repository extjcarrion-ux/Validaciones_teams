#app/teams_validation_service/fuente_de_la_verdad.py
import json
import warnings
import pandas as pd
from pathlib import Path
from google.cloud.bigquery.exceptions import BigQueryError
from app.bigQuery.client.client import BigQueryClient
from config.config import settings
from config.log_config import logger
from app.utills.utills import (generar_request_id
                               ,reprocess
                               ,read_sql_file)

################ config #################
pd.set_option('display.max_rows', 5)
warnings.simplefilter("ignore", UserWarning)
#########################################

class ListaUsuarios:
  def __init__(self,name_file = None, project_id=settings.project_prod):
       self.name_file   = str(name_file)
       self.dir_path    = Path(settings.path_output)
       self.path_file   = Path(settings.path_output,self.name_file)
       self.project_id  = project_id
       self.client      = BigQueryClient().ambientProd()

  #################################################################
  def exec_query(self,reprocesar:bool = True):
    ### Define tu consulta ###
    logger.info(
            "Iniciando exec_query | reprocesar=%s | proyecto=%s",
            reprocesar,
            self.project_id
        )
    success,message,df_mensajes   = True,"OK",pd.DataFrame()
    try:
      msn,query = read_sql_file("data/query_sql/fuente_de_la_verdad.sql")

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

      for manager, group in df_main.groupby("manager_corp_email_clear"):
          manager_email = manager
          manager_name = group["manager_name"].iloc[0]

          team_members = [
              {
                  "title": json.dumps(f'{row["emp_name"]} ({row["emp_corp_email_clear"]})')[1:-1], #"title": f'{row["emp_name"]} ({row["emp_corp_email_clear"]})',
                  "value": row["emp_corp_email_clear"]
              }
              for _, row in group.iterrows()
          ]

          choices_json_str = ",\n".join(
              f'        {{"title": "{member["title"]}", "value": "{member["value"]}"}}'
              for member in team_members
          )

          #### 3. Utilizar un f-string para construir el JSON completo
          adaptive_card_json_str = f"""
              {{
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                  {{
                    "type": "TextBlock",
                    "text": "Validación de equipo - {manager_email}",
                    "weight": "Bolder",
                    "size": "Medium"
                  }},
                  {{
                    "type": "TextBlock",
                    "text": "Selecciona qué reportes directos pertenecieron a tu equipo al 31 de diciembre del 2025 (excluye externos y practicantes):",
                    "wrap": true
                  }},
                  {{
                    "type": "Input.ChoiceSet",
                    "id": "equipo_validado",
                    "isMultiSelect": true,
                    "style": "expanded",
                    "choices": [
              {choices_json_str}
                    ]
                  }}
                ,
                  {{
                      "type": "Input.Toggle",
                      "title": "Falta alguien en la lista",
                      "id": "falta_gente",
                      "valueOn": "1",
                      "valueOff": "0"
                  }}      
                ],
                "actions": [
                  {{
                    "type": "Action.Submit",
                    "title": "Enviar"
                  }}
                ]
              }}
          """

          # 4. (Opcional) Convertir el string JSON a un diccionario de Python
          adaptive_card_dict = json.loads(adaptive_card_json_str)    

          mensajes.append({
              "destinatario": manager,
              "mensaje": adaptive_card_dict
          })

      for m in mensajes:
          m["mensaje"] = json.dumps(m["mensaje"], ensure_ascii=False, indent=4)

      # Crear el DataFrame auxiliar
      df_mensajes = pd.DataFrame(mensajes)
      ############## genera id ################      
      df_mensajes["request_id"] = df_mensajes["destinatario"].apply(generar_request_id)

      ############## pruebas ################
      # df_mensajes["destinatario"] = "ext_jcarrion@Falabella.cl"
      
      if reprocesar:
                logger.info("Iniciando reprocesamiento de request_id")
                df_mensajes = reprocess(df_mensajes)

      ######################################
      success,message = self.download_Data(df_mensajes)
      logger.info(
                "Proceso finalizado | success=%s | registros=%d",
                success,
                len(df_mensajes)
            )

    except BigQueryError:
      logger.exception("Error BigQuery durante exec_query")
      return False, "BigQueryError", pd.DataFrame()

    except Exception:
      logger.exception("Error inesperado durante exec_query")
      return False, "Exception", pd.DataFrame()

    return success,message,df_mensajes

  #################################################################
  def download_Data(self, data: pd.DataFrame):
    success: bool = True
    message: str = "OK"

    try:
      if self.path_file is None:
            output_path = self.dir_path / "output"
      else:
            output_path = self.path_file

      logger.info("Guardando archivos de salida en %s", output_path)

      data.to_excel(f"{output_path}.xlsx", index=False)
      data.to_csv(f"{output_path}.csv", index=False, sep=";", encoding="utf-8")

      logger.info("Archivos guardados correctamente")

    except Exception:
        logger.exception("Error al guardar archivos de salida")
        return False, "Exception"

    return success, message


