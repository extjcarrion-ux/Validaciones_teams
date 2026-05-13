##app/flow/flow.py
import time
import pandas as pd
from pathlib import Path
from config.config import settings
from config.log_config import logger
from app.utills.utills import (chunk_dataframe,get_date_time,
                                get_array,read_json_file
                                ,get_encoding,reprocess
                                )
from app.processData.read_data import ProcessFile
from app.bigQuery.client.client import BigQueryClient
from app.teams_validation_service.http import EnvSolicitud
from app.bigQuery.bigquery_repository import BigQueryTableRepository
from app.bigQuery.merge_config.merge_config import MERGE_CONFIG
from app.teams_validation_service.fuente_de_la_verdad import ListaUsuarios
from typing import Tuple, Dict, Any

# -------------------------------------------------- #
def step_leer_query(key: str | None = None) -> Tuple[bool, Dict[str, Any]]:
    json_query = read_json_file(settings.directory_querys)

    if key is None:
        logger.info("Leyendo queries desde archivo JSON")
        return True, json_query

    if key not in json_query:
        logger.error("La key '%s' no se encuentra en el archivo JSON", key)
        return False, dict()

    logger.info("Leyendo key=%s desde archivo JSON", key)
    json_key = json_query.get(key)
    return True, json_key if isinstance(json_key, dict) else {}

# -------------------------------------------------- #
def step_cargar_bigquery(df: pd.DataFrame, tabla: str, dropTable: bool):    
    allowed = settings.allowed_bq_tables
    if tabla not in allowed.values():
        raise ValueError(
            "La tabla '%s' no se encuentra dentro de las tablas permitidas",
            tabla
        )

    logger.info(
        "Cargando datos en BigQuery | tabla=%s | registros=%d | dropTable=%s",
        tabla,
        len(df),
        dropTable
    )

    repo = BigQueryTableRepository(
        table=str(tabla),
        project_id=str(settings.project_qa),
        client=BigQueryClient().ambientQA()
    )

    ok, msg = repo.load_staging(df, dropTable)

    if not ok:
        logger.error("Error load_staging | tabla=%s | msg=%s", tabla, msg)
        raise RuntimeError(msg)

    ok, msg = repo.merge_into(
        table_final=tabla,
        config=MERGE_CONFIG[tabla]
    )

    if not ok:
        logger.error("Error merge_into | tabla=%s | msg=%s", tabla, msg)
        raise RuntimeError(msg)

    logger.info("Carga BigQuery finalizada correctamente | tabla=%s", tabla)
    return ok


# -------------------------------------------------- #
def step_descargar_destinatarios(query_key: str, reprocesar: bool = True):
    logger.info(
        "Iniciando descarga de destinatarios | archivo=%s | reprocesar=%s",
        query_key,
        reprocesar)

    success,data_json = step_leer_query(key=query_key)

    if not success:
        logger.error("Error leyendo query para destinatarios | msg=%s", data_json)
        return False, pd.DataFrame()

    sql_file = data_json.get("query_sql")
    json_file = data_json.get("schema")

    if not sql_file:
        raise ValueError("No se encontró 'query_sql' en la configuración")

    if not json_file:
        raise ValueError("No se encontró 'schema json' en la configuración")

    lista = ListaUsuarios(query_key)
    success, msg, archivo = lista.exec_query(reprocesar
                                                ,sql_file=sql_file
                                                ,json_template=json_file)

    logger.info(
        "Descarga de destinatarios exitosa | registros=%d",
        len(archivo))

    return True, pd.DataFrame(archivo)


# -------------------------------------------------- #
def step_registrar_pendientes_bq(archivo: pd.DataFrame):
    logger.info(
        "Registrando pendientes en BigQuery | registros=%d",
        len(archivo))

    df_archivo = archivo.assign(
        status_code=0,
        success=False,
        mensaje=archivo["mensaje"].apply(get_array),
        timestamp=get_date_time())

    df_archivo.rename(
        columns={"mensaje": "lista_colaboradores"},
        inplace=True)

    tabla_bq = settings.allowed_bq_tables["data_teams"]

    ok = step_cargar_bigquery(
        df_archivo,
        tabla_bq,
        dropTable=True)
    return ok

# -------------------------------------------------- #
def step_enviar_formularios(archivo: str):
    logger.info("Enviando formularios | archivo=%s", archivo)

    json_dest = EnvSolicitud(archivo)
    success, msg, df_destinatarios = json_dest.lista_destinatarios()

    if not success:
        logger.error("Error obteniendo destinatarios | msg=%s", msg)
        raise RuntimeError(msg)

    success, result_df = json_dest.envio_json(df_destinatarios)

    if not success:
        logger.error("Error enviando formularios")
        raise RuntimeError("Error enviando formularios")

    logger.info(
        "Formularios enviados correctamente | registros=%d",
        len(result_df)
    )
    return success, pd.DataFrame(result_df)


# -------------------------------------------------- #
def step_cargar_data_automate(path: Path, archivo: str):
    tabla_response = settings.allowed_bq_tables["data_automate"]
    logger.info(
        "Cargando data Automate | archivo=%s | tabla=%s",
        archivo,
        tabla_response
    )
    try:
        data = ProcessFile(path=path
                           ,archivo=archivo)
        parametros = MERGE_CONFIG[tabla_response]
        success, state, df_data = data.read_csv(parametros)

        if not success:
            logger.error("Error leyendo CSV Automate | state=%s", state)
            return False, state

        step_cargar_bigquery(df_data,
                            tabla_response,
                            dropTable=True)
        return True, "OK"
    except Exception:
        logger.exception("Error en step_cargar_data_automate")
        return False, "Exception"


# -------------------------------------------------- #
def step_enviar_y_persistir_por_lotes(
    archivo: str,
    chunk_size: int = settings.chunk_size):

    logger.info(
        "Inicio envío por lotes | archivo=%s | chunk_size=%d",
        archivo
        ,chunk_size)

    tabla_bq  = settings.allowed_bq_tables["data_teams"]
    json_dest = EnvSolicitud(archivo)
    success, msg, df_destinatarios = json_dest.lista_destinatarios()

    ######################################################
    if settings.environment == "QA":
        df_destinatarios["destinatario"] = "ext_jcarrion@Falabella.cl"
    ######################################################
    print(df_destinatarios)

    if not success:
        logger.error("Error obteniendo destinatarios | msg=%s", msg)
        raise RuntimeError(msg)

    total = len(df_destinatarios)
    logger.info("Total destinatarios a procesar: %d", total)

    for idx, df_chunk in enumerate(
        chunk_dataframe(df_destinatarios, chunk_size),start=1):

        logger.info(
            "Procesando lote %d | registros=%d",
            idx,
            len(df_chunk))

        success, df_result = json_dest.envio_json(df_chunk)

        if not success:
            logger.warning(
                "Error en envío lote %d | continuando",
                idx)

        step_cargar_bigquery(
            df_result,
            tabla_bq,
            dropTable=False)

        logger.info(
            "Lote %d persistido en BigQuery | registros=%d",
            idx,
            len(df_result))

        time.sleep(1)

# -------------------------------------------------- #
def step_cargar_dataframe(file_name:str=str(''),reprocesar:bool=True) -> tuple[bool,pd.DataFrame]:
    logger.info("Cargando DataFrame desde archivo | path=%s", file_name)
    path_file = Path(settings.path_output,file_name+".csv")
    try:
        df = pd.read_csv(path_file,sep=";", encoding = get_encoding(path_file))
        logger.info("DataFrame cargado correctamente | registros=%d", len(df))

        if reprocesar:    
            logger.info("Iniciando reprocesamiento de request_id")
            df = reprocess(df)

        if df.empty:
            logger.warning("El DataFrame está vacío después de cargar el archivo")
            return False,pd.DataFrame()

        return True,pd.DataFrame(df)

    except Exception as e:
        logger.error("Error cargando DataFrame | msg=%s", str(e))
        return False,pd.DataFrame()

# -------------------------------------------------- #
def run_full_flow():
    logger.info("Inicio ejecución flujo completo")
    file_dest = "destinatarios"
    success, archivo = step_descargar_destinatarios(file_dest)
    success = step_registrar_pendientes_bq(archivo)

    if success:
        step_enviar_y_persistir_por_lotes(file_dest)

    logger.info("Flujo completo finalizado correctamente")

