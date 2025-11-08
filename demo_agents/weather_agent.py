# demo_agents/weather_agent.py
import requests, time, random, sys
URL = "http://127.0.0.1:8000/heartbeat"  # only if you used your earlier REST heartbeat; in MCP world you may integrate differently
# But for demo, we will POST to the Supervisor REST API if you add one; otherwise provide a simple approach below.

# Simplest: send a local file-based heartbeat by calling a small HTTP endpoint you provide.
# For this MCP-based approach, easiest is to run a local REST heartbeat server that Supervisor can poll.
# Here we simulate the agent process that Supervisor restarts (so Supervisor restarts this script).

def run():
    print("WeatherAgent starting; sending periodic 'alive' mark to file-based store.")
    while True:
        # simulate doing work
        time.sleep(2)
        # update a local "beat file" (Supervisor could also call agent's /health endpoint)
        with open("/tmp/weather_agent_beat.txt", "w") as f:
            f.write(str(time.time()))
        # occasionally crash for demo
        if random.random() < 0.05:
            print("WeatherAgent simulating crash")
            sys.exit(1)

if __name__ == "__main__":
    run()
