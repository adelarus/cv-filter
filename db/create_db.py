import json
from sqlalchemy import DateTime, create_engine, Table, Column, Integer, String, MetaData
import os

file_name = 'tasks.db'
engine = create_engine(f'sqlite:///{file_name}')
metadata = MetaData()

try:
    os.remove(file_name)
except FileNotFoundError:
    pass

tasks = Table('tasks', metadata,
              Column('id', Integer, primary_key=True),
              Column('status', String),
              Column('type', String),
              Column('filename', String),
              Column('payload', String),
              Column('timestamp', DateTime)
            )
metadata.create_all(engine)
conn = engine.connect()