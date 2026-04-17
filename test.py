#### test.py
import os
from app.flow.flow import *

def main():
    os.system("cls")
    ####################################
    print("➡ Reprocesando flujo parcial")
    success,json_query = step_leer_query()

    if success and json_query:
      for key,value in json_query.items():
        logger.info("Ejecutando flujo para key=%s", key)
        success,archivo=step_cargar_dataframe(key)

        if success:
            success = step_registrar_pendientes_bq(archivo)

            if success:
              step_enviar_y_persistir_por_lotes(key)

if __name__ == "__main__":
    main()



