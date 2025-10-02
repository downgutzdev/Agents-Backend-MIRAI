# Mirai Backend Agents API 🤖

[🇧🇷 Versão em Português](#pt) | [🇺🇸 English Version](#en)

---

## <a id="pt"></a> 🇧🇷 Versão em Português

### 📋 Sobre o Projeto

**Mirai Backend Agents API** é uma API backend desenvolvida em FastAPI que gerencia workflows de agentes de IA para sistemas educacionais. O sistema permite diferentes tipos de sessões de conversação, incluindo sessões naturais, sessões de aula e workflows analíticos.

### ⚠️ Aviso Importante

**Este repositório é apenas para visualização** - não está pronto para uso real pois requer:

- 🔑 Chaves de API privadas para agentes de IA
- 🗄️ Configuração do Redis para armazenamento de sessões
- 🐘 Configuração do PostgreSQL para persistência de dados
- 🌐 Integrações com serviços externos de IA
- ⚙️ Configurações de ambiente específicas

### 🛠️ Tecnologias Utilizadas

- **FastAPI** - Framework web moderno e rápido
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados principal
- **Redis** - Cache e armazenamento de sessões
- **Uvicorn** - Servidor ASGI
- **Alembic** - Migrações de banco de dados
- **Python-dotenv** - Gerenciamento de variáveis de ambiente

### 📁 Estrutura do Projeto

```
├── app/
│   ├── models/          # Modelos de dados (Estudante, Sessão)
│   ├── routers/         # Endpoints da API
│   ├── workflows/       # Lógica de workflows de IA
│   ├── utils/           # Utilitários e helpers
│   └── data/            # Dados fake para desenvolvimento
├── tests/               # Testes automatizados
├── config.py           # Configurações dos agentes
└── main.py             # Ponto de entrada da aplicação
```

### 🚀 Instruções de Instalação

Este projeto **não pode ser instalado ou executado** sem as configurações privadas necessárias:

1. ❌ Chaves de API para os agentes de IA
2. ❌ Configuração do banco PostgreSQL
3. ❌ Configuração do Redis
4. ❌ URLs dos serviços externos

Para fins de desenvolvimento, seria necessário:
```bash
pip install -r requirements.txt
# Configurar variáveis de ambiente
# Configurar bancos de dados
# Configurar integrações externas
```

### 📝 Licença

Este projeto é para fins educacionais e de demonstração.

### 📧 Contato

Para mais informações sobre este projeto, entre em contato com a equipe de desenvolvimento.

---

## <a id="en"></a> 🇺🇸 English Version

### 📋 About the Project

**Mirai Backend Agents API** is a FastAPI-based backend that manages AI agent workflows for educational systems. The system supports different types of conversation sessions, including natural sessions, class sessions, and analytical workflows.

### ⚠️ Important Notice

**This repository is for viewing only** - it is not ready for real use because it requires:

- 🔑 Private API keys for AI agents
- 🗄️ Redis configuration for session storage
- 🐘 PostgreSQL configuration for data persistence
- 🌐 External AI service integrations
- ⚙️ Specific environment configurations

### 🛠️ Technologies Used

- **FastAPI** - Modern and fast web framework
- **SQLAlchemy** - Database ORM
- **PostgreSQL** - Main database
- **Redis** - Cache and session storage
- **Uvicorn** - ASGI server
- **Alembic** - Database migrations
- **Python-dotenv** - Environment variable management

### 📁 File Structure

```
├── app/
│   ├── models/          # Data models (Student, Session)
│   ├── routers/         # API endpoints
│   ├── workflows/       # AI workflow logic
│   ├── utils/           # Utilities and helpers
│   └── data/            # Fake data for development
├── tests/               # Automated tests
├── config.py           # Agent configurations
└── main.py             # Application entry point
```

### 🚀 Installation Instructions

This project **cannot be installed or run** without the necessary private configurations:

1. ❌ API keys for AI agents
2. ❌ PostgreSQL database configuration
3. ❌ Redis configuration
4. ❌ External service URLs

For development purposes, it would require:
```bash
pip install -r requirements.txt
# Configure environment variables
# Set up databases
# Configure external integrations
```

### 📝 License

This project is for educational and demonstration purposes.

### 📧 Contact

For more information about this project, please contact the development team.
