use test_db;

-- Import orders.csv into test_db

with cancellation_sla as(select
count(*) as total_orders,
sum(case when NULLIF(canceled_at,'') is NOT NULL THEN 1 ELSE 0 END) as cancelled,
sum(case when NULLIF(canceled_at,'') is NOT NULL AND timestampdiff(MINUTE, created_at, canceled_at)>60 THEN 1 ELSE 0 END) 
as violations
from orders)

select *,
ROUND(((violations*100)/total_orders),2) as violation_rate_pct
from cancellation_sla;