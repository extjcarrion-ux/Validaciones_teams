import os
from app.fuente_de_la_verdad import ListaUsuarios
from app.http import EnvSolicitud
from config.config import settings

os.system("cls")

### ------------------------------ ###
file_dest = "destinatarios"

### ------------------------------ ###
# lista = ListaUsuarios(file_dest)
# archivo = lista.exec_query()
### ------------------------------ ###


dest      = "ext_jcarrion@Falabella.cl"
mensaje   = "aca"
json_dest = EnvSolicitud(file_dest)


df_destinatarios = json_dest.listaDestinatarios()
res       = json_dest.enviojson(df_destinatarios[2])

