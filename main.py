from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import json
import os
from uuid import uuid4
from agents.oa.api import initialize_assistant as init_agent, initialize_thread
from agents.oa.agent import Agent
from models.schemas import AgentData, Message, ChatRequest, Thread
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Dictionary to store initialized agents
agents = {}

# Dictionary to store threads
threads = {}

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at the root URL
@app.get("/")
async def read_index():
    return FileResponse('index.html')

# Initialize agent endpoint
@app.post("/initialize_agent")
async def initialize_agent(agent_data: AgentData):
    try:
        agent = Agent(**agent_data.dict())  # Initialize the Agent class
        agent.assistant = init_agent(**agent_data.dict())  # Initialize the assistant within the Agent
        
        # Create a new thread for the agent
        new_thread = initialize_thread()
        new_thread_id = new_thread.id
        threads[new_thread_id] = Thread(id=new_thread_id)
        agent.thread = threads[new_thread_id]  # Assign the new thread to the agent
        
        if agent.assistant:
            agents[agent_data.name] = agent  # Store the agent in the dictionary

            return {"status": "success", "agent_id": agent.assistant.id, "thread_id": new_thread_id}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
    except Exception as e:
        logger.error(f"Error initializing agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    global threads
    global agents
    try:
        logger.info(f"Received chat request: {request.json()}")
        agent_name = request.agent_data.name
        if agent_name not in agents:
            raise HTTPException(status_code=404, detail="Agent not found. Please initialize the agent first.")
        
        agent = agents[agent_name]
        response = agent.chat(request.message.content[0]['text'])
        
        # Store the message in the thread
        thread = threads[agent.thread.id]
        thread.messages.append(request.message)
        thread.messages.append(Message(role="assistant", content=[{"text": response[0]}]))
        
        logger.info(f"Chat response: {response}")
        return {"status": "success", "responses": response}
    except Exception as e:
        logger.error(f"Error during chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)