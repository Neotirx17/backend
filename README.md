# Backend - Malabo Microcrédito (FastAPI)

## Requisitos
- Python 3.11+

## Instalação
```bash
python -m venv .venv
# Windows PowerShell
. .venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
```

## Executar
```bash
uvicorn backend.app.main:app --reload
```

- API: http://127.0.0.1:8000
- Docs: http://127.0.0.1:8000/docs

## Autenticação
- Login: `POST /auth/login` (OAuth2 form)
  - username: admin
  - password: admin123

## Endpoints iniciais
- `GET /health`
- `POST /auth/login`
- `GET /members` (Bearer token; roles: admin, tecnico, agente)

## Notas
- Banco: SQLite em `backend/app.db`
- CORS liberado para `http://localhost:5173`
- Seed automático no startup (dados básicos)
