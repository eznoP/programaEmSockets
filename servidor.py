"""Servidor TCP da Lista de Tarefas. Uso: python servidor.py"""

import socket
import sys
import threading

from protocolo import HOST, PORTA, MAX_LINHA, ERRO_REQUISICAO, ERRO_NAO_ENCONTRADA


class Tarefas:
    """Estado compartilhado entre as threads. O lock protege o dicionário."""

    def __init__(self):
        self._lock = threading.Lock()
        self._itens = {}  # id -> [texto, feita]
        self._prox = 1

    def adicionar(self, texto):
        with self._lock:
            id_ = self._prox
            self._prox += 1
            self._itens[id_] = [texto, False]
            return id_

    def listar(self):
        with self._lock:
            return [(i, feita, texto) for i, (texto, feita) in sorted(self._itens.items())]

    def marcar(self, id_):
        with self._lock:
            self._existente(id_)[1] = True

    def remover(self, id_):
        with self._lock:
            self._existente(id_)
            del self._itens[id_]

    def _existente(self, id_):
        if id_ not in self._itens:
            raise KeyError(id_)
        return self._itens[id_]


def processar(linha, tarefas):
    """Recebe uma linha de requisição e devolve a lista de linhas de resposta."""
    cmd, _, arg = linha.strip().partition(" ")
    cmd = cmd.upper()
    arg = arg.strip()
    try:
        if cmd == "ADD" and arg:
            return [f"OK {tarefas.adicionar(arg)}"]
        if cmd == "LIST" and not arg:
            itens = tarefas.listar()
            return [f"OK {len(itens)}"] + [f"{i} {'T' if feita else 'F'} {t}" for i, feita, t in itens]
        if cmd == "DONE" and arg.isdigit():
            tarefas.marcar(int(arg))
            return ["OK"]
        if cmd == "DEL" and arg.isdigit():
            tarefas.remover(int(arg))
            return ["OK"]
        if cmd == "SAIR" and not arg:
            return ["OK"]
    except KeyError:
        return [f"ERRO {ERRO_NAO_ENCONTRADA} tarefa {arg} não existe"]
    return [f"ERRO {ERRO_REQUISICAO} requisição inválida: {linha.strip()!r}"]


def mostrar_recebimento(endereco, linha):
    """Mostra na tela a mensagem que o cliente enviou ao servidor.

    `linha` já vem com o "\\n" final, então os bytes contados aqui são
    exatamente o que aparece na coluna Length do Wireshark.
    """
    dados = linha.encode("utf-8")
    print(f"[{endereco[0]}:{endereco[1]} -> servidor] {linha.rstrip(chr(10))}  ({len(dados)} bytes)")


def enviar(f, linhas):
    for linha in linhas:
        f.write(linha + "\n")
    f.flush()


def atender(conn, endereco, tarefas):
    print(f"[+] {endereco} conectou")
    conn.settimeout(60)  # cliente parado por 60s é desconectado
    with conn, conn.makefile("rw", encoding="utf-8", newline="\n") as f:
        try:
            while True:
                linha = f.readline(MAX_LINHA + 1)
                if not linha:  # cliente fechou
                    break
                if not linha.endswith("\n"):  # linha longa demais ou cortada
                    if len(linha) > MAX_LINHA:
                        enviar(f, [f"ERRO {ERRO_REQUISICAO} linha maior que {MAX_LINHA} bytes"])
                    break
                mostrar_recebimento(endereco, linha)
                enviar(f, processar(linha, tarefas))
                if linha.strip().upper() == "SAIR":
                    break
        except (OSError, UnicodeDecodeError) as e:
            print(f"[!] {endereco}: {e}")
    print(f"[-] {endereco} saiu")


def main():
    tarefas = Tarefas()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((HOST, PORTA))
        except OSError as e:
            sys.exit(f"Não consegui usar {HOST}:{PORTA}: {e}")
        s.listen()
        print(f"Servidor ouvindo em {HOST}:{PORTA} (Ctrl+C encerra)")
        try:
            while True:
                conn, endereco = s.accept()
                threading.Thread(target=atender, args=(conn, endereco, tarefas), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServidor encerrado.")


if __name__ == "__main__":
    main()
