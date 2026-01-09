import time
from typing import Annotated
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel

from src.config import settings


class AccessToken(BaseModel):
    iss: str
    sub: int
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    access_token: AccessToken


def sign_jwt(user_id: int) -> JWTToken:
    now = time.time()
    payload = {
        "iss": settings.jwt_issuer,
        # PyJWT validates `sub` as a string.
        # Pydantic will coerce it back to int when validating the token model.
        "sub": str(user_id),
        "aud": settings.jwt_audience,
        "exp": now + (60 * settings.jwt_expires_minutes),
        "iat": now,
        "nbf": now,
        "jti": uuid4().hex,
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {"access_token": token}


async def decode_jwt(token: str) -> JWTToken | None:
    try:
        decoded_token = jwt.decode(
            token,
            settings.jwt_secret,
            audience=settings.jwt_audience,
            algorithms=[settings.jwt_algorithm],
        )
        _token = JWTToken.model_validate({"access_token": decoded_token})
        return _token if _token.access_token.exp >= time.time() else None
    except Exception:
        return None


async def decode_jwt_with_error(token: str) -> tuple[JWTToken | None, str | None]:
    try:
        decoded_token = jwt.decode(
            token,
            settings.jwt_secret,
            audience=settings.jwt_audience,
            algorithms=[settings.jwt_algorithm],
        )
        _token = JWTToken.model_validate({"access_token": decoded_token})
        if _token.access_token.exp < time.time():
            return None, "ExpiredSignature"
        return _token, None
    except Exception as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> JWTToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            scheme = scheme.strip()
            credentials = credentials.strip()

            # Common client mistakes (especially in Insomnia):
            # - sending quotes around the token
            # - duplicating the Bearer prefix ("Bearer Bearer <token>")
            if credentials.startswith("Bearer "):
                credentials = credentials.removeprefix("Bearer ").strip()
            if (credentials.startswith('"') and credentials.endswith('"')) or (
                credentials.startswith("'") and credentials.endswith("'")
            ):
                credentials = credentials[1:-1].strip()

            if scheme.lower() != "bearer":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication scheme.")

            payload, error = await decode_jwt_with_error(credentials)
            if not payload:
                if settings.environment != "production" and error:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Invalid or expired token. {error}",
                    )
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")
            return payload
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization code.")


async def get_current_user(token: Annotated[JWTToken, Depends(JWTBearer())]) -> dict[str, int]:
    return {"user_id": token.access_token.sub}


def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return current_user
