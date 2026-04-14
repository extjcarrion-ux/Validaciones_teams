##app/flow/flow.py
# app/flow/flow.py
import time
import pandas as pd
from config.config import settings
from config.log_config import logger

from app.utills.utills import (
    chunk_dataframe,
    get_date_time,
    get_array
)
from app.processData.read_data import ProcessFile
from app.bigQuery.client.client import BigQueryClient
from app.teams_validation_service.http import EnvSolicitud
from app.bigQuery.bigquery_repository import BigQueryTableRepository
from app.bigQuery.merge_config.merge_config import MERGE_CONFIG
from app.teams_validation_service.fuente_de_la_verdad import ListaUsuarios


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
def step_descargar_destinatarios(file_dest: str, reprocesar: bool = True):
    logger.info(
        "Iniciando descarga de destinatarios | archivo=%s | reprocesar=%s",
        file_dest,
        reprocesar
    )

    lista = ListaUsuarios(file_dest)
    success, msg, archivo = lista.exec_query(reprocesar)

    if not success:
        logger.error("Error descargando destinatarios | msg=%s", msg)
        raise RuntimeError(msg)

    logger.info(
        "Descarga de destinatarios exitosa | registros=%d",
        len(archivo)
    )
    return success, archivo


# -------------------------------------------------- #
def step_registrar_pendientes_bq(archivo: pd.DataFrame):
    logger.info(
        "Registrando pendientes en BigQuery | registros=%d",
        len(archivo)
    )

    df_archivo = archivo.assign(
        status_code=0,
        success=False,
        mensaje=archivo["mensaje"].apply(get_array),
        timestamp=get_date_time()
    )

    df_archivo.rename(
        columns={"mensaje": "lista_colaboradores"},
        inplace=True
    )

    tabla_bq = settings.allowed_bq_tables["data_teams"]

    ok = step_cargar_bigquery(
        df_archivo,
        tabla_bq,
        dropTable=True
    )

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
    return success, result_df


# -------------------------------------------------- #
def step_cargar_data_automate(path: str, archivo: str):
    tabla_response = settings.allowed_bq_tables["data_automate"]
    logger.info(
        "Cargando data Automate | archivo=%s | tabla=%s",
        archivo,
        tabla_response
    )
    try:
        data = ProcessFile(path=path, archivo=archivo)
        parametros = MERGE_CONFIG[tabla_response]
        success, state, df_data = data.read_csv(parametros)
        if not success:
            logger.error("Error leyendo CSV Automate | state=%s", state)
            return False, state
        step_cargar_bigquery(
            df_data,
            tabla_response,
            dropTable=True
        )
        return True, "OK"
    except Exception:
        logger.exception("Error en step_cargar_data_automate")
        return False, "Exception"


# -------------------------------------------------- #
def step_enviar_y_persistir_por_lotes(
    archivo: str,
    chunk_size: int = 5
):
    logger.info(
        "Inicio envío por lotes | archivo=%s | chunk_size=%d",
        archivo,
        chunk_size
    )
    tabla_bq = settings.allowed_bq_tables["data_teams"]
    json_dest = EnvSolicitud(archivo)
    success, msg, df_destinatarios = json_dest.lista_destinatarios()

    if not success:
        logger.error("Error obteniendo destinatarios | msg=%s", msg)
        raise RuntimeError(msg)

    total = len(df_destinatarios)
    logger.info("Total destinatarios a procesar: %d", total)

    for idx, df_chunk in enumerate(
        chunk_dataframe(df_destinatarios, chunk_size),
        start=1
    ):
        logger.info(
            "Procesando lote %d | registros=%d",
            idx,
            len(df_chunk)
        )
        success, df_result = json_dest.envio_json(df_chunk)
        if not success:
            logger.warning(
                "Error en envío lote %d | continuando",
                idx
            )
        step_cargar_bigquery(
            df_result,
            tabla_bq,
            dropTable=False
        )
        logger.info(
            "Lote %d persistido en BigQuery | registros=%d",
            idx,
            len(df_result)
        )
        time.sleep(1)


# -------------------------------------------------- #
def run_full_flow():
    logger.info("Inicio ejecución flujo completo")
    file_dest = "destinatarios"
    success, archivo = step_descargar_destinatarios(file_dest)
    success = step_registrar_pendientes_bq(archivo)

    if success:
        step_enviar_y_persistir_por_lotes(file_dest)

    logger.info("Flujo completo finalizado correctamente")
