## app/bigquery/bigquery_repository.py
import pandas as pd
from config.log_config import logger
from google.cloud import bigquery
from google.cloud.bigquery.exceptions import BigQueryError

class BigQueryTableRepository:
    def __init__(self, table: str, project_id: str, client):
        self.table = str(table)
        self.project_id = project_id
        self.client = client

        self._load_settings()

        logger.debug(
            "Inicializando BigQueryTableRepository | table=%s | project_id=%s | sandbox=%s",
            self.table,
            self.project_id,
            self.sandbox,
        )
    
    #########################################################
    def _load_settings(self):
        from config.config import settings

        self.environment = settings.project_qa
        self.sandbox = settings.bigquery_sandbox_qa
        self.stg_table = f"stg_{self.table}"

    #########################################################
    def read_query(self, query: str) -> pd.DataFrame:
        logger.debug("Ejecutando query de lectura")

        try:
            df = self.client.query(query).to_dataframe()
            logger.info("Query ejecutada correctamente | filas=%s", len(df))
            return df

        except Exception as e:
            logger.exception("Error ejecutando query de lectura")
            return pd.DataFrame()

    #########################################################
    def load_staging(self, data: pd.DataFrame, dropTable: bool = False):
        df = pd.DataFrame(data)
        project = f"{self.project_id}.{self.sandbox}"

        logger.info(
            "Cargando datos a staging | tabla=%s | filas=%s | dropTable=%s",
            self.stg_table,
            len(df),
            dropTable,
        )
        logger.debug("Preview staging (5 filas):\n%s", df.head(5))
        try:
            if df.empty:
                raise ValueError("Dataframe vacío")

            if dropTable:
                query_drop = f"DROP TABLE IF EXISTS `{project}.{self.stg_table}`;"
                self.client.query(query_drop).result()

                logger.warning(
                    "Tabla staging eliminada antes de la carga | tabla=%s",
                    self.stg_table,
                )

            table_id = f"{self.sandbox}.{self.stg_table}"
            job_config = bigquery.LoadJobConfig(
                schema=[bigquery.SchemaField("request_id", "STRING")]
            )

            self.client.load_table_from_dataframe(
                df, table_id, job_config=job_config
            ).result()

            logger.info("Carga a staging completada exitosamente | tabla=%s", table_id)
            return True, "OK"

        except BigQueryError as e:
            logger.exception("BigQueryError cargando staging | tabla=%s", self.stg_table)
            return False, f"BigQueryError: {e}"

        except Exception as e:
            logger.exception("Error inesperado cargando staging | tabla=%s", self.stg_table)
            return False, f"Exception: {e}"

    #########################################################
    def merge_into(self, table_final: str, config: dict):
        project = f"{self.project_id}.{self.sandbox}"
        logger.info(
            "Iniciando MERGE | staging=%s | tabla_final=%s",
            self.stg_table,
            table_final,
        )

        try:
            # ---------------- PK ---------------- #
            if len(config["pk"]) > 1:
                pk = " AND ".join(f"t.{i} = s.{i}" for i in config["pk"])
            else:
                pk = "".join(f"t.{i} = s.{i}" for i in config["pk"])

            # ---------------- INSERT ---------------- #
            insert_cols = ",\n  ".join(config["columns"].keys())
            insert_vals = ",\n  ".join(config["columns"].values())
            order_by = ", ".join(config["order_by"].keys())

            # ---------------- UPDATE ---------------- #
            update_set = ",\n  ".join(
                f"{col} = {val}" for col, val in config["update"].items()
            )

            # ---------------- WHERE UPDATE ---------------- #
            where_update_cfg = config.get("where_update", {})

            if not any(where_update_cfg.values()):
                where_set = ""
                logger.debug("MERGE sin condición where_update")
            else:
                where_set = "\n ".join(
                    f"AND t.{col} = {val}"
                    for col, val in where_update_cfg.items()
                )

                logger.debug("where_update aplicado: %s", where_set)

            query = f"""
            MERGE `{project}.{table_final}` t
            USING (
                SELECT a.*
                FROM `{project}.{self.stg_table}` AS a
                QUALIFY ROW_NUMBER() OVER (
                    PARTITION BY request_id
                    ORDER BY {order_by} DESC
                ) = 1
            ) s
            ON {pk}

            WHEN MATCHED {where_set}
            THEN
                UPDATE SET
                    {update_set}

            WHEN NOT MATCHED THEN
                INSERT (
                    {insert_cols}
                )
                VALUES (
                    {insert_vals}
                );
            """

            logger.debug("Query MERGE generada:\n%s", query)
            self.client.query(query).result()
            logger.info(
                "MERGE completado exitosamente | tabla_final=%s",
                table_final,
            )
            return True, "OK"

        except BigQueryError as e:
            logger.exception(
                "BigQueryError durante MERGE | tabla_final=%s",
                table_final,
            )
            return False, f"BigQueryError: {e}"

        except Exception as e:
            logger.exception(
                "Error inesperado durante MERGE | tabla_final=%s",
                table_final,
            )
            return False, f"Exception: {e}"


