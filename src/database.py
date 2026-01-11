# Camada de infraestrutura de banco de dados.
#
# Aqui ficam objetos compartilhados para acesso ao banco:
# - `database`: conexão assíncrona (lib `databases`)
# - `metadata`: catálogo de tabelas do SQLAlchemy
# - `engine`: engine do SQLAlchemy (útil para `create_all` e migrations)
#
# O projeto usa:
# - SQLAlchemy para declarar tabelas
# - `databases` para executar queries async

import databases
import sqlalchemy as sa

from src.config import settings

# Conexão assíncrona com o banco (usada pelo service).
database = databases.Database(settings.database_url)

# MetaData armazena as definições das tabelas (ex.: `posts`).
metadata = sa.MetaData()

is_sqlite = settings.database_url.startswith("sqlite")

if is_sqlite:
    # SQLite tem uma restrição por thread; `check_same_thread=False` evita
    # erros quando o app executa em contexto assíncrono.
    engine = sa.create_engine(settings.database_url, connect_args={"check_same_thread": False})
else:
    # Para Postgres/Outros, não precisamos desse connect_args.
    engine = sa.create_engine(settings.database_url)
