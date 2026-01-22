##app/teams_validation_service/http.py
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

class EnvSolicitud:
    def __init__(self,file_dest):
        self.file_dest   = file_dest        
        self.dir_path    = settings.path_output
        self.file_result = settings.path_result

    ####################################################
    def lista_destinatarios(self):
        success,message= True,"OK"
        ### ---------------------------- ###
        print(f"Procesando lista de destinatarios !")
        ### ---------------------------- ###
        file_dest = Path(self.dir_path,self.file_dest+".xlsx")

        if not file_dest.exists():
            return False,f"La ruta {file_dest} no existe",pd.DataFrame()

        if file_dest.suffix != ".xlsx":
            return False,f"El archivo no es un excel",pd.DataFrame()

        try:
            data = pd.read_excel(file_dest,sheet_name="Sheet1")
            print(f"{len(data)} Destinatarios OK!")
            return success,message,data
        ### ---------------------------- ###
        except ValueError as e:
            return False, f"Error en el Excel: {e}", pd.DataFrame()

        except Exception as e:
            return False, f"Error inesperado: {e}", pd.DataFrame()

    ####################################################
    def creacion_json(self, destinatario: str, mensaje: str):
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
    def envio_json(self,data:pd.DataFrame):
        total,i = len(data),1
        success,lista_result,df_result = True,[],pd.DataFrame()
        try:
            for row in data.itertuples(index=False):
                response,msn = self.creacion_json(row[0], row[1])
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
