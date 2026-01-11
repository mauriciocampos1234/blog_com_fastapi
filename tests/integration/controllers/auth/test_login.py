# Testes de integração do endpoint /auth/login.

from fastapi import status
from httpx import AsyncClient


async def test_login_success(client: AsyncClient):
    # Given
    # Entrada esperada do login: um JSON com `user_id`.
    data = {"user_id": 1}

    # When
    # Chamamos o endpoint real da aplicação (em memória).
    response = await client.post("/auth/login", json=data)

    # Then
    # O login deve devolver 200 e um token não-nulo.
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["access_token"] is not None
