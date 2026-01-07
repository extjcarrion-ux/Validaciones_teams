#!/usr/bin/env python
# Librerias
import pandas as pd
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
from tkinter import filedialog, simpledialog
from warnings import filterwarnings
import numpy as np
from datetime import datetime, timezone
import pytz
from google.cloud import bigquery
from google.cloud.exceptions import NotFound
from tkinter import Tk
import tkinter as tk
# Define la zona horaria GMT-4
gmt_minus_4 = pytz.timezone("Etc/GMT+4")

# Obtén la hora actual en GMT-4
current_timestamp = datetime.now(gmt_minus_4)
filterwarnings("ignore")
# Conexiones a BigQuery
#QA = bigquery.Client("tc-sc-bi-bigdata-edp-qa")
# In[3]:

import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:/Users/genesys/AppData/Roaming/gcloud/application_default_credentials.json"
from google.cloud import bigquery

# Inicializa un cliente de BigQuery
QA = bigquery.Client(project = 'tc-sc-bi-bigdata-edp-qa')

# In[5]:

root = tk.Tk()
root.withdraw()  # Oculta la ventana principal
root.attributes('-topmost', True)  # Asegura que esté en primer plano
# Mostrar el diálogo para abrir archivo
file_path = filedialog.askopenfilename()
# Cierra la ventana raíz después de seleccionar archivo
root.destroy()
file_name = os.path.splitext(os.path.basename(file_path))[0]
file_name = file_name.replace('_', '-')

# Detectar extensión
ext = os.path.splitext(file_path)[1].lower()

# Leer archivo según tipo
if ext == ".csv":
    df = pd.read_csv(file_path, sep=";", decimal=".")
elif ext == ".xlsx":
    df = pd.read_excel(file_path, sheet_name=0,engine="openpyxl")
else:
    raise ValueError("Formato no soportado. Usa .csv o .xlsx")

# In[11]:
df_ok = df[ df['TareaCompletada'].isna() ]


# In[61]:
df_ok_aux = df_ok[['Usuario','colaboradores']]
df_ok_aux['Usuario'] = df_ok_aux['Usuario'].str.lower()
df_ok_aux['colaboradores'] = df_ok_aux['colaboradores'].str.lower()


# In[62]:
print(df_ok_aux)

# In[53]:


# Inicializa un cliente de BigQuery
client = bigquery.Client(project = 'tc-sc-bi-bigdata-edp-prod')
# Define tu consulta
query = """
with test as (
        select *
        from `tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear`
        where emp_update_period = 202507
        )

        select
        lower(hc.emp_id_corp_clear) emp_id_corp_clear,
        lower(hc.emp_corp_email_clear) emp_corp_email_clear,

        concat(
        coalesce(hc.emp_first_name_clear,''),' ',
        coalesce(hc.emp_last_name_1_clear,''),' ',
        coalesce(hc.emp_last_name_2_clear,'')) as emp_name,

        lower(mana.emp_id_corp_clear) as manager_id_corp_clear ,
        lower(mana.emp_corp_email_clear) as manager_corp_email_clear,

        concat(
        coalesce(mana.emp_first_name_clear,''),' ',
        coalesce(mana.emp_last_name_1_clear,''),' ',
        coalesce(mana.emp_last_name_2_clear,'')) as manager_name,

        from test hc

        left join test as mana on mana.emp_id_corp_clear = hc.emp_manager_id_corp_clear

        where true
        and hc.emp_update_period = 202507
        and mana.emp_id_corp_clear in ('CL0113255440', 'CL0116611114', 'CL0117676715', 'PE0344922895', 'PE0346377208'
        ,'CO141026253519', 'AR402726561361', 'CL0113769917', 'CL0117339378', 'CL0116010998', 'CL0116264784', 'CO141101455947','PE06681400', 'PE0343016928', 'MX35GODI820920MN5', 'CL017968029', 'CL0118276140', 'CL0116795739', 'MX35JIDF721120R47'
        ,'CO141057579366', 'CL0117597158', 'CL0116649099', 'PE0342689045', 'PE0341114930', 'PE0344415844', 'CL0113691170','CL0112937774', 'CL0113915344', 'CL0117253535', 'CO141012426140', 'CO141020774667', 'PE0344829253', 'CL0112590666'
        ,'CL0115395244', 'CO1452899937', 'MX35NACE8901082S9', 'AR402095636597', 'CL0119284547', 'CL0117048285', 'CL0117704142', 'CO18711048','PE0374626872', 'PE069055420', 'MX21GAFF810819HNLRLR02', 'CL0119201131', 'PE0342508651', 'CL0127725040', 'MX21ZALB921126MSPVRL02'
        ,'CL0128138063', 'CL0117705024', 'CL0115375751', 'CL0117664596', 'PE0342613166', 'AR402321850295', 'AR402031008830', 'IN49AMUPB4230B','PE0341587358', 'CL0117535674', 'CL0117310192', 'CL0110618635', 'PE0345633531', 'PE0340170668', 'CL0116553836', 'CL0124017136'
        ,'CO141032396235', 'CL0116608617', 'CL0117265125', 'PE08223130712', 'CL0117959874', 'CL0116956075', 'CL0114293973', 'CL0115075267', 'CL019571294', 'CL0116143373', 'CL0114450602', 'CL0115939676', 'CL0148219362', 'PE0346054389', 'CL0116410935', 'CL0110496720', 'CL0116210318', 'CL0113434415', 'CL0113433378', 'CL0119246425', 'CL0113633988', 'PE066993698', 'CL0115941512', 'CL0110972854', 'CO1443868999', 'CL0114616328', 'CO141022377871', 'CL0114382489', 'CO141000119773', 'PE0344691719', 'PE0343669966', 'CL0116714957', 'CO181035126', 'CO181035122', 'CL0118393459', 'CL0123696318', 'CL0119620027', 'CL0117498949', 'CO141004214116', 'CL0117346899', 'CO1453114157', 'CL0126660742', 'CL0115544175', 'CL0115397985', 'CL0116874042', 'CO141075225707', 'PE0345359377', 'PE0340286603', 'CL0119023651', 'CL0126258377', 'CO141018428154', 'CO181009123', 'CL0117697170', 'CL0116122757', 'CL0116008758', 'PE0342264769', 'CL0116017548', 'AR402034559794', 'CO141069433680', 'CL0112121413', 'CL0126485375', 'CO141016039269', 'CL0113281601', 'PE0341814900', 'PE0347729153', 'PE0370359914', 'CL0118805473', 'CL0115352989', 'CL017048946', 'PE0309335439', 'PE0346032135', 'CL0117058625', 'CL0117962416', 'PE0345910938', 'PE0347584517', 'CL0125347261', 'CL0115963491', 'CL0113047700', 'PE0310300518', 'CL0115610915', 'PE0375444425', 'CL0116020445', 'PE0346364067', 'CL0119638485', 'CL0117168568', 'CL0115561713', 'CL0110856654', 'CO141015394943', 'PE0342548020', 'PE0342859004', 'CL0125793812', 'MX21CUZA910826HDFRVR01', 'CL0115322182', 'CL0148201808', 'CO141020754041', 'CO141018437485', 'AR402738671898', 'PE0344290895', 'CO141000375931', 'CO141110517643', 'PE0370294814', 'PE0376609015', 'CL0117408730', 'PE0370036337', 'PE0340555095', 'PE0343168040', 'MX21JARB931215HNLSDR07', 'CL0117672683', 'CL0115645770', 'CL0118569381', 'CL0118364237')
"""
# Ejecuta la consulta
query_job = client.query(query)

# Recupera los resultados de la consulta y conviértelos en un DataFrame de Pandas
df_hc = query_job.result().to_dataframe()

# In[54]:
df_hc_aux = df_hc[['manager_corp_email_clear', 'emp_corp_email_clear']]

# In[55]:
df_hc_aux.sort_values(by='manager_corp_email_clear')

# In[56]:
df_grouped = df_hc_aux.groupby('manager_corp_email_clear').agg({
    'emp_corp_email_clear': lambda x: ', '.join(map(str, x))
}).reset_index()


# In[63]:
df_grouped = df_ok_aux
df_grouped['colaboradores'] = df_grouped['colaboradores'].apply(
    lambda x: str(x).split(',') if pd.notnull(x) else [])
df_flat = df_grouped.explode('colaboradores').reset_index(drop=True)

###############
print(df_flat)
# In[64]:

###############
df_merged = df_hc_aux.merge(
    df_flat,
    left_on=['manager_corp_email_clear', 'emp_corp_email_clear'],
    right_on=['Usuario', 'colaboradores'],
    how='left'  # o 'left' si querés mantener todos los de df_hc_aux
)


# In[65]:
print(df_merged)
#[ ~ df_merged['Usuario'].isna() ]
# In[69]:
from datetime import date
df_merged.to_excel(f'resultado_{date.today().strftime('%d%m%Y')}.xlsx', index=False)

