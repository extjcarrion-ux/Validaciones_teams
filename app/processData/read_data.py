## app/processData/read_data.py
import hashlib
import pandas as pd
from pathlib import Path
from pandas.errors import DataError, InvalidColumnName, EmptyDataError
from config.log_config import logger
from app.utills.utills import get_encoding, get_date_time

class ProcessFile:
    def __init__(self, path: Path, archivo: str):
        self.path = Path(path)
        self.file = archivo

    # -------------------------------------------------- #
    def generate_hash(self, row, cols):
        values = [
            str(row[c]).strip().lower()
            for c in cols
        ]
        value = "|".join(values)
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    # -------------------------------------------------- #
    def read_csv(self, parametros: dict):
        df_result = pd.DataFrame()
        ruta = self.path / self.file

        logger.info("Procesando archivo | ruta=%s", ruta)

        try:
            if not ruta.exists():
                logger.error("Archivo no existe | ruta=%s", ruta)
                return False, "La ruta no existe", df_result

            columns_cfg = parametros.get("columns")
            if not columns_cfg:
                logger.error("No se especificaron columnas en parámetros")
                return False, "No se especificaron columnas", df_result

            columnas = list(columns_cfg.keys())

            logger.info(
                "Leyendo archivo CSV | columnas_esperadas=%d",
                len(columnas)
            )
            df = pd.read_csv(
                ruta,
                sep=";",
                header=0,
                encoding=get_encoding(ruta)
            )
            df["edp_load_datetime"] = get_date_time()
            col_filtradas = [c for c in columnas if c in df.columns]
            col_no_encontradas = [c for c in columnas if c not in df.columns]

            if col_no_encontradas:
                logger.error(
                    "Columnas no encontradas en archivo | columnas=%s",
                    col_no_encontradas
                )
                return (
                    False,
                    f"Columnas no encontradas: {col_no_encontradas}",
                    df_result
                )
            df_result = df[col_filtradas].copy()
            # elimina filas con null en la primera columna clave
            df_result = df_result.dropna(subset=[col_filtradas[0]])
            df_result = df_result.fillna("")

            keys_cols = parametros.get("pk") or col_filtradas

            logger.info(
                "Generando hash por fila | columnas_pk=%s",
                keys_cols
            )
            df_result["row_hash"] = df_result.apply(
                self.generate_hash,
                axis=1,
                cols=keys_cols
            )
            logger.info(
                "Archivo procesado correctamente | filas=%d",
                len(df_result)
            )
            return True, "OK", df_result

        except EmptyDataError:
            logger.exception("Archivo CSV vacío")
            return False, "EmptyDataError", df_result

        except InvalidColumnName:
            logger.exception("Nombre de columna inválido")
            return False, "InvalidColumnName", df_result

        except DataError:
            logger.exception("Error de datos en CSV")
            return False, "DataError", df_result

        except Exception:
            logger.exception("Error inesperado procesando archivo CSV")
            return False, "Exception", df_result

        


