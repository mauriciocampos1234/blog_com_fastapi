# Schemas (entrada) do recurso Post.
#
# Schemas são modelos Pydantic usados para validar/parsing do que o cliente envia.
#
# - `PostIn`: body do POST /posts/
# - `PostUpdateIn`: body do PATCH /posts/{id} (campos opcionais)

from pydantic import AwareDatetime, BaseModel


class PostIn(BaseModel):
    # Payload de criação de post.
    title: str
    content: str
    published_at: AwareDatetime | None = None
    published: bool = False


class PostUpdateIn(BaseModel):
    # Payload de atualização parcial.
    # Todos os campos são opcionais para permitir PATCH (enviar apenas o que mudou).
    title: str | None = None
    content: str | None = None
    published_at: AwareDatetime | None = None
    published: bool | None = None
