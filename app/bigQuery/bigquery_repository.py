## app/bigquery/bigquery_table.py
from google.cloud import bigquery
from google.cloud.bigquery.exceptions import BigQueryError
import pandas as pd

class BigQueryTableRepository:
    def __init__(self, table, project_id, client):
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
        project = f"{self.project_id}.{self.sandbox}"
        ### ---------------------------- ###
        print(f"""Subiendo datos de la tabla {self.stg_table} !\n
              {df.head(5) } \n""")
        ### ---------------------------- ###
        try:
            if df.empty:
                raise ValueError("Dataframe vacio")

            query = f"""
                DROP TABLE IF EXISTS `{project}.{self.stg_table}`;
                """
      ################# Ejecuta la consulta ##################
            query_job = self.client.query(query)

            table_id = f"{self.sandbox}.{self.stg_table}"
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
    def merge_into(self, table_final: str, config: dict):
        project = f"{self.project_id}.{self.sandbox}"
        ### ---------------------------- ###
        print(f"Ejecutando Merge de la tabla {self.table} !")
        ### ---------------------------- ###
        try:
            pk = "".join(config["pk"])
            columns = config["columns"]
            insert_cols = ",\n  ".join(columns.keys())
            insert_vals = ",\n  ".join(columns.values())

            query = f"""                
                MERGE `{project}.{table_final}` t
                USING `{project}.{self.stg_table}` s
                ON t.{pk} = s.{pk}

                WHEN NOT MATCHED THEN
                INSERT (
                         {insert_cols}
                        )
                VALUES (
                    {insert_vals}
                    );
                
                DROP TABLE `{project}.{self.stg_table}`;
                """
      ################# Ejecuta la consulta ##################
            query_job = self.client.query(query)
            response, msn = True,"OK"
            # ### ---------------------------- ###
            print(f"Merge de la tabla {self.table} Exitoso!")
            # ### ---------------------------- ###

        except BigQueryError as e:
            response,msn = False,f"BigQueryError: {e}"
            print(f"BigQueryError: {e}")
        except Exception as e:
            response,msn = False,f"Exception: {e}"
            print(f"Exception: {e}")
        return response,msn


