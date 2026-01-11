# Model (tabela) de Posts.
#
# Aqui declaramos a tabela SQLAlchemy que será criada no banco.
#
# Repare que este projeto usa SQLAlchemy *Core* (Table/Column), não ORM.

import sqlalchemy as sa

from src.database import metadata

posts = sa.Table(
    "posts",
    metadata,
    # Identificador único do post.
    sa.Column("id", sa.Integer, primary_key=True),

    # Título do post (único) — o banco não permite dois posts com mesmo título.
    sa.Column("title", sa.String(150), nullable=False, unique=True),

    # Corpo/conteúdo do post.
    sa.Column("content", sa.String, nullable=False),

    # Data/hora de publicação (pode ser nula).
    sa.Column("published_at", sa.TIMESTAMP(timezone=True), nullable=True),

    # Flag indicando se está publicado.
    sa.Column("published", sa.Boolean, default=False),
)
