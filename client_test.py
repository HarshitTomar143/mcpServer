import asyncio
from mcp import AsyncClient
import json

async def main():
    # 1️⃣ Connect to the MCP Hub
    client = AsyncClient("ws://127.0.0.1:8000")  # Your MCP central hub WebSocket address
    await client.start()

    # 2️⃣ Call the `list_agents` tool
    print("\n🧩 Listing Agents...")
    resp = await client.call_tool("list_agents", {})
    print(json.dumps(resp, indent=2))

    # 3️⃣ Get all agents' health
    print("\n❤️ Checking Health of All Agents...")
    resp = await client.call_tool("health_all", {})
    print(json.dumps(resp, indent=2))

    # 4️⃣ Query a specific agent (like data-agent)
    print("\n📋 Fetching Data from Data Agent...")
    resp = await client.call_tool("call_agent_tool", {
        "agent": "data-agent",
        "query": "list_users"
    })
    print(json.dumps(resp, indent=2))

    # 5️⃣ Try summarizing text
    print("\n🧠 Summarizing Text via Gemini Agent...")
    resp = await client.call_tool("summarize_with_gemini", {
        "text": "Artificial Intelligence is transforming industries and education worldwide."
    })
    print(json.dumps(resp, indent=2))

    await client.close()

if __name__ == "__main__":
    asyncio.run(main())
