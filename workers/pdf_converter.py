import json
import os
import chromadb
import uuid
from pdfminer.high_level import extract_text
from celery import Celery

CVS_PATH = 'cvs'
CELERY_BROKER_URL = f"sqlalchemy+sqlite:///db.sqlite3"

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="pdf_texts", 
    metadata={
        "hnsw:space": "cosine"
    })
pdf_converter = Celery("tasks", broker=CELERY_BROKER_URL)

@pdf_converter.task
def convert_pdf(filename):
    if not os.path.exists(os.path.join(CVS_PATH, filename)):
        raise Exception(f"File {filename} not found")
    
    text = extract_text(os.path.join(CVS_PATH, filename))
    doc_id = str(uuid.uuid4())
    
    collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[{"filename": filename}]
    )

    print(f"No of items {collection.count()}")
    print(f"{filename} was indexed")


def process_pdf(filename, text):
    if not os.path.exists(os.path.join(CVS_PATH, filename)):
        raise Exception(f"File {filename} not found")
 
    doc_id = str(uuid.uuid4())
    
    collection.add(
        ids=[doc_id],
        documents=[text],
        metadatas=[{"filename": filename}]
    )

    print(f"No of items {collection.count()}")
    print(f"{filename} was indexed")


def index_skills(filename, skills_list):
    print(f"Indexing skills for {filename}")

    for skill in skills_list:
        doc_id = str(uuid.uuid4())
        collection.add(
            ids=[doc_id],
            documents=[json.dumps(skill)],
            metadatas=[{"filename": filename, "skill_name": json.dumps(skill)}]
        )
          
    print(f"Items index: {len(skills_list)}")