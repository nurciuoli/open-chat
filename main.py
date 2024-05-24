from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from myGpt import Agent
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
app = FastAPI()
# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Define the Pydantic models
class Message(BaseModel):
    msg: str
    additional_prompt: Optional[str] = "remember to double check your work"
    images: Optional[List[str]] = None
    files: Optional[List[str]] = None
    stream: Optional[bool] = False

class InitializeResponse(BaseModel):
    message: str

def listify_msgs(messages):
    print('cp: organizing msgs')
    out_msgs=[]
    for message in messages:
        assert message.content[0].type == "text"
        msg_value = message.content[0].text.value
        out_msgs.append(msg_value)
    print('cp: msgs organized')
    return out_msgs


from agent_tools import delegate_instructions_json

agent = Agent(system_prompt="""BACKGROUND: you are a manager, your job is to delegate_instructions to a team of efficient workers
             YOU ONLY HAVE ONE SHOT""",
             tools=[{"type": "function", "function":delegate_instructions_json}])

counter=0

@app.post("/chat")
def chat(message: Message):
    try:
        global agent
        global counter
        agent.chat(
            msg=message.msg,
            additional_prompt=message.additional_prompt,
            images=message.images,
            files=message.files,
        )
        counter+=1
        responses = listify_msgs(agent.messages)[counter:]
        counter +=len(responses)
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/", response_class=HTMLResponse)
async def get_index():
    with open("index.html") as f:
        return HTMLResponse(content=f.read(), status_code=200)


# Running the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
