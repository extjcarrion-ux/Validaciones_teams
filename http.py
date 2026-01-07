import requests
import json
import time
# 1. La URL de tu Power Automate
url = "https://defaultc4a8886bf140478bac47249555c30a.fd.environment.api.powerplatform.com:443/powerautomate/automations/direct/workflows/4e006e90e0fd42189f02eb0c11f198bf/triggers/manual/paths/invoke?api-version=1&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=zUVsJTLAY1pDGDUwB0wBQcgN1bfADSjjqyeNbgp4ZiM"

### 2. El Payload (Los datos que vas a enviar)
# He usado los datos de tu ejemplo anterior que coinciden con el esquema
destinatario_valor = "ext_jcarrion@Falabella.cl"
mensaje_valor = """
{
    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
    "type": "AdaptiveCard",
    "version": "1.4",
    "body": [
        {
            "type": "TextBlock",
            "text": "Validación de equipo - aaarancibiad@sodimac.cl",
            "weight": "Bolder",
            "size": "Medium"
        },
        {
            "type": "TextBlock",
            "text": "Selecciona qué colaboradores pertenecen a tu equipo:",
            "wrap": true
        },
        {
            "type": "Input.ChoiceSet",
            "id": "equipo_validado",
            "isMultiSelect": true,
            "style": "expanded",
            "choices": [
                {
                    "title": "Pietro Angelo Giacchero Mebus (pgiacchero@sodimac.cl)",
                    "value": "pgiacchero@sodimac.cl"
                },
                {
                    "title": "Valentina Cueto Gaozza (vcueto@sodimac.cl)",
                    "value": "vcueto@sodimac.cl"
                },
                {
                    "title": "Pablo Andres Assael Repetto (paassael@sodimac.cl)",
                    "value": "paassael@sodimac.cl"
                },
                {
                    "title": "Monica Javiera Vega Sobarzo (mvegas@sodimac.cl)",
                    "value": "mvegas@sodimac.cl"
                },
                {
                    "title": "Francisco Ignacio Cubillos Baldessari (fcubillos@sodimac.cl)",
                    "value": "fcubillos@sodimac.cl"
                },
                {
                    "title": "Aníbal Esteban Segura Flores (asegura@sodimac.cl)",
                    "value": "asegura@sodimac.cl"
                },
                {
                    "title": "Luis Andres Zuñiga Adasme (luazunigaad@sodimac.cl)",
                    "value": "luazunigaad@sodimac.cl"
                },
                {
                    "title": "Pablo Eduardo  Yevenes Vitagliano (peyevenes@sodimac.cl)",
                    "value": "peyevenes@sodimac.cl"
                },
                {
                    "title": "Dino Francisco Girardi Donoso (dgirardi@sodimac.cl)",
                    "value": "dgirardi@sodimac.cl"
                },
                {
                    "title": "Monica Loreto Retamal Olivares (mlretamal@sodimac.cl)",
                    "value": "mlretamal@sodimac.cl"
                }
            ]
        },
        {
            "type": "Input.Toggle",
            "title": "Falta alguien en la lista",
            "id": "falta_gente",
            "valueOn": "1",
            "valueOff": "0"
        }
    ],
    "actions": [
        {
            "type": "Action.Submit",
            "title": "Enviar"
        }
    ]
}
"""

### 3. Cabeceras (Power Automate espera JSON)
headers = {
    "Content-Type": "application/json"
}
for i in range(0,1):
    payload = {
	  "destinatario": destinatario_valor,
 	  "mensaje": mensaje_valor
        }

    response = requests.post(url, json=payload)

    print(f"Envío {i} → Status {response.status_code}")
    print(response.text)

    time.sleep(0.2)

