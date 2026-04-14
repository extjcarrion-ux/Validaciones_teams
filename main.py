# main.py
import os
from app.flow.flow import *

def mostrar_menu():
    print("\n================ MENÚ =================")
    print("1  Descargar destinatarios")
    print("2  Cargar data desde Power Automate (CSV)")
    print("3  Reprocesar + Enviar + Persistir")
    print("4  Enviar + Persistir")
    print("5  Ejecutar flujo completo")
    print("0  Salir")
    print("=======================================")

def main():
    os.system("cls")
    file_dest = "destinatarios"

    while True:
        mostrar_menu()
        respuesta = input("Seleccione una opción: ").strip()
        if respuesta == "1":
            print("➡ Descargando destinatarios")
            success, archivo = step_descargar_destinatarios(
                file_dest=file_dest,
                reprocesar=True
            )

        elif respuesta == "2":
            print("➡ Cargando data desde Power Automate")
            step_cargar_data_automate(
                path="C:/Users/genesys/Downloads",
                archivo="test(Sheet1).csv"
            )

        elif respuesta == "3":
            print("➡ Reprocesando flujo parcial")
            success, archivo = step_descargar_destinatarios(
                file_dest=file_dest,
                reprocesar=True
            )

            if success:
                success = step_registrar_pendientes_bq(archivo)
                if success:
                    step_enviar_y_persistir_por_lotes(file_dest)

        elif respuesta == "4":
            print("➡ Reprocesando flujo parcial - solo envío y persistencia")

            # if success:
            #     success = step_registrar_pendientes_bq(archivo)
            #     if success:
            #         step_enviar_y_persistir_por_lotes(file_dest)

        elif respuesta == "5":
            print("➡ Ejecutando flujo completo")
            run_full_flow()

        elif respuesta == "0":
            print("👋 Saliendo del programa")
            break

        else:
            print(f"❌ Opción '{respuesta}' no válida")

if __name__ == "__main__":
    main()

