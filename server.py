# server.py
import asyncio
import subprocess
import time
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP, Context

# Initialize the MCP Server
mcp = FastMCP("NeuroWeave-Supervisor")

AGENTS: Dict[str, Dict[str, Any]] = {}
HEALTH_LOG = []
HEARTBEAT_TIMEOUT = 8


# ------------------------------------------------------------
# Utility Logging
# ------------------------------------------------------------
def log_event(event: str):
    ts = time.time()
    HEALTH_LOG.append({"ts": ts, "event": event})
    print(f"[{time.strftime('%H:%M:%S', time.localtime(ts))}] {event}")


# ------------------------------------------------------------
# Agent Management
# ------------------------------------------------------------
def register_agent(name: str, run_cmd: str | None = None):
    """Registers an agent and optionally defines its run command."""
    AGENTS[name] = {"status": "unknown", "last_seen": 0.0, "run_cmd": run_cmd}
    log_event(f"Agent registered: {name}")


@mcp.tool()
def get_agent_status(name: str) -> Dict[str, Any]:
    """Get status of a specific agent"""
    agent = AGENTS.get(name)
    if not agent:
        return {"error": "agent_not_found"}
    return {"name": name, "status": agent["status"], "last_seen": agent["last_seen"]}


@mcp.tool()
async def list_agents() -> Dict[str, Any]:
    """List all registered agents and their statuses"""
    return {name: {"status": v["status"], "last_seen": v["last_seen"]} for name, v in AGENTS.items()}


# ------------------------------------------------------------
# Auto-repair / Restart Logic
# ------------------------------------------------------------
async def _attempt_restart_agent(name: str) -> bool:
    agent = AGENTS.get(name)
    if not agent:
        log_event(f"Repair failed: {name} not found")
        return False

    run_cmd = agent.get("run_cmd")
    if not run_cmd:
        log_event(f"No run_cmd for {name}; cannot auto-restart.")
        return False

    log_event(f"Attempting to restart agent {name} with: {run_cmd}")
    try:
        subprocess.Popen(run_cmd, shell=True)
        agent["status"] = "recovering"
        agent["last_seen"] = time.time()
        log_event(f"Restart triggered for {name}")
        return True
    except Exception as e:
        log_event(f"Restart error for {name}: {e}")
        return False


@mcp.tool()
async def repair_agent(name: str, ctx: Context | None = None) -> Dict[str, Any]:
    """Manually trigger repair for a given agent"""
    if name not in AGENTS:
        return {"ok": False, "error": "agent_not_found"}

    log_event(f"repair_agent called for {name}")
    ok = await _attempt_restart_agent(name)
    return {"ok": ok, "agent": name}


# ------------------------------------------------------------
# Health Resource & Prompt
# ------------------------------------------------------------
@mcp.resource("neuroweave://health-log")
def health_log_resource() -> str:
    """Returns the last 200 health log entries"""
    lines = [
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ev['ts']))} - {ev['event']}"
        for ev in HEALTH_LOG[-200:]
    ]
    return "\n".join(lines)


@mcp.prompt()
def repair_prompt(agent_name: str, severity: str = "medium") -> str:
    """Provides an instruction prompt for the operator"""
    return (
        f"You are an operator agent. Agent `{agent_name}` has {severity} severity. "
        f"Check logs, restart the service if safe, and verify heartbeat."
    )


# ------------------------------------------------------------
# Monitoring Loop
# ------------------------------------------------------------
async def monitor_loop():
    """Continuously monitors all agents and restarts them if unresponsive."""
    while True:
        now = time.time()
        for name, info in list(AGENTS.items()):
            last = info.get("last_seen", 0.0)
            status = info.get("status", "unknown")
            if last == 0:
                continue
            if now - last > HEARTBEAT_TIMEOUT and status == "healthy":
                AGENTS[name]["status"] = "unhealthy"
                log_event(f"Auto-detected failure for {name}; initiating repair")
                await _attempt_restart_agent(name)
        await asyncio.sleep(3)


# ------------------------------------------------------------
# Startup Handler (Replaces @mcp.on_startup)
# ------------------------------------------------------------
async def startup(ctx: Context):
    """Startup logic that registers and launches agents."""
    register_agent("WeatherAgent", run_cmd="python demo_agents/weather_agent.py")
    register_agent("FinanceAgent", run_cmd="python demo_agents/finance_agent.py")
    register_agent("TrafficAgent", run_cmd="python demo_agents/traffic_agent.py")

    for a in AGENTS:
        AGENTS[a]["status"] = "unknown"

    log_event("Supervisor startup complete; launching monitor loop.")
    asyncio.create_task(monitor_loop())


# Attach startup handler manually
mcp.startup_handler = startup


# ------------------------------------------------------------
# Entry Point
# ------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(mcp.start())
