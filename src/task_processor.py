import concurrent
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from workers.pdf_converter import process_pdf
from workers.pdf_converter import index_skills
from multiprocessing import Lock
from pdfminer.high_level import extract_text
from chatwrap.client import LLMClient
import json

import os

CVS_PATH = 'CVs'
LLM_SERVER_URL = 'https://api.openai.com/v1/chat/completions'

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

        llmClient = LLMClient(LLM_SERVER_URL)

        skills_response = llmClient.send_request(text)

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

    #tasks = session.query(Task).filter_by(status='PENDING').all()
    tasks = [session.query(Task).first()]

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(process_task, task, session) for task in tasks]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    session.close()

if __name__== "__main__":

    # while True:
    #     processTasks()
    #     time.sleep(5)


    processTasks()