from chromadb import EmbeddingFunction
import os
import json
from openai import OpenAI
import chromadb
from uuid import uuid4
from langfuse.decorators import observe
from Utils.parser import *
from langfuse import Langfuse
from Utils.jinjaProcessor import *
langfuse = Langfuse()

class MultilingualEmbeddingFunction(EmbeddingFunction):
    def __init__(self):
        super().__init__()
        base_url = os.environ.get("EMBEDDING_URL")
        #api_key = os.environ.get("EMBEDDING_KEY")
        self.model_name = os.environ.get("EMBEDDING_MODEL")
        self.emb_client = OpenAI(
            base_url=base_url,
            api_key="pretend_this_is_an_api_key"
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
    
class ContextRetriever():
    def __init__(self):
        self.client = OpenAI(
            api_key = os.environ.get("GEMINI_API"),
            base_url = os.environ.get("GEMINI_BASE_URL")
        )
        self.model_name = os.environ.get("GEMINI_MODEL")
        self.dbname="IndoJuni",
        self.filename="Knowledge base/productCatalog.json",
        self.dbpath="VectorDB"

        try:
            self.dbcollection = self._createDbCollection()
        except Exception as e:
            self.dbcollection = self._getDbCollection()
    
    # Create database to store text chunks
    def _createDbCollection(self):
        custom_emb_func = MultilingualEmbeddingFunction()
        dbclient = chromadb.Client()
        dbclient = chromadb.PersistentClient(path=self.dbpath)
        dbcollection = dbclient.create_collection(
            name=self.dbname, embedding_function=custom_emb_func
        )
        with open(self.filename, "r") as f:
            chunk_text_docs = json.load(f)

        for i, doc in enumerate(chunk_text_docs):
            dbcollection.add(
                documents=str(doc),
                ids=str(uuid4()),
                metadatas={"source": self.filename, "chunk": i},
            )

        return dbcollection

    def _getDbCollection(self):
        dbclient = chromadb.Client()
        dbclient = chromadb.PersistentClient(path=self.dbpath)
        custom_emb_func = MultilingualEmbeddingFunction()
        dbcollection = dbclient.get_collection(name=self.dbname, embedding_function=custom_emb_func)
        return dbcollection
    
    @observe(name = "Rewrite Query")
    def _rewriteQuery(self,messages):
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
    def retrieveContext(self, user_message, chat_history):

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

        response = self._rewriteQuery(messages)
        response = extract_json_dict(response.choices[0].message.content)

        if response['Rewritten query'] == "NONE":
            return "No relevant information found."
        else:
            context_list = []
            for subquery in response['Subquery']:
                results = self.dbcollection.query(
                    query_texts=subquery,
                    n_results=2,
                )
                for doc in results['documents'][0]:
                    context_list.append(doc)
                    
        context = "\n".join(doc for doc in context_list)
        return context

