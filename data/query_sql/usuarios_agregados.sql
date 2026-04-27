----- usuarios agregados

with test as (
  select *
  from `tc-sc-bi-bigdata-edp-qa.sbox_jcarrion.20260430_usuarios_agregados`
  )

select
--------------------------------------------
hc.emp_id_corp_clear,
hc.emp_email_clear as emp_corp_email_clear,
hc.emp_name as emp_name,

mana.manager_id_corp_clear as manager_id_corp_clear ,
mana.manager_corp_email_clear as manager_corp_email_clear,
mana.manager_name as manager_name,

from test hc
inner join test as mana on mana.emp_id_corp_clear = hc.emp_id_corp_clear
---------------------------------------------------
where true 
---
and mana.emp_email_clear is not null
AND hc.emp_email_clear IS NOT NULL
-------------------
group by all
order by  mana.manager_corp_email_clear, hc.emp_email_clear asc



