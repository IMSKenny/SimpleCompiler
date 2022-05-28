# Синтаксический анализатор

from text import *
import scan
from scan import *
import table
import items
import enum
from gen import *
import gen


keyWordNotUse = 0
_keyWord = {
    'and': keyWordNotUse,
    'del': keyWordNotUse,
    'for': keyWordNotUse,
    'is': keyWordNotUse,
    'raise': keyWordNotUse,
    'assert': keyWordNotUse,
    'elif': keyWordNotUse,
    'from': keyWordNotUse,
    'lambda': keyWordNotUse,
    'return': keyWordNotUse,
    'break': keyWordNotUse,
    'else': keyWordNotUse,
    'global': keyWordNotUse,
    'not': keyWordNotUse,
    'try': keyWordNotUse,
    'class': keyWordNotUse,
    'except': keyWordNotUse,
    'if': keyWordNotUse,
    'or': keyWordNotUse,
    'while': keyWordNotUse,
    'continue': keyWordNotUse,
    'exec': keyWordNotUse,
    'import': keyWordNotUse,
    'pass': keyWordNotUse,
    'yield': keyWordNotUse,
    'def': keyWordNotUse,
    'nally': keyWordNotUse,
    'in': keyWordNotUse,
    'print': keyWordNotUse
}

textPy = ""
ind = 1
nameFile = 'no_name'


class Types(enum.Enum):
    Bool, Int = range(2)

def indent(ind):
    return ' '*4*ind

def lnIndent(ind):
    if ind == 1:
        return '\n'
    return '\n' + ' '*4*(ind - 1)
    
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
    global textPy, ind

    check(Lex.NAME)
    name = scan.name()
    if name in _keyWord:
        Error('Нельзя использовать \'' + scan.name() + '\': зарезервированное слово.')
    else:
        textPy += name.upper()               #const to uppercase
    nextLex()
    skip(Lex.EQ)
    textPy += ' = '
    value = ConstExpr()
    textPy += str(value)
    textPy += lnIndent(ind)
    table.new(items.Const(name, Types.Int, value))


def Type():
    check(Lex.NAME)
    x = table.find(scan.name())
    if type(x) != items.Type:
        expect("имя типа")
    nextLex()


# ОбъявлПерем = Имя {"," Имя} ":" Тип.
def VarDecl():
    check(Lex.NAME)
    table.new(items.Var(scan.name(), Types.Int))
    if scan.name() in _keyWord:
        Error('Нельзя использовать \'' + scan.name() + '\': зарезервированное слово.')
    nextLex()
    while lex() == Lex.COMMA:
        nextLex()
        check(Lex.NAME)
        table.new(items.Var(scan.name(), Types.Int))
        if scan.name() in _keyWord:
            Error('Нельзя использовать \'' + scan.name() + '\': зарезервированное слово.')
        nextLex()
    skip(Lex.COLON)
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
        textPy += ' ' + lexName(lex()) + ' '
        op = lex()
        nextLex()
        T = Term()
        TestInt(T)
        if op == Lex.MINUS:
            Gen(cm.NEG)
    else:
        T = Term()
    while lex() in {Lex.PLUS, Lex.MINUS}:
        textPy += ' ' + lexName(lex()) + ' '
        op = lex()
        TestInt(T)
        nextLex()
        T = Term()
        TestInt(T)
        if op == Lex.PLUS:
            Gen(cm.ADD)
        else:
            Gen(cm.SUB)
    return T


# Слагаемое = Множитель {ОперУмн Множитель}.
def Term():
    global textPy

    T = Factor()
    while lex() in {Lex.MULT, Lex.DIV, Lex.MOD}:
        if lex() == Lex.MOD:
            textPy += ' % '
        elif lex() == Lex.DIV:
            textPy += ' // '
        else:
            textPy += ' * '
        Op = lex()
        TestInt(T)
        nextLex()
        T = Factor()
        TestInt(T)
        if Op == Lex.DIV:
            Gen(cm.DIV)
        elif Op == Lex.MULT:
            Gen(cm.MULT)
        else:
            Gen(cm.MOD)
    return T


# Множитель =
#    Имя ["(" Выраж ")"]
#    | Число
#    | "(" Выраж ")".
def Factor():
    global textPy

    if lex() == Lex.NAME:
        x = table.find(scan.name())
        if type(x) == items.Const:
            GenConst(x.value)   # значение константы
            textPy += str(scan.name()).upper()
            nextLex()
            return x.typ
        elif type(x) == items.Var:   # y = x
            GenAddr(x)
            Gen(cm.LOAD)
            textPy += str(scan.name())
            nextLex()
            return x.typ
        elif type(x) == items.Func:
            # textPy += 'def '
            # textPy += str(scan.name())
            nextLex()
            skip(Lex.LPAR)
            # textPy += '('
            Function(x)
            skip(Lex.RPAR)
            # textPy += ')'
            return x.typ
        else:
            expect("имя константы, переменной или функции")
    elif lex() == Lex.NUM:
        Gen(scan.num())
        textPy += str(scan.num())
        nextLex()
        return Types.Int
    elif lex() == Lex.LPAR:
        textPy += '('
        nextLex()
        T = Expression()
        skip(Lex.RPAR)
        textPy += ')'
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
        if lex() == Lex.EQ:
            textPy += ' == '
        elif lex() == Lex.NE:
            textPy += ' != '
        else:
            textPy += ' ' + lexName(lex()) + ' '
        op = lex()
        TestInt(T)
        nextLex()
        T = SimpleExpression()
        TestInt(T)
        GenComp(op)
        return Types.Bool
    else:
        return T


def Parameter():
    Expression()


# Переменная ":=" Выраж
def AssStatement(x):
    global textPy

    # x - переменная
    GenAddr(x)
    skip(Lex.NAME)
    skip(Lex.ASS)
    textPy += ' = '
    T = Expression()
    if x.typ != T:
        ctxError("Несоответсвие типов при присваивании")
    Gen(cm.SAVE)


def IntExpr():
    T = Expression()
    if T != Types.Int:
        expect("выражение целого типа")


def Variable():
    global textPy

    check(Lex.NAME)
    v = table.find(scan.name())
    if type(v) != items.Var:
        expect("имя переменной")
    if scan.name() in _keyWord:
        Error('Нельзя использовать \'' + scan.name() + '\': зарезервированное слово.')
    else:
        textPy += scan.name()
    GenAddr(v)
    nextLex()


def Procedure(x):
    global textPy

    if x.name == "HALT":
        value = ConstExpr()
        GenConst(value)
        Gen(cm.STOP)
        textPy = textPy[:-4]
        textPy += 'exit(' + str(value) + ')'
    elif x.name == "INC":
        # INC(v); INC(v, n)
        Variable()
        Gen(cm.DUP)
        Gen(cm.LOAD)
        textPy += ' += '
        if lex() == Lex.COMMA:
            nextLex()
            IntExpr()
        else:
            textPy += '1'
            Gen(1)
        Gen(cm.ADD)
        Gen(cm.SAVE)
    elif x.name == "DEC":
        # DEC(v); DEC(v, n)
        Variable()
        Gen(cm.DUP)
        Gen(cm.LOAD)
        textPy += ' -= '
        if lex() == Lex.COMMA:
            nextLex()
            IntExpr()
        else:
            textPy += '1'
            Gen(1)
        Gen(cm.SUB)
        Gen(cm.SAVE)
    elif x.name == "In.Open":
        pass
    elif x.name == "In.Int":
        Variable()
        Gen(cm.IN)
        Gen(cm.SAVE)
        textPy += ' = int(input(\'Enter integer number: \'))'
    elif x.name == "Out.Int":
        # Out.Int(e, f)            print(f"{IntExpr()}: {IntExpr()}", end='')
        textPy += 'print(f\"{'                             
        IntExpr()                                    
        skip(Lex.COMMA)
        textPy += ': {'                                   
        IntExpr()
        Gen(cm.OUT)
        textPy += '}}\", end=\'\')'                         
    elif x.name in {"Out.Ln", "Out.Ln()"}:
        Gen(cm.LN)                       
    else:
        assert False


def Function(x):
    global textPy
    
    if x.name == "ABS":
        textPy += '('
        IntExpr()       # x
        textPy += '**2)**0.5'
        Gen(cm.DUP)    # x, x
        Gen(0)          # x, x, 0
        Gen(gen.PC + 3) # x, x, 0, A
        Gen(cm.IFGE)
        Gen(cm.NEG)
    elif x.name == "MIN":
        # MIN(INTEGER)
        Type()
        textPy = 'def minint():\n' + ' '*4 + 'return -2147483648\n' + textPy
        textPy += "minint()"
        Gen(MAXINT)
        Gen(cm.NEG)
        Gen(1)
        Gen(cm.SUB)
    elif x.name == "MAX":
        # MAX(INTEGER)
        Type()
        textPy = 'def maxint():\n' + ' '*4 + 'return 2147483647\n' + textPy
        textPy += "maxint()"
        Gen(MAXINT)
    elif x.name == "ODD":
        textPy += 'bool('
        IntExpr()    # x
        textPy += ' % 2)'
        Gen(2)       # x, 2
        Gen(cm.MOD) # x MOD 2
        Gen(0)       # x MOD 2, 0
        Gen(0)       # x MOD 2, 0, 0 - фиктивный адрес перехода
        Gen(cm.IFEQ)
    else:
        assert False


# [Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
def CallStatement(x):
    global textPy

    # x - процедура или модуль
    skip(Lex.NAME)
    if lex() == Lex.DOT:
        if type(x) != items.Module:
            expect("имя модуля слева от точки")
        nextLex()
        check(Lex.NAME)
        key = x.name + '.' + scan.name()
        if key == 'Out.Ln':
            textPy += 'print()'
        if key == 'In.Int':
            textPy += lnIndent(ind)
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
    elif x.name == 'Out.Ln':
        Gen(cm.LN)
    elif x.name not in {"Out.Ln", "In.Open"}:
        expect("Out.Ln или In.Open")


# Переменная ":=" Выраж
# |[Имя "."] Имя ["(" [Параметр {"," Параметр}] ")"]
def AssOrCall():
    global textPy

    check(Lex.NAME)
    x = table.find(scan.name())
    if scan.name() not in {'In', 'Out', 'INC', 'DEC'}:
        textPy += scan.name()
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
    global textPy, ind
    
    textPy += lnIndent(ind)
    skip(Lex.IF)
    textPy += 'if '
    BoolExpr()
    CondPC = gen.PC
    LastGOTO = 0
    skip(Lex.THEN)
    textPy += ':'
    ind += 1
    StatSeq()
    while lex() == Lex.ELSIF:
        ind -= 1
        Gen(LastGOTO)
        Gen(cm.GOTO)
        LastGOTO = gen.PC
        fixup(CondPC, gen.PC)
        textPy = textPy[:-4]
        textPy += 'elif '
        nextLex()
        BoolExpr()
        CondPC = gen.PC
        skip(Lex.THEN)
        textPy += ':'
        ind += 1
        StatSeq()
    if lex() == Lex.ELSE:
        ind -= 1
        Gen(LastGOTO)
        Gen(cm.GOTO)
        LastGOTO = gen.PC 
        ovm.printCode(gen.PC)
        fixup(CondPC, gen.PC)
        textPy = textPy[:-4]
        textPy += 'else:'
        ind += 1
        nextLex()
        StatSeq()
    else:
        fixup(CondPC, gen.PC)
    skip(Lex.END)
    fixup(LastGOTO, gen.PC)


def TestBool(T):
    if T != Types.Bool:
        expect("логическое выражение")


def BoolExpr():
    T = Expression()
    TestBool(T)


# WHILE Выраж DO
#       ПослОператоров
# END
def WhileStatement():
    global textPy, ind
    
    WhilePC = gen.PC
    textPy += lnIndent(ind)
    skip(Lex.WHILE)
    textPy += 'while '
    BoolExpr()
    CondPC = gen.PC
    textPy += ':'
    ind += 1
    skip(Lex.DO)
    StatSeq()
    skip(Lex.END)
    Gen(WhilePC)
    Gen(cm.GOTO)
    fixup(CondPC, gen.PC)



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
    global textPy, ind

    if lex() == Lex.NAME:
        if scan.name() not in {'In', 'END', 'IF', 'WHILE', 'Open'}:
            textPy += lnIndent(ind)
        AssOrCall()
    elif lex() == Lex.IF:
        IfStatement()
    elif lex() == Lex.WHILE:
        WhileStatement()


# ПослОператоров =
#    Оператор {";"
#    Оператор }.
def StatSeq():
    global textPy, ind

    Statement()
    while lex() == Lex.SEMI:
        nextLex()
        Statement()
    if scan.name() not in {'In', 'END', 'IF', 'WHILE', 'Open'}:
        textPy += lnIndent(ind)
    else:
        ind -= 1



# Модуль =
#    MODULE Имя ";"
#    [Импорт]
#    ПослОбъявл
#    [BEGIN
#       ПослОператоров]
# END Имя ".".
def Module():
    global nameFile, module, textPy

    skip(Lex.MODULE)
    if lex() == Lex.NAME:
        module = scan.name()  # Петров Гергий
        nameFile = module
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
    textPy += '\n'
    check(Lex.NAME)
    x = table.find(scan.name())
    if type(x) != items.Module:
        expect("имя модуля")
    elif x.name != module:  # Пeтров Георгий
        expect("имя модуля " + module)
    nextLex()
    skip(Lex.DOT)
    Gen(cm.STOP)
    AllocVars()
    
    
def AllocVars():
    vars = table.getVars()
    for v in vars:
        if v.addr > 0:
            fixup(v.addr, gen.PC)
            Gen(0)
        else:
            error.Warning("Переменная " + v.name + " объявлена, но не используется")


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
