import ply.lex as lex
import sys

# lista de tokens
tokens = (

    # Palabras reservadas
    'ABSOLUTE',
    'ABSTRACT',
    'AND',
    'DIV',
    'FILE',
    'IN',
    'OF',
    'RECORD',
    'TYPE',
    'ARRAY',
    'DO',
    'FOR',
    'LABEL',
    'OR',
    'REPEAT',
    'UNTIL',
    'BEGIN',
    'DOWNTO',
    'FUNCTION',
    'MOD',
    'PACKED',
    'SET',
    'VAR',
    'CASE',
    'ELSE',
    'GOTO',
    'NIL',
    'PROCEDURE',
    'THEN',
    'WHILE',
    'CONST',
    'END',
    'IF',
    'NOT',
    'PROGRAM',
    'TO',
    'WITH',

    # Operadores aritméticos
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',

    # Operadores relacionales
    'EQUAL',
    'DISTINT',
    'GREATER',
    'LESS',
    'GREATEREQUAL',
    'LESSEQUAL',

    # Asignación
    'ASSIGN',

    # Símbolos
    'SEMICOLON',
    'COMMA',
    'LPAREN',
    'RPAREN',
    'LBRACKET',
    'RBRACKET',
    'COLON',
    'DOT',

    # Otros
    'ID',
    'NUMBER',
)

# Operadores
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'

# Relacionales
t_EQUAL = r'='
t_DISTINT = r'<>'
t_GREATER = r'>'
t_LESS = r'<'
t_GREATEREQUAL = r'>='
t_LESSEQUAL = r'<='

# Asignación Pascal
t_ASSIGN = r':='

# Símbolos
t_SEMICOLON = r';'
t_COMMA = r','
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_COLON = r':'
t_DOT = r'\.'

# Palabras reservadas

def t_ABSOLUTE(t): r'absolute'; return t
def t_ABSTRACT(t): r'abstract'; return t
def t_AND(t): r'and'; return t
def t_DIV(t): r'div'; return t
def t_FILE(t): r'file'; return t
def t_IN(t): r'in'; return t
def t_OF(t): r'of'; return t
def t_RECORD(t): r'record'; return t
def t_TYPE(t): r'type'; return t
def t_ARRAY(t): r'array'; return t
def t_DO(t): r'do'; return t
def t_FOR(t): r'for'; return t
def t_LABEL(t): r'label'; return t
def t_OR(t): r'or'; return t
def t_REPEAT(t): r'repeat'; return t
def t_UNTIL(t): r'until'; return t
def t_BEGIN(t): r'begin'; return t
def t_DOWNTO(t): r'downto'; return t
def t_FUNCTION(t): r'function'; return t
def t_MOD(t): r'mod'; return t
def t_PACKED(t): r'packed'; return t
def t_SET(t): r'set'; return t
def t_VAR(t): r'var'; return t
def t_CASE(t): r'case'; return t
def t_ELSE(t): r'else'; return t
def t_GOTO(t): r'goto'; return t
def t_NIL(t): r'nil'; return t
def t_PROCEDURE(t): r'procedure'; return t
def t_THEN(t): r'then'; return t
def t_WHILE(t): r'while'; return t
def t_CONST(t): r'const'; return t
def t_END(t): r'end'; return t
def t_IF(t): r'if'; return t
def t_NOT(t): r'not'; return t
def t_PROGRAM(t): r'program'; return t
def t_TO(t): r'to\b'; return t #toca poner \b para que no lea to de total como un to
def t_WITH(t): r'with'; return t

# Ignorar espacios
t_ignore = ' \t'

def t_INVALID_ID(t):
    r'\d+[a-zA-Z_][a-zA-Z0-9_]*'
    print(f"Error léxico: identificador inválido '{t.value}'")


# Números
def t_NUMBER(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t


# Identificadores
def t_ID(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t


# Comentarios Pascal { }
def t_comment1(t):
    r'\{(.|\n)*?\}'
    t.lexer.lineno += t.value.count('\n')


# Comentarios Pascal (* *)
def t_comment2(t):
    r'\(\*(.|\n)*?\*\)'
    t.lexer.lineno += t.value.count('\n')


# Comentarios tipo //
def t_comment3(t):
    r'//.*'


# Saltos de línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)


# Manejo de errores
def t_error(t):
    print("Lexical error:", t.value[0])
    t.lexer.skip(1)


# Construcción del lexer
lexer = lex.lex()


# Función de prueba
def test(data, lexer):
    lexer.input(data)
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(tok)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        fin = sys.argv[1]
    else:
        fin = 'Prueba2.c'

    f = open(fin, 'r')
    data = f.read()

    print(data)
    print("\nTOKENS:\n")

    test(data, lexer)


    #Apoyo con IA en ER chatgpt