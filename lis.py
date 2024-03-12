import math
import operator as op
from typing import Optional

# TODO: Implement additional features from http://norvig.com/lispy2.html
def tokenize(chars: str) -> list:
    "Convert a string into a list of tokens."
    return chars.replace("(", " ( ").replace(")", " ) ").split()


def parse(program: str) -> str | int | float | list:
    "Read a Scheme expression from a string."
    return read_from_tokens(tokenize(program))


def read_from_tokens(tokens: list) -> str | int | float | list:
    "Read expression from a list of tokens"
    if len(tokens) == 0:
        raise SyntaxError("Unexpected end of file")
    token = tokens.pop(0)
    match token:
        case "(":
            L = []
            while tokens[0] != ")":
                L.append(read_from_tokens(tokens))
            tokens.pop(0)  # this has to be ")" because we've exited the while loop
            return L
        case ")":
            raise SyntaxError("Invalid parenthesis closure")
        case _:
            return atom(token)


def atom(token: str) -> str | int | float:
    "Convert numbers to numbers, all other tokens to symbols"
    if (
        token.lstrip("-")
        .replace(".", "", 1)
        .replace("e-", "", 1)
        .replace("e", "", 1)
        .isdigit()
    ):
        if int(token) == float(token):
            return int(token)
        else:
            return float(token)
    else:
        return token


class Env(dict):
    "An environment: a dict of {'var': val} pairs, with an optional out environment"

    def __init__(self, params=(), args=(), outer: Optional["Env"] = None):
        self.update(zip(params, args))
        self.outer = outer

    def find(self, var) -> "Env":
        "Find the innermost Env where var appears"
        if var in self:
            return self
        elif not self.outer:
            raise ValueError(f"{var} not in environment")
        else:
            return self.outer.find(var)
        
class Procedure(object):
    "A user defined Scheme procedure"
    def __init__(self, params, body, env):
        self.params, self.body, self.env = params, body, env
    def __call__(self, *args):
        return eval(self.body, Env(self.params, args, outer=self.env))
    
def standard_env() -> Env:
    "An environment with some Scheme standard procedures."
    env = Env()
    env.update(vars(math)) # sin, cos, sqrt, pi, ...
    env.update({
        '+':       op.add,
        '-':       op.sub,
        '*':       op.mul, 
        '/':       op.truediv, 
        '>':       op.gt,
        '<':       op.lt,
        '>=':      op.ge,
        '<=':      op.le,
        '=':       op.eq, 
        'abs':     abs,
        'append':  op.add,  
        'apply':   lambda proc, args: proc(*args),
        'begin':   lambda *x: x[-1],
        'car':     lambda x: x[0],
        'cdr':     lambda x: x[1:], 
        'cons':    lambda x,y: [x] + y,
        'eq?':     op.is_, 
        'expt':    pow,
        'equal?':  op.eq, 
        'length':  len, 
        'list':    lambda *x: list(x), 
        'list?':   lambda x: isinstance(x, list), 
        'map':     map,
        'max':     max,
        'min':     min,
        'not':     op.not_,
        'null?':   lambda x: x == [], 
        'number?': lambda x: isinstance(x, float | int),  
		'print':   print,
        'procedure?': callable,
        'round':   round,
        'symbol?': lambda x: isinstance(x, str),
    })
    return env

def eval(x, env: Env = standard_env()):
    if isinstance(x, str):
        return env.find(x)[x]
    elif not isinstance(x, list):
        return x
    op, *args = x  # pull out operator as first token
    if op == 'quote':
        return args[0]
    elif op == 'if':
        (test, consequence, alternative) = args
        expression = (consequence if eval(test, env) else alternative)
        return eval(expression, env)
    elif op == "define":
        (symbol, expression) = args
        env[symbol] = eval(expression, env)
    elif op == "set!":
        (symbol, expression) = args
        env.find(symbol)[symbol] = eval(expression, env)
    elif op == 'lambda':
        (params, body) = args
        return Procedure(params, body, env)
    else:
        proc = eval(op, env)
        vals = [eval(arg, env) for arg in args]
        return proc(*vals)
    
def schemestr(expression) -> str:
    "Convert Python Object to Scheme-readable string"
    if isinstance(expression, list):
        return '(' + ' ' + str(list(map(schemestr, expression))) + ')'
    elif isinstance(expression, map):
        return '(' + ' '.join(map(schemestr, list(expression))) + ')'
    else:
        return str(expression)
    
def repl(prompt: str = "lis.py>>>"):
    "Read, Evaluate, Print Loop"
    while True:
        try:
            val = eval(parse(input(prompt)))
            if val is not None:
                print(schemestr(val))
        except Exception as e:
            print(f"Invalid Input: {e}")

if __name__ == "__main__":
    # program = "(begin (define r 10) (* pi (* r r)))"

    # print(parse(program))

    repl()
