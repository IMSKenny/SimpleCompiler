# Компилятор языка "О"
import pars
import ovm
import text
import gen

print('-'*54)
print('Конвертер языка "O" в язык Python.')
print('-'*54 + '\n')

text.Reset()
# pars.TestText()
# pars.TestScan()
pars.Compile()
# print(pars.textPy)
print("Конвертация завершена.")
text.safeFile(pars.textPy)
print("Результат записан в файл: ", pars.nameFile + '.py')
print('\n')
# ovm.M[0] = 100
# ovm.M[1] = 10
# ovm.M[2] = ovm.OUT
ovm.printCode(gen.PC)
ovm.Run()
