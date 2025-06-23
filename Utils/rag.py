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
from langfuse import Langfuse
from langchain.document_loaders import Docx2txtLoader
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
    
def extract_json_dict(text):
    """
    Extracts and parses the JSON dictionary from the input text.

    Args:
        text (str): The input text containing a JSON object inside {}.

    Returns:
        dict: The parsed JSON dictionary.

    Raises:
        ValueError: If no valid JSON object is found or if parsing fails.
    """
    # Use regex to find the JSON object enclosed in {}
    match = re.search(r"\{.*\}", text, re.DOTALL)

    if not match:
        print("No match found in the text.")
        return None

    # Extract the JSON string
    json_str = match.group(0)

    json_str = re.sub(r"\\'", "'", json_str)

    try:
        # Parse the JSON string into a Python dictionary
        json_dict = json.loads(json_str)
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None

    return json_dict

# Read data
def readJSONLines(filename):
    json_dict_list = []
    with open(filename, "r") as f:
        for line in f.readlines():
            
            json_dict = extract_json_dict(line)
            json_dict_list.append(json_dict)

    product_list = []

    for json_dict in json_dict_list:
        product = json.dumps(json_dict, ensure_ascii=False)
        product_list.append(product)

    return product_list

# Create database to store text chunks
def createDbCollection(dbname, filename,dbpath):
    custom_emb_func = MultilingualEmbeddingFunction()
    dbclient = chromadb.Client()
    dbclient = chromadb.PersistentClient(path=dbpath)
    dbcollection = dbclient.create_collection(
        name=dbname, embedding_function=custom_emb_func
    )
    chunk_text_docs = readJSONLines(filename)

    for i, doc in enumerate(chunk_text_docs):
        dbcollection.add(
            documents=doc,
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

@observe()
# Retrieve and Generate (RAG)
def RAG(dbcollection, query):
    results = dbcollection.query(
        query_texts=query,
        n_results=5,
    )
    context = "\n".join(doc for doc in results['documents'][0])
    return context