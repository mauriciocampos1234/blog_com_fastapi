# Testes de integração do endpoint POST /posts/.

from fastapi import status
from httpx import AsyncClient


async def test_create_post_success(client: AsyncClient, access_token: str):
    # Given
    # Para acessar /posts/, precisamos de Authorization Bearer.
    headers = {"Authorization": f"Bearer {access_token}"}

    # Payload válido conforme PostIn (title e content são obrigatórios).
    data = {"title": "post 1", "content": "some content", "published_at": "2024-04-12T04:33:14.403Z", "published": True}

    # When
    # Cria o post.
    response = await client.post("/posts/", json=data, headers=headers)

    # Then
    content = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert content["id"] is not None


async def test_create_post_invalid_payload_fail(client: AsyncClient, access_token: str):
    # Given
    headers = {"Authorization": f"Bearer {access_token}"}

    # Falta o campo obrigatório `title`.
    data = {"content": "some content", "published_at": "2024-04-12T04:33:14.403Z", "published": True}

    # When
    response = await client.post("/posts/", json=data, headers=headers)

    # Then
    content = response.json()

    # 422 significa que a validação Pydantic do body falhou.
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert content["detail"][0]["loc"] == ["body", "title"]


async def test_create_post_not_authenticated_fail(client: AsyncClient):
    # Given
    # Sem Authorization, a API deve bloquear.
    data = {"content": "some content", "published_at": "2024-04-12T04:33:14.403Z", "published": True}

    # When
    response = await client.post("/posts/", json=data, headers={})

    # Then
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
