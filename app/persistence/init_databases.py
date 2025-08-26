#!/usr/bin/env python3
"""
Script para inicializar os bancos de dados de cada módulo separadamente.
Execute este script antes de usar os agentes para garantir que as tabelas estejam criadas.
"""

def init_finance_db():
    """Inicializa o banco de dados do módulo finance."""
    from app.feature.finance.persistence.db import create_db_and_tables
    print("Inicializando banco de dados finance...")
    create_db_and_tables()
    print("✅ Banco finance inicializado com sucesso!")

def init_relationships_db():
    """Inicializa o banco de dados do módulo relationships."""
    from app.feature.relationships.persistence.db import create_db_and_tables
    print("Inicializando banco de dados relationships...")
    create_db_and_tables()
    print("✅ Banco relationships inicializado com sucesso!")

def init_all_databases():
    """Inicializa todos os bancos de dados."""
    init_finance_db()
    print()
    init_relationships_db()
    print()
    print("🎉 Todos os bancos de dados foram inicializados!")

if __name__ == "__main__":
    init_all_databases()
