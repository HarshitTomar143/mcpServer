
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Any, Dict

app = FastAPI(title="MathAgent")
AGENT_NAME = "math-agent"

class CallIn(BaseModel):
    input: Dict[str, Any]
    meta: Dict[str, Any] = {}

class CallOut(BaseModel):
    status: str
    result: Dict[str, Any]
    meta: Dict[str, Any] = {}

@app.get("/health")
def health():
    return {"status": "ok", "agent": AGENT_NAME, "ts": time.time()}

@app.post("/call")
def call(payload: CallIn):
    inp = payload.input or {}
    op = inp.get("operation")
    if not op:
        raise HTTPException(status_code=400, detail="operation required in input.operation")

    try:
        if op == "add":
            a = float(inp.get("a", 0)); b = float(inp.get("b", 0))
            return {"status":"ok", "result":{"value": a + b}, "meta":{"agent":AGENT_NAME}}
        if op == "sub":
            a = float(inp.get("a", 0)); b = float(inp.get("b", 0))
            return {"status":"ok", "result":{"value": a - b}, "meta":{"agent":AGENT_NAME}}
        if op == "mul":
            a = float(inp.get("a", 0)); b = float(inp.get("b", 0))
            return {"status":"ok", "result":{"value": a * b}, "meta":{"agent":AGENT_NAME}}
        if op == "div":
            a = float(inp.get("a", 0)); b = float(inp.get("b", 1))
            if b == 0:
                raise HTTPException(status_code=400, detail="division by zero")
            return {"status":"ok", "result":{"value": a / b}, "meta":{"agent":AGENT_NAME}}
        if op == "percent":
            total = float(inp.get("total", 0)); part = float(inp.get("part", 0))
            if total == 0:
                raise HTTPException(status_code=400, detail="total cannot be zero")
            pct = (part / total) * 100
            return {"status":"ok", "result":{"value": pct}, "meta":{"agent":AGENT_NAME}}
        if op == "avg":
            arr = inp.get("values", [])
            if not isinstance(arr, list) or len(arr) == 0:
                raise HTTPException(status_code=400, detail="values must be a non-empty list")
            vals = [float(x) for x in arr]
            return {"status":"ok", "result":{"value": sum(vals)/len(vals)}, "meta":{"agent":AGENT_NAME}}

       
        raise HTTPException(status_code=400, detail=f"unsupported operation: {op}")
    except ValueError:
        raise HTTPException(status_code=400, detail="numeric values required for operation")
