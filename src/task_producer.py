from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from argparse import ArgumentParser
import os

CVS_PATH = 'CVs'
Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    type = Column(String)
    status = Column(String)
    filename = Column(String)
    payload = Column(String)

def saveNewTask(filename):
    engine = create_engine('sqlite:///tasks.db')
    Session = sessionmaker(bind=engine)
    session = Session()

    task = Task(type='EXTRACT_SKILLS', status='PENDING', filename=filename, payload="")
    session.add(task)
    session.commit()
    session.close()

def cli(params): 
    file_path = params.path

    for filename in os.listdir(file_path):
        
        saveNewTask(filename)
        print(f"File {filename} was indexed")

if __name__== "__main__":

    args = ArgumentParser('CV indexing')
    
    args.add_argument('--path', help='path of CV folder', default='cd ')

    params = args.parse_args()

    cli(params)
