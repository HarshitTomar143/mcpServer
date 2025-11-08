"""
server.py — Central MCP Orchestrator (manual tool registration)
Compatible with FastMCP versions that require manual mcp.add_tool(...) registration.
"""

import time
from typing import Dict, Any, Optional
import httpx
from fastmcp import FastMCP  # import the core only, avoid decorator imports

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
SERVER_NAME = "mcp-central-hub"
AGENTS: Dict[str, str] = {
    "finance-agent": "http://127.0.0.1:8001",
    "data-agent": "http://127.0.0.1:8002",
    "math-agent": "http://127.0.0.1:8003",
    "health-agent": "http://127.0.0.1:8004",
    "summarizer-gemini": "http://127.0.0.1:8005",
}

# Create the FastMCP orchestrator
mcp = FastMCP(SERVER_NAME, version="1.0.0")  # use 1.x style for compatibility

# ------------------------------------------------------------
# Helper - synchronous HTTP calls (simple and reliable)
# ------------------------------------------------------------
def call_agent_sync(agent: str, endpoint: str, data: Optional[dict] = None, timeout: float = 15.0) -> dict:
    """
    Synchronously call agent HTTP endpoints using httpx.Client.
    Returns a dict with either the JSON response or an error description.
    """
    if agent not in AGENTS:
        return {"error": f"Agent '{agent}' not found"}

    base_url = AGENTS[agent].rstrip("/")
    url = f"{base_url}/{endpoint.lstrip('/')}"
    try:
        with httpx.Client(timeout=timeout) as client:
            if data is not None:
                resp = client.post(url, json=data)
            else:
                resp = client.get(url)
            resp.raise_for_status()
            # try to parse JSON; fallback to text
            try:
                return resp.json()
            except Exception:
                return {"status": "ok", "text": resp.text}
    except Exception as e:
        return {"error": str(e), "agent": agent}

# ------------------------------------------------------------
# Tools implemented as plain functions (accept generic payloads)
# ------------------------------------------------------------
def list_agents_tool(payload: Optional[dict] = None) -> dict:
    """Return the registered agents and their base URLs."""
    return {"status": "ok", "agents": AGENTS, "ts": time.time()}

def health_all_tool(payload: Optional[dict] = None) -> dict:
    """Query /health on all agents and return aggregated results."""
    results: Dict[str, Any] = {}
    for name in AGENTS.keys():
        results[name] = call_agent_sync(name, "health")
    return {"status": "ok", "timestamp": time.time(), "results": results}

def call_agent_tool(payload: Optional[dict]) -> dict:
    """
    Generic tool to call another agent's /call endpoint.
    Expected payload format (flexible):
      {
        "agent": "math-agent",
        "query": "some_query_name",
        "input": { ... }   # optional
      }
    """
    if not payload or not isinstance(payload, dict):
        return {"error": "payload must be an object with agent and query keys"}

    agent = payload.get("agent")
    query = payload.get("query")
    input_data = payload.get("input", {})

    if not agent or not query:
        return {"error": "agent and query are required in payload"}

    # build MCP-style call payload for agent
    call_payload = {"input": {"query": query}}
    if isinstance(input_data, dict):
        call_payload["input"].update(input_data)

    result = call_agent_sync(agent, "call", call_payload)
    return {"status": "ok", "agent": agent, "result": result}

def summarize_with_gemini_tool(payload: Optional[dict]) -> dict:
    """
    Convenience wrapper that calls the summarizer agent's /call endpoint.
    Accepts payload like:
      {"text": "..."}  OR  {"input": {"text": "..."}}  OR same shape as call_agent_tool
    """
    if not payload or not isinstance(payload, dict):
        return {"error": "payload must be an object containing text"}

    # accept flexible shapes
    if "input" in payload and isinstance(payload["input"], dict):
        text = payload["input"].get("text") or payload["input"].get("body")
    else:
        text = payload.get("text") or payload.get("body")

    if not text:
        return {"error": "text required (payload.text or payload.input.text)"}

    agent_payload = {"input": {"text": text}}
    result = call_agent_sync("summarizer-gemini", "call", agent_payload)
    return {"status": "ok", "summary": result}

# ------------------------------------------------------------
# Minimal compatibility: attach `.key` and metadata expected by older fastmcp
# ------------------------------------------------------------
# Some fastmcp tool managers expect callables to expose a `.key` attribute.
# Provide them so mcp.add_tool(...) works reliably.
list_agents_tool.key = "list_agents"
list_agents_tool.description = "List registered agents"

health_all_tool.key = "health_all"
health_all_tool.description = "Get /health from all agents"

call_agent_tool.key = "call_agent_tool"
call_agent_tool.description = "Proxy a call to a specific agent's /call endpoint"

summarize_with_gemini_tool.key = "summarize_with_gemini"
summarize_with_gemini_tool.description = "Summarize text via the Gemini summarizer agent"

# ------------------------------------------------------------
# Register the tools with the MCP server (manual registration)
# ------------------------------------------------------------
# older FastMCP builds use mcp.add_tool(func)
mcp.add_tool(list_agents_tool)
mcp.add_tool(health_all_tool)
mcp.add_tool(call_agent_tool)
mcp.add_tool(summarize_with_gemini_tool)

# ------------------------------------------------------------
# Start message and run
# ------------------------------------------------------------
if __name__ == "__main__":
    print("\n🚀 MCP Central Hub (manual registration) starting.")
    print("🔗 Connected agents:")
    for a, url in AGENTS.items():
        print(f"  - {a}: {url}")
    print("✅ Registered tools: list_agents, health_all, call_agent_tool, summarize_with_gemini\n")

    # run the MCP server (blocking)
    mcp.run()
