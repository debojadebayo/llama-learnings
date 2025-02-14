from flask import Flask, request, jsonify, make_response
from multiprocessing.managers import BaseManager
import os
from flask_cors import CORS
from werkzeug.utils import secure_filename

app = Flask(__name__) 
CORS(app)

manager = BaseManager(("", 5000), b"password")
manager.register("query_index")
manager.register("insert_into_index")
manager.regiser("get_documents_list")
manager.connect()


@app.route("/query", methods=["GET"])
def query_index():
    global index 
    query_text = request.args.get("text", None)
    if query_text is None:
        return ("No text found, please include a ?text=blah parameter in the URL", 400,)
    
    response = manager.query_index(query_text)._getvalue()
    response_json = {
        "text": str(response),
        "sources": [{"text": str(x.text), 
                     "similarity": round(x.score, 2),
                     "doc_id": str(x.id_),
                     "start": x.node_info['start'],
                     "end": x.node_info['end'],
                    } for x in response.source_nodes]
        
    }
    return make_response(jsonify(response_json)), 200

@app.route("/uploadFile", methods=["POST"])
def upload_file():
    global manager 
    if "file" not in request.files:
        return "Please send a POST request with a file", 400
    
    filepath = None 
    
    try: 
        uploaded_file = request.files["file"]
        filename = secure_filename(uploaded_file.filename)
        filepath = os.path.join("documents", os.path.basename(filename))
        uploaded_file.save(filepath)
        
        if request.form.get("filename_as_doc_id", None) is not None:
            manager.insert_into_index(filepath, doc_id=filename)
        else: 
            maanager.insert_into_index(filepath) 
        
    except Exception as e:
        if filepath is not None and os.path.exists(filepath):
            os.remove(filepath)
        return f"Error uploading file: {str(e)}", 500
    
    if filepath is not None and os.path.exists(filepath):
        os.remove(filepath)
        
    return "File uploaded successfully", 200

@app.route("/getDocumentsList") 
def get_documents_list():
    document_list = manager.get_documents_list() 
    
    return make_response(jsonify(document_list)), 200

@app.route("/")
def home():
    return "Hello World! Welcome to the lllama_index docker image"

if __name__ == "__main__":
    app.run(host= "0.0.0.0", port=5066, debug=True)