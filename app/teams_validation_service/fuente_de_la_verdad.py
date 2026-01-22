import json
import warnings
import pandas as pd
from pathlib import Path
from google.cloud.bigquery.exceptions import BigQueryError
from app.bigQuery.client.client import BigQueryClient
from config.config import settings

########### config ##############
pd.set_option('display.max_rows', 5)
warnings.simplefilter("ignore", UserWarning)
#################################

class ListaUsuarios:
  def __init__(self,name_file = None, project_id=settings.project_prod):
       self.name_file   = str(name_file)
       self.dir_path    = Path(settings.path_output)
       self.path_file   = Path(settings.path_output,self.name_file)
       self.project_id  = project_id
       self.client      = BigQueryClient().ambientProd()

  #################################################################
  def exec_query(self):
    ### Define tu consulta ###
    success,message,df_mensajes   = True,"OK",pd.DataFrame()
    try:
      query = f"""
              with test as (
                  select *
                  from `tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear` as a
                  where emp_update_period = 202512 and (a.emp_end_date_employer >= "2025-12-31"
                                                        or a.emp_end_date_employer is null)

                  qualify row_number() over(partition by a.emp_id_corp order by emp_start_date_employer desc ) = 1
                  )

              select
              --------------------------------------------
              hc.emp_id_corp_clear,
              hc.emp_corp_email_clear,
              concat(
              coalesce(hc.emp_first_name_clear,''),' ',
              coalesce(hc.emp_last_name_1_clear,''),' ',
              coalesce(hc.emp_last_name_2_clear,'')) as emp_name,

              mana.emp_id_corp_clear as manager_id_corp_clear ,
              mana.emp_corp_email_clear as manager_corp_email_clear,
              concat(
              coalesce(mana.emp_first_name_clear,''),' ',
              coalesce(mana.emp_last_name_1_clear,''),' ',
              coalesce(mana.emp_last_name_2_clear,'')) as manager_name,

              from test hc
              inner join test as mana on mana.emp_id_corp_clear = hc.emp_manager_id_corp_clear
              ---------------------------------------------------
              where true 
              and hc.emp_update_period = 202512
              and hc.employer_fiscal_country not in ('India', 'China')
              and lower(hc.workplace_unified)='casa matriz'
              and hc.emp_job_subfamily_code not in ('TM-4','TM-3')
              ---
              and mana.emp_corp_email_clear is not null
              -------------------
              and lower(mana.emp_corp_email_clear) in ("bespinola@falabella.cl",
              "asotog@falabella.cl",
              "aoliveira@falabella.cl",
              "cpperez@falabella.cl")

              group by all
              qualify count(1) over (partition by mana.emp_id_corp_clear ) < 25
              order by  mana.emp_corp_email_clear,hc.emp_corp_email_clear asc
              limit 10
              """

      ### Ejecuta la consulta
      query_job = self.client.query(query)
      ### Recupera los resultados de la consulta y conviértelos en un DataFrame de Pandas
      df_main = query_job.result().to_dataframe()
      ### Agrupar por manager
      mensajes = []

      for manager, group in df_main.groupby("manager_corp_email_clear"):
          manager_email = manager
          manager_name = group["manager_name"].iloc[0]

          team_members = [
              {
                  "title": json.dumps(f'{row["emp_name"]} ({row["emp_corp_email_clear"]})')[1:-1], #"title": f'{row["emp_name"]} ({row["emp_corp_email_clear"]})',
                  "value": row["emp_corp_email_clear"]
              }
              for _, row in group.iterrows()
          ]

          choices_json_str = ",\n".join(
              f'        {{"title": "{member["title"]}", "value": "{member["value"]}"}}'
              for member in team_members
          )

          #### 3. Utilizar un f-string para construir el JSON completo
          adaptive_card_json_str = f"""
              {{
                "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                  {{
                    "type": "TextBlock",
                    "text": "Validación de equipo - {manager_email}",
                    "weight": "Bolder",
                    "size": "Medium"
                  }},
                  {{
                    "type": "TextBlock",
                    "text": "Selecciona qué colaboradores pertenecieron a tu equipo al 31 de diciembre del 2025:",
                    "wrap": true
                  }},
                  {{
                    "type": "Input.ChoiceSet",
                    "id": "equipo_validado",
                    "isMultiSelect": true,
                    "style": "expanded",
                    "choices": [
              {choices_json_str}
                    ]
                  }}
                ,
                  {{
                      "type": "Input.Toggle",
                      "title": "Falta alguien en la lista",
                      "id": "falta_gente",
                      "valueOn": "1",
                      "valueOff": "0"
                  }}      
                ],
                "actions": [
                  {{
                    "type": "Action.Submit",
                    "title": "Enviar"
                  }}
                ]
              }}
          """

          # 4. (Opcional) Convertir el string JSON a un diccionario de Python
          adaptive_card_dict = json.loads(adaptive_card_json_str)    

          mensajes.append({
              "destinatario": manager,
              "mensaje": adaptive_card_dict
          })


      for m in mensajes:
          m["mensaje"] = json.dumps(m["mensaje"], ensure_ascii=False, indent=4)

      # Crear el DataFrame auxiliar
      df_mensajes = pd.DataFrame(mensajes)
      
      ############## pruebas ################
      df_mensajes["destinatario"] = "ext_jcarrion@Falabella.cl"

      ######################################
      print(f"Archivo con {len(df_mensajes)} Registros")
      success,message = self.downloadData(df_mensajes)

    except BigQueryError as e:
      success,message = False,f"BigQueryError:{e}"  

    except Exception as e:
      success,message = False,f"Exception:{e}"

    return success,message,df_mensajes

  #################################################################
  def downloadData(self,data:pd.DataFrame):
    success,message = True,"OK"
    try:
      if self.name_file == "None":
        name_file = Path(self.dir_path,"output")
        print("paso aca", self.name_file)
      else:
          name_file = self.path_file

      data.to_excel(f"{name_file}.xlsx", index=False)
      data.to_csv(f"{name_file}.csv", index=False,sep=";" ,encoding="utf-8")

      ### -------------------------------------------------- ###
      print("Archivo con Destinatarios Guardado en :",name_file)
      ### -------------------------------------------------- ###

    except Exception as e:
      success,message = False,f"Exception:{e}"

    return success,message


