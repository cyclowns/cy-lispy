# norvig.com/lispy.html

import math
import operator as op

# typedefs for scheme objects
Symbol = str
Number = (int, float)
Atom   = (Symbol, Number)
List   = list
Exp    = (Atom, List)
Env    = dict # environment, {variable: value} mapping

# general interpretation process is like this:
# program source -> parse() -> AST -> eval() -> program output

# parsing is: lexical analysis (sequence of tokens, simple descriptive analysis)
# -> syntactic analysis (normative, tokens -> AST)

# lisp-y tokens are parens, symbols, and numbers
# first thing up is the lexer/tokenizer, which just uses str.split() to get tokens
# separated by spaces

def tokenize(chars: str) -> list:
    "Converts a string of characters -> a list of a tokens"
    return chars.replace('(', ' ( ').replace(')', ' ) ').split()

# now for the syntactic analysis
# very basic (reminds me of b****fuck interpretation): start at any ( and pop off all tokens til you reach a )
# if an expression starts with ), syntax error
# iterates over all tokens starting at a (, atomizing them if they're a symbol/number and
# recursing if its another (

def parse(program: str) -> Exp:
    return read_from_tokens(tokenize(program))

def read_from_tokens(tokens: list) -> Exp:
    "Read an expression from a sequence of tokens"
    if len(tokens) == 0:
        raise SyntaxError('EOF: empty token sequence')
    token = tokens.pop(0)
    if token == '(':
        expr = []
        while tokens[0] != ')':
            expr.append(read_from_tokens(tokens))
        tokens.pop(0) # pop off )
        return expr
    elif token == ')':
        raise SyntaxError('started token sequence with )')
    else:
        return atom(token)

def atom(token: str) -> Atom:
    "Numbers -> numbers, all other tokens -> symbols"
    try: return int(token)
    except ValueError:
        try: return float(token)
        except ValueError:
            return Symbol(token)

# we need an idea of variables and how to interpret/map keywords, so heres our environment

def standard_env() -> Env:
    env = Env()
    env.update(vars(math)) # basic mathematical functions
    env.update({
        '+': op.add, '-': op.sub, '*': op.mul, '/': op.truediv,
        'v': op.gt, '<': op.lt, '>=': op.ge, '<=': op.le, '=': op.eq,
        'abs':     abs,
        'append':  op.add,
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1], # TODO figure out what this even means
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1],
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_,
        'expt':    pow,
        'equal?':  op.eq,
        'length':  len,
        'list':    lambda *x: List(x),
        'list?':   lambda x: isinstance(x, List),
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [],
        'number?': lambda x: isinstance(x, Number),
        'print':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, Symbol),
    })
    return env

global_env = standard_env()

# time for actual evaluation of an AST
# little reference of lisp-y syntax:
# var refs:       Symbol, variables essentially
# const literals: Number
# conditional:    (if test conseq alt), ternary statements
# definition:     (define symbol exp), define vars
# procedure call: (proc arg..) call procedure with args

def eval(x: Exp, env=global_env) -> Exp:
    "Evaluate an expression in an environment."
    if isinstance(x, Symbol): # var refs
        return env[x]
    elif isinstance(x, Number): # const literals
        return x
    elif x[0] == 'if': # conditionals
        (_, test, conseq, alt) = x
        exp = (conseq if eval(test, env) else alt)
        return eval(exp, env) # TODO figure out what all of this means
    elif x[0] == 'define': # definition
        (_, symbol, exp) = x
        env[symbol] = eval(exp, env)
    else: # proc call
        proc = eval(x[0], env)
        args = [eval(arg, env) for arg in x[1:]]
        return proc(*args)

# writing eval(parse(..)) is annoying, so REPL (read/eval/print loop)

def repl(prompt='cy-lispy > '):
    "A prompt REPL."
    while True:
        val = eval(parse(input(prompt)))
        if val is not None:
            print(schemestr(val))

def schemestr(exp):
    "Converts python obj into a readable lisp-like (scheme syntax) string"
    if isinstance(exp, List):
        return '(' + ' '.join(map(schemestr, exp)) + ')'
    else:
        return str(exp)
