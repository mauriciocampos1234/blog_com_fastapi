# DIO Blog API (FastAPI)

Projeto de estudo que implementa uma API REST assíncrona para um “blog”, com autenticação via JWT e CRUD de posts.

A ideia aqui é ter um backend simples, mas com alguns conceitos bem reais do dia a dia (camadas, migrações, autenticação, testes e deploy em produção).

## O que essa API faz

- Autenticação: gera um token JWT no login (endpoint `/auth/login`).
- Posts: cria, lista, busca por ID, atualiza e remove posts (endpoints em `/posts`).
- Proteção de rotas: endpoints de posts exigem `Authorization: Bearer <token>`.
- Banco de dados: funciona com SQLite no desenvolvimento/testes e com Postgres em produção.

## Stack e bibliotecas usadas

Principais tecnologias do projeto:

- **FastAPI**: framework web (rotas, validação, docs Swagger/OpenAPI).
- **Uvicorn**: servidor ASGI para rodar a aplicação.
- **Pydantic / pydantic-settings**: validação de entrada/saída e carregamento de variáveis de ambiente.
- **PyJWT**: geração e validação de tokens JWT.
- **databases** (async) + **SQLAlchemy Core**: acesso assíncrono ao banco e definição das tabelas.
- **Alembic**: migrações do banco (criar/alterar tabelas de forma versionada).
- **pytest + pytest-asyncio + httpx**: testes de integração rodando o app em memória (sem subir servidor).

## Estrutura do projeto (visão rápida)

- `src/controllers/`: define as rotas (camada HTTP).
- `src/services/`: regras e operações de negócio (ex.: CRUD no banco).
- `src/models/`: definição das tabelas (SQLAlchemy Core).
- `src/schemas/`: modelos Pydantic de entrada/saída.
- `src/security.py`: JWT e dependências de autenticação.
- `migrations/`: controle de versão do banco via Alembic.
- `tests/`: testes de integração.

## Rodar localmente

### 1) Instalar dependências

```bash
poetry install
```

### 2) Variáveis de ambiente

Crie um arquivo `.env` (pode copiar de `.env.example`, se existir) e ajuste as variáveis.

Exemplo para desenvolvimento rápido com SQLite:

```env
DATABASE_URL=sqlite:///./app.db
ENVIRONMENT=development
JWT_SECRET=change-me
JWT_EXPIRES_MINUTES=60
```

### 3) Criar/atualizar tabelas (migrations)

```bash
poetry run alembic upgrade head
```

### 4) Subir a API

```bash
poetry run uvicorn src.main:app --reload
```

Base URL local: `http://localhost:8000`

## Rotas principais

### Auth → Login (gera token)

- **POST** `/auth/login`
- Body (JSON):

```json
{ "user_id": 1 }
```

- Resposta (JSON):

```json
{ "access_token": "..." }
```

### Posts (rotas protegidas)

Em todas as requisições de `/posts`, envie:

- `Authorization: Bearer <SEU_TOKEN>`
- `Content-Type: application/json`

Endpoints:

- **GET** `/posts/`
  - Query params obrigatórios:
    - `published`: aceita `true/false` ou `on/off`
    - `limit`: número inteiro
  - Query param opcional:
    - `skip`: inteiro (default `0`)
  - Exemplo: `/posts/?published=on&limit=10&skip=0`
- **GET** `/posts/{id}` (ex.: `/posts/1`)
- **POST** `/posts/`
- **PATCH** `/posts/{id}` (envie só os campos que quiser atualizar)
- **DELETE** `/posts/{id}`

## Testes automatizados

Rodar a suíte de testes:

```bash
poetry run pytest -q
```

Observação: os testes usam `httpx` com `ASGITransport`, então o app roda “em memória” (sem rede), deixando os testes mais rápidos.

## Testes manuais com Insomnia (local e produção)

Usamos o **Insomnia** para testar a API manualmente, tanto local quanto em produção.

Uma forma simples de organizar isso é criar environments:

- **local**: `base_url = http://localhost:8000`
- **produção (Render)**: `base_url = https://<sua-app>.onrender.com`

Daí, nas requisições, usar `{{ base_url }}/posts/`, `{{ base_url }}/auth/login`, etc.

Dica importante: a requisição de login (`/auth/login`) deve ficar como **No Auth**. Depois, nas rotas protegidas, você coloca o token em `Authorization: Bearer ...`.

## Banco de dados e DBeaver

O projeto pode usar dois bancos, dependendo do ambiente:

- **SQLite** (desenvolvimento e/ou testes): banco em arquivo (ex.: `app.db` / `tests.db`).
- **PostgreSQL** (produção): usado no deploy do Render.

Para visualizar/inspecionar dados, tabelas e rodar SQL, usamos o **DBeaver**:

- SQLite: crie uma conexão “SQLite” apontando para o arquivo `.db`.
- Postgres (Render): crie uma conexão “PostgreSQL” usando host/porta/usuário/senha fornecidos pelo Render (ou a `DATABASE_URL`).

Isso ajuda bastante a entender o que está acontecendo “por baixo” (tabelas, inserts, updates e constraints).

## Deploy no Render (produção)

O deploy foi feito no **Render**:

- Build command: [render-build.sh](render-build.sh) (instala Poetry e dependências).
- Start command: [render-deploy.sh](render-deploy.sh) (roda migrations e inicia o Uvicorn).

Variáveis de ambiente típicas no Render:

- `DATABASE_URL` (Postgres fornecido pelo Render)
- `ENVIRONMENT=production`
- `JWT_SECRET` (valor forte/aleatório)
- `JWT_EXPIRES_MINUTES` (opcional)
