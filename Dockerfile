FROM indojuni-chatbot:base

WORKDIR /app
COPY . .

EXPOSE 8114
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8114"]
