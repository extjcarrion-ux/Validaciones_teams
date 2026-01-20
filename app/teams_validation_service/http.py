import time
import uuid
import warnings
import requests
import pandas as pd
from pathlib import Path

from config.config import settings
from app.utills.utills import obtener_arreglo,obtener_fecha_hora

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
        self.dir_path    = settings.path_output
        self.file_dest   = file_dest
        self.file_result = settings.path_result

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
        colaboradores = obtener_arreglo(mensaje)
        requests_id = str(uuid.uuid4())
        stat = True

        result = {
            "request_id":requests_id,
            "destinatario": destinatario,
            "lista_colaboradores": colaboradores
        }

        try:
            payload = {
                "request_id":requests_id,
                "destinatario": destinatario,
                "mensaje": mensaje
            }

            response = requests.post(url, json=payload)
            result["status_code"] = int(response.status_code)

            time.sleep(0.2)

        except Exception as e:
            stat = False
            result["status_code"] = int(400)
            result["error"] = str(e)

        return stat, result

    ####################################################
    def enviojson(self,data:pd.DataFrame):
        total,i = len(data),1
        success,lista_result,df_result = True,[],pd.DataFrame()
        try:
            for row in data.itertuples(index=False):
                response,msn = self.creacionjson(row[0], row[1])
                lista_result.append(
                                    {**msn,
                                    "success": response,
                                    "timestamp":obtener_fecha_hora()
                                    })

                print(f"""  {i}/{total} - {row[0]} - status code:{msn.get("status_code") }""")
                i = i+1

            df_result = pd.DataFrame(lista_result)
            df_result.to_csv(Path(self.file_result,"resultado.csv"), sep=";",header=True)

        except Exception as e:
            print(e)

        return success,df_result

