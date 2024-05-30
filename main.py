from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Dict, Any
import logging
import json
import os
from myGpt import get_messages_from_thread, initialize_assistant as init_agent, Agent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Dictionary to store initialized agents
agents = {}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at the root URL
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# Define Pydantic models
class AgentData(BaseModel):
    system_prompt: str
    name: str
    model: str

class Message(BaseModel):
    role: str
    content: List[Dict[str, Any]]

class ChatRequest(BaseModel):
    agent_data: AgentData
    message: Message

# Initialize agent endpoint
@app.post("/initialize_agent")
async def initialize_agent(agent_data: AgentData):
    try:
        agent = Agent(**agent_data.dict())  # Initialize the Agent class
        agent.assistant = init_agent(**agent_data.dict())  # Initialize the assistant within the Agent
        if agent.assistant:
            agents[agent_data.name] = agent  # Store the agent in the dictionary
            return {"status": "success", "agent_id": agent.assistant.id}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        logger.info(f"Received chat request: {request.json()}")
        agent_name = request.agent_data.name
        if agent_name not in agents:
            raise HTTPException(status_code=404, detail="Agent not found. Please initialize the agent first.")
        
        agent = agents[agent_name]
        response = agent.chat(request.message.content[0]['text'])
        logger.info(f"Chat response: {response}")
        return {"status": "success", "responses": response}
    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Retrieve messages endpoint
@app.get("/messages/{thread_id}")
async def get_messages(thread_id: str):
    try:
        messages = get_messages_from_thread(thread_id)
        if messages:
            return {"status": "success", "messages": messages['data']}
        else:
            raise HTTPException(status_code=404, detail="Thread not found")
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)