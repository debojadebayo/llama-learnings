import os
import pickle
from multiprocessing import Lock 
from multiprocessing.managers import BaseManager
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex, 
    StorageContext,
    load_index_from_storage,
)
from dotenv import load_dotenv
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings import OpenAIEmbedding 
from llama_index.llms import OpenAI


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") 

index = None 
stored_docs = {}

"""
A lock to ensure only one thread is accessing the index at a time. Prevents mutation of index whilst  querying 
"""
lock = Lock()

index_dir = "./.index"
pkl_name = "stored_documents.pkl"

def initialise_index():
    """Creates a new global index or loads ones from the pre-set path."""
    
    global index, stored_docs
    
    transformations = SentenceSplitter(chunk_size= 512)
    embed_model = OpenAIEmbedding(model_name = "text-embedding-3-small")
    
    with lock:
   
        if os.path.exists(index_dir):
            storage_context = StorageContext.from_defaults(persist_dir=index_dir)
            index = load_index_from_storage(storage_context)
        else:
            index = VectorStoreIndex(nodes=[], embed_model=embed_model)
            index.storage_context.persist(index_dir)
        if os.path.exists(pkl_name):
            with open(pkl_name, "rb") as f:
                stored_docs = pickle.load(f)

def query_index(query_text):
    global index  
    llm = OpenAI(model="gpt-4o-mini")
    query_engine = index.as_query_engine(similarity_top_k=3, llm=llm)
    response = query_engine.query(query_text)
    return response

def insert_into_index(doc_text, doc_id=None):
    global index, stored_docs
    documents = SimpleDirectoryReader(input_files=[doc_text]).load_data()
    
    with lock:  
        for document in documents: 
           if doc_id is not None:
               document.id_ = doc_id
           index.insert(document)
           stored_docs[document.id_] = document.text[0:200]
        
        index.storage_context.persist(index_dir)
        
        with open(pkl_name, "wb") as f:
            pickle.dump(stored_docs, f)
    return 

def get_documents_list():
    """Get the list of currently stored documents."""
    global stored_doc
    documents_list = []
    for doc_id, doc_text in stored_docs.items():
        documents_list.append({"id": doc_id, "text": doc_text})

    return documents_list
        
if __name__ == "__main__":
    print("Initialising index...")
    initialise_index()
    
    # setup up server 
    
    manager = BaseManager(("", 5000), b"password")
    manager.register("query_index", query_index)
    manager.register("insert_into_index", insert_into_index)
    manager.register("get_documents_list", get_documents_list)
    server = manager.get_server()
    
    print("starting server...")
    server.serve_forever()