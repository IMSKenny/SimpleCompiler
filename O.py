# Компилятор языка "О"
import pars
import ovm
import scan
import text
import gen

print('Компилятор языка "O"')

def Init():
    text.Reset()

def Done():
    pass

Init()
# pars.TestText()
# pars.TestScan()
pars.Compile()
# print(pars.textPy)
print("Компиляция завершена")
text.safeFile(pars.textPy)
print("Результат записан в файл: ", pars.nameFile, '.py')
# ovm.M[0] = 100
# ovm.M[1] = 10
# ovm.M[2] = ovm.OUT
ovm.printCode(gen.PC)
ovm.Run()
Done()