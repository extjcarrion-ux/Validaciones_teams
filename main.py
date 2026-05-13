# main.py
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
    step_cargar_dataframe)


def mostrar_menu():
    print("\n================ MENÚ =================")
    print("1  Descargar destinatarios")
    print("2  Cargar data desde Power Automate (CSV)")
    print("3  Reprocesar + Enviar + Persistir")
    print("4  Enviar + Persistir (No Descarga destinatarios)")
    print("5  Ejecutar flujo completo")
    print("0  Salir")
    print("=======================================")

def main():
    os.system("cls" if os.name == "nt" else "clear")
    file_dest = "destinatarios"

    while True:
        mostrar_menu()
        respuesta = input("Seleccione una opción: ").strip()

        ##################################
        if respuesta == "1":
            print("➡ Descargando destinatarios")
            json_query = read_json_file(settings.directory_querys)

            for item in json_query:
                logger.info("Procesando key=%s", item)
                success, archivo = step_descargar_destinatarios(
                                                query_key=item,
                                                reprocesar=True)

        ##### actualiza el CSV con Power Automate y lo carga a BigQuery
        elif respuesta == "2":
            print("➡ Cargando data desde Power Automate")
            step_cargar_data_automate(
                path= Path.home()/"Downloads",
                archivo="test(Sheet1).csv"
            )

        ##################################
        elif respuesta == "3":
            success,json_query = step_leer_query()

            if success and json_query:
                for key,value in json_query.items():
                    logger.info("Descargar + Enviar + Persistir para key=%s", key)
                    success, archivo = step_descargar_destinatarios(
                                        query_key=key,
                                        reprocesar=True)

                    if success:
                        success = step_registrar_pendientes_bq(archivo)
                        if success:
                            step_enviar_y_persistir_por_lotes(key)

        ##################################
        elif respuesta == "4":
            print("➡ Reprocesando flujo parcial - solo envío y persistencia")
            success,json_query = step_leer_query()

            if success and json_query:
                for key,value in json_query.items():
                    logger.info("Ejecutando flujo para key=%s", key)
                    success,archivo=step_cargar_dataframe(key,reprocesar=True)

                    if success:
                        success = step_registrar_pendientes_bq(archivo)

                        if success:
                            step_enviar_y_persistir_por_lotes(key)

        ##################################
        elif respuesta == "5":
            print("➡ Ejecutando flujo completo")
            run_full_flow()

        ##################################
        elif respuesta == "0":
            print("👋 Saliendo del programa")
            break

        ##################################
        else:
            print(f"❌ Opción '{respuesta}' no válida")

if __name__ == "__main__":
    main()


