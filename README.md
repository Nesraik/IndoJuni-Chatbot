# CHATBOT
A bot for assisting INDOJUNI customer.

## Tools
### Implemented
- Search product List -> search list of product using keyword
- Get product in cart -> get list of product in cart
- Add product to cart -> add product into cart
- Modify product in cart -> modify product (name,quantity) in cart
- Show Invoice -> show the invoice
- Checkout cart -> checkout the current cart

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
CHATBOT_MODEL = "gemini-2.5-flash-lite"
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

## Next Approach
- Test interaction again using every tool (if needed)
- Make LLM judge