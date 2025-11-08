# finance_agent.py
import json
import random
import time

agent_status = {"FinanceAgent": "healthy"}
finance_data = {}

print("🟢 FinanceAgent started...")

while True:
    time.sleep(3)

    # Randomly make agent fail or healthy
    if random.random() < 0.2:
        agent_status["FinanceAgent"] = "failed"
        print("⚠️ FinanceAgent simulated task failure")
    else:
        agent_status["FinanceAgent"] = "healthy"
        print("✅ FinanceAgent heartbeat sent.")

        # Generate some fake financial data
        finance_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "revenue": random.randint(10000, 50000),
            "expenses": random.randint(2000, 10000),
            "profit": random.randint(2000, 10000)
        }

        # Write data to JSON
        with open("finance_data.json", "w") as f:
            json.dump(finance_data, f, indent=4)

        print("💾 Finance data updated:", finance_data)

    # Update agent health status
    with open("agent_status.json", "w") as f:
        json.dump(agent_status, f)
