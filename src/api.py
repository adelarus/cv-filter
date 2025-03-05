import os
import uuid
from flask import Flask, jsonify, request
from chatwrap.client import LLMClient
from workers.pdf_converter import convert_pdf
import chromadb

app = Flask(__name__)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="pdf_texts", 
    metadata={
        "hnsw:space": "cosine"
    })
LLM_SERVER_URL = 'http://localhost:1234/v1'

CVS_PATH = 'CVs'

@app.route('/cv/upload', methods=['POST'])
def upload_file():
 
    file = request.files['file']
   
    if not os.path.exists(CVS_PATH):
        os.makedirs(CVS_PATH)
       
    file.save(os.path.join(CVS_PATH, file.filename))
   
    convert_pdf.delay(file.filename)
 
    return 'Uploaded'

@app.route('/candidates/find', methods=['POST'])
def find_candidates():
    query_text = request.get_json().get('query') 

    threshold = request.get_json().get('threshold', 0.8)

    print(f"No of items {collection.count()}")

    results = collection.query(
        query_texts=[query_text],
        n_results=5
    )

    metadatas = results.get('metadatas', [{}])[0] 
    filenames = [metadata.get('filename') for metadata in metadatas]

    distances = results.get('distances', [{}])[0]
    
    similarity = list(zip(filenames, distances))

    sorted_similarity = sorted(similarity, key=lambda x: x[1])
    filtered_similarity = [item for item in sorted_similarity if item[1] < threshold]

    return jsonify(filtered_similarity)

if __name__ == '__main__':
    app.run()