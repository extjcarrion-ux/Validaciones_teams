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
--------------------------------------------------------
-- select 
-- datetime(a.timestamp, "America/Santiago") AS fecha
-- ,b.responseTime
-- ,b.responder_displayName
-- ,a.* except(request_id,timestamp,success,status_code,lista_colaboradores)
-- --,a.lista_colaboradores
-- ,ARRAY_LENGTH(a.lista_colaboradores) AS lista_colaboradores
-- --,b.equipo_validado
-- ,ARRAY_LENGTH(b.equipo_validado) AS equipo_validado
-- ,b.falta_gente
-- ,(ARRAY_LENGTH(a.lista_colaboradores)
-- -ARRAY_LENGTH(b.equipo_validado)) as Equipo_incompleto
-- ,ROUND(
--   SAFE_DIVIDE(
--     ARRAY_LENGTH(IFNULL(b.equipo_validado, [])),
--     ARRAY_LENGTH(IFNULL(a.lista_colaboradores, []))
--   ) * 100,2) AS percent
-- ,'' as Percent_con_penalizacion_x_incompletitud
-- ,'' as Percent_de_error_en_precision
-- ,'' as aux
-- ,'' as Linea_de_Negocio
-- ,'' as Pais
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
-- left join (
--   select * 
--   from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as s
--   QUALIFY ROW_NUMBER() OVER (PARTITION BY s.request_id ORDER BY s.responseTime DESC) = 1
--   ) as b
-- on a.request_id = b.request_id
-- where DATE(a.timestamp, "America/Santiago") = current_date()-1
-- order by a.timestamp desc;

-- select *
-- from `tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear` as a


