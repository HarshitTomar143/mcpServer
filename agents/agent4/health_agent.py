
import asyncio
import time
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import psutil 

app = FastAPI(title="HealthAgent")
AGENT_NAME = "health-agent"


STATE = {"status": "ok"}

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
        cpu = "5%"
        mem = "30%"
    return {"status": status, "agent": AGENT_NAME, "ts": time.time(), "cpu": cpu, "memory": mem}

@app.post("/call")
def call(payload: CallIn):
    """
    Return a structured status object (MCP style).
    Accepts optional 'detail' or 'simulate' commands.
    """
    inp = payload.input or {}
    cmd = inp.get("cmd")
    if cmd == "status":
        return {"status":"ok", "result": {"status": STATE["status"], "cpu": "see /health", "memory": "see /health"}, "meta":{"agent":AGENT_NAME}}
    return {"status":"ok", "result": {"status": STATE["status"], "cpu":"see /health", "memory":"see /health"}, "meta":{"agent":AGENT_NAME}}

@app.post("/restart")
async def restart():
    """
    Demo-only restart. Simulates a restart cycle:
      - transitions to 'restarting'
      - waits 1 second
      - sets to 'ok'
    """
   
    if STATE["status"] == "restarting":
        return {"status":"ok", "message":"already restarting", "agent":AGENT_NAME}
    STATE["status"] = "restarting"
   
    await asyncio.sleep(1.0)
    STATE["status"] = "ok"
    return {"status":"ok", "message":"restarted", "agent":AGENT_NAME}


@app.post("/set_faulty")
def set_faulty():
    STATE["status"] = "faulty"
    return {"status":"ok", "agent":AGENT_NAME, "new": "faulty"}

@app.post("/set_ok")
def set_ok():
    STATE["status"] = "ok"
    return {"status":"ok", "agent":AGENT_NAME, "new": "ok"}
