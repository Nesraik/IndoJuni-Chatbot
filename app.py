from fastapi import FastAPI, Request
# uvicorn app:app --host 0.0.0.0 --port 8114 --reload
app = FastAPI()


# Get user prompt
@app.post("/api/v1/chat")
async def chat(request: Request):
    access_key_bearer: str = request.headers.get("Authorization", "")
    if access_key_bearer == "":
        return {"error": "Unauthorized"}, 401
    access_key = access_key_bearer.split(" ")[1]
    print(f"Access Key: {access_key}")
    return [
        {
            "role": "agent",
            "content": "Hello! How can I assist you today?",
        }
    ]


@app.get("/api/v1/init")
async def init(request: Request):
    access_key_bearer: str = request.headers.get("Authorization", "")
    if access_key_bearer == "":
        return {"error": "Unauthorized"}, 401
    access_key = access_key_bearer.split(" ")[1]
    print(f"Access Key: {access_key}")
    return [
        {
            "role": "agent",
            "content": "Hello! How can I assist you today?",
        }
    ]
