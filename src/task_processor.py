import concurrent
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

from multiprocessing import Lock
from pdfminer.high_level import extract_text
from chatwrap.client import LLMClient
from dotenv import load_dotenv
from src.index_utils import index_skills
import src.system_prompts as sp

import os

CVS_PATH = 'CVs'
LLM_SERVER_URL = 'https://api.openai.com/v1/chat/completions'

load_dotenv()

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    status = Column(String)
    filename = Column(String)
    payload = Column(String)

def process_task(task, session):
    try:        
        task.status = 'IN_PROGRESS'
    
        lock = Lock()   
          
        print(f"Processing task {task.id}")
        text = extract_text(os.path.join(CVS_PATH, task.filename))

        llmClient = LLMClient(LLM_SERVER_URL, os.getenv('OPENAI_API_KEY'))

        skills_response = llmClient.send_request(text, system_prompt = sp.SKILLS_EXTRACTOR)

        index_skills(task.filename, skills_response)
        
        task.status = 'COMPLETED'

        with lock:
            session.commit()

        print(f"Task {task.id} processed")
    except Exception as e:
        task.status = 'FAILED'
        print(f"Error processing task {task.id}: {e}") 

        with lock:
            session.commit() 

    print(f"Task {task.id} processed")

def processTasks():
    engine = create_engine('sqlite:///tasks.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    tasks = session.query(Task).filter_by(status='PENDING').all()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_task, task, session) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    session.close()

if __name__== "__main__":

    while True:
        processTasks()
        time.sleep(5)