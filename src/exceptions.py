# Exceções de domínio.
#
# O objetivo dessas exceções é separar:
# - regra de negócio (service levanta a exceção)
# - camada HTTP (controller/handler converte em resposta)

from http import HTTPStatus


class NotFoundPostError(Exception):
    # Erro usado quando um post não é encontrado.
    #
    # Ele é capturado por um exception handler em src/main.py para
    # retornar HTTP 404 com um `detail` padronizado.

    def __init__(self, message: str = "Post not found", status_code: int = HTTPStatus.NOT_FOUND) -> None:
        # Guarda a mensagem do erro (vai virar `detail` na resposta).
        self.message = message
        # Guarda o status HTTP (por padrão 404).
        self.status_code = status_code
