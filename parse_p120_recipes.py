
"""
segments ::= segment (','? segment)*
segment ::=
  | wait
  | expr mod_clause?
  | identifier
min_follow ::= '(' [0-9]+ ')'
number ::= [0-9]+
wait ::= ('wait'|'w') expr
expr ::= times_expr ([+-] times_expr)*
times_expr ::= atom (([*/]|mod) atom)*
identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
mod_clause ::= '(' 'mod' [0-9]+ ')'
atom ::=
  | '(' expr ')'
  | number
  | identifier
"""

from dataclasses import dataclass
import re
import sys

token_types = {
    'whitespace': re.compile(r'\s+'),
    'minimum_follow': re.compile(r'\(\s*([0-9]+)\s*\)'),
    'mod_clause': re.compile(r'\(\s*mod\s+([0-9]+)\s*\)'),
    'set': re.compile(r'set\b'),
    'wait': re.compile(r'(wait|w)\b'),
    'mode': re.compile(r'mode (p120|sc)'),
    'times_operator': re.compile(r'[*/]|mod'),
    'identifier': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*\b'),
    'number': re.compile(r'[0-9]+\b'),
    'add_operator': re.compile(r'[+-]'),
    'lparen': re.compile(r'\('),
    'rparen': re.compile(r'\)'),
    'comma': re.compile(r','),
}

@dataclass
class Token:
    i: int
    type: str
    text: str
    match: re.Match

def tokenize(input):
    tokens = []
    i = 0
    while i < len(input):
        for name, regex in token_types.items():
            m = regex.match(input, i)
            if m:
                if name != 'whitespace':
                    tokens.append(Token(i, name, m[0], m))
                i += len(m[0])
                break
        else:
            raise Exception(f"Unexpected token starting at '{input[i:i+10]}...'")

    return tokens

@dataclass
class Segment:
    delay: int = None
    mod: int = None
    minimum: int = None
    wait: int = None
    set: int = None
    mode: str = None

    def __repr__(self):
        r = map(lambda a: f'{a[0]}={a[1]}', filter(
            lambda a: a[1] is not None,
            [
                ('delay', self.delay),
                ('mod', self.mod),
                ('minimum', self.minimum),
                ('wait', self.wait),
                ('set', self.set),
                ('mode', self.mode),
            ]
        ))
        return f'Segment({', '.join(r)})'

@dataclass
class Expr:
    value: int = None
    op: str = None
    a: Expr = None
    b: Expr = None

    def __repr__(self):
        if self.value:
            return repr(self.value)
        return f'({self.a} {self.op} {self.b})'
    
    def eval(self):
        if self.value is not None:
            return self.value
        elif self.op == '+':
            return self.a.eval() + self.b.eval()
        elif self.op == '-':
            return self.a.eval() - self.b.eval()
        elif self.op == '*':
            return self.a.eval() * self.b.eval()
        elif self.op == '/':
            return self.a.eval() / self.b.eval()
        elif self.op == 'mod':
            return self.a.eval() % self.b.eval()

def parse_ast(input, macros):
    tokens = tokenize(input)

    def next(n):
        r = tokens[0:n]
        del tokens[0:n]
        return r

    def syntax_error(token, message):
        raise SyntaxError(f'SyntaxError at {token.text} (column {token.m.pos}):\n{message}')

    def parse_atom():
        match next(1):
            case (Token(type='lparen'),):
                val = parse_expression(False)
                rparen = next(1)
                if rparen.type != 'rparen':
                    syntax_error(tokens[0], 'Expected end paren')
                return val
            case (Token(type='number', text=text),):
                return Expr(value=int(text))

    def parse_times_expression():
        val = parse_atom()
        while tokens and tokens[0].type == 'times_operator':
            op_tok = tokens.pop(0)
            val = Expr(
                op=op_tok.text,
                a=val,
                b=parse_atom()
            )
        return val

    def parse_expression():
        val = parse_times_expression()
        while tokens and tokens[0].type == 'add_operator':
            op_tok = tokens.pop(0)
            val = Expr(
                op=op_tok.text(),
                a=val,
                b=parse_times_expression()
            )
        return val

    def expand_macro(text):
        if text not in macros:
            raise SyntaxError(f'Unknown macro {text}')
        return parse_ast(macros[text], macros)

    def parse_segment():
        match next(1):
            case (Token(type='wait'),):
                expr = parse_expression()
                return Segment(wait=expr)
            case (Token(type='identifier', text=text),):
                return expand_macro(text)
            case (Token(type='minimum_follow', match=m),):
                return Segment(minimum=int(m[1]))
            case (Token(type='set'),):
                expr = parse_expression()
                mod = next(1)[0]
                if mod.type != 'mod_clause':
                    syntax_error(mod, f'Expected mod clause')
                return Segment(set=expr,mod=int(mod.match[1]))
            case (Token(type='mode', match=m),):
                return Segment(mode=m[1])
            case _ as t:
                tokens.insert(0, t[0])
                expr = parse_expression()
                mod = None
                if tokens and tokens[0].type == 'mod_clause':
                    mod_tok = next(1)[0]
                    mod = int(mod_tok.match[1])
                return Segment(delay=expr,mod=mod)

    def parse_segments():
        segments = []
        s = parse_segment()
        match s:
            case Segment():
                segments.append(s)
            case _:
                segments.extend(s)
        while tokens:
            match tokens[0:1]:
                case (Token(type='comma'),):
                    # remove optional commas
                    tokens.pop(0)
            if tokens:
                s = parse_segment()
                print(s)
                match s:
                    case Segment():
                        segments.append(s)
                    case _:
                        segments.extend(s)
        return segments

    return parse_segments()

@dataclass
class Parse:
    delays: list[int]
    start_mode: str

def parse_p120_recipe(input, macros):
    ast = parse_ast(input, macros)
    mode = 'p120'
    start_mode = mode
    set_start_mode = False
    after_minimum_follow = True
    i = 0
    delays = []
    next_delay = 0
    set_mod = 120
    for segment in ast:
        match segment:
            case Segment(mode=m) if m is not None:
                mode = m
            case Segment(set=set, mod=mod) as s if set is not None:
                set_mod = mod
                i = set.eval() + next_delay
            case Segment(minimum=minimum) if minimum is not None:
                after_minimum_follow = True
                next_delay += minimum
            case Segment(delay=delay) if delay is not None:
                if mode == 'p120' and after_minimum_follow and segment.mod is None:
                    segment.mod = 8
                after_minimum_follow = False
                if segment.mod is not None:
                    if segment.mod > set_mod:
                        raise ValueError(f'Trying to send a glider mod {segment.mod}, but there was no "set ... (mod {segment.mod})"')
                    parity = (i + next_delay) % segment.mod
                    next_delay += (segment.delay.eval() - parity) % segment.mod
                else:
                    next_delay += delay.eval()
                delays.append(next_delay)
                if not set_start_mode:
                    start_mode = mode
                    set_start_mode = True
                i += next_delay
                next_delay = 0
            case Segment(wait=wait) if wait is not None:
                next_delay += wait.eval()


    return Parse(delays=delays, start_mode=start_mode)

if __name__ == '__main__':
    print(parse_p120_recipe(sys.argv[1]))