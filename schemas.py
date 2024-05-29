from typing import List
from pydantic import BaseModel
# This file can contain Pydantic schemas for request and response validation if needed
class AgentData(BaseModel):
    system_prompt: str = "You are a helpful chat-based assistant"
    name: str = "AgentGpt"
    model: str = "gpt-3.5-turbo-1106"
    tools: List[str] = []
    files: List[str] = []

class ChatRequest(BaseModel):
    agent_data: AgentData
    msg: str