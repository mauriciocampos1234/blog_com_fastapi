# Ponto de entrada (bootstrap) da API FastAPI.
#
# Este módulo é responsável por:
# - Criar a instância `FastAPI` (metadados, docs OpenAPI, CORS)
# - Conectar/desconectar do banco no ciclo de vida (startup/shutdown)
# - Registrar rotas (controllers) e handlers de exceção
#
# Dica para estudantes: normalmente você só precisa mexer aqui para:
# - adicionar novos routers
# - configurar CORS
# - configurar eventos/lifespan

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.controllers import auth, post
from src.config import settings
from src.database import database, engine, metadata
from src.exceptions import NotFoundPostError


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Gerencia o ciclo de vida da aplicação.
    #
    # O FastAPI chama isso automaticamente:
    # - antes de começar a receber requests (startup)
    # - e ao encerrar (shutdown)
    #
    # Aqui fazemos:
    # - (dev) criar tabelas automaticamente
    # - conectar no banco async
    # - desconectar no final

    # Em desenvolvimento, cria tabelas automaticamente (atalho didático).
    # Em produção, preferimos migrations (Alembic) e não `create_all`.
    if settings.environment != "production":
        # Cria as tabelas declaradas no `metadata` no banco configurado.
        metadata.create_all(engine)

    # Abre conexão async com o banco (lib `databases`).
    await database.connect()

    # `yield` separa startup do shutdown: o app roda enquanto estiver "no meio".
    yield

    # Fecha conexão ao encerrar o app.
    await database.disconnect()


tags_metadata = [
    {
        "name": "auth",
        "description": "Operações para autenticação",
    },
    {
        "name": "post",
        "description": "Operações para manter posts.",
        "externalDocs": {
            "description": "Documentação externa para Posts.api",
            "url": "https://post-api.com/",
        },
    },
]

servers = [
    {"url": "http://127.0.0.1:8000", "description": "Ambiente de desenvolvimento"},
    {
        "url": "https://blog-com-fastapi.onrender.com",
        "description": "Ambiente de produção",
    },
]


app = FastAPI(
    title="DIO blog API",
    version="1.2.0",
    summary="API para blog pessoal.",
    # Descrição mostrada na documentação (Swagger).
    description=(
        "DIO blog API ajuda você a criar seu blog pessoal. 🚀\n\n"
        "## Posts\n\n"
        "Você será capaz de fazer:\n\n"
        "* **Criar posts**.\n"
        "* **Recuperar posts**.\n"
        "* **Recuperar posts por ID**.\n"
        "* **Atualizar posts**.\n"
        "* **Excluir posts**.\n"
        "* **Limitar quantidade de posts diários**\n"
    ),
    openapi_tags=tags_metadata,
    servers=servers,
    redoc_url=None,
    # openapi_url=None, # disable docs
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    # Para front-ends e testes em navegadores, CORS evita bloqueios.
    # Em produção, o ideal é restringir `allow_origins`.
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(post.router, tags=["post"])


@app.exception_handler(NotFoundPostError)
async def not_found_post_exception_handler(request: Request, exc: NotFoundPostError):
    # Transforma a exceção de domínio `NotFoundPostError` em HTTP 404.
    #
    # A ideia é: o service levanta uma exceção específica quando não encontra o post;
    # o FastAPI converte isso em uma resposta HTTP consistente.
    return JSONResponse(
        # Status HTTP a ser devolvido (por padrão 404).
        status_code=exc.status_code,
        # Corpo da resposta no padrão FastAPI: {"detail": "..."}.
        content={"detail": exc.message},
    )
