# Service (camada de aplicação) do recurso Post.
#
# O service é onde colocamos regras e acesso a dados, deixando o controller
# mais simples.
#
# Ele usa:
# - `database` (conexão async) para executar queries
# - `posts` (tabela SQLAlchemy) para montar SQL

from databases.interfaces import Record

from src.database import database
from src.exceptions import NotFoundPostError
from src.models.post import posts
from src.schemas.post import PostIn, PostUpdateIn


class PostService:
    async def read_all(self, published: bool, limit: int, skip: int = 0) -> list[Record]:
        # Lista posts filtrando por status de publicação.
        # Monta um SELECT na tabela posts.
        query = posts.select().where(posts.c.published == published).limit(limit).offset(skip)
        # Executa a query e devolve todos os registros.
        return await database.fetch_all(query)

    async def create(self, post: PostIn) -> int:
        # Cria um post e devolve o `id` gerado.
        # Monta um INSERT com os valores vindos do payload.
        command = posts.insert().values(
            # Define o título.
            title=post.title,
            # Define o conteúdo.
            content=post.content,
            # Define a data de publicação (pode ser None).
            published_at=post.published_at,
            # Define se está publicado.
            published=post.published,
        )
        # Executa o INSERT e retorna o id gerado.
        return await database.execute(command)

    async def read(self, id: int) -> Record:
        # Busca um post por id (ou levanta NotFoundPostError).
        return await self.__get_by_id(id)

    async def update(self, id: int, post: PostUpdateIn) -> Record:
        # Atualiza um post e devolve o registro atualizado.
        # Passo 1: verifica se existe.
        total = await self.count(id)
        # Se não existir, levanta uma exceção de domínio (vira 404 no handler).
        if not total:
            raise NotFoundPostError

        # Passo 2: pega só os campos enviados no PATCH.
        data = post.model_dump(exclude_unset=True)
        # Passo 3: monta o UPDATE filtrando pelo id.
        command = posts.update().where(posts.c.id == id).values(**data)
        # Passo 4: executa o UPDATE.
        await database.execute(command)

        # Passo 5: busca e devolve o registro atualizado.
        return await self.__get_by_id(id)

    async def delete(self, id: int) -> None:
        # Remove um post.
        # Obs.: aqui não validamos se o post existia; deletar um id inexistente
        # normalmente não gera erro (delete idempotente).
        # Monta o DELETE filtrando pelo id.
        command = posts.delete().where(posts.c.id == id)
        # Executa o DELETE.
        await database.execute(command)

    async def count(self, id: int) -> int:
        # Conta quantos posts existem com o id informado.
        # Aqui usamos uma SQL crua (string) com parâmetro nomeado (:id).
        query = "select count(id) as total from posts where id = :id"
        # Executa e pega apenas um registro.
        result = await database.fetch_one(query, {"id": id})
        # Retorna o total encontrado.
        return result.total

    async def __get_by_id(self, id: int) -> Record:
        # Busca por id e levanta `NotFoundPostError` se não existir.
        # Monta o SELECT filtrando pelo id.
        query = posts.select().where(posts.c.id == id)
        # Executa e devolve um registro (ou None).
        post = await database.fetch_one(query)
        # Se não veio nada, o post não existe.
        if not post:
            raise NotFoundPostError
        # Retorna o registro encontrado.
        return post
