import asyncio
import time
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List

# ✅ FastMCP client imports (correct for v2.13.0)
from fastmcp import Client as FastMCPClient
from fastmcp.client.transports import PythonStdioTransport

app = FastAPI(title="DataAgent")
AGENT_NAME = "DataAgent"

# Local in-memory DB simulation
DB: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "Harshit", "role": "student", "email": "harshit@example.com"},
    2: {"id": 2, "name": "Samrat", "role": "webdev", "email": "samrat@example.com"},
    3: {"id": 3, "name": "Aisha", "role": "ml", "email": "aisha@example.com"},
}

# Heartbeat config
HEARTBEAT_INTERVAL = 5  # seconds

class CallIn(BaseModel):
    input: Dict[str, Any]
    meta: Dict[str, Any] = {}


@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_NAME, "ts": time.time(), "count": len(DB)}


@app.post("/call")
def call(payload: CallIn):
    inp = payload.input or {}
    q = inp.get("query")

    if not q:
        raise HTTPException(status_code=400, detail="input.query required")

    # ---- Query Handlers ----
    if q == "get_user":
        uid = inp.get("id")
        if uid is None:
            raise HTTPException(status_code=400, detail="id required for get_user")
        user = DB.get(int(uid))
        if not user:
            raise HTTPException(status_code=404, detail="not found")
        return {"status": "ok", "result": {"data": user}, "meta": {"agent": AGENT_NAME}}

    if q == "list_users":
        return {"status": "ok", "result": {"data": list(DB.values())}, "meta": {"agent": AGENT_NAME}}

    if q == "search":
        term = str(inp.get("term", "")).lower()
        by_role = inp.get("role")
        results: List[Dict[str, Any]] = []
        for u in DB.values():
            if by_role and u.get("role") == by_role:
                results.append(u)
            elif term and (term in u.get("name", "").lower() or term in u.get("email", "").lower()):
                results.append(u)
        return {"status": "ok", "result": {"data": results}, "meta": {"agent": AGENT_NAME}}

    if q == "insert":
        payload_data = inp.get("data")
        if not isinstance(payload_data, dict):
            raise HTTPException(status_code=400, detail="data object required for insert")
        new_id = max(DB.keys()) + 1 if DB else 1
        payload_data["id"] = new_id
        DB[new_id] = payload_data
        return {"status": "ok", "result": {"data": payload_data}, "meta": {"agent": AGENT_NAME}}

    raise HTTPException(status_code=400, detail="unknown query")


@app.post("/restart")
def restart():
    """Simulate a restart command."""
    return {"status": "ok", "message": "restart simulated", "agent": AGENT_NAME}


# ---- MCP Connection Logic ----
async def mcp_connect():
    """Connect to the MCP Supervisor via stdio transport."""
    try:
        # ✅ Launch the supervisor automatically via stdio
        transport = PythonStdioTransport(
            script_path="../server.py",  # Adjust if server.py path differs
            python_cmd="python"
        )
        client = FastMCPClient(transport)

        async with client:
            print(f"[{AGENT_NAME}] Connected to MCP Supervisor")
            while True:
                try:
                    # Send periodic heartbeat to supervisor
                    await client.call_tool("get_agent_status", {"name": AGENT_NAME})
                    print(f"[{AGENT_NAME}] Heartbeat sent ✅")
                except Exception as e:
                    print(f"[{AGENT_NAME}] Heartbeat failed: {e}")
                await asyncio.sleep(HEARTBEAT_INTERVAL)

    except Exception as e:
        print(f"[{AGENT_NAME}] MCP connection error: {e}")


# ---- Launch MCP connection loop ----
@app.on_event("startup")
async def on_startup():
    asyncio.create_task(mcp_connect())


# ---- Entry Point ----
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8012)
