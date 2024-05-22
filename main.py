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

# Initialize the agent (this would be part of your existing code)
agent = Agent()

@app.post("/chat")
def chat(message: Message):
    try:
        global agent
        responses = agent.chat(
            msg=message.msg,
            additional_prompt=message.additional_prompt,
            images=message.images,
            files=message.files,
        )
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
