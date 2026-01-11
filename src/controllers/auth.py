# Controller (rotas HTTP) de autenticação.
#
# Aqui temos um "login" simplificado para fins didáticos:
# - você envia um `user_id`
# - o servidor devolve um JWT assinado
#
# Não existe senha/banco de usuários neste projeto; o foco é entender JWT.

from fastapi import APIRouter

from src.schemas.auth import LoginIn
from src.security import sign_jwt
from src.views.auth import LoginOut

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=LoginOut)
async def login(data: LoginIn):
    # `data` já foi validado pelo Pydantic (LoginIn) a partir do JSON do body.
    # Aqui pegamos o `user_id` e geramos um token JWT.
    return sign_jwt(user_id=data.user_id)
