# Сообщения об ошибках
import loc
import text

def _error(msg, p):
    while text.ch() not in {text.chEOL, text.chEOT}:
        text.nextCh()
    print(' ' * (p - 1), '^', sep='')
    print(msg)
    exit(1)


def lexError(msg):
    _error(msg, loc.pos)

def expect(msg):
    _error("Ожидается " + msg, loc.lexPos)

def ctxError(msg):
    _error(msg, loc.lexPos)

def Error(msg):
    print()
    print(msg)
    exit(2)