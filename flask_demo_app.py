from flask import Flask, request
from multiprocessing.managers import BaseManager
from index_server import index, initialise_index

app = Flask(__name__) 


manager = BaseManager(("", 5000), b"password")
manager.register("query_index")
manager.connect()

@app.route("/")
def home():
    return "Hello World!"

@app.route("/query", methods=["GET"])
def query_index():
    global index 
    query_text = request.args.get("text", None)
    if query_text is None:
        return ("No text found, please include a ?text=blah parameter in the URL", 400,)
    response = manager.query_index(query_text)._getvalue()
    return str(response), 200
    


if __name__ == "__main__":
    app.run(host= "0.0.0.0", port=5066, debug=True)