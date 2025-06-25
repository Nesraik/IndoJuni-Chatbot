from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from chromadb import Documents, EmbeddingFunction, Embeddings
import os
import re
import json
from openai import OpenAI
import chromadb
from uuid import uuid4
from google.genai import types
from google import genai
from langfuse.decorators import observe
from Utils.parser import *
from langfuse import Langfuse
from langchain.document_loaders import Docx2txtLoader
from Utils.jinjaProcessor import *
langfuse = Langfuse()
    
class MultilingualEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        super().__init__()
        base_url = os.environ.get("EMBEDDING_URL")
        api_key = os.environ.get("EMBEDDING_KEY")
        self.model_name = "intfloat/multilingual-e5-large"
        self.emb_client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

    def __call__(self, input):
        outputs = self.emb_client.embeddings.create(
            model=self.model_name,
            input=input,
        )
        embeddings = []
        for out in outputs.data:
            embeddings.append(out.embedding)
        return embeddings

# Create database to store text chunks
def createDbCollection(dbname, filename,dbpath):
    custom_emb_func = MultilingualEmbeddingFunction()
    dbclient = chromadb.Client()
    dbclient = chromadb.PersistentClient(path=dbpath)
    dbcollection = dbclient.create_collection(
        name=dbname, embedding_function=custom_emb_func
    )
    with open(filename, "r") as f:
        chunk_text_docs = json.load(f)

    for i, doc in enumerate(chunk_text_docs):
        dbcollection.add(
            documents=str(doc),
            ids=str(uuid4()),
            metadatas={"source": filename, "chunk": i},
        )

    return dbcollection

def getDbCollection(dbpath,dbname):
    dbclient = chromadb.Client()
    dbclient = chromadb.PersistentClient(path=dbpath)
    custom_emb_func = MultilingualEmbeddingFunction()
    dbcollection = dbclient.get_collection(name=dbname, embedding_function=custom_emb_func)
    return dbcollection

class LLMRewriter():
    def __init__(self):
        self.client = OpenAI(
            api_key = os.environ.get("GeminiAPI"),
            base_url = "https://generativelanguage.googleapis.com/v1beta/"
        )
        self.model_name = "gemini-2.0-flash"

    @observe(name = "Rewrite Query")
    def rewriteQuery(self,messages):
        response = self.client.chat.completions.create(
            model = self.model_name,
            messages = messages,
            temperature=0.1,
            top_p=0.1,
            presence_penalty=0.0,
        )
        return response

@observe()
# Retrieve and Generate (RAG)
def RAG(dbcollection, user_message,chat_history):

    temp = {
        "user_message": user_message,
        "chat_history": chat_history
    }

    user_prompt = process_template('Prompt/rewriter_prompt.jinja', temp)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that rewrites user message into relevant query for RAG."
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ]

    Rewriter= LLMRewriter()
    response = Rewriter.rewriteQuery(messages)
    response = extract_json_dict(response.choices[0].message.content)

    if response['Rewritten query'] == "NONE":
        return "No relevant information found."
    else:
        context_list = []
        for subquery in response['Subquery']:
            results = dbcollection.query(
                query_texts=subquery,
                n_results=2,
            )
            for doc in results['documents'][0]:
                context_list.append(doc)
                
    context = "\n".join(doc for doc in context_list)
    return context