# Configuração de testes (pytest).
#
# Este arquivo define fixtures reutilizadas em vários testes.
#
# Pontos-chave:
# - muda o banco para um SQLite de testes
# - cria/derruba tabelas antes/depois
# - cria um `AsyncClient` que chama o app FastAPI em memória (sem subir Uvicorn)

import asyncio

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.config import settings

# Durante os testes, usamos um SQLite separado para não mexer no banco local/produção.
settings.database_url = "sqlite:///tests.db"


@pytest_asyncio.fixture
async def db(request):
    # Fixture de banco.
    #
    # Conecta no banco, cria as tabelas e garante teardown no final do teste.
    from src.database import database, engine, metadata  # noqa
    from src.models.post import posts  # noqa

    await database.connect()
    metadata.create_all(engine)

    def teardown():
        # O pytest aceita finalizers síncronos; por isso aqui criamos
        # uma corrotina e executamos com `asyncio.run`.
        async def _teardown():
            await database.disconnect()
            metadata.drop_all(engine)

        asyncio.run(_teardown())

    request.addfinalizer(teardown)


@pytest_asyncio.fixture
async def client(db):
    # Cliente HTTP assíncrono para testes.
    #
    # `ASGITransport` permite chamar a aplicação diretamente (sem rede).
    # Isso deixa os testes mais rápidos e determinísticos.
    from src.main import app

    transport = ASGITransport(app=app)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    async with AsyncClient(base_url="http://test", transport=transport, headers=headers) as client:
        yield client


@pytest_asyncio.fixture
async def access_token(client: AsyncClient):
    # Gera um token JWT usando o endpoint de login.
    response = await client.post("/auth/login", json={"user_id": 1})
    return response.json()["access_token"]
