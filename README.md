## Funnel Data Assignment

This project analyzes events, message and orders data of devices to provide actionable insights for merchant. The analysis includes:

- Funnel conversion: Loaded → Interact → Clicks → Purchase, broken down by device.
- Intent distribution: percentage share of `detected_intent`, highlighting top 2 intents correlated with purchases.
- Order cancellation SLA compliance: checking violations against a 60-minute cancellation policy.
- Charts and JSON reports for visualization and further analysis.

### Folder Structure

```bash
/sql
  funnel.sql
  intent_distribution.sql
  cancellation_sla.sql
/src
  evo_report.py
/out
  report.json
  funnel.png
  intents.png
INSIGHTS.md
README.md
```

- `/data` : Contains data files (events.scv, messages.csv, orders.csv, inventory.csv, products.csv)
- `/sql` : Contains the SQL queries for the given tasks.
- `/src` : Contains pythn script evo_report.py for full data preprocessing and generating JSON and charts.
- `/out` : Contains the Generated JSON report and charts
- `INSIGHTS.md` : Provides insights and key takeaways


### Setup & Dependencies

1. Clone or download the repository
   ```bash
    git clone https://github.com/Akshharaa/funnel-data-assignment-AkshharaaTharigonda.git
    cd funnel-data-assignment-AkshharaaTharigonda ```
2. Install the required packages: `pip install pandas matplotlib seaborn plotly`

### How to Run:

1. Ussing CLI, execute evo_report.py to generate JSON report, funnel.png and intent.png charts
    * Run `python src/evo_report.py --events data/events.csv --messages data/messages.csv --orders data/orders.csv --out ./out/`

### Output:

The out folder contains:
* JSON report: It includes Funnel conversion by step conversion, Intent Distribution and top 2 purchse intents and Cancellation Check details.
* funnel.png: Funnel conversion by device
* intents.png: Top intents

