# Views (saída) de autenticação.

from pydantic import BaseModel


class LoginOut(BaseModel):
    # Resposta do login: devolve o token JWT.
    access_token: str
