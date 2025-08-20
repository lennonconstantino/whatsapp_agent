import os
from sqlmodel import SQLModel, create_engine

# TODO
#from app.persistance.models import *

# local stored database
DATABASE_URL = r"sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "app.db")

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()
