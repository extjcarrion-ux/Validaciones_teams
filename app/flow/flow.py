from app.teams_validation_service.fuente_de_la_verdad import ListaUsuarios
from app.teams_validation_service.http import EnvSolicitud
from app.bigQuery.bigquery_repository import BigQueryTableRepository
from app.bigQuery.client.client import BigQueryClient
from config.config import settings


# --------------------------------------------------
def step_descargar_destinatarios(file_dest: str):
    lista = ListaUsuarios(file_dest)
    success, msn, archivo = lista.exec_query()
    if not success:
        raise RuntimeError(msn)
    return archivo

# --------------------------------------------------
def step_enviar_formularios(archivo: str):
    json_dest          = EnvSolicitud(archivo)
    df_destinatarios   = json_dest.listaDestinatarios()
    success, result_df = json_dest.enviojson(df_destinatarios[2])
    if not success:
        raise RuntimeError("Error enviando formularios")

    return success,result_df

# --------------------------------------------------
def step_cargar_bigquery(df):
    client = BigQueryClient().ambientQA()
    tabla = str(settings.table_sandbox_qa)
    project_id = str(settings.project_qa)

    repo = BigQueryTableRepository(tabla, project_id, client)
    repo.load_staging(df)
    repo.merge_into(tabla, "request_id")

# --------------------------------------------------
def run_full_flow():
    archivo = step_descargar_destinatarios("destinatarios_test")
    df = step_enviar_formularios(str(archivo))
    step_cargar_bigquery(df)


