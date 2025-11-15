import logging
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi import HTTPException
from chatbot import Chatbot
# uvicorn app:app --host 0.0.0.0 --port 8114 --reload
app = FastAPI()
logger = logging.getLogger("uvicorn.error")

# Get user prompt
@app.post("/api/v1/chat")
async def chat(request: Request, response: Response):

    # Check authorization header
    access_key_bearer: str = request.headers.get("Authorization", "")
    if access_key_bearer.strip() == "" or access_key_bearer.strip() == "Bearer":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Unauthorized"}
    access_key: str = access_key_bearer.split(" ")[1]
    # logger.info(f"Access Key: {access_key}")

    # Handle bot request
    requestData: dict = await request.json()
    try:
        messages = requestData.get("messages", [])
        userPrompt = requestData.get("user_prompt", "")
        flag = requestData.get("flag", False)
        chatbot = Chatbot(access_token=access_key)

        messages, flag = chatbot.generate_single_chat_message(userPrompt, messages, flag)
        
        return {
            "messages": messages,
            "flag": flag
        }

    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return response.status_code
