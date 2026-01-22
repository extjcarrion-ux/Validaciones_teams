##app/flow/flow.py
from config.config import settings
from app.processData.read_data import ProcessFile
from app.bigQuery.client.client import BigQueryClient
from app.teams_validation_service.http import EnvSolicitud
from app.bigQuery.bigquery_repository import BigQueryTableRepository
from app.bigQuery.merge_config.merge_config import MERGE_CONFIG
from app.teams_validation_service.fuente_de_la_verdad import ListaUsuarios

# -------------------------------------------------- #
def step_descargar_destinatarios(file_dest: str):
    lista = ListaUsuarios(file_dest)
    success, msn, archivo = lista.exec_query()

    if not success:    
        raise RuntimeError(msn)

    return archivo

# -------------------------------------------------- #
def step_enviar_formularios(archivo: str):
    json_dest = EnvSolicitud(archivo)
    sucess,message,df_destinatarios = json_dest.lista_destinatarios()

    if sucess:
        success, result_df = json_dest.envio_json(df_destinatarios)
        if not success:
            raise RuntimeError("Error enviando formularios")
        return success,result_df
    else:
        print(f"Error:" , {message})

# -------------------------------------------------- #
def step_cargar_bigquery(df, tabla):
    allowed = settings.allowed_bq_tables

    if tabla not in allowed.values():
        return ValueError(
            f"la tabla '{tabla}' no se encuentra dentro de las tablas permitidas"
        )
    repo = BigQueryTableRepository(table = str(tabla)
                                   , project_id = str(settings.project_qa)
                                   , client = BigQueryClient().ambientQA())
    repo.load_staging(df)

    repo.merge_into(
        table_final=tabla,
        config=MERGE_CONFIG[tabla]
    )

# -------------------------------------------------- #
def step_cargar_data_automate(path,archivo):
    tabla_response = settings.allowed_bq_tables["data_automate"]
    data = ProcessFile(path=path
                    ,archivo=archivo)
    parametros = MERGE_CONFIG[tabla_response]
    sucess,state,data = data.read_csv(parametros)
    if sucess:
        step_cargar_bigquery(
            data,
            tabla_response
        )
    else:
        print("Error 'step_cargar_data_automate' ",state)

# -------------------------------------------------- #
def run_full_flow():
    file_dest = str("destinatarios_test")
    # archivo = step_descargar_destinatarios(
    #     file_dest)

    # sucess,df_destinatarios = step_enviar_formularios(
    #                             file_dest)

    #################################################
    # if sucess:
    #     tabla = settings.allowed_bq_tables["data_teams"]
    #     result = step_cargar_bigquery(df_destinatarios, tabla)


