import argparse
from datetime import datetime, date
from pathlib import Path
from sqlmodel import Session, create_engine, SQLModel
from app.feature.relationships.persistence.models import Person, Interaction, Reminder

# Uso:
# python -m app.feature.relationships.persistence.mock_data --db-name "relationships_app.db" --db-path "./"
# ou
# python mock_data.py --db-name "relationships_app.db" --db-path "./databases"

def main():
    # Parse argumentos da linha de comando
    parser = argparse.ArgumentParser(description="Carregar dados mock no banco")
    parser.add_argument("--db-name", "-d", 
                       default="mock_data.db", 
                       help="Nome do arquivo do banco de dados")
    parser.add_argument("--db-path", "-p", 
                       default=".", 
                       help="Caminho onde salvar o banco")
    
    args = parser.parse_args()
    
    # Criar caminho completo do banco
    db_path = Path(args.db_path) / args.db_name
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Criar engine
    engine = create_engine(f"sqlite:///{db_path}")

    SQLModel.metadata.create_all(engine)

    # Mock data for Person
    people = [
        {
            "id": 1, 
            "first_name": "João", 
            "last_name": "Silva", 
            "phone": "+55 11 99999-1111", 
            "tags": "cliente,tech,startup", 
            "birthday": date(1985, 3, 15), 
            "city": "São Paulo", 
            "notes": "CEO da TechStart, interessado em soluções de IA"
        },
        {
            "id": 2, 
            "first_name": "Maria", 
            "last_name": "Santos", 
            "phone": "+55 21 98888-2222", 
            "tags": "parceiro,design,creative", 
            "birthday": date(1990, 7, 22), 
            "city": "Rio de Janeiro", 
            "notes": "Designer freelancer, sempre pontual nos projetos"
        },
        {
            "id": 3, 
            "first_name": "Carlos", 
            "last_name": "Oliveira", 
            "phone": "+55 31 97777-3333", 
            "tags": "fornecedor,logistica,confiável", 
            "birthday": date(1978, 11, 8), 
            "city": "Belo Horizonte", 
            "notes": "Proprietário da LogiFast, excelente serviço"
        },
        {
            "id": 4, 
            "first_name": "Ana", 
            "last_name": "Costa", 
            "phone": "+55 41 96666-4444", 
            "tags": "investidor,financeiro,estratégico", 
            "birthday": date(1982, 5, 12), 
            "city": "Curitiba", 
            "notes": "Partner da Venture Capital, sempre busca inovação"
        },
        {
            "id": 5, 
            "first_name": "Pedro", 
            "last_name": "Ferreira", 
            "phone": "+55 51 95555-5555", 
            "tags": "mentor,experiência,network", 
            "birthday": date(1975, 9, 30), 
            "city": "Porto Alegre", 
            "notes": "Ex-executivo da Microsoft, agora consultor independente"
        }
    ]

    # Mock data for Interaction
    interactions = [
        {
            "id": 1, 
            "person_id": 1, 
            "date": datetime(2024, 1, 15, 14, 30), 
            "channel": "whatsapp", 
            "type": "consulta", 
            "summary": "João perguntou sobre integração com APIs de IA", 
            "sentiment": 0.8
        },
        {
            "id": 2, 
            "person_id": 1, 
            "date": datetime(2024, 1, 20, 10, 15), 
            "channel": "email", 
            "type": "proposta", 
            "summary": "Enviada proposta comercial para projeto de chatbot", 
            "sentiment": 0.9
        },
        {
            "id": 3, 
            "person_id": 2, 
            "date": datetime(2024, 1, 18, 16, 45), 
            "channel": "telefone", 
            "type": "reunião", 
            "summary": "Discussão sobre redesign da interface do usuário", 
            "sentiment": 0.7
        },
        {
            "id": 4, 
            "person_id": 3, 
            "date": datetime(2024, 1, 22, 9, 0), 
            "channel": "whatsapp", 
            "type": "negociação", 
            "summary": "Acordo sobre preços de entrega para próximos 6 meses", 
            "sentiment": 0.6
        },
        {
            "id": 5, 
            "person_id": 4, 
            "date": datetime(2024, 1, 25, 15, 20), 
            "channel": "zoom", 
            "type": "apresentação", 
            "summary": "Pitch para investimento em nova funcionalidade", 
            "sentiment": 0.85
        },
        {
            "id": 6, 
            "person_id": 5, 
            "date": datetime(2024, 1, 28, 11, 30), 
            "channel": "linkedin", 
            "type": "networking", 
            "summary": "Pedro compartilhou nosso post sobre inovação em IA", 
            "sentiment": 0.9
        }
    ]

    # Mock data for Reminder
    reminders = [
        {
            "id": 1, 
            "person_id": 1, 
            "due_date": datetime(2024, 2, 5, 9, 0), 
            "reason": "Follow-up sobre proposta enviada", 
            "status": "open"
        },
        {
            "id": 2, 
            "person_id": 2, 
            "due_date": datetime(2024, 1, 30, 14, 0), 
            "reason": "Reunião de alinhamento do projeto de design", 
            "status": "completed"
        },
        {
            "id": 3, 
            "person_id": 3, 
            "due_date": datetime(2024, 2, 10, 16, 0), 
            "reason": "Renovação do contrato de logística", 
            "status": "open"
        },
        {
            "id": 4, 
            "person_id": 4, 
            "due_date": datetime(2024, 2, 15, 10, 0), 
            "reason": "Decisão sobre investimento", 
            "status": "open"
        },
        {
            "id": 5, 
            "person_id": 5, 
            "due_date": datetime(2024, 2, 1, 15, 30), 
            "reason": "Mentoria sobre estratégia de crescimento", 
            "status": "open"
        }
    ]

    with Session(engine) as session:
        # Insert People first (because interactions and reminders reference people)
        print("Inserindo pessoas...")
        for person_data in people:
            person = Person(**person_data)
            session.add(person)
        
        # Insert Interactions
        print("Inserindo interações...")
        for interaction_data in interactions:
            interaction = Interaction(**interaction_data)
            session.add(interaction)

        # Insert Reminders
        print("Inserindo lembretes...")
        for reminder_data in reminders:
            reminder = Reminder(**reminder_data)
            session.add(reminder)

        session.commit()
    
    print(f"Dados de relacionamentos inseridos em: {db_path}")
    print(f"Total de pessoas: {len(people)}")
    print(f"Total de interações: {len(interactions)}")
    print(f"Total de lembretes: {len(reminders)}")

if __name__ == "__main__":
    main()
