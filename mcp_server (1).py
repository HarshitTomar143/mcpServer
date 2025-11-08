
# from fastapi import FastAPI
# from fastapi.responses import JSONResponse
# import random

# app = FastAPI()
# agent_status = {"FinanceAgent": "healthy", "HR_Agent": "healthy"}

# @app.get("/status")
# def get_status():
#     return JSONResponse(agent_status)

# @app.post("/report_failure/{agent_name}")
# def report_failure(agent_name: str):
#     agent_status[agent_name] = "failed"
#     return {"message": f"Failure reported for {agent_name}"}

# @app.post("/heal/{agent_name}")
# def heal_agent(agent_name: str):
#     agent_status[agent_name] = "healing"
#     # simulate healing
#     agent_status[agent_name] = "healthy"
#     return {"message": f"{agent_name} healed successfully"}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="127.0.0.1", port=8000)
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

app = FastAPI()
agent_status = {"FinanceAgent": "healthy"}

class Heartbeat(BaseModel):
    name: str

class Report(BaseModel):
    name: str
    status: str

@app.post("/heartbeat")
def heartbeat(data: Heartbeat):
    agent_status[data.name] = "healthy"
    print(f"✅ {data.name} heartbeat received.")
    return {"message": "Heartbeat OK"}

@app.post("/report")
def report(data: Report):
    agent_status[data.name] = data.status
    print(f"⚠️ {data.name} reported status: {data.status}")
    return {"message": "Report received"}

@app.get("/status")
def get_status():
    return agent_status

if __name__ == "__main__":
    print("🟢 MCP Server started on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
