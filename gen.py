# Генератор кода

import ovm

PC = 0  # Счетчик команд времени компиляции

def convert(cmd):
    global PC

    ovm.M[PC] = cmd
    PC += 1


def convertConst(c):
    convert(abs(c))
    if c < 0:
        convert(ovm.NEG)

def convertAddr(v):
    convert(100)