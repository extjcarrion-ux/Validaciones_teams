import json
from datetime import datetime

def objetener_arreglo(data,value:str = "choices"):
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


def objetener_fecha():
    date_     = datetime.now().strftime("%d-%m-%Y")
    datetime_ = datetime.now().strftime("%d-%m-%Y")
    try:
        print(date_)
        print(datetime_)

    except Exception as e:
        print(str(e))
    
    return date_

objetener_fecha()

