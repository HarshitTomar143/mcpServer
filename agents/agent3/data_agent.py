
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict, List, Optional

app = FastAPI(title="DataAgent")
AGENT_NAME = "data-agent"

DB: Dict[int, Dict[str, Any]] = {
    1: {"id": 1, "name": "Harshit", "role": "student", "email": "harshit@example.com"},
    2: {"id": 2, "name": "Samrat", "role": "webdev", "email": "samrat@example.com"},
    3: {"id": 3, "name": "Aisha",  "role": "ml", "email": "aisha@example.com"}
}

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

  
    if q == "get_user":
        uid = inp.get("id")
        if uid is None:
            raise HTTPException(status_code=400, detail="id required for get_user")
        user = DB.get(int(uid))
        if not user:
            raise HTTPException(status_code=404, detail="not found")
        return {"status":"ok", "result": {"data": user}, "meta": {"agent": AGENT_NAME}}

   
    if q == "list_users":
        return {"status":"ok", "result": {"data": list(DB.values())}, "meta": {"agent": AGENT_NAME}}

    
    if q == "search":
        term = str(inp.get("term", "")).lower()
        by_role = inp.get("role")
        results: List[Dict[str, Any]] = []
        for u in DB.values():
            if by_role and u.get("role") == by_role:
                results.append(u)
            elif term and (term in u.get("name","").lower() or term in u.get("email","").lower()):
                results.append(u)
        return {"status":"ok", "result": {"data": results}, "meta": {"agent": AGENT_NAME}}

   
    if q == "insert":
        payload_data = inp.get("data")
        if not isinstance(payload_data, dict):
            raise HTTPException(status_code=400, detail="data object required for insert")
        new_id = max(DB.keys()) + 1 if DB else 1
        payload_data["id"] = new_id
        DB[new_id] = payload_data
        return {"status":"ok", "result": {"data": payload_data}, "meta":{"agent":AGENT_NAME}}

    raise HTTPException(status_code=400, detail="unknown query")


@app.post("/restart")
def restart():
   
    return {"status":"ok", "message":"restart simulated", "agent": AGENT_NAME}
