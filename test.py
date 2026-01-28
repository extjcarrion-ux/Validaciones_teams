#main.py
import os
import pandas as pd
from app.flow.flow import *
from app.utills.utills import obtener_fecha_hora

################################################
os.system("cls")
################################################
file_dest  = "destinatarios_test"

# sucess,archivo = step_descargar_destinatarios(
#                             file_dest = file_dest
#                              )

# step_registrar_pendientes_bq(archivo)
# -------------------------------------------------- #
# df_archivo = archivo.assign(status_code=None
#                      ,success=False
#                      ,timestamp=obtener_fecha_hora())

# tabla_bq = settings.allowed_bq_tables["data_teams"]

# step_cargar_bigquery(df_archivo
#                      ,tabla_bq)

# run_full_flow()
