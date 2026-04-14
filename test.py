#app/teams_validation_service/fuente_de_la_verdad.py
import json
from app.utills.utills import read_sql_file
from pathlib import Path
import warnings
import pandas as pd
from config.config import settings
from config.log_config import logger
from app.utills.utills import generar_request_id,reprocess

################ config #################
pd.set_option('display.max_rows', 5)
warnings.simplefilter("ignore", UserWarning)
#########################################

# file_path = "data/query_sql/usuarios_ingles.sql"
# file = read_sql_file(file_path)
# print(file)

directory_querys = {
    "usuarios_ingles": ["app/json_schema/spanish_schema.json"
                        ,"data/query_sql/usuarios_ingles.sql"],
    "usuarios_spanish": ["app/json_schema/spanish_schema.json"
                         ,"data/query_sql/usuarios_spanish"],
    "fuente_de_la_verdad":["app/json_schema/spanish_schema.json"
                         ,"data/query_sql/fuente_de_la_verdad.sql"]
}

def read_json_file(file_path):
    try:
      if not Path(file_path).is_file():
          logger.error("El archivo JSON no existe: %s", file_path)
          return None

      with open(file_path, 'r', encoding='utf-8') as file:
          logger.info("El archivo JSON existe: %s", file_path)          
          return json.load(file)
    
    except Exception as e:
      logger.exception("Error al leer el archivo JSON: %s", file_path)
      return None


for valor, ruta in directory_querys.items():
    if valor == "usuarios_ingles":
        file_path = Path(ruta[0])
        archivo = read_json_file(file_path)



