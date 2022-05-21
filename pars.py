# Синтаксический анализатор

from text import *
import scan
from scan import *
import table
import items
import enum
import gen
import ovm


textPy = ""
n = 1


class Types(enum.Enum):
    Bool, Int = range(2)

def indent(n):
    return ' '*4*n

def lnIndent(n):
    if n == 1:
        return '\n'
    return '\n' + ' '*4*(n - 1)
    
def TestText():
    while ch() != chEOT:
        nextCh()


def TestScan():
    nextCh()
    nextLex()
    n = 0
    while lex() != Lex.EOT:
        n += 1
        print(lex())
        nextLex()
    print("Число лексем", n)


def skip(L):
    if lex() == L:
        nextLex()
    else:
        expect(lexName(L))


def check(L):
    if lex() != L:
        expect(lexName(L))


def ImportModule():
    check(Lex.NAME)
    name = scan.name()
    if name in {"In", "Out"}:
        table.new(items.Module(name))
    else:
        ctxError("Предусмотрены только модули In и Out")
    nextLex()


# Импорт =
#    IMPORT Имя {"," Имя} ";".
def Import():
    skip(Lex.IMPORT)
    ImportModule()
    while lex() == Lex.COMMA:
        nextLex()
        ImportModule()
    skip(Lex.SEMI)


# КонстВыраж = ["+" | "-"] (Число | Имя).
def ConstExpr():
    sign = 1
    if lex() in {Lex.PLUS, Lex.MINUS}:
        if lex() == Lex.MINUS:
            sign = -1
        nextLex()
    if lex() == Lex.NUM:
        value = scan.num() * sign
        nextLex()
        return value
    elif lex() == Lex.NAME:
        x = table.find(scan.name())
        nextLex()  # Петров Георгий
        if type(x) != items.Const:
            expect("константа")
        else:
            return x.value * sign
    else:
        expect("число или имя")


# ОбъявлКонст = Имя "=" КонстВыраж.
def ConstDecl():
    global textPy, n

    check(Lex.NAME)
    name = scan.name()
    textPy += name                                       #
    nextLex()
    skip(Lex.EQ)
    textPy += ' = '                                      #
    value = ConstExpr()
    textPy += str(value)                                      #
    #textPy += lnIndent(n)                                #
    #textPy += lnIndent(n)                                #
    table.new(items.Const(name, Types.Int, value))


def Type():
    check(Lex.NAME)
    x = table.find(scan.name())
    if type(x) != items.Type:
        expect("имя типа")
    nextLex()


# ОбъявлПерем = Имя {"," Имя} ":" Тип.
def VarDecl():
    global textPy, n

    check(Lex.NAME)
    #textPy += str(lex())                                              #нужно посмотреть
    table.new(items.Var(scan.name(), Types.Int))
    nextLex()
    while lex() == Lex.COMMA:
        #textPy += ','                                            #
        nextLex()
        check(Lex.NAME)
        #textPy += str(lex())                                          #нужно посмотреть
        table.new(items.Var(scan.name(), Types.Int))
        nextLex()
    skip(Lex.COLON)
    #textPy += lnIndent(n)                                        #
    #textPy += lnIndent(n)                                        #
    Type()


# ПослОбъявл =
#    {CONST
#       {ОбъявлКонст ";"}
#    |VAR
#       {ОбъявлПерем ";"} }.
def DeclSeq():
    while lex() in {Lex.CONST, Lex.VAR}:
        if lex() == Lex.CONST:
            nextLex()
            while lex() == Lex.NAME:
                ConstDecl()
                skip(Lex.SEMI)
        else:  # VAR
            nextLex()
            while lex() == Lex.NAME:
                VarDecl()
                skip(Lex.SEMI)


# ПростоеВыраж = ["+"|"-"] Слагаемое {ОперСлож Слагаемое}.
def SimpleExpression():
    global textPy

    if lex() in {Lex.PLUS, Lex.MINUS}:
        textPy += ' ' + lexName(lex()) + ' '                                 #
        nextLex()
        T = Term()
        TestInt(T)
    else:
        T = Term()
    while lex() in {Lex.PLUS, Lex.MINUS}:
        textPy += ' ' + lexName(lex()) + ' '                                 #
        TestInt(T)
        nextLex()
        T = Term()
        TestInt(T)
    return T


# Слагаемое = Множитель {ОперУмн Множитель}.
def Term():
    global textPy

    T = Factor()
    while lex() in {Lex.MULT, Lex.DIV, Lex.MOD}:
        textPy += ' ' + lexName(lex()) + ' '                                 #
        TestInt(T)
        nextLex()
        T = Factor()
        TestInt(T)
    return T


# Множитель =
#    Имя ["(" Выраж ")"]
#    | Число
#    | "(" Выраж ")".
def Factor():
    global textPy, n

    if lex() == Lex.NAME:
        x = table.find(scan.name())
        if type(x) == items.Const:
            gen.convertConst(x.value)   # значение константы
            textPy += str(scan.name())
            nextLex()
            return x.typ
        elif type(x) == items.Var:   # y = x
            gen.convertAddr(x)
            gen.convert(ovm.LOAD)
            textPy += str(scan.name())
            nextLex()                                           #
            return x.typ
        elif type(x) == items.Func:
            textPy += 'def '                                       #
            textPy += str(scan.name())                                           #
            nextLex()
            skip(Lex.LPAR)
            textPy += '('                                          #
            Function(x)
            skip(Lex.RPAR)
            textPy += ')'                                          #
            return x.typ
        else:
            expect("имя константы, переменной или функции")
    elif lex() == Lex.NUM:
        gen.convert(scan.num())
        textPy += str(scan.num())
        nextLex()
        return Types.Int
    elif lex() == Lex.LPAR:
        textPy += '('                                              #
        nextLex()
        T = Expression()
        skip(Lex.RPAR)
        textPy += ')'                                              #
        return T
    else:
        expect("имя, число или '('")


def TestInt(T):
    if T != Types.Int:
        expect("выражение целого типа")


# Выраж = ПростоеВыраж [Отношение ПростоеВыраж].
def Expression():
    global textPy, n

    T = SimpleExpression()
    if lex() in {Lex.EQ, Lex.NE, Lex.GT, Lex.GE, Lex.LT, Lex.LE}:
        textPy += ' ' + lexName(lex()) + ' '                                 #
        TestInt(T)
        nextLex()
        T = SimpleExpression()
        TestInt(T)
        return Types.Bool
    else:
        return T


def Parameter():
    Expression()


# Переменная ":=" Выраж
def AssStatement(x):
    global textPy, n

    # x - переменная
    skip(Lex.NAME)
    #textPy += str(lex())                                    #нужно посмотреть
    skip(Lex.ASS)
    textPy += ' = '                                        #
    T = Expression()
    if x.typ != T:
        ctxError("Несоответсвие типов при присваивании")


def IntExpr():
    T = Expression()
    if T != Types.Int:
        expect("выражение целого типа")


def Variable():
    check(Lex.NAME)
    v = table.find(scan.name())
    if type(v) != items.Var:
        expect("имя переменной")
    nextLex()


def Procedure(x):
    global textPy, n

    if x.name == "HALT":
        value = ConstExpr()
        textPy += 'exit'                   #
    elif x.name == "INC":
        # INC(v); INC(v, n)
        Variable()
        textPy += ' += '                   #
        if lex() == Lex.COMMA:
            nextLex()
            IntExpr()
        else:
            textPy += ' 1 '                #
    elif x.name == "DEC":
        # DEC(v); DEC(v, n)
        Variable()
        textPy += ' -= '                   #
        if lex() == Lex.COMMA:
            nextLex()
            IntExpr()
        else:
            textPy += ' 1 '                #
    elif x.name == "In.Open":
        pass
    elif x.name == "In.Int":
        Variable()
    elif x.name == "Out.Int":
        # Out.Int(e, f)            print(f"{IntExpr()}: {IntExpr()}", end='')
        textPy += 'print(f"{'                             #
        IntExpr()
        textPy += '}'                                     #
        skip(Lex.COMMA)
        textPy += ': {'                                   #
        IntExpr()
        textPy += '}", end=\'\')'                         #
    elif x.name == "Out.Ln":
        textPy += 'print()'                               #
    else:
        assert False


def Function(x):
    if x.name == "ABS":
        IntExpr()
    elif x.name == "MIN":
        # MIN(INTEGER)
        Type()
    elif x.name == "MAX":
        # MAX(INTEGER)
        Type()
    elif x.name == "ODD":
        IntExpr()
    else:
        assert False


# [Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
def CallStatement(x):
    # x - процедура или модуль
    skip(Lex.NAME)
    if lex() == Lex.DOT:
        if type(x) != items.Module:
            expect("имя модуля слева от точки")
        nextLex()
        check(Lex.NAME)
        key = x.name + '.' + scan.name()
        x = table.find(key)
        if type(x) != items.Proc:
            expect("процедура")
        nextLex()
    elif type(x) != items.Proc:
        expect("имя процедуры")

    if lex() == Lex.LPAR:
        nextLex()
        Procedure(x)
        skip(Lex.RPAR)
    elif x.name not in {"Out.Ln", "In.Open"}:
        expect("Out.Ln или In.Open")


# Переменная ":=" Выраж
# |[Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
def AssOrCall():
    global textPy, n

    check(Lex.NAME)
    x = table.find(scan.name())
    if scan.name() not in {'In', 'Out'}:
        textPy += scan.name()                                      #
    if type(x) == items.Var:
        AssStatement(x)
    elif type(x) == items.Proc or type(x) == items.Module:
        CallStatement(x)
    else:
        expect("имя переменной или процедуры")


#    IF Выраж THEN
#       ПослОператоров
#    {ELSIF Выраж THEN
#       ПослОператоров}
#    [ELSE
#       ПослОператоров]
#     END
def IfStatement():
    global textPy, n

    skip(Lex.IF)
    textPy += 'if '              #
    BoolExpr()
    skip(Lex.THEN)
    textPy += ':'                #
    n += 1
    textPy += lnIndent(n)
    StatSeq()
    while lex() == Lex.ELSIF:
        textPy += 'elif'         #
        nextLex()
        BoolExpr()
        skip(Lex.THEN)
        textPy += ':'            #
        n += 1
        #textPy += lnIndent(n)
        StatSeq()
    if lex() == Lex.ELSE:
        textPy += 'else:'        #
        n += 1
        #textPy += lnIndent(n)
        nextLex()
        StatSeq()
    skip(Lex.END)


def TestBool(T):
    if T != Types.Bool:
        expect("логическое выражение")


def BoolExpr():
    global textPy

    T = Expression()
    TestBool(T)
    #textPy += str(lex())               #


# WHILE Выраж DO
#       ПослОператоров
# END
def WhileStatement():
    global textPy, n

    skip(Lex.WHILE)
    textPy += 'while '            #
    BoolExpr()
    skip(Lex.DO)
    textPy += ':'                 #
    n += 1
    textPy += lnIndent(n)
    StatSeq()
    skip(Lex.END)


# Оператор = [
#    Переменная ":=" Выраж
#    |[Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
#    |IF Выраж THEN
#       ПослОператоров
#    {ELSIF Выраж THEN
#       ПослОператоров}
#    [ELSE
#       ПослОператоров]
#     END
#    |WHILE Выраж DO
#       ПослОператоров
#     END
# ].
def Statement():
    if lex() == Lex.NAME:
        AssOrCall()
    elif lex() == Lex.IF:
        IfStatement()
    elif lex() == Lex.WHILE:
        WhileStatement()


# ПослОператоров =
#    Оператор {";"
#    Оператор }.
def StatSeq():
    global textPy, n

    #n += 1                              #
    #textPy += lnIndent(n)               # под вопросом
    Statement()
    while lex() == Lex.SEMI:
        textPy += lnIndent(n)           #
        nextLex()
        Statement()
    n -= 1                              #
    #textPy += lnIndent(n)               #


# Модуль =
#    MODULE Имя ";"
#    [Импорт]
#    ПослОбъявл
#    [BEGIN
#       ПослОператоров]
# END Имя ".".
def Module():
    skip(Lex.MODULE)
    if lex() == Lex.NAME:
        module = scan.name()  # Петров Гергий
        table.new(items.Module(module))
        nextLex()
    else:
        expect("имя")
    skip(Lex.SEMI)
    if lex() == Lex.IMPORT:
        Import()
    DeclSeq()
    if lex() == Lex.BEGIN:
        nextLex()
        StatSeq()
    skip(Lex.END)
    check(Lex.NAME)
    x = table.find(scan.name())
    if type(x) != items.Module:
        expect("имя модуля")
    elif x.name != module:  # Пeтров Георгий
        expect("имя модуля " + module)
    nextLex()
    skip(Lex.DOT)


def Compile():
    nextCh()
    nextLex()
    table.openScope()

    T = Types

    table.add(items.Func("ABS", T.Int))
    table.add(items.Func("MAX", T.Int))
    table.add(items.Func("MIN", T.Int))
    table.add(items.Func("ODD", T.Bool))
    table.add(items.Proc("HALT"))
    table.add(items.Proc("INC"))
    table.add(items.Proc("DEC"))
    table.add(items.Proc("In.Open"))
    table.add(items.Proc("In.Int"))
    table.add(items.Proc("Out.Int"))
    table.add(items.Proc("Out.Ln"))
    table.add(items.Type("INTEGER", T.Int))

    table.openScope()
    Module()
    table.closeScope()
    table.closeScope()
