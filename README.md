# CHATBOT
A bot for assisting INDOJUNI customer. This version of chatbot uses the latest kimi-instruct

## Tools
### Implemented
- Get product details
- Get product in cart
- Add product to cart
- Modify product in cart
- Show Invoice

### Work In Progress
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

# EMBEDDING
EMBEDDING_MODEL = "intfloat/multilingual-e5-large"
EMBEDDING_URL = http://elima.cafaku.dev/v1

# LANGFUSE 
LANGFUSE_SECRET_KEY=********************************
LANGFUSE_PUBLIC_KEY=********************************
LANGFUSE_HOST="http://localhost:3000"

# GEMINI
GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/"
GeMINI_API = *************

# CHATBOT
CHATBOT_BASE_URL = "https://api.groq.com/openai/v1"
CHATBOT_MODEL = "moonshotai/kimi-k2-instruct"
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

## Next Approach
- Incorporate knowledge graph into chatbot. Use RAG as a fall-back in case knowledge graph fails to retrieve relevant item