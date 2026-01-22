## app/processData/read_data.py
import hashlib
import pandas as pd
from pathlib import Path
from pandas.errors import DataError, InvalidColumnName, EmptyDataError
from app.utills.utills import get_encoding,obtener_fecha_hora

class ProcessFile:
    def __init__(self, path: str, archivo: str):
        self.path = Path(path)
        self.file = archivo

    def generate_hash(self, row, cols):
        values = [str(row[c]).strip().lower()
                for c in cols]

        value = "|".join(values)
        return hashlib.sha256(value.encode("utf-8")).hexdigest()

    def read_csv(self, parametros: dict):
        df_result = pd.DataFrame()
        ruta = self.path / self.file
        ### ---------------------------- ###
        print(f"Procesando archivo {ruta}")
        ### ---------------------------- ###
        try:
            if not ruta.exists():
                return False, "La ruta no existe", df_result

            columns_cfg = parametros.get("columns")
            if not columns_cfg:
                return False, "No se especificaron columnas", df_result

            ##########################################################
            columnas = list(columns_cfg.keys())
            df = pd.read_csv(ruta, sep=";", header=0,encoding=get_encoding(ruta))
            df["edp_load_datetime"] = obtener_fecha_hora()

            col_filtradas = [c for c in columnas if c in df.columns]
            col_no_encontradas = [c for c in columnas if c not in df.columns]

            ##########################################################
            if col_no_encontradas:
                return False, f"Error | Columnas no encontradas en el Archivo: {col_no_encontradas}", df_result

            df_result = df[col_filtradas].copy()
            ### elimina si existe vacios en la primera columna de las fila encontradas ###
            df_result = df_result.dropna(subset=[col_filtradas[0]])
            df_result = df_result.fillna("")

            if parametros.get("pk"):
                keys_cols = parametros.get("pk")
            else:
                keys_cols = col_filtradas

            df_result["row_hash"] = df_result.apply(
                self.generate_hash,
                axis=1,
                cols=keys_cols
            )

            ### ---------------------------- ###
            print(f"Archivo {self.file} OK !")
            ### ---------------------------- ###
            return True, "OK", df_result

        except EmptyDataError as e:
            return False, f"EmptyDataError: {e}", df_result
        except InvalidColumnName as e:
            return False, f"InvalidColumnName: {e}", df_result
        except DataError as e:
            return False, f"DataError: {e}", df_result
        except Exception as e:
            return False, str(e), df_result
        

