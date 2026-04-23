#### test.py
import os
from pathlib import Path
from config.config import settings
from config.log_config import logger
from app.flow.flow import (read_json_file,
    step_descargar_destinatarios,
    step_cargar_data_automate,
    step_registrar_pendientes_bq,
    step_enviar_y_persistir_por_lotes,
    run_full_flow,
    step_leer_query,
    step_cargar_dataframe
    )

def main():
    os.system("cls")
    json_query = read_json_file(settings.directory_querys)

    for item in json_query:
        logger.info("Procesando key=%s", item)
        success, archivo = step_descargar_destinatarios(
                                        query_key=item,
                                        reprocesar=True)

main()



