# Лексический анализатор (сканер)

import string
from enum import Enum

from text import *
from error import *


class Lex(Enum):
    NONE, NAME, NUM, MODULE, IMPORT, BEGIN, END, CONST, \
    VAR, WHILE, DO, IF, THEN, ELSIF, ELSE, MULT, DIV, MOD, \
    PLUS, MINUS, EQ, NE, LT, LE, GT, GE, DOT, COMMA, \
    COLON, SEMI, ASS, LPAR, RPAR, EOT = range(34)


MAXINT = 0x7FFFFFFF

_lex = Lex.NONE
_num = 0
_name = ""

_kw = {
    'MODULE': Lex.MODULE,
    'IMPORT': Lex.IMPORT,
    "CONST": Lex.CONST,
    "VAR": Lex.VAR,
    "BEGIN": Lex.BEGIN,
    "END": Lex.END,
    "IF": Lex.IF,
    "THEN": Lex.THEN,
    "ELSIF": Lex.ELSIF,
    "ELSE": Lex.ELSE,
    "WHILE": Lex.WHILE,
    "DO": Lex.DO,
    "DIV": Lex.DIV,
    "MOD": Lex.MOD,
    "ARRAY": Lex.NONE,
    "RECORD": Lex.NONE,
    "POINTER": Lex.NONE,
    "SET": Lex.NONE,
    "WITH": Lex.NONE,
    "CASE": Lex.NONE,
    "OF": Lex.NONE,
    "LOOP": Lex.NONE,
    "EXIT": Lex.NONE,
    "PROCEDURE": Lex.NONE,
    "FOR": Lex.NONE,
    "TO": Lex.NONE,
    "BY": Lex.NONE,
    "IN": Lex.NONE,
    "IS": Lex.NONE,
    "NIL": Lex.NONE,
    "OR": Lex.NONE,
    "TYPE": Lex.NONE,
    "REPEAT": Lex.NONE,
    "UNTIL": Lex.NONE,
    "RETURN": Lex.NONE
}

_names = {
    Lex.NAME: 'имя',
    Lex.NUM: 'число',
    Lex.MULT: '"*"',
    Lex.PLUS: '"+"',
    Lex.MINUS: '"-"',
    Lex.EQ: '"="',
    Lex.NE: '"#"',
    Lex.LT: '"<"',
    Lex.LE: '"<="',
    Lex.GT: '">"',
    Lex.GE: '">="',
    Lex.DOT: '"."',
    Lex.COMMA: '","',
    Lex.COLON: '":"',
    Lex.SEMI: '";"',
    Lex.ASS: '":="',
    Lex.LPAR: '"("',
    Lex.RPAR: '")"',
    Lex.EOT: 'конец текста'
}


def lexName(L):
    return _names.get(L, L.name)


def scanIdent():
    global _lex, _name
    _name = ch()  # Первая буква
    nextCh()
    while ch() in string.ascii_letters + string.digits:
        _name += ch()
        nextCh()
    _lex = _kw.get(_name, Lex.NAME)


def scanNumber():
    global _num, _lex
    _num = 0;
    while ch() in string.digits:
        # _num = 10 * _num + int(ch())
        if _num <= (MAXINT - int(ch())) // 10:
            _num = 10 * _num + int(ch())
        else:
            lexError("Слишком большое число")
        nextCh()

    # if _num > MAXINT:
    #     lexError("Слишком большое число")
    _lex = Lex.NUM


def Comment():
    nextCh()  # *
    while True:
        while ch() not in {'*', chEOT, '('}:
            nextCh()
        if ch() == chEOT:
            lexError("Не закончен комментарий")
        elif ch() == '*':
            nextCh()
            if ch() == ')':
                nextCh()
                break
        else:
            nextCh()
            if ch() == '*':
                Comment()


def nextLex():
    global _lex

    while ch() in {chSPACE, chTAB, chEOL}:
        nextCh()

    loc.lexPos = loc.pos

    if ch() in string.ascii_letters:
        scanIdent()
    elif ch() in string.digits:
        scanNumber()
    elif ch() == ';':
        _lex = Lex.SEMI
        nextCh()
    elif ch() == '(':
        nextCh()
        if ch() == '*':
            Comment()
            nextLex()
        else:
            _lex = Lex.LPAR
    elif ch() == ')':
        _lex = Lex.RPAR
        nextCh()
    elif ch() == ',':
        _lex = Lex.COMMA
        nextCh()
    elif ch() == '.':
        _lex = Lex.DOT
        nextCh()
    elif ch() == ':':
        nextCh()
        if ch() == '=':
            _lex = Lex.ASS
            nextCh()
        else:
            _lex = Lex.COLON
        nextCh()
    elif ch() == '>':
        nextCh()
        if ch() == '=':
            _lex = Lex.GE
            nextCh()
        else:
            _lex = Lex.GT
    elif ch() == '<':
        nextCh()
        if ch() == '=':
            _lex = Lex.LE
            nextCh()
        else:
            _lex = Lex.LT
    elif ch() == '=':
        _lex = Lex.EQ
        nextCh()
    elif ch() == '#':
        _lex = Lex.NE
        nextCh()
    elif ch() == '+':
        _lex = Lex.PLUS
        nextCh()
    elif ch() == '-':
        _lex = Lex.MINUS
        nextCh()
    elif ch() == '*':
        _lex = Lex.MULT
        nextCh()
    elif ch() == chEOT:
        _lex = Lex.EOT
    else:
        lexError("Недопустимый символ")


def lex():
    return _lex


def name():
    return _name


def num():
    return _num
