import os
from sqlmodel import SQLModel, create_engine

from app.feature.finance.persistance.models import *

DATABASE_DB = "finance_app.db"

# local stored database
#DATABASE_URL = r"sqlite:///" + os.path.join(os.path.dirname(__file__), DATABASE_DB)
#DATABASE_URL = r"sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), DATABASE_DB)
DATABASE_URL = r"sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), DATABASE_DB)

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()
