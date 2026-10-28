"""Cliente TCP da Lista de Tarefas. Uso: python cliente.py"""

import socket
import sys

from protocolo import HOST, PORTA, MAX_LINHA

MENU = "Comandos: add <texto> | list | done <id> | del <id> | sair"


def traduzir(entrada):
    """Converte o que o usuário digitou em requisição do protocolo. None = inválido."""
    cmd, _, arg = entrada.strip().partition(" ")
    cmd = cmd.lower()
    arg = arg.strip()
    if cmd == "add" and arg:
        return f"ADD {arg}"
    if cmd == "list" and not arg:
        return "LIST"
    if cmd in ("done", "del") and arg.isdigit():
        return f"{cmd.upper()} {arg}"
    if cmd == "sair" and not arg:
        return "SAIR"
    return None


def ler_linha(f):
    linha = f.readline(MAX_LINHA + 1)
    if not linha:
        raise ConnectionError("servidor fechou a conexão")
    return linha.rstrip("\n")


def trocar(f, requisicao):
    """Envia uma requisição e devolve as linhas de resposta."""
    f.write(requisicao + "\n")
    f.flush()
    cabecalho = ler_linha(f)
    if requisicao == "LIST" and cabecalho.startswith("OK"):
        n = int(cabecalho.split()[1])
        return [cabecalho] + [ler_linha(f) for _ in range(n)]
    return [cabecalho]


def main():
    try:
        s = socket.create_connection((HOST, PORTA), timeout=10)
    except OSError as e:
        sys.exit(f"Não consegui conectar em {HOST}:{PORTA}: {e}\nO servidor está rodando?")

    with s, s.makefile("rw", encoding="utf-8", newline="\n") as f:
        print(f"Conectado a {HOST}:{PORTA}. {MENU}")
        while True:
            try:
                entrada = input("> ")
            except (EOFError, KeyboardInterrupt):
                entrada = "sair"
            requisicao = traduzir(entrada)
            if requisicao is None:
                print(f"Comando inválido. {MENU}")
                continue
            try:
                print("\n".join(trocar(f, requisicao)))
            except (OSError, ValueError) as e:
                print(f"Erro de comunicação: {e}")
                break
            if requisicao == "SAIR":
                break
    print("Até mais!")


if __name__ == "__main__":
    main()
