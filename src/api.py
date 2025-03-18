import os

from flask import Flask, jsonify, request
from flask.helpers import send_from_directory

from chatwrap.client import LLMClient
from src.index_utils import convert_pdf

import chromadb

from flask_cors import CORS
from src.scoring_utils import Matches

import src.system_prompts as sp

app = Flask(__name__)
app.json.sort_keys = False

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

    matches_list = Matches()

    for skill in skills_response:
        query_text = f"{skill['skill']} {skill['years']} years"
        
        results = collection.query(
            query_texts=[query_text],
            n_results=15
        )

        metadatas = results.get('metadatas', [{}])[0] 
        distances = results.get('distances', [{}])[0]
        filenames = [metadata.get('filename') for metadata in metadatas]
        skills = [metadata.get('skill_name') for metadata in metadatas]

        results = list(zip(filenames, distances, skills, metadatas))

        matches_list.add_matches(skill, results)

    final_scores = matches_list.calculate_scores()

    #remove duplicate skills
    for cv in final_scores:
        final_scores[cv]['skills'] = list(set(final_scores[cv]['skills']))

    return jsonify(final_scores)

@app.route('/cv/<cv_name>')
def get_cv(cv_name):
    return send_from_directory('../CVs', cv_name)

if __name__ == '__main__':
    app.run()