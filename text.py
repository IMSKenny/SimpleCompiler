# Драйвер исходного текста

import sys
import loc
import error

chEOT = "\0"
chEOL = "\n"
chSPACE = ' '
chTAB = '\t'

_src = ""
_i = 0
_ch = ""


def Reset():
    global _src
    if len(sys.argv) < 2:
        error.Error("Запуск: python O.py <файл программы>")
    else:
        try:
            _f = open(sys.argv[1])
        except:
            error.Error("Ошибка открытия файла")
        _src = _f.read()
        _f.close()


def nextCh():
    global _src, _i, _ch
    if _i < len(_src):
        _ch = _src[_i]
        print(_ch, end="")
        loc.pos += 1
        _i += 1
        if _ch in {'\n', '\r'}:
            _ch = chEOL
            loc.pos = 0
    else:
        _ch = chEOT


def ch():
    return _ch
