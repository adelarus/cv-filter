import json
from sqlalchemy import DateTime, create_engine, Table, Column, Integer, String, MetaData

engine = create_engine('sqlite:///tasks.db')
metadata = MetaData()
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