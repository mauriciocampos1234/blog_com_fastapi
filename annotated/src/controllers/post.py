# Arquivo: src/controllers/post.py (versão anotada para estudo)
#
# Este módulo define as rotas HTTP do recurso "posts".
# Ele não fala diretamente com o banco: delega para `PostService`.
#
# Importante: todas as rotas aqui exigem autenticação JWT (login_required).

from fastapi import APIRouter, Depends, status  # Router, injeção de dependência e códigos HTTP

from src.schemas.post import PostIn, PostUpdateIn  # Schemas de entrada: criação e atualização parcial
from src.security import login_required  # Dependência que bloqueia acesso sem token válido
from src.services.post import PostService  # Camada de serviço (regras e acesso ao banco)
from src.views.post import PostOut  # Modelo de saída (response_model)

# Cria um router com prefixo /posts.
# `dependencies=[Depends(login_required)]` => antes de entrar em qualquer rota,
# o FastAPI executa `login_required`; se falhar, retorna 401/403.
router = APIRouter(prefix="/posts", dependencies=[Depends(login_required)])

service = PostService()  # Instancia o service uma vez para ser usado pelas rotas


@router.get("/", response_model=list[PostOut])  # Define GET /posts/ e diz que a resposta é uma lista de PostOut
async def read_posts(published: bool, limit: int, skip: int = 0):  # Query params: published, limit e skip (opcional)
    # `published` filtra posts publicados ou não.
    # `limit` limita o total retornado (paginação simples).
    # `skip` pula N registros (offset) para paginação.
    return await service.read_all(published=published, limit=limit, skip=skip)  # Busca no banco e devolve a lista


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)  # Define POST /posts/ e retorna 201
async def create_post(post: PostIn):  # Recebe o body JSON validado por PostIn
    # Cria o post no banco e recebe de volta o `id` gerado.
    post_id = await service.create(post)  # Executa INSERT no banco e retorna o id
    # Monta a resposta juntando o payload original + id.
    return {**post.model_dump(), "id": post_id}  # Devolve o novo post com id


@router.get("/{id}", response_model=PostOut)  # Define GET /posts/{id}
async def read_post(id: int):  # Recebe o id da URL e converte para int
    # Busca 1 post pelo id.
    # Se não existir, o service levanta NotFoundPostError e vira 404 pelo handler.
    return await service.read(id)  # Retorna o registro encontrado


@router.patch("/{id}", response_model=PostOut)  # Define PATCH /posts/{id}
async def update_post(id: int, post: PostUpdateIn):  # Recebe id e body com campos opcionais
    # Atualiza apenas os campos enviados (PATCH).
    # Se o id não existir, o service levanta NotFoundPostError (404).
    return await service.update(id=id, post=post)  # Executa UPDATE e devolve o registro atualizado


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)  # Define DELETE /posts/{id} com 204
async def delete_post(id: int):  # Recebe id para deletar
    # Deleta o post pelo id.
    # Retorna 204 (sem body). Mesmo que não exista, o service pode só executar e não falhar.
    await service.delete(id)  # Executa DELETE no banco
