import json
import time

def route_query(user_query):
    if "finance" in user_query.lower() or "budget" in user_query.lower():
        return "FinanceAgent"
    else:
        return "Unknown"

print("💬 QueryAgent started...")
while True:
    query = input("\nEnter your query: ")

    agent = route_query(query)
    print(f"➡️ Routing query to: {agent}")

    # Read health info
    with open("agent_status.json", "r") as f:
        status = json.load(f)

    if agent in status and status[agent] == "healthy":
        print(f"✅ {agent} is healthy. Fetching data...")

        # Fetch finance data
        with open("finance_data.json", "r") as f:
            data = json.load(f)
        print(f"📊 Latest Finance Data:\n{json.dumps(data, indent=4)}")

    else:
        print(f"❌ {agent} is FAILED or unavailable. Try again later.")
