# Arquitetura do WhatsApp Agent

## 🏗️ Visão Geral da Arquitetura

O WhatsApp Agent é um sistema de agentes inteligentes baseado em arquitetura de domínio limpo (Clean Domain Architecture) que implementa um padrão de orquestração de IA para gerenciamento de tarefas pessoais via WhatsApp. O sistema utiliza uma arquitetura em camadas com separação clara de responsabilidades e padrões de design orientados a agentes.

## 🎯 Conceitos Arquiteturais Aplicados

### **1. Domain-Driven Design (DDD)**
- **Bounded Contexts**: Features isoladas (Finance, Relationships)
- **Aggregates**: Entidades principais com regras de negócio
- **Value Objects**: Campos específicos com validações
- **Domain Services**: Lógica de negócio encapsulada

### **2. Clean Architecture**
- **Independência de Frameworks**: FastAPI como detalhe de implementação
- **Independência de UI**: Interface WhatsApp como camada externa
- **Independência de Banco**: SQLModel como abstração de dados
- **Independência de Agentes Externos**: OpenAI como serviço externo

### **3. Multi-Agent System (MAS)**
- **RoutingAgent**: Orquestrador de intenções
- **TaskAgent**: Executores especializados
- **Tool**: Ferramentas de execução
- **Cooperação**: Agentes trabalham em conjunto
- **LangChain Integration**: Padronização com LangChain OpenAI para melhor integração
- **Tool Consolidation**: Sistema de report_tool para consolidação automática de resultados

### **4. Event-Driven Architecture**
- **Webhooks**: Recebimento de mensagens WhatsApp
- **Background Tasks**: Processamento assíncrono
- **Event Sourcing**: Histórico de execução dos agentes

## 🏛️ Estrutura de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                       │
├─────────────────────────────────────────────────────────────┤
│  FastAPI Webhook Endpoints                                 │
│  • /webhook (POST) - Recebe mensagens WhatsApp            │
│  • /webhook (GET) - Verificação do webhook                │
│  • /health, /readiness - Health checks                    │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                        │
├─────────────────────────────────────────────────────────────┤
│  Message Service                                           │
│  • Autenticação de usuários                               │
│  • Roteamento para agentes                                │
│  • Transcrição de áudio                                   │
│  • Envio de respostas                                     │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN LAYER                            │
├─────────────────────────────────────────────────────────────┤
│  Agents & Tools                                           │
│  • RoutingAgent - Orquestração                            │
│  • TaskAgent - Execução especializada                     │
│  • Tool - Ferramentas de execução                         │
│  • Base Classes - Abstrações comuns                       │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                   INFRASTRUCTURE LAYER                      │
├─────────────────────────────────────────────────────────────┤
│  External Services                                         │
│  • OpenAI GPT + LangChain - Processamento de linguagem    │
│  • WhatsApp Business API - Comunicação                    │
│  • SQLite - Persistência de dados                         │
│  • Ngrok - Túnel para desenvolvimento                     │
└─────────────────────────────────────────────────────────────┘
```

## 🧠 Padrão de Agentes Inteligentes

### **Arquitetura de Agentes**

```mermaid
graph TB
    subgraph "User Interface"
        WA[WhatsApp]
        WEB[Web Interface]
    end
    
    subgraph "Integration Layer"
        MS[Message Service]
        WH[Webhook Handler]
    end
    
    subgraph "Agent Orchestration"
        RA[Routing Agent]
        FA[Finance Agent]
        RELA[Relationships Agent]
    end
    
    subgraph "Task Execution"
        TA1[Query Agent]
        TA2[Add Agent]
        TA3[Log Agent]
        TA4[Schedule Agent]
    end
    
    subgraph "Tool Layer"
        T1[Query Tools]
        T2[Add Tools]
        T3[Log Tools]
        T4[Schedule Tools]
    end
    
    subgraph "Data Layer"
        DB1[Finance DB]
        DB2[Relationships DB]
        MODELS[SQLModel]
    end
    
    subgraph "External AI"
        OPENAI[OpenAI GPT]
        WHISPER[Whisper]
    end
    
    WA --> WH
    WEB --> WH
    WH --> MS
    MS --> RA
    RA --> FA
    RA --> RELA
    FA --> TA1
    FA --> TA2
    RELA --> TA3
    RELA --> TA4
    TA1 --> T1
    TA2 --> T2
    TA3 --> T3
    TA4 --> T4
    T1 --> MODELS
    T2 --> MODELS
    T3 --> MODELS
    T4 --> MODELS
    MODELS --> DB1
    MODELS --> DB2
    RA --> OPENAI
    MS --> WHISPER
```

### **Fluxo de Execução**

```mermaid
sequenceDiagram
    participant WA as WhatsApp
    participant WH as Webhook
    participant MS as Message Service
    participant RA as Routing Agent
    participant TA as Task Agent
    participant T as Tool
    participant DB as Database
    participant AI as OpenAI
    
    WA->>WH: Envia mensagem
    WH->>MS: Processa payload
    MS->>MS: Autentica usuário
    MS->>RA: Roteia intenção
    RA->>AI: Interpreta linguagem natural
    AI->>RA: Retorna agente apropriado
    RA->>TA: Seleciona Task Agent
    TA->>T: Executa ferramenta
    T->>DB: Persiste/consulta dados
    DB->>T: Retorna resultado
    T->>TA: Processa resultado
    TA->>MS: Retorna resposta
    MS->>WA: Envia resposta
```

## 🏢 Estrutura de Domínios

### **Domain Core (app/domain/)**

```
app/domain/
├── agents/           # Agentes base e abstrações
│   ├── agent.py     # Agent - Agente base com LangChain
│   ├── routing.py   # RoutingAgent - Orquestrador de intenções
│   ├── task.py      # TaskAgent - Executor de tarefas
│   └── utils.py     # Utilitários para agentes
├── tools/            # Ferramentas base
│   ├── tool.py      # Tool - Classe base para ferramentas
│   ├── report_tool.py # Ferramenta de relatório padrão
│   └── utils/       # Utilitários para ferramentas
├── message_service.py # Serviço de mensagens
└── exceptions.py     # Exceções de domínio
```

### **Feature Domains (app/feature/)**

```
app/feature/
├── finance/          # Domínio financeiro
│   ├── domain/      # Agentes e ferramentas financeiras
│   └── persistence/ # Modelos e banco financeiro
└── relationships/    # Domínio de relacionamentos
    ├── domain/      # Agentes e ferramentas de relacionamento
    └── persistence/ # Modelos e banco de relacionamentos
```

## 🔧 Padrões de Design Implementados

### **1. Strategy Pattern**
- **RoutingAgent**: Estratégias diferentes para diferentes tipos de intenção
- **TaskAgent**: Estratégias diferentes para diferentes tipos de tarefa
- **Tool**: Estratégias diferentes para diferentes operações

### **2. Factory Pattern**
- **Tool Creation**: Ferramentas criadas dinamicamente
- **Agent Creation**: Agentes instanciados com configurações específicas
- **Model Validation**: Validação automática via Pydantic

### **3. Observer Pattern**
- **Step History**: Histórico de execução dos agentes
- **Event Logging**: Logs de eventos e resultados
- **Background Tasks**: Processamento assíncrono de mensagens

### **4. Template Method Pattern**
- **OpenAIAgent.run()**: Template para execução de agentes
- **Tool.run()**: Template para execução de ferramentas
- **TaskAgent.load_agent()**: Template para carregamento de agentes

### **5. Dependency Injection**
- **Tool Injection**: Ferramentas injetadas nos agentes
- **Client Injection**: Cliente OpenAI injetado nos agentes
- **Context Injection**: Contexto injetado nas execuções

## 🗄️ Modelo de Dados

### **Esquema Geral do Sistema**

```mermaid
erDiagram
    USER {
        int id PK
        string first_name
        string last_name
        string phone
        enum role
    }
    
    EXPENSE {
        int id PK
        string description
        float net_amount
        float gross_amount
        float tax_rate
        datetime date
    }
    
    REVENUE {
        int id PK
        string description
        float net_amount
        float gross_amount
        float tax_rate
        datetime date
    }
    
    CUSTOMER {
        int id PK
        string company_name
        string first_name
        string last_name
        string phone
        string address
        string city
        string zip
        string country
    }
    
    PERSON {
        int id PK
        string first_name
        string last_name
        string phone
        string tags
        date birthday
        string city
        string notes
    }
    
    INTERACTION {
        int id PK
        int person_id FK
        datetime date
        string channel
        string type
        string summary
        float sentiment
    }
    
    REMINDER {
        int id PK
        int person_id FK
        datetime due_date
        string reason
        string status
    }
    
    USER ||--o{ EXPENSE : creates
    USER ||--o{ REVENUE : creates
    USER ||--o{ CUSTOMER : creates
    USER ||--o{ PERSON : creates
    PERSON ||--o{ INTERACTION : has
    PERSON ||--o{ REMINDER : has
```

### **Separação de Bancos**
- **`finance_app.db`**: Dados financeiros (Expense, Revenue, Customer)
- **`relationships_app.db`**: Dados de relacionamentos (Person, Interaction, Reminder)
- **Isolamento**: Cada feature tem seu próprio banco para independência
- **Inicialização Controlada**: Bancos são criados sob demanda para evitar conflitos

## 🔄 Fluxo de Dados

### **Pipeline de Processamento**

```mermaid
flowchart LR
    subgraph "Input"
        WA[WhatsApp Message]
        AUDIO[Audio File]
        IMAGE[Image File]
    end
    
    subgraph "Processing"
        PARSER[Message Parser]
        AUTH[User Authentication]
        EXTRACTOR[Content Extractor]
    end
    
    subgraph "AI Processing"
        ROUTER[Intent Router]
        EXECUTOR[Task Executor]
        TOOL[Tool Execution]
    end
    
    subgraph "Output"
        RESPONSE[Response Generation]
        SENDER[Message Sender]
    end
    
    WA --> PARSER
    AUDIO --> PARSER
    IMAGE --> PARSER
    PARSER --> AUTH
    AUTH --> EXTRACTOR
    EXTRACTOR --> ROUTER
    ROUTER --> EXECUTOR
    EXECUTOR --> TOOL
    TOOL --> RESPONSE
    RESPONSE --> SENDER
    SENDER --> WA
```

### **Fluxo de Decisão**

```mermaid
flowchart TD
    START[Recebe Mensagem] --> VALIDATE{Valida Usuário}
    VALIDATE -->|Não Autorizado| REJECT[Rejeita]
    VALIDATE -->|Autorizado| EXTRACT[Extrai Conteúdo]
    EXTRACT --> ROUTE[Routeia Intenção]
    ROUTE --> AGENT{Seleciona Agente}
    AGENT -->|Finance| FINANCE[Finance Agent]
    AGENT -->|Relationships| REL[Relationships Agent]
    FINANCE --> EXECUTE[Executa Tarefa]
    REL --> EXECUTE
    EXECUTE --> RESPOND[Gera Resposta]
    RESPOND --> SEND[Envia WhatsApp]
    SEND --> END[Fim]
```

## 🚀 Padrões de Integração

### **1. Webhook Integration**
- **Verificação**: Token de verificação para segurança
- **Validação**: Timestamp para evitar mensagens antigas
- **Processamento**: Background tasks para não bloquear

### **2. AI Integration**
- **OpenAI GPT**: Roteamento de intenções e execução de tarefas (completo)
- **Google Gemini**: Suporte limitado com limitações de tool calling
- **Whisper**: Transcrição de áudio para processamento
- **Function Calling**: Execução estruturada de ferramentas
- **Schema Resolution**: Resolução automática de referências JSON para compatibilidade

### **3. Database Integration**
- **SQLModel**: ORM moderno com validação Pydantic
- **SQLite**: Banco local para desenvolvimento e MVP
- **Migrations**: Criação automática de tabelas

### **4. External API Integration**
- **WhatsApp Business API**: Comunicação bidirecional
- **Meta Graph**: Autenticação e webhooks
- **Ngrok**: Túnel para desenvolvimento local

## 🔒 Segurança e Autenticação

### **Camadas de Segurança**

```mermaid
graph TB
    subgraph "External Layer"
        WA[WhatsApp]
        INTERNET[Internet]
    end
    
    subgraph "Security Layer"
        TOKEN[Verification Token]
        AUTH[User Authentication]
        RATE[Rate Limiting]
    end
    
    subgraph "Application Layer"
        VALID[Input Validation]
        SANIT[Data Sanitization]
        LOG[Audit Logging]
    end
    
    subgraph "Data Layer"
        ENCRYPT[Data Encryption]
        ACCESS[Access Control]
        BACKUP[Backup Strategy]
    end
    
    WA --> TOKEN
    INTERNET --> TOKEN
    TOKEN --> AUTH
    AUTH --> VALID
    VALID --> SANIT
    SANIT --> LOG
    LOG --> ENCRYPT
    ENCRYPT --> ACCESS
    ACCESS --> BACKUP
```

### **Mecanismos de Segurança**
- **Verification Token**: Validação de webhooks WhatsApp
- **User Authentication**: Controle por número de telefone
- **Input Validation**: Validação Pydantic em todos os inputs
- **Rate Limiting**: Proteção contra spam
- **Data Isolation**: Bancos separados por feature

## 📊 Monitoramento e Observabilidade

### **Logging Strategy**

```mermaid
graph LR
    subgraph "Log Sources"
        AGENT[Agent Execution]
        TOOL[Tool Execution]
        API[API Calls]
        DB[Database Operations]
    end
    
    subgraph "Log Levels"
        DEBUG[Debug]
        INFO[Info]
        WARN[Warning]
        ERROR[Error]
    end
    
    subgraph "Log Outputs"
        CONSOLE[Console]
        FILE[File]
        METRICS[Metrics]
        ALERTS[Alerts]
    end
    
    AGENT --> DEBUG
    TOOL --> INFO
    API --> WARN
    DB --> ERROR
    DEBUG --> CONSOLE
    INFO --> FILE
    WARN --> METRICS
    ERROR --> ALERTS
```

### **Métricas de Performance**
- **Response Time**: Tempo de processamento das mensagens
- **Success Rate**: Taxa de sucesso das operações
- **Error Rate**: Taxa de erro por tipo de operação
- **Resource Usage**: Uso de memória e CPU

## 🔄 Padrões de Resiliência

### **1. Circuit Breaker**
- **OpenAI API**: Proteção contra falhas da API externa
- **WhatsApp API**: Proteção contra falhas de comunicação
- **Database**: Proteção contra falhas de persistência

### **2. Retry Pattern**
- **API Calls**: Tentativas múltiplas para APIs externas
- **Database Operations**: Retry para operações de banco
- **Message Processing**: Retry para processamento de mensagens

### **3. Fallback Strategy**
- **AI Unavailable**: Fallback para respostas padrão
- **Database Unavailable**: Cache local temporário
- **External Service Down**: Modo offline limitado

## 🧪 Estratégia de Testes

### **Pirâmide de Testes**

```mermaid
graph TD
    subgraph "Test Pyramid"
        E2E[End-to-End Tests]
        INT[Integration Tests]
        UNIT[Unit Tests]
    end
    
    subgraph "Coverage"
        AGENTS[Agent Logic]
        TOOLS[Tool Functions]
        MODELS[Data Models]
        API[API Endpoints]
    end
    
    E2E --> API
    INT --> TOOLS
    INT --> MODELS
    UNIT --> AGENTS
    UNIT --> TOOLS
    UNIT --> MODELS
```

### **Tipos de Teste**
- **Unit Tests**: Lógica de agentes e ferramentas
- **Integration Tests**: Interação entre componentes
- **End-to-End Tests**: Fluxo completo de mensagens
- **Performance Tests**: Latência e throughput

## 🚀 Estratégia de Deploy

### **Ambientes**

```mermaid
graph LR
    subgraph "Development"
        LOCAL[Local Machine]
        NGROK[Ngrok Tunnel]
        SQLITE[SQLite Local]
    end
    
    subgraph "Staging"
        STAGE[Staging Server]
        PROXY[Reverse Proxy]
        STAGE_DB[Staging Database]
    end
    
    subgraph "Production"
        PROD[Production Server]
        LB[Load Balancer]
        PROD_DB[Production Database]
    end
    
    LOCAL --> NGROK
    NGROK --> STAGE
    STAGE --> PROD
    SQLITE --> STAGE_DB
    STAGE_DB --> PROD_DB
```

### **CI/CD Pipeline**
- **Build**: Compilação e validação de código
- **Test**: Execução automática de testes
- **Deploy**: Deploy automático para staging
- **Promote**: Promoção manual para produção

## 📈 Escalabilidade e Performance

### **Estratégias de Escalabilidade**

```mermaid
graph TB
    subgraph "Horizontal Scaling"
        LB[Load Balancer]
        INST1[Instance 1]
        INST2[Instance 2]
        INST3[Instance 3]
    end
    
    subgraph "Vertical Scaling"
        CPU[CPU Optimization]
        MEM[Memory Optimization]
        DISK[Disk I/O Optimization]
    end
    
    subgraph "Caching Strategy"
        REDIS[Redis Cache]
        MEMORY[In-Memory Cache]
        CDN[CDN for Static]
    end
    
    LB --> INST1
    LB --> INST2
    LB --> INST3
    INST1 --> CPU
    INST2 --> MEM
    INST3 --> DISK
    CPU --> REDIS
    MEM --> MEMORY
    DISK --> CDN
```

### **Otimizações de Performance**
- **Async Processing**: Background tasks para mensagens
- **Connection Pooling**: Pool de conexões de banco
- **Caching**: Cache de respostas frequentes
- **Batch Processing**: Processamento em lote quando possível

## 🔮 Roadmap Arquitetural

### **Fase 1: Consolidação (Atual)**
- ✅ Arquitetura base implementada
- ✅ Features Finance e Relationships funcionais
- ✅ Padrões de agentes estabelecidos
- ✅ Migração para LangChain OpenAI
- ✅ Correção de validações de ferramentas
- ✅ Isolamento de bancos de dados
- ✅ Suporte a Google Gemini (com limitações)
- ✅ Sistema de consolidação report_tool
- ✅ Resolução de schemas JSON para compatibilidade

### **Fase 2: Escalabilidade**
- [ ] Migração para PostgreSQL/MySQL
- [ ] Implementação de cache Redis
- [ ] Load balancing e auto-scaling
- [ ] Monitoramento avançado

### **Fase 3: Microserviços**
- [ ] Separação em serviços independentes
- [ ] API Gateway centralizado
- [ ] Service mesh para comunicação
- [ ] Deploy com Kubernetes

### **Fase 4: IA Avançada**
- [ ] Fine-tuning de modelos
- [ ] Embeddings para busca semântica
- [ ] Análise preditiva de relacionamentos
- [ ] Recomendações personalizadas

---

**Documento de Arquitetura**  
**Versão**: 1.0  
**Última atualização**: Janeiro 2025  
**Status**: Implementado e funcional  
**Arquitetura**: Clean Domain + Multi-Agent System + Tool Consolidation
