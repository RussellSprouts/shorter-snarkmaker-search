
"""
segments ::= segment (','? segment)*
segment ::=
  | wait
  | expr mod_clause?
  | identifier let_args?
min_follow ::= '(' [0-9]+ ')'
number ::= -?[0-9]+
wait ::= ('wait'|'w') expr
advance_debris ::= 'advance_debris' expr
swim ::= 'swim' expr
expr ::= times_expr ([+-] times_expr)*
times_expr ::= atom (([*/]|mod) atom)*
identifier ::= [a-zA-Z_][a-zA-Z0-9_]*
variable ::= '$'[a-zA-Z0-9_]*
mod_clause ::= '(' 'mod' [0-9]+ ')'
atom ::=
  | '(' expr ')'
  | number
  | variable
comment ::= '#' .* '\n'
let_clause ::= 'let' identifier let_args? '=' segments 'in'
let_variable_clause ::= 'let' variable '=' expr 'in'
let_args ::= '(' (let_arg (',' let_arg)*)? ')'
let_arg ::= l-?[0-9]+ | d-?[0-9]+ | 'l' '(' expr ')' | 'd' '(' expr ')'

"""

from dataclasses import dataclass
import re
import sys
from collections import ChainMap, namedtuple
import math

token_types = {
    'let': re.compile(r'let\b'),
    'in': re.compile(r'in\b'),
    'equals': re.compile(r'='),
    'whitespace': re.compile(r'\s+'),
    'comment': re.compile(r'#.*\n'),
    'minimum_follow': re.compile(r'\(\s*([0-9]+)\s*\)'),
    'mod_clause': re.compile(r'\(\s*mod\s+([0-9]+)\s*\)'),
    'set': re.compile(r'set\b'),
    'wait': re.compile(r'(wait|w)\b'),
    'advance_debris': re.compile(r'(advance_debris)\b'),
    'swim': re.compile(r'(swim)\b'),
    'mode': re.compile(r'mode\s+(p120|sc)'),
    'times_operator': re.compile(r'[*/]|mod'),
    'lane': re.compile(r'l(-?[0-9]+)\b'),
    'depth': re.compile(r'd(-?[0-9]+)\b'),
    'lane_particle': re.compile(r'l\b'),
    'depth_particle': re.compile(r'd\b'),
    'identifier': re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*\b'),
    'variable': re.compile(r'\$[a-zA-Z0-9_]*\b'),
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
                if name not in ('whitespace', 'comment'):
                    tokens.append(Token(i, name, m[0], m))
                i += len(m[0])
                break
        else:
            raise Exception(f"Unexpected token starting at '{input[i:i+10]}...'")

    return tokens

@dataclass
class Segment:
    pass

@dataclass
class DelaySegment(Segment):
    delay: Expr
    mod: int

@dataclass
class MinimumSegment(Segment):
    minimum: Expr

@dataclass
class WaitSegment(Segment):
    wait: Expr

@dataclass
class SetSegment(Segment):
    set: Expr
    mod: int = None
    depth: Expr = None

@dataclass
class ModeSegment(Segment):
    mode: str

@dataclass
class AdvanceDebrisSegment(Segment):
    advance_debris: Expr

@dataclass
class SwimSegment(Segment):
    swim: Expr

@dataclass
class MacroCallSegment(Segment):
    name: str
    lane: Expr|None
    depth: Expr|None

@dataclass
class LetMacroSegment(Segment):
    name: str
    lane: Expr|None
    depth: Expr|None
    body: list[Segment]
    scope: list[Segment]

@dataclass
class EvaluatedMacro:
    name: str
    lane: int|None
    depth: int|None
    body: list[Segment]
    scope: ChainMap

@dataclass
class LetVariableSegment(Segment):
    name: str
    value: Expr
    scope: list[Segment]

@dataclass
class Expr:
    value: int = None
    op: str = None
    a: Expr = None
    b: Expr = None
    variable: str = None

    def __repr__(self):
        if self.value:
            return repr(self.value)
        if self.variable:
            return self.variable
        return f'({self.a} {self.op} {self.b})'
    
    def eval(self, scope, state):
        if self.value is not None:
            return self.value
        elif self.variable is not None:
            return scope[self.variable](state)
        a = self.a.eval(scope, state)
        b = self.b.eval(scope, state)

        if self.op == '+':
            return a + b
        elif self.op == '-':
            return a - b
        elif self.op == '*':
            return a * b
        elif self.op == '/':
            return a // b
        elif self.op == 'mod':
            return a % b

def parse_ast(input):
    tokens = tokenize(input)
    def next(n):
        r = tokens[0:n]
        del tokens[0:n]
        return r

    def syntax_error(token, message):
        raise SyntaxError(f'SyntaxError at {token.text} (column {token.i}):\n{message}')

    def parse_atom():
        match next(1):
            case (Token(type='lparen'),):
                val = parse_expression()
                (rparen,) = next(1)
                if rparen.type != 'rparen':
                    syntax_error(tokens[0], 'Expected end paren')
                return val
            case (Token(type='number', text=text),):
                return Expr(value=int(text))
            case (Token(type='variable', text=text),):
                return Expr(variable=text)

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
                op=op_tok.text,
                a=val,
                b=parse_times_expression()
            )
        return val

    def parse_let_args():
        lane = None
        depth = None
        while tokens and tokens[0].type != 'rparen':
            match(next(1)):
                case (Token(type='depth', match=m),):
                    depth = Expr(value = int(m[1]))
                case (Token(type='lane', match=m),):
                    lane = Expr(value = int(m[1]))
                case (Token(type='depth_particle'),):
                    if tokens[0].type != 'lparen':
                        syntax_error(tokens[0], 'Expected a depth expression d(...)')
                    depth = parse_expression()
                case (Token(type='lane_particle'),):
                    if tokens[0].type != 'lparen':
                        syntax_error(tokens[0], 'Expected a lane expression l(...)')
                    depth = parse_expression()
                case a:
                    syntax_error(a[0], 'Expected a depth or lane indicator, like "d-1", "l12", or "d(5*5)"')
            if tokens[0].type == 'comma':
                next(1)
        (rparen,) = next(1)
        if rparen.type != 'rparen':
            syntax_error(tokens[0], 'Expected end paren')

        return lane, depth

    def parse_let():
        name = next(1)
        match name:
            case (Token(type='identifier', text=text),):
                lane = None
                depth = None
                if tokens[0].type == 'lparen':
                    _ = next(1)
                    lane, depth = parse_let_args()

                (equals,) = next(1)
                if equals.type != 'equals':
                    syntax_error(equals, "Expected equals after let, got '{name.text}' '{equals.text}'")
 
                segments = parse_segments('in')
                (in_tok,) = next(1)
                if in_tok.type != 'in':
                    syntax_error(in_tok, f'Expected `in` after let')
                return LetMacroSegment(
                    name=text,
                    lane=lane,
                    depth=depth,
                    body=segments,
                    scope=parse_segments()
                )
            case (Token(type='variable', text=text),):
                (equals,) = next(1)
                if equals.type != 'equals':
                    syntax_error(equals, "Expected equals after let name, got '{name.text}' '{equals.text}'")
 
                expr = parse_expression()
                (in_tok,) = next(1)
                if in_tok.type != 'in':
                    syntax_error(in_tok, f'Expected `in` after let')
                return LetVariableSegment(name=text, value=expr, scope=parse_segments())
            case _:
                raise SyntaxError(f'Expected macro/variable name after let')

    def parse_macro_call(name):
        match tokens[0:2]:
            case (Token(type='lparen'), Token(type='depth')) | (Token(type='lparen'), Token(type='depth_particle')) | (Token(type='lparen'), Token(type='lane')) | (Token(type='lparen'), Token(type='lane_particle')):
                next(1)
                lane, depth = parse_let_args()
                return MacroCallSegment(name, lane, depth)
        return MacroCallSegment(name)

    def parse_segment():
        match next(1):
            case (Token(type='let'),):
                return parse_let()
            case (Token(type='wait'),):
                expr = parse_expression()
                return WaitSegment(wait=expr)
            case (Token(type='identifier', text=text),):
                return parse_macro_call(text)
            case (Token(type='minimum_follow', match=m),):
                return MinimumSegment(minimum=int(m[1]))
            case (Token(type='advance_debris'),):
                expr = parse_expression()
                return AdvanceDebrisSegment(advance_debris=expr)
            case (Token(type='swim'),):
                expr = parse_expression()
                return SwimSegment(swim=expr)
            case (Token(type='set'),):
                expr = parse_expression()
                mod = next(1)[0]
                if mod.type != 'mod_clause':
                    syntax_error(mod, f'Expected mod clause')
                return SetSegment(set=expr,mod=int(mod.match[1]))
            case (Token(type='mode', match=m),):
                return ModeSegment(mode=m[1])
            case _ as t:
                tokens.insert(0, t[0])
                expr = parse_expression()
                mod = None
                if tokens and tokens[0].type == 'mod_clause':
                    mod_tok = next(1)[0]
                    mod = int(mod_tok.match[1])
                return DelaySegment(delay=expr,mod=mod)

    def parse_segments(until_type = None):
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
                case (Token(type=a),) if a == until_type:
                    return segments
            if tokens:
                s = parse_segment()
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
    advance_debris: int

def parse_p120_recipe(input, macros):

    State = namedtuple('State', ['mode', 'start_mode', 'advance_debris', 'set_start_mode', 'after_minimum_follow', 'i', 'delays', 'next_delay', 'set_mod', 'next_glider'])
    SwimResult = namedtuple('SwimResult', ['first_possible_time', 'target', 'next_glider', 'full_state'])

    state = State(
        mode='p120',
        start_mode='p120',
        advance_debris=0,
        set_start_mode=False,
        after_minimum_follow=False,
        i=0,
        delays=(),
        next_delay=0,
        set_mod=120,
        next_glider=0
    )
    global_scope = ChainMap({
        '$currentTime': lambda state: state.i
    })

    ast = parse_ast(input)
    print(ast)

    def evaluate(segment, state, scope):
        match segment:
            case ModeSegment(mode=m):
                state = state._replace(mode=m)
                mode = m
            case SetSegment(set, mod):
                state = state._replace(
                    set_mod=mod,
                    i=set.eval(scope, state) + state.next_delay
                )
                set_mod = mod
            case MinimumSegment(minimum=minimum):
                state = state._replace(
                    after_minimum_follow=True,
                    next_delay=state.next_delay + minimum
                )
            case DelaySegment(delay, mod):
                if state.mode == 'p120' and state.after_minimum_follow and mod is None:
                    mod = 8
                elif state.mode == 'sc' and state.after_minimum_follow and mod is None:
                    mod = 2
                state = state._replace(after_minimum_follow=False)
                if mod is not None:
                    if mod > state.set_mod:
                        raise ValueError(f'Trying to send a glider mod {mod}, but there was no "set ... (mod {mod})"')
                    parity = (state.i + state.next_delay) % mod
                    state = state._replace(
                        next_delay=state.next_delay + (delay.eval(scope, state) - parity) % mod
                    )
                else:
                    state = state._replace(
                        next_delay=state.next_delay + delay.eval(scope, state)
                    )
                if not state.set_start_mode:
                    state = state._replace(
                        start_mode=state.mode,
                        set_start_mode=True
                    )

                state = state._replace(
                    delays=state.delays + (state.next_delay,),
                    i=state.i + state.next_delay,
                    next_delay=0
                )
            case WaitSegment(wait):
                state = state._replace(
                    next_delay=state.next_delay + wait.eval(scope, state)
                )
            case AdvanceDebrisSegment(advance_debris=ad):
                state = state._replace(
                    advance_debris=ad.eval(scope, state)
                )
            case SwimSegment(swim):
                n = swim.eval(scope, state)
                state = state._replace(
                    i=state.i + (state.set_mod * n) % 8,
                    next_glider=state.next_glider + state.set_mod * n
                )
            case LetMacroSegment(name, lane, depth, body, scope=visible_scope):
                qualified_name = name
                if lane:
                    lane = lane.eval(scope, state)
                    qualified_name = f'{name}({lane})'
                if depth:
                    depth = depth.eval(scope, state)
                new_scope = scope.new_child({
                    qualified_name: EvaluatedMacro(
                        name=name,
                        lane=lane,
                        depth=depth,
                        body=body,
                        scope=scope
                    )
                })
                for s in visible_scope:
                    state = evaluate(s, state, new_scope)
            case LetVariableSegment(name, value, scope=visible_scope):
                new_scope = scope.new_child({
                    name: lambda _: value.eval(scope, state)
                })
                for s in visible_scope:
                    state = evaluate(s, state, new_scope)
            case MacroCallSegment(name, lane, depth):
                qualified_name = name
                if lane:
                    lane = lane.eval(scope, state)
                    qualified_name = f'{name}({lane})'
                if depth:
                    depth = depth.eval(scope, state)
                name = f'{name}({lane})'
                if qualified_name not in scope:
                    raise ValueError('Unknown macro {qualified_name}')
                macro = scope[qualified_name]

                if depth is not None:
                    # requesting an output at a specific depth,
                    # so we automatically swim or delay to match it.
                    if macro.depth is None:
                        macro.depth = 0
                    first_possible_time = state.i + state.next_delay
                    first_glider = None
                    for first_glider in macro.body:
                        if isinstance(first_glider, DelaySegment):
                            break
                    else:
                        raise ValueError(f"Macro {qualified_name} requested at depth {depth}, but macro has no outputs.")
                    recipe_parity = first_glider.delay.eval(macro.scope, state)
                    target = state.next_glider + (depth - macro.depth) * 4 + recipe_parity
                    offset = (target - recipe_parity) % 8

                    while target < first_possible_time:
                        swim_results = []
                        for macro_name, definition in scope.items():
                            if not macro_name.startswith('swim_'):
                                continue
                            new_state = evaluate(MacroCallSegment(macro_name, None, None), state, scope)
                            swim_results.append(SwimResult(
                                first_possible_time=new_state.i + new_state.next_delay,
                                target=target+(new_state.next_glider - state.next_glider),
                                next_glider=new_state.next_glider,
                                full_state=new_state
                            ))
                        if not swim_results:
                            raise ValueError("Requested macro {qualified_name}, but there are no swim_ recipes defined to get to that depth.")
                        
                        solutions = list(filter(lambda r: r.target > r.first_possible_time, swim_results))
                        if solutions:
                            solutions.sort(key=lambda r: r.first_possible_time)
                            best = solutions[0]
                        else:
                            # otherwise take the one that brings us closest.
                            swim_results.sort(key=lambda r: r.first_possible_time - r.target, reverse=True)
                            best = swim_results[0]

                        first_possible_time = best.first_possible_time
                        target = best.target
                        offset = (target - recipe_parity) % 8
                        state = best.full_state

                    wait = ((target - first_possible_time) // 8) * 8
                    if wait != 0 and math.isfinite(wait):
                        state = state._replace(next_delay=state.next_delay + wait)

                for s in macro.body:
                    state = evaluate(s, state, macro.scope)

        return state
    for s in ast:
        state = evaluate(s, state, global_scope)

    return Parse(delays=state.delays, start_mode=state.start_mode, advance_debris=state.advance_debris)

if __name__ == '__main__':
    print(parse_p120_recipe(sys.argv[1], {}))