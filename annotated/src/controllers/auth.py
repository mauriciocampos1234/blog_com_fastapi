# Arquivo: src/controllers/auth.py (versão anotada para estudo)
#
# Este módulo define rotas HTTP de autenticação.
# Aqui existe um "login" didático: você envia `user_id` e recebe um token JWT.

from fastapi import APIRouter  # Importa o roteador do FastAPI (para agrupar rotas)

from src.schemas.auth import LoginIn  # Modelo de entrada (valida o JSON do body)
from src.security import sign_jwt  # Função que gera/assina o JWT
from src.views.auth import LoginOut  # Modelo de saída (padroniza a resposta)

router = APIRouter(prefix="/auth")  # Cria um router com prefixo /auth (todas as rotas começam com /auth)


@router.post("/login", response_model=LoginOut)  # Define POST /auth/login e força o formato de resposta
async def login(data: LoginIn):  # Função assíncrona que atende o endpoint; `data` já vem validado pelo Pydantic
    # Recebe o `user_id` do cliente (ex.: {"user_id": 1})
    # Chama a função que gera um JWT assinado com esse user_id.
    # Retorna um dict no formato {"access_token": "..."}.
    return sign_jwt(user_id=data.user_id)  # Gera o token e devolve para o cliente
