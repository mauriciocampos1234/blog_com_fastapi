# Controller (rotas HTTP) do recurso Post.
#
# Este arquivo define endpoints REST para:
# - listar posts
# - criar post
# - ler por id
# - atualizar parcialmente (PATCH)
# - deletar
#
# Repare que todas as rotas aqui são protegidas por JWT via `login_required`.

from fastapi import APIRouter, Depends, status

from src.schemas.post import PostIn, PostUpdateIn
from src.security import login_required
from src.services.post import PostService
from src.views.post import PostOut

# Router de posts.
# `dependencies=[Depends(login_required)]` significa que toda rota
# neste router exige autenticação (header Authorization: Bearer <token>).
router = APIRouter(prefix="/posts", dependencies=[Depends(login_required)])

service = PostService()


@router.get("/", response_model=list[PostOut])
async def read_posts(published: bool, limit: int, skip: int = 0):
    # `published` vem da query string e filtra posts publicados ou não.
    # `limit` vem da query string e limita quantos registros voltar.
    # `skip` é opcional e implementa paginação via offset.
    return await service.read_all(published=published, limit=limit, skip=skip)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=PostOut)
async def create_post(post: PostIn):
    # `post` é o body JSON validado pelo Pydantic (PostIn).
    # Primeiro, pedimos ao service para persistir no banco e nos devolver o id.
    post_id = await service.create(post)
    # Depois, montamos a resposta com os dados enviados + o id gerado.
    return {**post.model_dump(), "id": post_id}


@router.get("/{id}", response_model=PostOut)
async def read_post(id: int):
    # `id` vem do path (/posts/{id}) e o FastAPI converte para int.
    # O service busca no banco; se não existir, levanta NotFoundPostError (vira 404).
    return await service.read(id)


@router.patch("/{id}", response_model=PostOut)
async def update_post(id: int, post: PostUpdateIn):
    # `post` é um payload parcial (todos os campos são opcionais).
    # O service executa UPDATE somente dos campos enviados.
    return await service.update(id=id, post=post)


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_post(id: int):
    # Remove o post pelo id.
    # Retorna 204 sem body.
    await service.delete(id)
