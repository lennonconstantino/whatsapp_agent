import os
from sqlmodel import SQLModel, create_engine

from app.feature.finance.persistence.models import *

# local stored database
DATABASE_URL = r"sqlite:///" + os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))), "finance_app.db")

engine = create_engine(DATABASE_URL, echo=False)

def create_db_and_tables():
    """Cria as tabelas específicas do módulo finance."""
    # Importar apenas os modelos do finance para evitar conflitos
    from app.feature.finance.persistence.models import Expense, Revenue, Customer
    
    # Criar engine específico para este módulo
    finance_engine = create_engine(DATABASE_URL, echo=False)
    
    # Criar apenas as tabelas do finance
    SQLModel.metadata.create_all(finance_engine)

# Removido: create_db_and_tables() - não executar automaticamente
