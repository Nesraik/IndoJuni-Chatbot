import logging
from fastapi import FastAPI, Request, Response, status
# uvicorn app:app --host 0.0.0.0 --port 8114 --reload
app = FastAPI()
# or logging.getLogger(__name__) for app-specific logs
logger = logging.getLogger("uvicorn.error")


# Get user prompt
@app.post("/api/v1/chat")
async def chat(request: Request, response: Response):
    access_key_bearer: str = request.headers.get("Authorization", "")
    if access_key_bearer.strip() == "" or access_key_bearer.strip() == "Bearer":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Unauthorized"}
    access_key: str = access_key_bearer.split(" ")[1]
    # logger.info(f"Access Key: {access_key}")
    requestData: dict = await request.json()
    messageData: list[dict] = requestData.get("data", [])
    userPrompt: str = [item for item in messageData if item.get(
        "role") == "user"][-1].get("content", "")
    if userPrompt == "":
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Data is required"}
    return {
        "data": [
            {
                "role": "agent",
                "content": "You said " + userPrompt,
            }
        ]
    }


@app.post("/api/v1/init")
async def init(request: Request, response: Response):
    access_key_bearer: str = request.headers.get("Authorization", "")
    if access_key_bearer.strip() == "" or access_key_bearer.strip() == "Bearer":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Unauthorized"}

    access_key: str = access_key_bearer.split(" ")[1]
    # logger.info(f"Access Key: {access_key}")
    return {
        "data": [
            {
                "role": "system",
                "content": "You are a online assistant that helps people find information.",
            },
            {
                "role": "agent",
                "content": "Hello! How can I assist you today?",
            }
        ]
    }
