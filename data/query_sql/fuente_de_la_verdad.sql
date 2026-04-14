with test as (
  select *
  from `tc-sc-bi-bigdata-edp-prod.trf_cor_cl_edp_restricted_prod.acc_btd_cor_emp_headcount_clear` as a
  where emp_update_period = 202512 and (a.emp_end_date_employer >= "2025-12-31"
                                        or a.emp_end_date_employer is null)
  qualify row_number() over(partition by a.emp_id_corp order by emp_start_date_employer desc ) = 1
  )

select
--------------------------------------------
hc.emp_id_corp_clear,
hc.emp_corp_email_clear,
concat(
coalesce(hc.emp_first_name_clear,''),' ',
coalesce(hc.emp_last_name_1_clear,''),' ',
coalesce(hc.emp_last_name_2_clear,'')) as emp_name,

mana.emp_id_corp_clear as manager_id_corp_clear ,
mana.emp_corp_email_clear as manager_corp_email_clear,
concat(
coalesce(mana.emp_first_name_clear,''),' ',
coalesce(mana.emp_last_name_1_clear,''),' ',
coalesce(mana.emp_last_name_2_clear,'')) as manager_name,

from test hc
inner join test as mana on mana.emp_id_corp_clear = hc.emp_manager_id_corp_clear
---------------------------------------------------
where true 
and hc.emp_update_period = 202512
and hc.employer_fiscal_country not in ('India', 'China')
and lower(hc.workplace_unified)='casa matriz'
and hc.emp_job_subfamily_code not in ('TM-4','TM-3')
---
and mana.emp_corp_email_clear is not null
and mana.emp_business_name not in ('Hub Digital','Homecenter Sodimac Corona')
---
and mana.emp_corp_email_clear not like "%mallplaza.com"
-------------------
group by all
qualify count(1) over (partition by mana.emp_id_corp_clear ) < 25
order by  mana.emp_corp_email_clear,hc.emp_corp_email_clear asc
--limit 6000


