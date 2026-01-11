# Schemas (entrada) de autenticação.

from pydantic import BaseModel


class LoginIn(BaseModel):
    # Payload do login didático (envia um `user_id`).
    user_id: int
