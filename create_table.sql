-------------------------------------------------------------------------
CREATE TABLE `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data_test` (
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
DROP TABLE IF EXISTS `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data_test`;

CREATE TABLE `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data_test` (
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
--------------------------------------------------------
-- with data_val
-- as
-- (select
-- a.request_id
-- ,datetime(a.timestamp, "America/Santiago") AS fecha
-- ,b.responseTime
-- ,case
-- when b.submitActionId is null then "Pendiente Respuesta"
-- else b.submitActionId end as submitActionId
-- ,a.* except(request_id,timestamp,success,status_code,lista_colaboradores)
-- --,a.lista_colaboradores
-- ,ARRAY_LENGTH(a.lista_colaboradores) AS lista_colaboradores
-- --,b.equipo_validado
-- ,ARRAY_LENGTH(b.equipo_validado) AS equipo_validado
-- ,b.falta_gente
-- ,case 
-- when ARRAY_LENGTH(a.lista_colaboradores) <> ARRAY_LENGTH(b.equipo_validado)
-- then 1 else 0 end as Equipo_incompleto

-- ,ROUND(
--   SAFE_DIVIDE(
--     ARRAY_LENGTH(IFNULL(b.equipo_validado, [])),
--     ARRAY_LENGTH(IFNULL(a.lista_colaboradores, []))
--   ) * 100,2) AS percent

-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
-- left join (
--           select * 
--           from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as s
--           --QUALIFY ROW_NUMBER() OVER (PARTITION BY s.request_id ORDER BY s.responseTime DESC) = 1
--           ) as b
-- on a.request_id = b.request_id
-- --where DATE(a.timestamp, "America/Santiago") = current_date()
-- --and b.submitActionId = "Enviar"
-- order by a.timestamp desc)

-- select * except(destinatario)
-- ,(dt.lista_colaboradores/ dt.equipo_validado * 
-- (case when dt.Equipo_incompleto = 1 then 0.5
-- else 1  end) )  as Percent_con_penalizacion_x_incompletitud


-- ,'' as Percent_de_error_en_precision
-- ,'' as aux
-- ,'' as Linea_de_Negocio
-- ,'' as Pais
-- from data_val as dt
-- order by dt.request_id desc



-- select *
-- from `tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear` as a

-- select *
-- from `tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear` as a


-- ################ validacion ###############################
-- select
-- case
-- when b.submitActionId = 'Enviar' then a.request_id
-- when trim(b.submitActionId) = 'Error técnico - Tarjeta no válida o fallo de Teams' 
-- and b.Q >3 then a.request_id
-- when b.submitActionId is null and a.status_code = 202 then a.request_id
-- else "No Aplica" end as request_id
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
-- -------------------------------------
-- left join ( 
-- select b.*,c.Q
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
-- -------------------------------------
-- left join (
--         select b.request_id,b.submitActionId, count(b.submitActionId) Q
--         from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
--         group by b.request_id,b.submitActionId
-- ) as c on b.request_id = c.request_id
-- -------------------------------------
-- QUALIFY ROW_NUMBER() OVER (PARTITION BY b.request_id ORDER BY b.responseTime DESC) = 1
-- ) as b
-- on a.request_id = b.request_id
-- where true

-- ###################### exclucion ############################################
-- select
-- a.request_id
-- ,a.status_code
-- ,b.submitActionId
-- ,b.Q
-- ,case
-- when b.submitActionId = 'Enviar' then a.request_id
-- when trim(b.submitActionId) = 'Error técnico - Tarjeta no válida o fallo de Teams' 
-- and b.Q >3 then a.request_id
-- when b.submitActionId is null and a.status_code = 202 then a.request_id
-- else "No Aplica" end as request_id
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a
-- left join ( 
--           select b.*,c.Q
--           from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
--           -------------------------------------
--           left join (
--                     select b.request_id,b.submitActionId, count(b.submitActionId) Q
--                     from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.response_validation_data` as b
--                     group by b.request_id,b.submitActionId
--           ) as c on b.request_id = c.request_id
--           -------------------------------------
--           QUALIFY ROW_NUMBER() OVER (PARTITION BY b.request_id ORDER BY b.responseTime DESC) = 1
--           ) as b
-- on a.request_id = b.request_id
-- where true
-- --and a.request_id in ('{lista_request_id}')
-- order by a.timestamp desc
