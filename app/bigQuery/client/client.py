## app/bigquery/clien/client.py
from google.cloud import bigquery
from google.cloud.bigquery.exceptions import BigQueryError

class BigQueryClient:
    def __init__(self):
        self.load_credentials()
    
    def load_credentials(self):
        from config.config import settings
        self.sandbox         = settings.bigquery_sandbox_qa
        self.proyect_prod_id = settings.project_prod
        self.proyect_qa_id   = settings.project_qa
        self.proyect_qa_id   = settings.project_qa

    def ambientProd(self):
        clientProd   = bigquery.Client(project=self.proyect_prod_id)

        return clientProd

    def ambientQA(self):
        clientQA   = bigquery.Client(project=self.proyect_qa_id)

        return clientQA