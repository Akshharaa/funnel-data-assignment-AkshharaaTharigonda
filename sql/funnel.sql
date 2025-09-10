CREATE DATABASE IF NOT EXISTS test_db;
USE test_db;

-- import events.csv into test.db

with step_counts as(SELECT device, event_name as step, COUNT(Distinct user_id) as users
from events
where event_name in ('Loaded', 'Interact', 'Clicks', 'Purchase')
group by device, event_name),

step_orders as(select device, step, users,
CASE step 
	when 'Loaded' then 1
	when 'Interact' then 2
	when 'Clicks' then 3
	when 'Purchase' then 4
END as step_order
from step_counts),

funnel as(select device, step, users, step_order,
LAG(users) over(partition by device order by step_order) as prev_users,
FIRST_VALUE(users) over(partition by device order by step_order) as start_value
from step_orders)

select step, users, 
ROUND(case when prev_users is NULL THEN 100 else ((users*100)/prev_users) END,2) as conv_from_prev_pct,
ROUND(((users*100)/start_value),2) as conv_from_start_pct, device
from funnel
order by device, step_order;

-- Possible Drop-off reasons:
-- Users facing friction in the checkout (Limited payment options etc).
-- Poor product details and unclear pricing can be a barrier for purchase.
-- Interface changes while placing the order from a mobile or a desktop with different page loading time reduces conversion rate.
