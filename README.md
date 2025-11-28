# CHATBOT
A bot for assisting INDOJUNI customer. This version of chatbot uses the latest kimi-instruct model.

## Tools
### Implemented
- Get product details
- Get product in cart
- Add product to cart
- Modify product in cart
- Show Invoice
- Checkout cart

## Prerequisite
Installation using the provided requirements file.
```bash
pip install -r requirements.txt
```

Create `.env` file containing
```env
# INDOJUNI CREDENTIAL
base_url = "https://indojuni.cafaku.dev"
email = "user@gmail.com"
password = *****

# LANGFUSE 
LANGFUSE_SECRET_KEY=********************************
LANGFUSE_PUBLIC_KEY=********************************
LANGFUSE_HOST="http://localhost:3000"

# CHATBOT
CHATBOT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/"
CHATBOT_MODEL = "gemini-2.5-flash"
CHATBOT_API_KEY = *******************************
```

## Usage
```python
from chatbot import Chatbot
chatbot = Chatbot()

## For testing in terminal
chatbot.run_conversation()

## For UI
messages, flag = chatbot.generate_single_chat_message(
    user_prompt,
    messages,
    flag
)
```

## Note
- RAG is discarded
- Checkout is temporarily unavailable

## Next Approach
- Test interaction using every tool