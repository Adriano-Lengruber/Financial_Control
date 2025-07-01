# Financial Control MVP

Aplicativo web de gestão de finanças pessoais com dashboards analíticos e sugestões inteligentes.

## 🏗️ Arquitetura

- **Backend**: Django REST Framework + PostgreSQL + Redis
- **Frontend**: React + TypeScript + Tailwind CSS
- **IA/ML**: Prophet, scikit-learn para forecasting e detecção de anomalias
- **Deploy**: Docker + docker-compose

## 🚀 Funcionalidades

- ✅ Autenticação JWT
- ✅ CRUD de transações, contas e categorias
- ✅ Dashboards com gráficos interativos
- ✅ Forecast de saldo futuro
- ✅ Detecção de anomalias
- ✅ Sugestões personalizadas de economia

## 🛠️ Configuração do Ambiente

### Pré-requisitos
- Docker e Docker Compose
- Node.js 18+
- Python 3.10+

### Instalação

1. Clone o repositório:
```bash
git clone <repository-url>
cd Financial_Control
```

2. Configure as variáveis de ambiente:
```bash
cp .env.example .env
```

3. Execute com Docker:
```bash
docker-compose up -d
```

4. Acesse a aplicação:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs/

## 📁 Estrutura do Projeto

```
Financial_Control/
├── backend/                 # Django REST API
│   ├── apps/               # Apps Django
│   ├── config/             # Configurações
│   ├── requirements/       # Dependências
│   └── manage.py
├── frontend/               # React App
│   ├── src/
│   ├── public/
│   └── package.json
├── docker/                 # Dockerfiles
├── .github/workflows/      # CI/CD
└── docker-compose.yml
```

## 🧪 Testes

```bash
# Backend
cd backend && python manage.py test

# Frontend
cd frontend && npm test
```

## 📝 Licença

MIT License
