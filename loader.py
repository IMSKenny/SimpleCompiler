# загрузчик программ

from ovm import M

def load(p):
    for PC, cmd in enumerate(p):
        M[PC] = cmd