#app/bigQuery/merge_config/merge_config.py
MERGE_CONFIG = {
    "teams_validation_data": {
        "pk": ["request_id"],
        "columns": {
            "request_id": "s.request_id",
            "destinatario": "s.destinatario",
            "lista_colaboradores": "s.lista_colaboradores",
            "status_code": "s.status_code",
            "success": "s.success",
            "timestamp": "TIMESTAMP(s.timestamp)"
        },
        "update":{
            "status_code": "s.status_code",
            "success": "s.success",
            "timestamp": "TIMESTAMP(s.timestamp)",
            "lista_colaboradores": "s.lista_colaboradores",
            },
        "where_update":{
            "success": "false",
            },
        "order_by":{
            "timestamp": "TIMESTAMP(s.timestamp)"
            }
    },

    "response_validation_data": {
        "pk": ["request_id","responseTime"],
        "columns": {
            "request_id": "s.request_id",
            "messageId": "s.messageId",
            "messageLink": "s.messageLink",
            "responseTime": "s.responseTime",
            "submitActionId": "s.submitActionId",
            "responder_objectId": "s.responder_objectId",
            "responder_tenantId": "s.responder_tenantId",
            "responder_email": "s.responder_email",
            "responder_userPrincipalName": "s.responder_userPrincipalName",
            "responder_displayName": "s.responder_displayName",
            "equipo_validado": "SPLIT(s.equipo_validado, ',')",
            "falta_gente": "s.falta_gente",
            "edp_load_datetime": "TIMESTAMP(s.edp_load_datetime)"
        },
        "update": {
            "request_id": "s.request_id",
            "messageId": "s.messageId",
            "messageLink": "s.messageLink",
            "responseTime": "s.responseTime",
            "submitActionId": "s.submitActionId",
            "responder_objectId": "s.responder_objectId",
            "responder_tenantId": "s.responder_tenantId",
            "responder_email": "s.responder_email",
            "responder_userPrincipalName": "s.responder_userPrincipalName",
            "responder_displayName": "s.responder_displayName",
            "equipo_validado": "SPLIT(s.equipo_validado, ',')",
            "falta_gente": "s.falta_gente",
            "edp_load_datetime": "TIMESTAMP(s.edp_load_datetime)"
    },
        "where_update":{
            "":""
            }
    ,
        "order_by":{
            "responseTime": "s.responseTime"
            }
}}
