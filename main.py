#main.py
import os
import pandas as pd
from app.flow.flow import *

################################################
os.system("cls")
################################################
file_dest  = "destinatarios_test"
# step_descargar_destinatarios(
#                             file_dest = file_dest
#                              )
################################################
step_enviar_formularios(
    archivo = file_dest
    )

################################################
# data_auto = step_cargar_data_automate(
#     path="C:/Users/genesys/Downloads",
#     archivo = "test(Sheet1).csv")

################################################
# run_full_flow()
################################################

