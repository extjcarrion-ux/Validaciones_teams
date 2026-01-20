## app/bigquery/bigquery_table.py
from google.cloud import bigquery
from google.cloud.bigquery.exceptions import BigQueryError
import pandas as pd

class BigQueryTableRepository:
    def __init__(self, table: str, project_id: str, client):
        self.table      = table
        self.project_id = project_id
        self.client     = client
        self.table      = str(table)
        self._loadSettings()

    #########################################################
    def _loadSettings(self):        
        from config.config import settings
        self.enviroment = settings.project_qa
        self.sandbox    = settings.bigquery_sandbox_qa
        self.stg_table  = str("stg_"+self.table)

    #########################################################
    def read(self) -> pd.DataFrame:
        sql = f"""
            SELECT *
            FROM `{self.sandbox}.{self.table}`
        """
        return self.client.query(sql).to_dataframe()

    #########################################################
    def load_staging(self,data):
        df = pd.DataFrame(data)
        try:
            if df.empty:
                raise ValueError("Dataframe vacio")

            table_id = f"{self.sandbox}.{self.stg_table}"
            print("/n",table_id)
            job_config = bigquery.LoadJobConfig(
                schema=[
                        bigquery.SchemaField("request_id", "STRING"),
                        ])

            job = self.client.load_table_from_dataframe(df, table_id, job_config=job_config)
            job.result()

            response, msn = True,"OK"

        except BigQueryError as e:
            response,msn = False,f"BigQueryError: {e}"
        except Exception as e:
            response,msn = False,f"Exception: {e}"
    
        return response,msn

    #########################################################    
    def merge_into(self,table_final:str, id:str):
        project = f"{self.project_id}.{self.sandbox}"
        try:
            query = f"""
                    MERGE `{project}.{table_final}` t
                    USING `{project}.{self.stg_table}` s
                    on  t.{id} = s.{id}

                    WHEN NOT MATCHED THEN
                    INSERT (
                        request_id,
                        destinatario,
                        lista_colaboradores,
                        status_code,
                        success,
                        timestamp
                    )
                    VALUES (
                        s.request_id,
                        s.destinatario,
                        SPLIT(s.lista_colaboradores, '|'),
                        s.status_code,
                        s.success,
                        timestamp(s.timestamp)
                    );

                    drop table  `{project}.{self.stg_table}`
                """

      ################## Ejecuta la consulta ##################
            query_job = self.client.query(query)
            response, msn = True,"OK"

        except BigQueryError as e:
            response,msn = False,f"BigQueryError: {e}"
        except Exception as e:
            response,msn = False,f"Exception: {e}"
    
        return response,msn


