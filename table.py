# Таблица имен

import error

_table = []

def openScope():
    _table.append({})

def closeScope():
    _table.pop()

def add(item):
    last = _table[-1]
    last[item.name] = item

def new(item):
    last = _table[-1]
    if item.name in last:
        error.ctxError("Повторное объявление имени")
    else:
        add(item)

def find(name):
    for block in reversed(_table):
        if name in block:
            return block[name]
    error.ctxError("Необъявленное имя")



