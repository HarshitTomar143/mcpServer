import json
import time

print("👀 Monitor Agent started...")

while True:
    try:
        # Read the current agent status
        with open("agent_status.json", "r") as f:
            data = json.load(f)
        
        # Check if agent failed
        if data["FinanceAgent"] == "failed":
            print("⚠️ FinanceAgent failed. Healing initiated...")
            time.sleep(2)
            print("✅ FinanceAgent restored successfully!")
            data["FinanceAgent"] = "healthy"

            # Update file after healing
            with open("agent_status.json", "w") as f:
                json.dump(data, f)
        else:
            print("💚 FinanceAgent is healthy.")

    except FileNotFoundError:
        print("Waiting for MCP server to create status file...")

    time.sleep(3)
