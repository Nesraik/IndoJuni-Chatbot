from fastapi import FastAPI, Request

app = FastAPI()


# Get user prompt
@app.post("/api/v1/chat")
async def chat(request: Request):
    return [
        {
            "role": "agent",
            "content": "Hello! How can I assist you today?",
        }
    ]


@app.get("/api/v1/init")
async def init():
    return [
        {
            "status": "initialized"
        }
    ]
