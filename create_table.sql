-------------------------------------------------------------------------
CREATE TABLE `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` (
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
DROP TABLE IF EXISTS `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data`;

CREATE TABLE `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` (
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
-- select * except(timestamp)
-- ,datetime(a.timestamp, "America/Santiago") AS fecha
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
-- where DATE(a.timestamp, "America/Santiago") = current_date()
-- order by a.timestamp desc;


-- select * except(edp_load_datetime)
-- ,datetime(a.edp_load_datetime, "America/Santiago") AS fecha
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as a
-- where DATE(a.edp_load_datetime, "America/Santiago") = current_date()
-- order by a.edp_load_datetime desc;

--------------------------------------------------------
-- select a.* except(timestamp,lista_colaboradores)
-- ,datetime(a.timestamp, "America/Santiago") AS fecha
-- ,b.responseTime
-- ,b.responder_email
-- ,b.responder_displayName
-- ,b.equipo_validado
-- ,b.falta_gente
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
-- left join `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
-- on a.request_id = b.request_id
-- where DATE(a.timestamp, "America/Santiago") = current_date()
-- order by a.timestamp desc;

