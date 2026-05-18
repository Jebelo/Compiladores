# =============================================================
#  MiniPascalSemantico.py
#  Analizador Semántico para Mini-Pascal
#
#  Flujo:
#    1. Importa MiniPascalSintactico (que a su vez importa el léxico)
#    2. Redefine las reglas de la gramática con acciones semánticas
#    3. Construye su propio parser (sobrescribe el del sintáctico)
#
#  Características:
#    • Tabla de símbolos con ámbitos (global / función / procedimiento)
#    • Verificación de variables declaradas, inicializadas y tipos
#    • Compatibilidad de tipos en asignaciones, operaciones y condiciones
#    • Traza completa de asignaciones (línea a línea)
#    • Resumen final con el último valor registrado de cada variable
# =============================================================

import ply.yacc as yacc
import MiniPascalSintactico          # ← importa el sintáctico (y con él el léxico)
import MiniPascalLexico
import sys

# Reutilizamos la lista de tokens del léxico
from MiniPascalLexico import tokens

VERBOSE = 1


# ══════════════════════════════════════════════════════════════
#  TABLA DE SÍMBOLOS CON ÁMBITOS
# ══════════════════════════════════════════════════════════════

class Simbolo:
    """Representa una variable en la tabla de símbolos."""
    def __init__(self, nombre, tipo, ambito, linea_decl):
        self.nombre       = nombre
        self.tipo         = tipo          # 'integer' | 'real' | 'string' | 'boolean' | 'unknown'
        self.ambito       = ambito        # 'global' | nombre de función/procedimiento
        self.inicializada = False
        self.valor_actual = None          # último valor semántico registrado
        self.linea_decl   = linea_decl


class TablaSimbolos:
    """
    Gestiona ámbitos anidados como una pila:
      - ámbito[0]  = global
      - ámbito[1+] = función o procedimiento activo
    """

    def __init__(self):
        self._pila_ambitos = ['global']      # pila de nombres de ámbito
        self._tablas       = {'global': {}}  # ambito -> {nombre: Simbolo}
        self.errores       = []              # lista de (linea, msg)
        self.advertencias  = []              # lista de (linea, msg)
        self.traza         = []              # lista de dicts con cada asignación

    # ── gestión de ámbitos ────────────────────────────────────
    @property
    def ambito_actual(self):
        return self._pila_ambitos[-1]

    def entrar_ambito(self, nombre):
        """Llamar al entrar a una función o procedimiento."""
        self._pila_ambitos.append(nombre)
        self._tablas[nombre] = {}

    def salir_ambito(self):
        """Llamar al salir de una función o procedimiento."""
        if len(self._pila_ambitos) > 1:
            self._pila_ambitos.pop()

    # ── operaciones sobre símbolos ────────────────────────────
    def declarar(self, nombre, tipo_raw, linea):
        tipo  = self._normalizar_tipo(tipo_raw)
        tabla = self._tablas[self.ambito_actual]
        if nombre in tabla:
            self._error(linea,
                f"Variable '{nombre}' ya fue declarada en el ámbito "
                f"'{self.ambito_actual}' (línea {tabla[nombre].linea_decl})")
        else:
            tabla[nombre] = Simbolo(nombre, tipo, self.ambito_actual, linea)

    def asignar(self, nombre, tipo_expr, linea, valor_expr=None):
        """Verifica tipos, actualiza el símbolo y registra en la traza."""
        sim = self._buscar(nombre, linea)
        if sim is None:
            return 'unknown'

        if not self._tipos_asignables(sim.tipo, tipo_expr):
            self._error(linea,
                f"Incompatibilidad de tipos: no se puede asignar '{tipo_expr}' "
                f"a '{nombre}' (tipo declarado '{sim.tipo}')")

        sim.inicializada  = True
        sim.valor_actual  = valor_expr

        self.traza.append({
            'linea'  : linea,
            'nombre' : nombre,
            'tipo'   : sim.tipo,
            'ambito' : sim.ambito,
            'valor'  : valor_expr,
        })
        return sim.tipo

    def usar(self, nombre, linea):
        """Devuelve el tipo; emite error/advertencia según corresponda."""
        sim = self._buscar(nombre, linea)
        if sim is None:
            return 'unknown'
        if not sim.inicializada:
            self._advertencia(linea,
                f"Variable '{nombre}' puede estar siendo usada sin inicializar")
        return sim.tipo

    # ── búsqueda con regla de ámbitos ─────────────────────────
    def _buscar(self, nombre, linea):
        """Busca primero en el ámbito actual y luego sube al global."""
        for ambito in reversed(self._pila_ambitos):
            if nombre in self._tablas.get(ambito, {}):
                return self._tablas[ambito][nombre]
        self._error(linea, f"Variable '{nombre}' usada sin declarar")
        return None

    # ── helpers ───────────────────────────────────────────────
    @staticmethod
    def _normalizar_tipo(t):
        t = t.lower()
        mapa = {
            'integer': 'integer', 'int':   'integer',
            'real':    'real',    'float': 'real',
            'string':  'string',  'str':   'string',
            'boolean': 'boolean', 'bool':  'boolean',
        }
        return mapa.get(t, 'unknown')

    @staticmethod
    def _tipos_asignables(tipo_var, tipo_expr):
        if 'unknown' in (tipo_var, tipo_expr):
            return True
        if tipo_var == tipo_expr:
            return True
        if tipo_var == 'real' and tipo_expr == 'integer':
            return True   # promoción implícita integer → real
        return False

    def _error(self, linea, msg):
        self.errores.append((linea, msg))

    def _advertencia(self, linea, msg):
        self.advertencias.append((linea, msg))

    def todos_los_simbolos(self):
        """Genera todos los Simbolo de todos los ámbitos."""
        for tabla in self._tablas.values():
            yield from tabla.values()

    # ── reporte final ─────────────────────────────────────────
    def reporte(self):
        SEP  = "=" * 64
        SEP2 = "-" * 64

        print(f"\n{SEP}")
        print("  REPORTE SEMANTICO COMPLETO")
        print(SEP)

        # 1. Tabla de símbolos por ámbito
        print("\n  [ TABLA DE SIMBOLOS ]")
        for ambito_nombre, tabla in self._tablas.items():
            if not tabla:
                continue
            alcance = "GLOBAL" if ambito_nombre == 'global' else f"LOCAL ({ambito_nombre})"
            print(f"\n  Ambito: {alcance}")
            print(f"  {'Variable':<15} {'Tipo':<10} {'Inicializada':<14} {'Valor final':<15} Linea decl.")
            print(f"  {SEP2}")
            for sim in tabla.values():
                init  = "si" if sim.inicializada else "no"
                valor = str(sim.valor_actual) if sim.valor_actual is not None else "---"
                print(f"  {sim.nombre:<15} {sim.tipo:<10} {init:<14} {valor:<15} {sim.linea_decl}")

        # 2. Traza de asignaciones
        print(f"\n  [ TRAZA DE ASIGNACIONES ]")
        if self.traza:
            print(f"\n  {'#':<5} {'Linea':<7} {'Variable':<15} {'Tipo':<10} {'Ambito':<15} Valor asignado")
            print(f"  {SEP2}")
            for i, reg in enumerate(self.traza, 1):
                valor = str(reg['valor']) if reg['valor'] is not None else "(expresion)"
                print(f"  {i:<5} {reg['linea']:<7} {reg['nombre']:<15} {reg['tipo']:<10} {reg['ambito']:<15} {valor}")
        else:
            print("\n  (sin asignaciones registradas)")

        # 3. Resumen de valores finales
        print(f"\n  [ RESUMEN FINAL DE VARIABLES ]")
        print(f"\n  {'Variable':<15} {'Ambito':<15} {'Tipo':<10} Ultimo valor")
        print(f"  {SEP2}")
        for sim in self.todos_los_simbolos():
            valor = str(sim.valor_actual) if sim.valor_actual is not None else "sin asignar"
            print(f"  {sim.nombre:<15} {sim.ambito:<15} {sim.tipo:<10} {valor}")

        # 4. Advertencias
        if self.advertencias:
            print(f"\n  [ ADVERTENCIAS ({len(self.advertencias)}) ]")
            for linea, msg in sorted(self.advertencias):
                print(f"  ! Linea {linea}: {msg}")

        # 5. Errores semánticos
        if self.errores:
            print(f"\n  [ ERRORES SEMANTICOS ({len(self.errores)}) ]")
            for linea, msg in sorted(self.errores):
                print(f"  X Linea {linea}: {msg}")
        else:
            print("\n  OK: Sin errores semanticos.")

        print(f"\n{SEP}\n")


# ══════════════════════════════════════════════════════════════
#  INSTANCIA GLOBAL DE LA TABLA
# ══════════════════════════════════════════════════════════════
tabla = TablaSimbolos()


# ══════════════════════════════════════════════════════════════
#  FUNCIONES AUXILIARES
# ══════════════════════════════════════════════════════════════

def _lineno(p, n):
    try:
        ln = p.lineno(n)
        return ln if ln else 0
    except Exception:
        return 0

def _t(x):
    """Extrae el tipo de (tipo, valor) o devuelve x si ya es string."""
    return x[0] if isinstance(x, tuple) else (x if x else 'unknown')

def _v(x):
    """Extrae el valor de (tipo, valor) o None."""
    return x[1] if isinstance(x, tuple) else None

def _tipo_operacion(t1, t2, op, linea):
    numericos = {'integer', 'real', 'unknown'}
    if t1 == 'unknown' or t2 == 'unknown':
        return 'unknown'
    if t1 in numericos and t2 in numericos:
        return 'real' if ('real' in (t1, t2)) else 'integer'
    tabla._error(linea, f"Operacion '{op}' no valida entre tipos '{t1}' y '{t2}'")
    return 'unknown'

def _tipo_condicion(t1, t2, op, linea):
    if t1 == 'unknown' or t2 == 'unknown':
        return 'boolean'
    numericos = {'integer', 'real'}
    if t1 in numericos and t2 in numericos:
        return 'boolean'
    if t1 == t2:
        return 'boolean'
    tabla._error(linea, f"Comparacion '{op}' entre tipos incompatibles: '{t1}' y '{t2}'")
    return 'boolean'

def _operar(v1, v2, op):
    """Evalúa la operación si ambos valores literales son conocidos."""
    if v1 is None or v2 is None:
        return None
    try:
        if op == '+': return v1 + v2
        if op == '-': return v1 - v2
        if op == '*': return v1 * v2
        if op == '/': return v1 / v2 if v2 != 0 else None
    except Exception:
        return None


# ══════════════════════════════════════════════════════════════
#  GRAMÁTICA CON ACCIONES SEMÁNTICAS
# ══════════════════════════════════════════════════════════════

# ── PROGRAMA ─────────────────────────────────────────────────
def p_program(p):
    'program : PROGRAM ID SEMICOLON declarations compound_statement DOT'
    print("Programa sintacticamente correcto!")
    tabla.reporte()

# ── DECLARACIONES ─────────────────────────────────────────────
def p_declarations_1(p):
    'declarations : VAR var_decl_list'

def p_declarations_2(p):
    'declarations : empty'

def p_var_decl_list_1(p):
    'var_decl_list : var_decl_list var_decl'

def p_var_decl_list_2(p):
    'var_decl_list : var_decl'

def p_var_decl(p):
    'var_decl : id_list COLON ID SEMICOLON'
    for (nombre, linea) in p[1]:
        tabla.declarar(nombre, p[3], linea)

def p_id_list_1(p):
    'id_list : id_list COMMA ID'
    p[0] = p[1] + [(p[3], _lineno(p, 3))]

def p_id_list_2(p):
    'id_list : ID'
    p[0] = [(p[1], _lineno(p, 1))]

# ── FUNCIONES ────────────────────────────────────────────────
def p_declarations_func(p):
    'declarations : subprogram_decl_list'

def p_subprogram_decl_list_1(p):
    'subprogram_decl_list : subprogram_decl_list subprogram_decl'

def p_subprogram_decl_list_2(p):
    'subprogram_decl_list : subprogram_decl'

def p_subprogram_decl_1(p):
    'subprogram_decl : FUNCTION ID LPAREN param_list RPAREN COLON ID SEMICOLON local_declarations compound_statement SEMICOLON'
    tabla.salir_ambito()

def p_subprogram_decl_2(p):
    'subprogram_decl : PROCEDURE ID LPAREN param_list RPAREN SEMICOLON local_declarations compound_statement SEMICOLON'
    tabla.salir_ambito()

def p_subprogram_open_1(p):
    'subprogram_open : FUNCTION ID'
    tabla.entrar_ambito(p[2])
    p[0] = p[2]

def p_subprogram_open_2(p):
    'subprogram_open : PROCEDURE ID'
    tabla.entrar_ambito(p[2])
    p[0] = p[2]

def p_param_list_1(p):
    'param_list : param_list SEMICOLON param'

def p_param_list_2(p):
    'param_list : param'

def p_param_list_3(p):
    'param_list : empty'

def p_param(p):
    'param : id_list COLON ID'
    for (nombre, linea) in p[1]:
        tabla.declarar(nombre, p[3], linea)
        sim = tabla._buscar(nombre, linea)
        if sim:
            sim.inicializada = True   # los parámetros vienen inicializados

def p_local_declarations_1(p):
    'local_declarations : VAR var_decl_list'

def p_local_declarations_2(p):
    'local_declarations : empty'

# ── BLOQUE BEGIN END ──────────────────────────────────────────
def p_compound_statement(p):
    'compound_statement : BEGIN statement_list END'

def p_statement_list_1(p):
    'statement_list : statement_list SEMICOLON statement'

def p_statement_list_2(p):
    'statement_list : statement'

# ── SENTENCIAS ────────────────────────────────────────────────
def p_statement_1(p):  'statement : assignment'
def p_statement_2(p):  'statement : if_statement'
def p_statement_3(p):  'statement : while_statement'
def p_statement_4(p):  'statement : for_statement'
def p_statement_5(p):  'statement : repeat_statement'
def p_statement_6(p):  'statement : compound_statement'
def p_statement_7(p):  'statement : empty'

# ── ASIGNACIÓN ────────────────────────────────────────────────
def p_assignment(p):
    'assignment : ID ASSIGN expression'
    nombre    = p[1]
    tipo_expr = _t(p[3])
    val_expr  = _v(p[3])
    linea     = _lineno(p, 1)
    tabla.asignar(nombre, tipo_expr, linea, val_expr)

# ── IF ────────────────────────────────────────────────────────
def p_if_statement_1(p):
    'if_statement : IF condition THEN statement'

def p_if_statement_2(p):
    'if_statement : IF condition THEN statement ELSE statement'

# ── WHILE ─────────────────────────────────────────────────────
def p_while_statement(p):
    'while_statement : WHILE condition DO statement'

# ── FOR ───────────────────────────────────────────────────────
def p_for_statement(p):
    'for_statement : FOR assignment TO expression DO statement'
    tipo_to = _t(p[4])
    if tipo_to not in ('integer', 'real', 'unknown'):
        tabla._error(_lineno(p, 1),
            f"El limite del FOR debe ser numerico, se encontro '{tipo_to}'")

# ── REPEAT UNTIL ──────────────────────────────────────────────
def p_repeat_statement(p):
    'repeat_statement : REPEAT statement_list UNTIL condition'

# ── CONDICIONES ───────────────────────────────────────────────
def p_condition_1(p):
    'condition : expression LESS expression'
    p[0] = (_tipo_condicion(_t(p[1]), _t(p[3]), '<',  _lineno(p, 2)), None)

def p_condition_2(p):
    'condition : expression GREATER expression'
    p[0] = (_tipo_condicion(_t(p[1]), _t(p[3]), '>',  _lineno(p, 2)), None)

def p_condition_3(p):
    'condition : expression EQUAL expression'
    p[0] = (_tipo_condicion(_t(p[1]), _t(p[3]), '=',  _lineno(p, 2)), None)

def p_condition_4(p):
    'condition : expression LESSEQUAL expression'
    p[0] = (_tipo_condicion(_t(p[1]), _t(p[3]), '<=', _lineno(p, 2)), None)

def p_condition_5(p):
    'condition : expression GREATEREQUAL expression'
    p[0] = (_tipo_condicion(_t(p[1]), _t(p[3]), '>=', _lineno(p, 2)), None)

def p_condition_6(p):
    'condition : expression DISTINT expression'
    p[0] = (_tipo_condicion(_t(p[1]), _t(p[3]), '<>', _lineno(p, 2)), None)

# ── EXPRESIONES ───────────────────────────────────────────────
def p_expression_1(p):
    'expression : expression PLUS term'
    t = _tipo_operacion(_t(p[1]), _t(p[3]), '+', _lineno(p, 2))
    p[0] = (t, _operar(_v(p[1]), _v(p[3]), '+'))

def p_expression_2(p):
    'expression : expression MINUS term'
    t = _tipo_operacion(_t(p[1]), _t(p[3]), '-', _lineno(p, 2))
    p[0] = (t, _operar(_v(p[1]), _v(p[3]), '-'))

def p_expression_3(p):
    'expression : term'
    p[0] = p[1]

def p_term_1(p):
    'term : term TIMES factor'
    t = _tipo_operacion(_t(p[1]), _t(p[3]), '*', _lineno(p, 2))
    p[0] = (t, _operar(_v(p[1]), _v(p[3]), '*'))

def p_term_2(p):
    'term : term DIVIDE factor'
    t = _tipo_operacion(_t(p[1]), _t(p[3]), '/', _lineno(p, 2))
    v = _operar(_v(p[1]), _v(p[3]), '/')
    p[0] = ('real' if t != 'unknown' else 'unknown', v)

def p_term_3(p):
    'term : factor'
    p[0] = p[1]

def p_factor_1(p):
    'factor : NUMBER'
    tipo = 'real' if isinstance(p[1], float) else 'integer'
    p[0] = (tipo, p[1])

def p_factor_2(p):
    'factor : ID'
    linea = _lineno(p, 1)
    tipo  = tabla.usar(p[1], linea)
    sim   = tabla._buscar(p[1], linea)
    valor = sim.valor_actual if sim else None
    p[0] = (tipo, valor)

def p_factor_3(p):
    'factor : LPAREN expression RPAREN'
    p[0] = p[2]

# ── VACÍO ─────────────────────────────────────────────────────
def p_empty(p):
    'empty :'
    p[0] = ('unknown', None)

# ── ERROR ─────────────────────────────────────────────────────
def p_error(p):
    if VERBOSE:
        if p:
            print(f"Error sintactico en linea {p.lineno}: token inesperado '{p.value}'")
            parser.errok()
        else:
            print("Error sintactico al final del archivo")
    else:
        raise Exception("syntax error")


# ══════════════════════════════════════════════════════════════
#  CONSTRUCCIÓN DEL PARSER SEMÁNTICO
# ══════════════════════════════════════════════════════════════
parser = yacc.yacc()


# ══════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    if len(sys.argv) > 1:
        fin = sys.argv[1]
    else:
        fin = 'Prueba2.c'

    f = open(fin, 'r')
    data = f.read()

    # Reiniciar tabla para cada ejecución
    tabla = TablaSimbolos()

    parser.parse(data, lexer=MiniPascalLexico.lexer.clone())