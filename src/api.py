import os
import uuid
from flask import Flask, jsonify, request
from chatwrap.client import LLMClient
from src.index_utils import convert_pdf
import chromadb
from flask_cors import CORS
from src.scoring_utils import calculate_score
import src.system_prompts as sp

app = Flask(__name__)
CORS(app)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="pdf_texts", 
    metadata={
        "hnsw:space": "cosine"
    })
LLM_SERVER_URL = 'https://api.openai.com/v1/chat/completions'

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

    llmClient = LLMClient(LLM_SERVER_URL, os.getenv('OPENAI_API_KEY'))

    skills_response = llmClient.send_request(query_text, system_prompt = sp.JOB_DESCRIPTION_EXTRACTOR)

    print(skills_response)

    threshold = request.get_json().get('threshold', 0.8)

    print(f"No of items {collection.count()}")

    results = collection.query(
        query_texts=[query_text],
        n_results=5
    )

    metadatas = results.get('metadatas', [{}])[0] 
    filenames = [metadata.get('filename') for metadata in metadatas]
    skills = [metadata.get('skill_name') for metadata in metadatas]

    distances = results.get('distances', [{}])[0]
    
    similarity = list(zip(filenames, distances, skills))

    sorted_similarity = sorted(similarity, key=lambda x: x[1])
    filtered_similarity = [item for item in sorted_similarity if item[1] < threshold]

    final_scores = calculate_score(filtered_similarity)

    return jsonify(final_scores)

if __name__ == '__main__':
    app.run()