use test_db;

-- Import messages.csv into test.db
-- Intent percentage of total

with intent_counts as(
select
coalesce(NULLIF(detected_intent,''),'unknown') as intent,
count(*) as count
from messages
group by intent)

select intent, count,
ROUND((count*100)/sum(count) over(),2) as pct_of_total
from intent_counts
order by count DESC;

-- Top 2 intents in Purchase Step

with purchase_sessions as(select DISTINCT session_id
from events where event_name ='Purchase')

select
coalesce(NULLIF(messages.detected_intent,''),'unknown') as intent,
count(DISTINCT messages.session_id) as session_count
from messages
join purchase_sessions on messages.session_id=purchase_sessions.session_id
group by intent
order by session_count DESC
LIMIT 2;

-- Most purchases happen in session where users asked about product_search and product_comparison.

