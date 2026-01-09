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
    # For local development, create tables automatically so the API works
    # even before running Alembic migrations.
    if settings.environment != "production":
        metadata.create_all(engine)
    await database.connect()
    yield
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
    {"url": "http://localhost:8000", "description": "Ambiente de desenvolvimento"},
    {
        "url": "https://dio-blog-fastapi.onrender.com",
        "description": "Ambiente de produção",
    },
]


app = FastAPI(
    title="DIO blog API",
    version="1.2.0",
    summary="API para blog pessoal.",
    description="""
DIO blog API ajuda você a criar seu blog pessoal. 🚀

## Posts

Você será capaz de fazer:

* **Criar posts**.
* **Recuperar posts**.
* **Recuperar posts por ID**.
* **Atualizar posts**.
* **Excluir posts**.
* **Limitar quantidade de posts diários** (_not implemented_).
                """,
    openapi_tags=tags_metadata,
    servers=servers,
    redoc_url=None,
    # openapi_url=None, # disable docs
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=["auth"])
app.include_router(post.router, tags=["post"])


@app.exception_handler(NotFoundPostError)
async def not_found_post_exception_handler(request: Request, exc: NotFoundPostError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )
