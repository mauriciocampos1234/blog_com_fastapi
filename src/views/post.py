# Views (saída) do recurso Post.
#
# Neste projeto, "views" são modelos Pydantic usados para padronizar a resposta
# da API (response_model).

from pydantic import AwareDatetime, BaseModel, NaiveDatetime


class PostOut(BaseModel):
    # Formato de post devolvido pela API.
    id: int
    title: str
    content: str

    # `published_at` pode vir com timezone (Aware) ou sem (Naive), dependendo
    # do driver/banco/serialização. Por isso aceitamos ambos.
    published_at: AwareDatetime | NaiveDatetime | None
