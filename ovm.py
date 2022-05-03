# Виртуальная машина

STOP = -1
ADD = -2
SUB = -3
MULT = -4
DIV = -5
MOD = -6
NEG = -7
LOAD = -8
SAVE = -9
DUP = -10
DROP = -11
SWAP = -12
OVER = -13
GOTO = -14
IFLT = -15
IFLE = -16
IFGT = -17
IFGE = -18
IFEQ = -19
IFNE = -20
IN = -21
OUT = -22
LN = -23

MEM_SIZE = 8 * 1024

M = [STOP] * MEM_SIZE


def Run:
    pc = 0
    sp = MEM_SIZE
    while True:
        cmd = M[pc]
        pc += 1
        if cmd >= 0:
            sp -= 1
            M[sp] = cmd
        elif cmd == ADD:
            sp += 1
            M[sp] = M[sp] + M[sp - 1]
        elif cmd == SUB:
            sp += 1
            M[sp] = M[sp] - M[sp - 1]
        elif cmd == MULT:
            sp += 1
            M[sp] = M[sp] * M[sp - 1]
        elif cmd == DIV:
            sp += 1
            M[sp] = M[sp] // M[sp - 1]
        elif cmd == MOD:
            sp += 1
            M[sp] = M[sp] % M[sp - 1]
        elif cmd == NEG:
            M[sp] = -M[sp]

