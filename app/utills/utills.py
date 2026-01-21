import json
import chardet
from pathlib import Path
from datetime import datetime, timezone

def obtener_arreglo(data,value:str = "choices"):
    choices,lista_resul = [],[]
    data = json.loads(data)

    try:
        for item in data.get("body", []):
            if item.get("type") == "Input.ChoiceSet":
                choices = item.get(value, [])
                break

        emails = [c["value"] for c in choices]

        for c in choices:
            lista_resul.append(c["value"])

    except Exception as e:
        lista_resul.append(str(e))
    
    return lista_resul


def obtener_fecha_hora() -> datetime:
    return datetime.now(timezone.utc)

def get_encoding(ruta:Path):
    try:
        with open(ruta, "rb") as f:
            result = chardet.detect(f.read(10000))
            encoding = result.get("encoding")

    except Exception as e:
        print("Error Enconding:", e)
        encoding = "utf-8"

    return str(encoding)

