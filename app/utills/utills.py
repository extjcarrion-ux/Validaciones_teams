import json
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
