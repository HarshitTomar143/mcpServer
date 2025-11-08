# append or create a new file demo_agents/summarizer_agent_http.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio
import os
import time

# import the summarizer functions from your MCP file
# assume your MCP file defines `health` and `summarize` functions and registers them with mcp
# adjust import path if needed:
from demo_agents import summarizer_agent_gemini as mcp_agent

app = FastAPI(title="SummarizerAgentHTTP")

class CallIn(BaseModel):
    input: dict = {}
    meta: dict = {}

@app.get("/health")
async def health():
    # Use the same health function logic (call it directly)
    try:
        # if your function expects payload, pass None
        return mcp_agent.health(None)
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/call")
async def call(payload: CallIn):
    # Route calls to the summarize tool (or generalize based on payload)
    inp = payload.input or {}
    # support two shapes: {"query":"summarize", "text": "..."} or {"text":"..."}
    query = inp.get("query") or inp.get("op") or "summarize"
    if query != "summarize":
        raise HTTPException(status_code=400, detail="only 'summarize' supported in this HTTP wrapper")

    # forward payload to your function:
    try:
        # your summarize expects either a dict with 'text' or the Pydantic model
        # use dict form to be robust
        body = {"text": inp.get("text") or inp.get("input", {}).get("text") or ""}
        result = mcp_agent.summarize(body)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Only start uvicorn if run as a script (optional)
if __name__ == "__main__":
    uvicorn.run("demo_agents.summarizer_agent_http:app", host="127.0.0.1", port=8005, reload=False)
