from pydantic import BaseModel
from typing import List, Dict, Any
# Define Pydantic models
class AgentData(BaseModel):
    system_prompt: str
    name: str
    model: str

class Message(BaseModel):
    role: str
    content: List[Dict[str, Any]] = []

class ChatRequest(BaseModel):
    agent_data: AgentData
    message: Message

class Thread(BaseModel):
    id: str
    messages: List[Message] = []
