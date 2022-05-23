# Генератор кода

import ovm
from scan import Lex


PC = 0  # Счетчик команд времени компиляции

def Gen(cmd):
    global PC

    ovm.M[PC] = cmd
    PC += 1


def GenConst(c):
    Gen(abs(c))
    if c < 0:
        Gen(ovm.NEG)

        
def GentAddr(v):
    Gen(v.addr)
    v.addr = PC + 1

    
def GenComp(op):
    Gen(0)
    if op == Lex.EQ:
        Gen(ovm.IFNE)
    elif op == Lex.NE:
        Gen(ovm.IFEQ)
    elif op == Lex.GE:
        Gen(ovm.IFLT)
    elif op == Lex.GT:
        Gen(ovm.IFLE)
    elif op == Lex.LE:
        Gen(ovm.IFGT)
    elif op == Lex.LT:
        Gen(ovm.IFGE)
        
        
def fixup(A, PC):
    while A > 0:
        temp = ovm.M[A - 2]
        ovm.M[A - 2] = PC
        A = temp        
