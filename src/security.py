# Segurança e autenticação via JWT.
#
# Este módulo concentra:
# - geração do token (`sign_jwt`)
# - validação/decodificação (`decode_jwt*`)
# - dependência de autenticação (`JWTBearer`)
# - helpers para proteger rotas (`get_current_user`, `login_required`)
#
# Fluxo típico:
# 1) Cliente chama POST /auth/login e recebe `access_token`
# 2) Cliente usa `Authorization: Bearer <token>` nas rotas protegidas
# 3) `JWTBearer` valida o token e libera o request

import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.config import settings


class AccessToken(BaseModel):
    # Modelo (Pydantic) dos claims que esperamos encontrar dentro do JWT.
    #
    # Em outras palavras: quando decodificamos o JWT, esperamos que ele tenha
    # essas chaves e tipos.

    iss: str
    sub: int
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    # Estrutura usada internamente após decodificar o JWT.

    access_token: AccessToken


def sign_jwt(user_id: int) -> JWTToken:
    # Assina e devolve um token JWT.
    #
    # O retorno é um dict no formato {"access_token": "..."} porque o controller
    # retorna isso diretamente e o response_model `LoginOut` espera essa chave.

    # Captura o tempo atual (epoch em segundos).
    now = time.time()
    # Monta o payload (claims) do JWT.
    payload = {
        # `iss` (issuer): quem emitiu o token.
        "iss": settings.jwt_issuer,
        # PyJWT valida `sub` como string; por isso convertemos aqui.
        # Pydantic converte de volta para int ao validar o modelo.
        "sub": str(user_id),
        # `aud` (audience): para quem o token foi emitido.
        "aud": settings.jwt_audience,
        # `exp` (expiration): quando o token expira.
        "exp": now + (60 * settings.jwt_expires_minutes),
        # `iat` (issued at): quando foi emitido.
        "iat": now,
        # `nbf` (not before): não aceitar antes deste instante.
        "nbf": now,
        # `jti`: identificador único do token (ajuda a diferenciar tokens).
        "jti": uuid4().hex,
    }
    # Assina/gera o token usando o segredo e o algoritmo configurados.
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    # Retorna no formato esperado pela resposta do login.
    return {"access_token": token}


async def decode_jwt(token: str) -> JWTToken | None:
    # Decodifica o token e devolve um modelo validado ou None.
    # Usa `audience` e `algorithms` para evitar aceitar tokens "errados".
    try:
        # Tenta decodificar e validar assinatura/claims.
        decoded_token = jwt.decode(
            token,  # token JWT (string)
            settings.jwt_secret,  # segredo para validar assinatura
            audience=settings.jwt_audience,  # audience esperada
            algorithms=[settings.jwt_algorithm],  # algoritmo permitido
        )
        # Valida estrutura/tipos via Pydantic.
        _token = JWTToken.model_validate({"access_token": decoded_token})
        # Se já expirou, devolve None.
        return _token if _token.access_token.exp >= time.time() else None
    except Exception:
        # Qualquer erro (assinatura inválida, audience errada, etc.) retorna None.
        return None


async def decode_jwt_with_error(token: str) -> tuple[JWTToken | None, str | None]:
    # Igual ao `decode_jwt`, mas devolve também uma string com o tipo de erro.
    # Isso é útil para mensagens de debug em desenvolvimento.
    try:
        # Decodifica o token.
        decoded_token = jwt.decode(
            token,  # token JWT (string)
            settings.jwt_secret,  # segredo
            audience=settings.jwt_audience,  # audience
            algorithms=[settings.jwt_algorithm],  # algoritmo
        )
        # Valida via Pydantic.
        _token = JWTToken.model_validate({"access_token": decoded_token})
        # Checa expiração manualmente.
        if _token.access_token.exp < time.time():
            # Retorna erro de expiração.
            return None, "ExpiredSignature"
        # Token válido.
        return _token, None
    except Exception as exc:
        # Retorna o nome da exceção para facilitar debug.
        return None, f"{exc.__class__.__name__}: {exc}"


class JWTBearer(HTTPBearer):
    # Dependência do FastAPI que valida o header Authorization (Bearer token).
    #
    # Quando você coloca `Depends(JWTBearer())` em uma rota (ou router), o FastAPI
    # executa este `__call__` antes de entrar no endpoint.

    def __init__(self, auto_error: bool = True):
        # Inicializa a classe base HTTPBearer.
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        # Extrai e valida o token do header Authorization.

        # Lê o header Authorization (ex.: "Bearer <token>").
        authorization = request.headers.get("Authorization", "")
        # Separa o header em duas partes: esquema e credenciais.
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            # Remove espaços extras.
            scheme = scheme.strip()
            # Remove espaços extras.
            credentials = credentials.strip()

            # Common client mistakes (especially in Insomnia):
            # - sending quotes around the token
            # - duplicating the Bearer prefix ("Bearer Bearer <token>")
            if credentials.startswith("Bearer "):
                # Se veio "Bearer Bearer <token>", remove o prefixo duplicado.
                credentials = credentials.removeprefix("Bearer ").strip()
            if (credentials.startswith('"') and credentials.endswith('"')) or (
                credentials.startswith("'") and credentials.endswith("'")
            ):
                # Se o token veio com aspas, remove as aspas.
                credentials = credentials[1:-1].strip()

            if scheme.lower() != "bearer":
                # Se o esquema não for Bearer, bloqueia.
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

            payload, error = await decode_jwt_with_error(credentials)
            if not payload:
                if settings.environment != "production" and error:
                    # Em dev, devolve o tipo de erro para facilitar debug.
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid or expired token. {error}",
                    )
                # Em produção, devolve uma mensagem genérica.
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
            # Se passou, devolve o payload validado.
            return payload
        else:
            # Não veio token (header ausente ou vazio).
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code.")


async def get_current_user(token: Annotated[JWTToken, Depends(JWTBearer())]) -> dict[str, int]:
    # Dependência que converte o token em um "usuário atual".
    # Aqui, por simplicidade, o usuário é só um dict com `user_id`.
    # Em um projeto real, você buscaria o usuário no banco.
    return {"user_id": token.access_token.sub}


def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    # Dependência de autorização.
    # Se não houver usuário atual, bloqueia o acesso.
    # Obs.: na prática, se o token falhar, normalmente a requisição já caiu no 401
    # antes de chegar aqui.
    if not current_user:
        # Se por algum motivo não houver usuário, bloqueia com 403.
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    # Se existe usuário, libera.
    return current_user
