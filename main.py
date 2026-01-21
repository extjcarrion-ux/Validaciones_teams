import os
import pandas as pd
from app.flow.flow import *
from config.config import settings
from app.processData.read_data import ProcessFile
from app.bigQuery.merge_config.merge_config import MERGE_CONFIG

################################################
os.system("cls")
################################################
file_dest  = "destinatarios_test"
#step_descargar_destinatarios(file_dest)
#################################################
# sucess,df_destinatarios = step_enviar_formularios(file_dest)
# ################################################
# if sucess:
#     tabla = settings.allowed_bq_tables["data_teams"]
#     result = step_cargar_bigquery(df_destinatarios, tabla)

########## carga respuestas #####################
data_auto = step_cargar_data_automate(
    path="C:/Users/genesys/Downloads",
    archivo = "test(Sheet1).csv")

#########################################################
# sucess = True
# df_destinatarios = pd.read_csv("data\\resultado\\resultado.csv"
#                                , sep = ";"
#                                ,index_col=0)