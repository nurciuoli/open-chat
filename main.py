from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from typing import List
import os
import logging

from services import (
    initialize_agent,
    handle_chat,
    save_chat_session,
    save_agent_template,
    load_message_history,
    load_agent_templates
)
from utils import get_file_content
from myGpt import Agent, get_messages_from_thread
from schemas import AgentData, ChatRequest

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

if not os.path.exists('data'):
    os.makedirs('data')


def list_messages_out(messages):
    print_list = []
    for message in messages:
        assert message.content[0].type == "text"
        msg_value = message.content[0].text.value
        msg_role = message.role
        print_list.append(f'{msg_role}: {msg_value}')
    return print_list



@app.post("/initialize_agent")
async def initialize_agent_endpoint(agent_data: AgentData):
    try:
        agent = Agent(system_prompt=agent_data.system_prompt,
                      name=agent_data.name,
                      model=agent_data.model)
        if agent:
            return {"message": "Agent initialized successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
    except Exception as e:
        logger.error(f"Exception during agent initialization: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize agent")
    


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        agent_data = request.agent_data.dict()
        msg = request.msg
        agent = handle_chat(agent_data, msg)
        if agent:
            thread_id = agent.thread.id  # Assuming there's a method to get the thread ID
            save_chat_session(thread_id)
            formatted_messages = list_messages_out(agent.messages)  # Format the messages
            return {"message": "Chat processed", "response": formatted_messages}
        else:
            raise HTTPException(status_code=500, detail="Chat processing failed")
    except Exception as e:
        logger.error(f"Exception during chat processing: {e}")
        raise HTTPException(status_code=500, detail="Chat processing failed")


@app.post("/save_template")
async def save_template(template_data: AgentData):
    try:
        save_agent_template(template_data.dict())
        return {"message": "Template saved successfully"}
    except Exception as e:
        logger.error(f"Exception saving template: {e}")
        raise HTTPException(status_code=500, detail="Failed to save template")


@app.get("/templates")
async def get_templates():
    try:
        templates = load_agent_templates()
        return {"templates": templates}
    except Exception as e:
        logger.error(f"Exception retrieving templates: {e}")
        raise HTTPException(status_code=500, detail="Failed to load templates")


@app.get("/files/{filename}")
async def get_file_content_endpoint(filename: str):
    try:
        content = get_file_content(filename)
        if content:
            return {"content": content}
        else:
            raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        logger.error(f"Exception retrieving file content: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve file content")


@app.get("/", response_class=HTMLResponse)
async def get_index():
    try:
        with open("static/index.html") as f:
            return HTMLResponse(content=f.read(), status_code=200)
    except Exception as e:
        logger.error(f"Exception serving index.html: {e}")
        raise HTTPException(status_code=500, detail="Failed to load index page")
if not os.path.exists('data'):
    os.makedirs('data')

@app.get("/messages/{thread_id}")
async def get_messages(thread_id: str):
    try:
        messages = get_messages_from_thread_retrieve(thread_id)
        out_messages = list_messages_out(messages)
        return {"messages": out_messages}
    except Exception as e:
        logger.error(f"Exception retrieving messages: {e}")
        raise HTTPException(status_code=404, detail="No message history found for this thread_id")

def get_messages_from_thread_retrieve(thread_id: str):
    try:
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": {"value": "Create 3 data visualizations based on the trends in this file."}}],
                "attachments": [
                    {
                        "file_id": "file_id_example",
                        "tools": [{"type": "code_interpreter"}]
                    }
                ]
            }
        ]
        return messages
    except Exception as e:
        logger.error(f"Error retrieving messages: {e}")
        raise e

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
