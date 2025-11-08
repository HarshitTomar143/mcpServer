import asyncio
import time
import psutil
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

# ✅ FastMCP imports (compatible with v2.13.0)
from fastmcp import Client as FastMCPClient
from fastmcp.client.transports import PythonStdioTransport

app = FastAPI(title="HealthAgent")
AGENT_NAME = "HealthAgent"

STATE = {"status": "ok"}
HEARTBEAT_INTERVAL = 5  # seconds


class CallIn(BaseModel):
    input: Dict[str, Any]
    meta: Dict[str, Any] = {}


@app.get("/health")
def health():
    """
    Return health status and basic metrics.
    Uses psutil if available, otherwise returns mocked CPU/memory.
    """
    status = STATE["status"]
    try:
        cpu = f"{psutil.cpu_percent(interval=0.1)}%"
        mem = f"{psutil.virtual_memory().percent}%"
    except Exception:
        cpu, mem = "5%", "30%"
    return {
        "status": status,
        "agent": AGENT_NAME,
        "ts": time.time(),
        "cpu": cpu,
        "memory": mem,
    }


@app.post("/call")
def call(payload: CallIn):
    """
    Return a structured status object (MCP style).
    Accepts optional 'detail' or 'simulate' commands.
    """
    inp = payload.input or {}
    cmd = inp.get("cmd")

    if cmd == "status":
        return {
            "status": "ok",
            "result": {
                "status": STATE["status"],
                "cpu": "see /health",
                "memory": "see /health",
            },
            "meta": {"agent": AGENT_NAME},
        }

    return {
        "status": "ok",
        "result": {
            "status": STATE["status"],
            "cpu": "see /health",
            "memory": "see /health",
        },
        "meta": {"agent": AGENT_NAME},
    }


@app.post("/restart")
async def restart():
    """
    Demo-only restart. Simulates a restart cycle:
      - transitions to 'restarting'
      - waits 1 second
      - sets to 'ok'
    """
    if STATE["status"] == "restarting":
        return {"status": "ok", "message": "already restarting", "agent": AGENT_NAME}

    STATE["status"] = "restarting"
    await asyncio.sleep(1.0)
    STATE["status"] = "ok"
    return {"status": "ok", "message": "restarted", "agent": AGENT_NAME}


@app.post("/set_faulty")
def set_faulty():
    STATE["status"] = "faulty"
    return {"status": "ok", "agent": AGENT_NAME, "new": "faulty"}


@app.post("/set_ok")
def set_ok():
    STATE["status"] = "ok"
    return {"status": "ok", "agent": AGENT_NAME, "new": "ok"}


# 🧠 --- MCP Connection Logic --- 🧠
async def mcp_connect():
    """
    Connect to the MCP Supervisor via stdio transport and send periodic heartbeats.
    """
    try:
        # Connect to the Supervisor running server.py
        transport = PythonStdioTransport(
            script_path="../server.py",  # Path to your supervisor
            python_cmd="python"
        )
        client = FastMCPClient(transport)

        async with client:
            print(f"[{AGENT_NAME}] Connected to MCP Supervisor ✅")
            while True:
                try:
                    await client.call_tool("get_agent_status", {"name": AGENT_NAME})
                    print(f"[{AGENT_NAME}] Heartbeat sent ❤️")
                except Exception as e:
                    print(f"[{AGENT_NAME}] Heartbeat failed ❌: {e}")
                await asyncio.sleep(HEARTBEAT_INTERVAL)

    except Exception as e:
        print(f"[{AGENT_NAME}] MCP connection error ⚠️: {e}")


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(mcp_connect())


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8013)
