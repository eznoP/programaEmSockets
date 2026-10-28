"""Checagem rápida, sem rede. Uso: python test_app.py"""

from servidor import Tarefas, processar
from cliente import traduzir

t = Tarefas()
assert processar("ADD comprar pão", t) == ["OK 1"]
assert processar("ADD estudar redes", t) == ["OK 2"]
assert processar("DONE 1", t) == ["OK"]
assert processar("LIST", t) == ["OK 2", "1 T comprar pão", "2 F estudar redes"]
assert processar("DEL 2", t) == ["OK"]
assert processar("DONE 2", t) == ["ERRO 404 tarefa 2 não existe"]
assert processar("ADD", t)[0].startswith("ERRO 400")
assert processar("XYZ", t)[0].startswith("ERRO 400")
assert traduzir("add algo") == "ADD algo"
assert traduzir("done x") is None
assert traduzir("sair") == "SAIR"
print("todos os testes passaram")
