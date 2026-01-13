import os
import time
import warnings
import requests
import pandas as pd

from pathlib import Path
from config.config import settings

########### config ##############
pd.set_option('display.max_rows', 5)
warnings.simplefilter("ignore", UserWarning)
#################################

### 1. La URL de tu Power Automate ###
url = str(settings.url_p_automate)

### 2. El Payload (Los datos que vas a enviar) ###
### He usado los datos de tu ejemplo anterior que coinciden con el esquema
class EnvSolicitud:
    def __init__(self,file_dest):
        self.dir_path  = settings.path_output
        self.file_dest = file_dest

    ####################################################
    def listaDestinatarios(self):
        success,message,data = True,"OK",pd.DataFrame()
        try:
            file_dest = Path(self.dir_path,self.file_dest+".xlsx")

            if Path().exists() and file_dest.suffix == ".xlsx":
                data = pd.read_excel(file_dest,sheet_name="Sheet1")

        except Exception as e:
                success,message = False,f"Exception: {e}"

        return success,message,data

    ####################################################
    def creacionjson(self, destinatario: str, mensaje: str):
        stat = True
        result = {
            "destinatario": destinatario,
            "lista_colaboradores": mensaje
        }

        try:
            payload = {
                "destinatario": destinatario,
                "mensaje": mensaje
            }

            response = requests.post(url, json=payload)
            print(f"Envío → Status {response.status_code}")

            result["status_code"] = str(response.status_code)

            time.sleep(0.2)

        except Exception as e:
            stat = False
            result["status_code"] = "400"
            result["error"] = str(e)

        return stat, result


    ####################################################
    def enviojson(self,data:pd.DataFrame):
        lista_result = []
        for row in data.itertuples(index=False):
            response,msn = self.creacionjson(row[0], row[1])
            lista_result.append(
                                {**msn,
                                 "success": response,
                                 "timestamp":pd.Timestamp.now()
                                 })
        
        df_result = pd.DataFrame(lista_result)
        print(df_result)
