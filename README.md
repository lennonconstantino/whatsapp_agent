# WhatsApp Agent - Sistema de Agentes Inteligentes

Sistema de agentes inteligentes para WhatsApp que permite gerenciar finanças pessoais e relacionamentos através de interface conversacional natural.

## 🚀 Funcionalidades

### 💰 **Feature Finance** 
- **Gestão de Receitas e Despesas**: Cadastro, consulta e análise de movimentações financeiras
- **Cálculo Automático de Impostos**: Taxa padrão de 19% com cálculos automáticos de valores líquidos/brutos
- **Gestão de Clientes**: Cadastro e consulta de clientes com informações completas
- **Relatórios**: Consultas personalizadas por período, categoria e valores

### 👥 **Feature Relationships**
- **Gestão de Contatos**: Cadastro e organização de pessoas importantes
- **Rastreamento de Interações**: Monitoramento de frequência e qualidade de contatos
- **Lembretes Inteligentes**: Agendamento de follow-ups, aniversários e datas especiais
- **Sugestões Personalizadas**: Recomendações baseadas em preferências e histórico

## 🛠️ Tecnologias

- **Backend**: FastAPI + Python 3.12
- **Banco de Dados**: SQLite com SQLModel
- **IA/LLM**: OpenAI GPT (Whisper para transcrição de áudio)
- **Integração**: WhatsApp Business API via Meta Graph
- **Deploy**: Uvicorn + Ngrok para desenvolvimento

## 📋 Pré-requisitos

- Python 3.12+
- Conta Meta Developer (WhatsApp Business API)
- Token de acesso OpenAI
- Ngrok para desenvolvimento local

## ⚙️ Configuração

### 1. **Variáveis de Ambiente**
Crie um arquivo `.env` na raiz do projeto:

```bash
# WhatsApp Business API
WHATSAPP_API_TOKEN=seu_token_aqui
MY_BUSINESS_TELEFONE=seu_numero_whatsapp

# OpenAI
OPENAI_API_KEY=sua_chave_openai

# Webhook
VERIFICATION_TOKEN=seu_token_webhook
```

### 2. **Usuários Autorizados**
Crie um arquivo `allowed_users.json` na raiz:

```json
[
  {
    "phone": "5511999999999",
    "first_name": "Seu",
    "last_name": "Nome",
    "id": 1
  }
]
```

### 3. **Instalação de Dependências**
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate     # Windows

# Instalar dependências
pip install -r requirements.txt
```

## 🚀 Inicialização

### 1. **Iniciar Ngrok** (para desenvolvimento)
```bash
ngrok http 8000
```

### 2. **Configurar Webhook WhatsApp**
- Acesse [Meta Developer Console](https://developers.facebook.com/)
- Configure a URL de callback: `https://seu-dominio.ngrok-free.app/webhook`
- Use o `VERIFICATION_TOKEN` configurado no `.env`

### 3. **Iniciar o Servidor**
```bash
# Desenvolvimento com reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Produção
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. **Carregar Dados Mock** (opcional)
```bash
# Finance
python -m app.feature.finance.persistence.mock_data

# Relationships
python -m app.feature.relationships.persistence.mock_data
```

## 📱 Como Usar

### **Gestão Financeira**
```
# Consultas
"Liste minhas despesas deste mês"
"Total de receitas entre 2024-01-01 e 2024-03-31"

# Adicionar
"Adicionar despesa: descrição=Almoço, net=120.00, data=2024-07-10"
"Registrar receita de projeto 10000.00 hoje"
```

### **Gestão de Relacionamentos**
```
# Contatos
"Adicionar contato Ana Silva phone 5511999999999 cidade São Paulo"

# Interações
"Conversei com João ontem por ligação sobre viagem foi ótimo"

# Lembretes
"Criar lembrete para falar com Maria amanhã motivo aniversário"
```

## 📁 Estrutura do Projeto

```
whatsapp_agent/
├── app/
│   ├── domain/           # Agentes base e ferramentas
│   ├── feature/          # Features específicas
│   │   ├── finance/      # Gestão financeira
│   │   └── relationships/ # Gestão de relacionamentos
│   ├── infrastructure/   # Configurações externas
│   └── persistence/      # Modelos e banco de dados
├── main.py               # Aplicação FastAPI
└── requirements.txt      # Dependências Python
```

## 📚 Documentação Detalhada

### **Arquitetura e Funcionalidades**
- **[RELATIONSHIPS_FEATURE.md](RELATIONSHIPS_FEATURE.md)**: Especificações completas da feature de relacionamentos
- **[FINANCE_FEATURE.md](FINANCE_FEATURE.md)**: Guia de uso da gestão financeira
- **[instructions.md](instructions.md)**: Configuração da Meta API e webhooks

### **Funcionalidades por Feature**

#### **Finance**
- **Entidades**: Expense, Revenue, Customer
- **Regras**: Cálculo automático de impostos (19%)
- **Agentes**: query_agent, add_expense_agent, add_revenue_agent, add_customer_agent

#### **Relationships**
- **Entidades**: Person, Interaction, Reminder
- **Foco**: Assistente social pessoal para relacionamentos
- **Agentes**: query_relationships_agent, add_person_agent, log_interaction_agent, schedule_reminder_agent

## 🔧 Desenvolvimento

### **Estrutura de Agentes**
- **RoutingAgent**: Roteia intenções para agentes específicos
- **TaskAgent**: Executa tarefas específicas com ferramentas dedicadas
- **Tools**: Operações CRUD e consultas especializadas

### **Adicionar Nova Feature**
1. Criar estrutura em `app/feature/nova_feature/`
2. Implementar modelos, ferramentas e agentes
3. Adicionar ao `message_service.py`
4. Configurar webhook e testes

## 🧪 Testes

```bash
# Testes unitários
python -m pytest

# Testes de integração
python -m pytest tests/integration/

# Testes end-to-end
python -m pytest tests/e2e/
```

## 🚨 Solução de Problemas

### **Erros Comuns**
- **"Agent not found"**: Verificar se o agente está registrado no RoutingAgent
- **"Missing values"**: Verificar se os modelos têm arg_model configurado
- **Webhook não funciona**: Verificar Ngrok e VERIFICATION_TOKEN

### **Logs e Debug**
- Ativar modo verbose nos agentes
- Verificar logs do FastAPI
- Monitorar chamadas da OpenAI API

## 🔒 Segurança

- **Autenticação**: Controle de usuários por número de telefone
- **Privacidade**: Dados locais, sem compartilhamento externo
- **Validação**: Input sanitization e validação de modelos Pydantic

## 📈 Roadmap

- [ ] Categorização automática de transações
- [ ] Integração com calendários externos
- [ ] Análise de sentimento em relacionamentos
- [ ] Dashboard web para visualização
- [ ] Exportação de dados (CSV/PDF)
- [ ] Notificações proativas

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma [Issue](../../issues)
- Consulte a documentação em [docs/](docs/)
- Entre em contato via [Discussions](../../discussions)

---

**Desenvolvido com ❤️ para facilitar a gestão pessoal via WhatsApp**