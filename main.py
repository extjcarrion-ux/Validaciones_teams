import os
import pandas as pd
from app.flow.flow import *
from config.config import settings

##################################
os.system("cls")
##################################

file_dest  = "destinatarios_test"
step_descargar_destinatarios(file_dest)

##################################
# sucess,df_destinatarios = step_enviar_formularios(file_dest)

# ##################################
# if sucess:
#     step_cargar_bigquery(df_destinatarios)

