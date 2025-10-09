FROM indojuni-chatbot:base

COPY . .

EXPOSE 8114
CMD ["python", "app.py"]
