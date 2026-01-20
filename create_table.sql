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


--truncate table `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.stg_teams_validation_data`
--drop table `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.stg_teams_validation_data`

-- select *
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.stg_teams_validation_data` as a;

-- select *
-- from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.teams_validation_data` as a;



