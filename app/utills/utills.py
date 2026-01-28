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
def chunk_dataframe(df: pd.DataFrame, chunk_size: int):
    logger.info(f"Ejecutando chunk_dataframe" )
    for i in range(0, len(df), chunk_size):
        yield df.iloc[i:i + chunk_size]

# -------------------------------------------------- #
def generar_request_id(destinatario: str) -> str:
    fecha = datetime.now(timezone.utc).date().isoformat()
    raw = f"{destinatario.lower().strip()}" #|{fecha}
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
        
        ambiente   = f"{settings.project_qa}.{settings.bigquery_sandbox_qa}"
        repo = BigQueryTableRepository(table = str("test")
                                    , project_id = str(settings.project_qa)
                                    , client = BigQueryClient().ambientQA())
        query_search = f"""
                select
                case
                when b.submitActionId = 'Enviar' then a.request_id
                when b.submitActionId is null and a.status_code = 202 then a.request_id
                else "No Aplica" end as request_id
                from `{ambiente}.teams_validation_data` as a
                left join ( 
                            select *                
                            from `{ambiente}.response_validation_data` as b
                            QUALIFY ROW_NUMBER() OVER (PARTITION BY b.request_id ORDER BY b.responseTime DESC) = 1
                            ) as b
                on a.request_id = b.request_id
                where true
                and a.request_id in ('{lista_request_id}')
                order by a.timestamp desc"""
        result_query = repo.read_query(query_search)
        return result_query
    
    except Exception as e:
            logger.error(f"Exception : {e}" )
            return pd.DataFrame()


# -------------------------------------------------- #
def reprocess(dfA: pd.DataFrame) -> pd.DataFrame:
    logger.info("Reprocesando %d registros", len(dfA))
    try:
        lista_request = dfA["request_id"].tolist()
        df_ids_b = validate_request_id(lista_request)

        if df_ids_b.empty:
            logger.info("No hay request_id a excluir")
            return dfA

        ids_b = set(df_ids_b["request_id"])
        dfA_filtrado = dfA[~dfA["request_id"].isin(ids_b)]

        logger.info("Registros finales: %d", len(dfA_filtrado))
        return dfA_filtrado.copy()

    except Exception:
        logger.exception("Error durante reprocesamiento")
        return dfA



