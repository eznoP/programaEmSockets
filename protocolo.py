"""Protocolo próprio da aplicação "Lista de Tarefas" (texto UTF-8 sobre TCP).

Cada mensagem é uma linha terminada em "\\n".

Requisições (cliente -> servidor):
    ADD <texto>     cria tarefa              -> OK <id>
    LIST            lista todas as tarefas   -> OK <n>, depois n linhas "<id> <F|T> <texto>"
    DONE <id>       marca tarefa como feita  -> OK
    DEL <id>        remove tarefa            -> OK
    SAIR            encerra a conexão        -> OK

Erros (servidor -> cliente):
    ERRO <codigo> <mensagem>
"""

HOST = "127.0.0.1"
PORTA = 5000
MAX_LINHA = 1024  # bytes; limite contra linhas gigantes

ERRO_REQUISICAO = 400
ERRO_NAO_ENCONTRADA = 404
