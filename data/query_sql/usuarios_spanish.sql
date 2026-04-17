--ESPAÑOL
with test as (
  select  ab.*, ac.employer_fiscal_country from tc-sc-bi-bigdata-edp-prod.acc_cor_corp_edp_restricted_prod.vw_trf_cor_emp_headcount_auto ab
  left join `tc-sc-bi-bigdata-edp-prod.xref_cor_hran_edp_prod.xref_hran_corp_employer` ac
  on ab.emp_employer_tax_id=ac.emp_employer_id
  where end_Date is null and emp_update_period=202604 
  and (emp_end_date_employer >= "2026-04-30" or emp_end_date_employer is null) and data_source='EC'
  and active_ind=true 
  and manual_feed_end_date<=current_date()
  group by all
  qualify row_number() over(partition by emp_id_corp order by emp_start_date_employer desc ) = 1
  )

select
--------------------------------------------
hc.emp_id_corp_clear,
hc.emp_email_clear as emp_corp_email_clear,
concat(
coalesce(hc.emp_first_name_clear,''),' ',
coalesce(hc.emp_last_name_1_clear,''),' ',
coalesce(hc.emp_last_name_2_clear,'')) as emp_name,

mana.emp_id_corp_clear as manager_id_corp_clear ,
mana.emp_email_clear as manager_corp_email_clear,
concat(
coalesce(mana.emp_first_name_clear,''),' ',
coalesce(mana.emp_last_name_1_clear,''),' ',
coalesce(mana.emp_last_name_2_clear,'')) as manager_name,

from test hc
inner join test as mana on mana.emp_id_corp_clear = hc.emp_manager_id_corp_clear
---------------------------------------------------
where true 
and hc.emp_update_period = 202604
and hc.employer_fiscal_country not in ('India', 'China')
and lower(hc.emp_workplace_type)='casa matriz'
and mana.emp_job_subfamily_code not in ('TM-4','TM-3')
---
and mana.emp_email_clear is not null
and hc.emp_business_name not in ('Hub Digital','Homecenter Sodimac Corona')

-------------------
group by all
order by  mana.emp_email_clear, hc.emp_email_clear asc

limit 10
