import ply.yacc as yacc
from MiniPascalLexico import tokens
import MiniPascalLexico
import sys

VERBOSE = 1
error_sintactico = False

# =========================
# PROGRAMA
# =========================
def p_program(p):
    'program : PROGRAM ID SEMICOLON declarations compound_statement DOT'
    
    if not error_sintactico:
        print("Programa sintácticamente correcto!")
    else:
        print("El programa tiene errores sintácticos.")

# =========================
# DECLARACIONES
# =========================
def p_declarations_1(p):
    'declarations : VAR var_decl_list' #Donde hay variables

def p_declarations_2(p):
    'declarations : empty' #Cuando no hay variables (vacio)

def p_var_decl_list_1(p):
    'var_decl_list : var_decl_list var_decl' #Lista de declaracaiones, permite varias lineas de variables

def p_var_decl_list_2(p):
    'var_decl_list : var_decl' #Seria el caso base donde solo hay una declaracion

def p_var_decl(p):
    'var_decl : id_list COLON ID SEMICOLON' #Declaracion de integer

def p_id_list_1(p):
    'id_list : id_list COMMA ID' #Identificadores separados por coma

def p_id_list_2(p):
    'id_list : ID' #Cuando solo hay un identificador

# =========================
# BLOQUE BEGIN END
# =========================
def p_compound_statement(p):
    'compound_statement : BEGIN statement_list END' #bloque principal begin...end

def p_statement_list_1(p):
    'statement_list : statement_list SEMICOLON statement' #lista de sentencias separadas por ;

def p_statement_list_2(p):
    'statement_list : statement' #caseo base donde es solo una sentencia

# =========================
# SENTENCIAS
# =========================
def p_statement_1(p):
    'statement : assignment'

def p_statement_2(p):
    'statement : if_statement'

def p_statement_3(p):
    'statement : while_statement'

def p_statement_4(p):
    'statement : for_statement'

def p_statement_5(p):
    'statement : repeat_statement'

def p_statement_6(p):
    'statement : compound_statement' #permite bloques anidados (begind...end dentro de otro)

def p_statement_7(p):
    'statement : empty' #sentencia vacia

# =========================
# ASIGNACION
# =========================
def p_assignment(p):
    'assignment : ID ASSIGN expression' #asignacion, ej: x := 1 + 2

# =========================
# IF ELSE
# =========================
def p_if_statement_1(p):
    'if_statement : IF condition THEN statement'

def p_if_statement_2(p):
    'if_statement : IF condition THEN statement ELSE statement'

# =========================
# WHILE
# =========================
def p_while_statement(p):
    'while_statement : WHILE condition DO statement'

# =========================
# FOR
# =========================
def p_for_statement(p):
    'for_statement : FOR assignment TO expression DO statement'

# =========================
# REPEAT UNTIL
# =========================
def p_repeat_statement(p):
    'repeat_statement : REPEAT statement_list UNTIL condition'

# =========================
# CONDICIONES
# =========================
def p_condition_1(p):
    'condition : expression LESS expression'

def p_condition_2(p):
    'condition : expression GREATER expression'

def p_condition_3(p):
    'condition : expression EQUAL expression'

def p_condition_4(p):
    'condition : expression LESSEQUAL expression'

def p_condition_5(p):
    'condition : expression GREATEREQUAL expression'

def p_condition_6(p):
    'condition : expression DISTINT expression'

# =========================
# EXPRESIONES
# =========================
def p_expression_1(p):
    'expression : expression PLUS term'

def p_expression_2(p):
    'expression : expression MINUS term'

def p_expression_3(p):
    'expression : term'

def p_term_1(p):
    'term : term TIMES factor'

def p_term_2(p):
    'term : term DIVIDE factor'

def p_term_3(p):
    'term : factor'

def p_factor_1(p):
    'factor : NUMBER'

def p_factor_2(p):
    'factor : ID'

def p_factor_3(p):
    'factor : LPAREN expression RPAREN'

# =========================
# VACIO
# =========================
def p_empty(p):
    'empty :'
    pass

# =========================
# ERROR
# =========================
def p_error(p):
    global error_sintactico
    error_sintactico = True

    if VERBOSE:
        if p:
            print(f"Error sintáctico en línea {p.lineno}: token inesperado '{p.value}'...")
            
            # Recuperación simple
            parser.errok()
        else:
            print("Error sintáctico al final del archivo...")
    else:
        raise Exception("syntax error")

parser = yacc.yacc()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        fin = sys.argv[1]
    else:
        fin = 'Prueba2.c'

    with open(fin, 'r') as f:
        data = f.read()

    parser.parse(data)

#Apoyo con IA para las gramáticas