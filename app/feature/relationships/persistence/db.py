import os
from sqlmodel import SQLModel, create_engine

from app.feature.relationships.persistence.models import *

# local stored database
DATABASE_URL = r"sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "relationships_app.db")

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    """Cria as tabelas específicas do módulo relationships."""
    # Importar apenas os modelos do relationships para evitar conflitos
    from app.feature.relationships.persistence.models import Person, Interaction, Reminder
    
    # Criar engine específico para este módulo
    relationships_engine = create_engine(DATABASE_URL, echo=False)
    
    # Criar apenas as tabelas do relationships
    SQLModel.metadata.create_all(relationships_engine)

# Removido: create_db_and_tables() - não executar automaticamente
