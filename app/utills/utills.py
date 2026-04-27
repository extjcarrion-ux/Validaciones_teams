#app/utills/utills.py
import json
import chardet
import hashlib
import pandas as pd
import random as rd
from pathlib import Path
from datetime import datetime, timezone,date
from config.config import settings
from config.log_config import logger
from app.bigQuery.bigquery_repository import BigQueryTableRepository
from app.bigQuery.client.client import BigQueryClient

# -------------------------------------------------- #
def get_array(data,value:str = "choices"):
    logger.info(f"Ejecutando get_array" )
    choices,lista_resul = [],[]
    data = json.loads(data)
    try:
        for item in data.get("body", []):
            if item.get("type") == "Input.ChoiceSet":
                choices = item.get(value, [])
                break

                emails = [c["value"] for c in choices]

        for c in choices:
            lista_resul.append(c["value"])

    except Exception as e:
        logger.error(f"Exception : {e}")
        lista_resul.append(str(e))
    
    return lista_resul

# -------------------------------------------------- #
def get_date_time() -> datetime:
    return datetime.now(timezone.utc)

# -------------------------------------------------- #
def get_encoding(ruta:Path):
    logger.info(f"Ejecutando get_encoding" )
    try:
        with open(ruta, "rb") as f:
            result = chardet.detect(f.read(10000))
            encoding = result.get("encoding")

    except Exception as e:
        logger.error(f"Error Enconding : {e}" )
        encoding = "utf-8"

    return str(encoding)
# -------------------------------------------------- #
def read_sql_file(file_path) -> tuple[bool,str]:
    if not Path(file_path).is_file():
        logger.error(f"El archivo {file_path} no existe.")
        return False, f"El archivo {file_path} no existe."

    file_path = Path(file_path)
    with open(file_path, 'r') as file:
        logger.info(f"El archivo {file_path} existe.")        
        return True,file.read()

def read_json_file(file_path):
    try:
      if not Path(file_path).is_file():
          logger.error("El archivo JSON no existe: %s", file_path)
          return {}

      with open(file_path, 'r', encoding='utf-8') as file:
          logger.info("El archivo JSON existe: %s", file_path)          
          return json.load(file)
    
    except Exception as e:
      logger.exception("Error al leer el archivo JSON: %s", file_path)
      return {}

# -------------------------------------------------- #
def chunk_dataframe(df: pd.DataFrame, chunk_size: int):
    logger.info(f"Ejecutando chunk_dataframe" )
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]

# -------------------------------------------------- #
def generar_request_id(destinatario: str) -> str:
    fecha = datetime.month
    raw   = f"{destinatario.lower().strip()}|{fecha}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# -------------------------------------------------- #
def random_mail():    
    correo = rd.choice(["ext_fgonzalezc@Falabella.cl","ext_jcarrion@Falabella.cl"
                    "tmorada@Falabella.cl","migarciab@Falabella.cl"])

    return correo

# -------------------------------------------------- #
def validate_request_id(request_id:list) -> pd.DataFrame:
    logger.info(f"Ejecutando validate_request_id" )
    try:
        lista_request_id = "','".join(request_id)
        repo = BigQueryTableRepository(table = str("test")
                                    , project_id = str(settings.project_qa)
                                    , client = BigQueryClient().ambientQA())
        query_search = f"""
            with teams_validation_data
            as
            (
            select *
            from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
            QUALIFY ROW_NUMBER() OVER (PARTITION BY a.destinatario ORDER BY a.timestamp DESC) = 1
            )
            select
            case
            when trim(b.submitActionId) = 'Enviar' then a.destinatario
            when trim(b.submitActionId) in ('Flujo quedó esperando - Nadie respondió la tarjeta'
                                            ,'Error técnico - Tarjeta no válida o fallo de Teams')
            and b.Q <3 then "Reenviar Aplica"
            when trim(b.submitActionId) = "" and a.status_code = 202 then a.destinatario
            ---"No Aplica Reenviar"
            else a.destinatario end as destinatario

            from `teams_validation_data` as a
            left join ( 
                    select b.*,c.Q
                    from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
                    -------------------------------------
                    left join (
                                select b.request_id,b.submitActionId, count(b.submitActionId) Q
                                from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
                                group by b.request_id,b.submitActionId
                    ) as c on b.request_id = c.request_id
                    -------------------------------------
                    QUALIFY ROW_NUMBER() OVER (PARTITION BY b.request_id ORDER BY b.responseTime DESC) = 1
                    ) as b
            on a.request_id = b.request_id
            where true
        and a.destinatario in ('{lista_request_id}')
        order by a.timestamp desc
        """
        result_query = repo.read_query(query_search)
        return result_query

    except Exception as e:
            logger.error(f"Exception : {e}" )
            return pd.DataFrame()

# -------------------------------------------------- #
def reprocess(dfA: pd.DataFrame) -> pd.DataFrame:
    logger.info("Reprocesando %d registros", len(dfA))
    try:
        lista_request = dfA["destinatario"].tolist()
        df_ids_b = validate_request_id(lista_request)

        if df_ids_b.empty:
            logger.info("No hay request_id a excluir")
            return dfA

        ids_b = set(df_ids_b["destinatario"])

        ### se excluyen los datos de ids_b
        dfA_filtrado = dfA[~dfA["destinatario"].isin(ids_b)]

        logger.info("Registros finales: %d", len(dfA_filtrado))
        return dfA_filtrado.copy()

    except Exception:
        logger.exception("Error durante reprocesamiento")
        return dfA

