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
                  from `{settings.project_prod}.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear`
                  where emp_update_period = 202507
                  )

              select
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
              left join test as mana on mana.emp_id_corp_clear = hc.emp_manager_id_corp_clear

              where true 
              and hc.emp_update_period = 202507
              --and mana.emp_id_corp_clear in ( 'CL0118170395','CL0126651263','CL0118022327','CL0119309600')
              and mana.emp_id_corp_clear in ( 
              SELECT emp_id_corp_clear FROM `tc-sc-bi-bigdata-edp-qa.sbox_tmorada.fuente-verdad-jefes`
              where not emp_id_corp_clear in ('CO181133977', 'PE068179664', 'PE067043184', 'CO18378379', 'CL0125451772', 'CL0112032587'
              , 'CO18378381', 'CL0148224663', 'CL0112854914', 'CL019979460', 'CL0113442409', 'CL0124547340', 'PE037872325', 'CL0114242364', 'CL0144477029', 'CL0113924832')
              limit 4
              )
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
                    "text": "Selecciona qué colaboradores pertenecen a tu equipo:",
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

      self.downloadData(df_mensajes)

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


