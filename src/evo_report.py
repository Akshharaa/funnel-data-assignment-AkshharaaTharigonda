import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import plotly.express as px

def main():
    # ----------------- CLI Arguments -----------------
    parser = argparse.ArgumentParser(description="Generate funnel, intent, and SLA reports")
    parser.add_argument("--events", required=True, help="events.csv")
    parser.add_argument("--messages", required=True, help="messages.csv")
    parser.add_argument("--orders", required=True, help="orders.csv")
    parser.add_argument("--out", required=True, help="out")
    args = parser.parse_args()

    # ----------------- Setup Output Folder -----------------
    os.makedirs(args.out, exist_ok=True)

    # ----------------- Load CSVs -----------------
    events = pd.read_csv(args.events)
    messages = pd.read_csv(args.messages)
    orders = pd.read_csv(args.orders)

    # ----------------- Funnel Analysis -----------------
    
    funnel_counts=events.groupby(['device','event_name'])['user_id'].nunique().reset_index()
    funnel_counts=funnel_counts.rename(columns={'user_id': 'users', 'event_name': 'step'})

    step_order=['Loaded','Interact', 'Clicks','Purchase']

    funnel_counts['step_order']=funnel_counts.step.apply(lambda x: step_order.index(x)+1)
    funnel_counts=funnel_counts.sort_values(['device', 'step_order'])

    funnel_counts['prev_users']=funnel_counts.groupby('device')['users'].shift(1)
    funnel_counts['start_value']=funnel_counts.groupby('device')['users'].transform('first')

    funnel_counts['conv_from_prev_pct'] = (funnel_counts['users'] / funnel_counts['prev_users'] * 100).round(2)
    funnel_counts['conv_from_start_pct'] = (funnel_counts['users'] / funnel_counts['start_value'] * 100).round(2)
    funnel_counts['conv_from_prev_pct']=funnel_counts['conv_from_prev_pct'].fillna(100)

    #funnel_counts.columns
    funnel_final=funnel_counts[['step','users','conv_from_prev_pct', 'conv_from_start_pct','device']]
    
    print("..............................FUNNEL CONVERSION........................")
    
    print(funnel_final)

    fig = px.funnel(
        funnel_final,
        x="users",
        y="step",
        color='device',
        title="Funnel Conversion by Device"
    )
    fig.write_image(os.path.join(args.out, "funnel.png")) 
    print("funnel.png saved successfully")
    
    #Intent Analysis
    
    messages["detected_intent"] = messages["detected_intent"].fillna("unknown")
    messages["detected_intent"] = messages["detected_intent"].replace("", "unknown")

    # Normal counting
    intent_counts = messages["detected_intent"].value_counts().reset_index()

    intent_counts.columns = ["intent", "count"]

    # Add percentage
    intent_counts["pct_of_total"] = (
        (intent_counts["count"] / intent_counts["count"].sum() * 100).round(2)
    )
    print("..............................INTENT ANALYSIS........................")
    print(intent_counts)
    
    #print(intent_counts.head(10))
    top10_intents = intent_counts.sort_values("count", ascending=False).head(10)

    fig, ax = plt.subplots(figsize=(10,6))  # Create figure explicitly
    sns.barplot(
        data=top10_intents,
        x="pct_of_total",
        y="intent",
        palette="viridis",
        ax=ax
    )
    ax.set_title("Top 10 Message Intents (%)")
    ax.set_xlabel("Percentage of Total Messages")
    ax.set_ylabel("Intent")
    fig.tight_layout()
    fig.savefig(os.path.join(args.out, "intents.png")) # Save using the figure object
    plt.close(fig)  # Close the figure
    print("intents.png saved successfully")



    # Merge messages with only purchase sessions
    messages_purchase = messages.merge(
        events[events["event_name"] == "Purchase"][["session_id"]],
        on="session_id",
        how="inner"
    )


    top2_purchase_intents = (
        messages_purchase["detected_intent"]
        .value_counts())
    top2_purchase_intents=top2_purchase_intents.head(2).reset_index()
    top2_purchase_intents.columns = ["intent", "purchase_count"]
    
    print("..............................Top 2 intents in Purchase category........................")
    print(top2_purchase_intents)
    top2_purchase_intents_list=top2_purchase_intents['intent'].tolist()
    
   
    # ----------------- SLA -----------------
    #change to datetime format
    orders["created_at"] = pd.to_datetime(orders["created_at"])
    orders["canceled_at"] = pd.to_datetime(orders["canceled_at"])

    orders['is_canceled']=orders['canceled_at'].notna()

    # Compute time difference in minutes
    orders["cancel_diff_min"] = (orders["canceled_at"] - orders["created_at"]).dt.total_seconds() / 60

    # Identify violations: canceled after 60 minutes
    orders["violation"] = orders["cancel_diff_min"] > 60

    total_orders = len(orders)
    canceled = orders["is_canceled"].sum()
    violations = orders["violation"].sum()
    violation_rate_pct = round(violations / total_orders * 100, 2)

    cancellation_sla = {
        "total_orders": total_orders,
        "canceled": int(canceled),
        "violations": int(violations),
        "violation_rate_pct": violation_rate_pct
    }
    print("..............................SLA........................")
    print(cancellation_sla)
    
    funnel_json = funnel_final.astype(object).to_dict(orient="records")
    intents_json = intent_counts.astype(object).to_dict(orient="records")


    # Cancellation SLA as dict (convert numpy numbers to Python int/float)
    cancellation_sla_json = {
        "total_orders": int(total_orders),
        "canceled": int(canceled),
        "violations": int(violations),
        "violation_rate_pct": float(violation_rate_pct)
    }

    # Combine
    report = {
        "funnel": funnel_json,
        "intents": intents_json,
        "top_purchase_intents": top2_purchase_intents_list,
        "cancellation_sla": cancellation_sla_json
    }


    with open(os.path.join(args.out, "report.json"), "w") as f:
        json.dump(report, f, indent=4)

    print(f"Report generated in: {args.out}")


if __name__ == "__main__":
    main()