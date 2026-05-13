-------------------------------------------------------------------------
CREATE TABLE `teams_validation_data` (
  request_id STRING NOT NULL,
  destinatario STRING,
  lista_colaboradores ARRAY<STRING>,
  status_code INT64,
  success BOOL,
  timestamp TIMESTAMP
)
OPTIONS (
  description = "Registro de envíos y validaciones hacia Power Automate / Teams"
);
-------------------------------------------------------------------------
-------------------------------------------------------------------------
DROP TABLE IF EXISTS `response_validation_data`;

CREATE TABLE `response_validation_data` (
  -- Identificadores
  request_id STRING NOT NULL,
  messageId STRING,
  messageLink STRING,

  -- Evento
  responseTime STRING,
  submitActionId STRING,

  -- Responder
  responder_objectId STRING,
  responder_tenantId STRING,
  responder_email STRING,
  responder_userPrincipalName STRING,
  responder_displayName STRING,

  -- Validaciones
  equipo_validado ARRAY<STRING>,
  falta_gente STRING,

  -- Metadata ETL
  edp_load_datetime TIMESTAMP
)
OPTIONS (
  description = "Registro de respuestas de Power Automate / Teams con metadata de validación y control ETL"
);
-------------------------------------------------------------------------
-------------------------------------------------------------------------

