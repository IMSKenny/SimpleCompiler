# Компилятор языка "О"
import pars
import scan
import text

print('Компилятор языка "O"')

def Init():
    text.Reset()

def Done():
    pass

Init()
# pars.TestText()
# pars.TestScan()
pars.Compile()
print("Компиляция завершена")
Done()