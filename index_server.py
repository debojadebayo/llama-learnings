import os
from multiprocessing import Lock 
from multiprocessing.managers import BaseManager
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex, 
    StorageContext,
    load_index_from_storage,
    Document
)
from dotenv import load_dotenv


load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY") 

index = None 

"""
A lock to ensure only one thread is accessing the index at a time.

When multiple users are uploading/ reading from vector index at the same time, 
this lock ensures that this happens one at a time. Prevents index from being 
mutated whilst another person is reading from database.

This prevents race conditions from occurring and ensures that the index is 
always in a valid state.
"""
lock = Lock()

def initialise_index():
    """Creates a new global index or loads ones from the pre-set path."""
    
    global index  
    
    with lock:
        index_dir = "./.index"
    
        if os.path.exists(index_dir):
            storage_context = StorageContext.from_defaults(persist_dir=index_dir)
            index = load_index_from_storage(storage_context)
        else:
            documents = SimpleDirectoryReader(input_files=["./documents/paul_graham_essay.txt"]).load_data()
            index = VectorStoreIndex.from_documents(
                documents, 
                storage_context=storage_context
            )
            index.storage_context.persist(index_dir)

def query_index(query_text):
    global index  
    query_engine = index.as_query_engine()
    response = query_engine.query(query_text)
    return str(response), 200

if __name__ == "__main__":
    print("Initialising index...")
    initialise_index()
    
    # setup up server 
    
    manager = BaseManager(("", 5000), b"password")
    manager.register("query_index", query_index)
    server = manager.get_server()
    
    print("starting server...")
    server.serve_forever()