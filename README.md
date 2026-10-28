# Lista de Tarefas em Rede (Sockets TCP)

Atividade avaliativa — Fundamentos de Redes de Computadores.

## Descrição da aplicação
Um servidor guarda uma lista de tarefas compartilhada. Vários clientes podem adicionar, listar, concluir e remover tarefas pela rede.

## Integrantes
- Enzo Rios Veras Ost Lopes
- Antônio Lucas de Oliveira Neto
- Arthur Gabriel Santos Lopes

## Arquitetura

```
 +-----------+      TCP (127.0.0.1:5000)       +------------------+
 | cliente.py| <-----------------------------> |  servidor.py     |
 | (processo)|   requisições / respostas       | (processo)       |
 +-----------+                                 | 1 thread/cliente |
                                               | Tarefas + Lock   |
                                               +------------------+
```

- **Servidor**: escuta na porta 5000, aceita conexões e cria uma thread por cliente. O dicionário de tarefas é protegido por um `threading.Lock`.
- **Cliente**: conecta, lê comandos do usuário e envia requisições no protocolo da aplicação.

## Protocolo TCP ou UDP
**TCP.**

**Justificativa:** a lista precisa chegar íntegra e na ordem certa. Um `DEL` ou `DONE` perdido deixaria cliente e servidor com estados diferentes. O TCP garante entrega, ordem e controle de erro. Também é orientado a conexão, o que combina com uma sessão de comandos. O custo (handshake e overhead) não pesa para mensagens curtas.

## Endereço IP e porta
- IP: `127.0.0.1` (localhost)
- Porta: `5000`

## Protocolo da aplicação
Protocolo de texto em UTF-8. Cada mensagem é uma linha terminada em `\n`. Linhas com mais de 1024 bytes são rejeitadas.

## Mensagens

| Requisição | Resposta |
|---|---|
| `ADD <texto>` | `OK <id>` |
| `LIST` | `OK <n>` seguido de `n` linhas `<id> <F\|T> <texto>` |
| `DONE <id>` | `OK` |
| `DEL <id>` | `OK` |
| `SAIR` | `OK` (servidor fecha a conexão) |
| (erro) | `ERRO <código> <mensagem>` |

Códigos de erro: `400` requisição inválida, `404` tarefa não encontrada.

## Instruções de execução
Requer Python 3.8+. Sem dependências externas.

```bash
# terminal 1
python3 servidor.py

# terminal 2 (quantos clientes quiser)
python3 cliente.py

# checagem sem rede
python3 test_app.py
```

Para o Wireshark: a captura é na interface `lo` com o filtro `tcp.port == 5000`.

## Respostas do roteiro

1. **Qual problema a aplicação resolve?** Permite manter uma lista de tarefas compartilhada entre processos em rede, com um único ponto de verdade (o servidor).
2. **Quem são os processos?** O processo cliente (`cliente.py`) e o processo servidor (`servidor.py`), cada um numa máquina ou terminal.
3. **Como ocorre a comunicação?** O servidor cria um socket, faz `bind` e `listen` na porta 5000 e fica em `accept`. O cliente cria um socket e faz `connect`. Depois disso, trocam linhas de texto: o cliente envia uma requisição, o servidor processa e responde. Cada cliente é atendido por uma thread própria.
4. **Protocolo de transporte:** TCP.
5. **Por que é adequado?** Não pode perder nem reordenar comandos (ver Justificativa acima).
6. **Protocolo da aplicação?** Protocolo de texto próprio, baseado em linhas (ver seção acima).
7. **Mensagens trocadas?** `ADD`, `LIST`, `DONE`, `DEL`, `SAIR` e suas respostas `OK` / `ERRO`.
8. **E se fosse UDP?** Não haveria conexão, então o servidor não saberia quem é cliente. Cada datagrama seria independente. Mensagens poderiam chegar fora de ordem ou se perder (um `DEL` perdido deixaria a lista divergente). Para usar UDP seria preciso implementar números de sequência, confirmação (ACK) e retransmissão por conta própria. Também seria preciso lidar com datagramas maiores que o MTU.
9. **Situações de erro?** Porta em uso ou servidor fora do ar; comando inválido; ID inexistente; linha longa demais; cliente que cai no meio da conversa; cliente parado (timeout); bytes que não são UTF-8.
10. **Como são tratadas?**
    - Porta em uso: mensagem clara e saída com erro (`servidor.py`, `main`).
    - Servidor fora do ar: `create_connection` falha e o cliente informa (`cliente.py`, `main`).
    - Comando inválido ou ID inexistente: o servidor responde `ERRO 400` ou `ERRO 404`; o cliente mostra a mensagem.
    - Linha longa demais: `ERRO 400` e fecha a conexão.
    - Queda ou timeout: `OSError` / `ConnectionError` é capturado; a thread do cliente termina sem derrubar o servidor.
    - UTF-8 inválido: capturado como `UnicodeDecodeError` na thread do cliente.
    - Ctrl+C no servidor encerra limpo; no cliente, equivale a `sair`.

