import sqlite3
import sys
import argparse
import re
import itertools
import functools
import pathlib

from arg_parser import range_str_to_list
from components import pattern_components
from font import write_text
from life_history import write_life_history
from lifetree import lt
from gliders import mk_glider, single_channel_stream


argparser = argparse.ArgumentParser(
    prog="oncoming.py", description="Search for glider patterns"
)

class ToolkitDef:
    min_spacing: int
    lane_offset: int
    period: int
    name: str

    def __init__(self, str):
        m = re.match(r'sc(\d+)b(\d+)p(\d+)', str)
        if not m:
            raise ValueError(f'Toolkit {str} is invalid. Expected something like sc90b5p120')
        self.name = m.group(0)
        self.min_spacing = int(m.group(1))
        self.lane_offset = int(m.group(2))
        self.period = int(m.group(3))

argparser.add_argument(
    '--toolkit',
    default='sc90b5p120',
    type=ToolkitDef,
    help="The oncoming gliders to search. Format sc[min spacing]b[lane_offset]p[period]. E.g., sc90b5p120",
)
argparser.add_argument(
    '--n-gun-gliders',
    type=int,
    default=10,
    help="How many gun gliders to simulate"
)
argparser.add_argument(
    '--simulate-gens',
    type=int,
    default=None,
    help="How many generations to simulate"
)
argparser.add_argument(
    '--alternating',
    type=lambda a: sorted((int(a.split(',')[0]), int(a.split(',')[1]))),
    default=None,
    help="Alternating repeat times when using a merge circuit"
)
argparser.add_argument(
    'recipes',
    type=pathlib.Path,
    help="Recipes to process"
)

args = argparser.parse_args()
simulate_gens = args.simulate_gens or args.toolkit.period * args.n_gun_gliders
gun_period = args.toolkit.period
def mk_fake_gun(n):
    fake_gun = sum([mk_glider(0, gun_period*x) for x in range(0, n)], start=lt.pattern(''))
    fake_gun = fake_gun('rot180')(-10 + args.toolkit.lane_offset, -11)
    return fake_gun
fake_gun = mk_fake_gun(args.n_gun_gliders)
expected_incoming_gliders = pattern_components(fake_gun[simulate_gens])

def recipe_stream_to_delays(stream):
    gliders = stream.split(',')
    result = []
    total = 0
    for g in gliders:
        m = re.match(r'^\(\s*(\d+)\s*\)\s*(?:\s*(\d+)\s*\+\s*)?(\d+)$', g.strip())
        if m:
            minimum_follow = int(m.group(1))
            addition = m.group(2)
            if addition:
                minimum_follow += int(addition)
            next_parity = int(m.group(3))
            parity = (total + minimum_follow) % 8
            g = minimum_follow + ((next_parity - parity) % 8)
            total += g
            result.append(g)
        else:
            g = int(g)
            total += g
            result.append(g)
    return result

def find_minimum_follow(r, consumed):
    delays = recipe_stream_to_delays(r)
    total = sum(delays)
    envelope = lt.pattern('5o$5o$5o$5o$5o').centre()
    '''
    expected_incoming_gliders = pattern_components(fake_gun[simulate_gens])
    p = fake_gun + single_channel_stream(delays)
    p = p[simulate_gens]
    escaping_gliders = []
    for c in pattern_components(p):
        for i, e in enumerate(expected_incoming_gliders):
            if c == e:
                escaping_gliders.append(i)
    n_escaping = max(escaping_gliders) + 1 if escaping_gliders else 0
    consumed = args.n_gun_gliders - n_escaping
    '''
    pattern = mk_fake_gun(consumed) + single_channel_stream(delays)
    @functools.lru_cache(maxsize=None)
    def pattern_at_gen(n):
        if n == 0:
            return pattern
        return pattern_at_gen(n-1)[1]
    def valid_spacing(i):
        follow_up_glider = mk_glider(0, total + i)
        glider_envelope = lt.pattern()
        for j in range(0, simulate_gens + i):
            follow_up_glider = follow_up_glider[1]
            glider_envelope += follow_up_glider.convolve(envelope)
            if (pattern_at_gen(j+1) & glider_envelope).nonempty():
                return False
        return True
    lower, upper = args.toolkit.min_spacing, args.toolkit.min_spacing + 1000
    if args.alternating and delays[-1] < args.alternating[1]:
        lower = args.alternating[1]
    if not valid_spacing(upper):
        return
    while lower != upper:
        mid = (lower + upper) // 2
        if valid_spacing(mid):
            upper = mid
        else:
            lower = mid + 1
    return lower

def parse_object(obj):
    m = re.match(r"^'([\w ]+)((?:\([^)]*\))*)'$", obj.strip())
    if not m:
        raise SyntaxError(f"Invalid object: {obj}")
    name = m.group(1)
    info = m.group(2)
    return {
        'name': name,
        'info': info
    }

gun_glider_names = set()
for i in range(0, args.n_gun_gliders):
    gun_glider_names.add(f"g{i}")

def parse_objects(objs):
    results = []
    gun_gliders = set()
    for o in re.split(r"('[^']*')", objs):
        o = o.strip()
        if not o or o == ',':
            continue
        obj = parse_object(o)
        if obj['name'] in gun_glider_names:
            gun_gliders.add(obj['name'])
        else:
            results.append(obj)        
    for i in range(0, args.n_gun_gliders):
        if not f"g{i}" in gun_gliders:
            break
    consumed = args.n_gun_gliders - i
    return {
        'consumed': consumed,
        'objects': results
    }

class Result:
    def __init__(self, rec, min_follow, total_time, consumed, glider):
        self.rec = rec
        self.min_follow = min_follow
        self.total_time = total_time
        self.consumed = consumed
        self.glider = glider

    def __repr__(self):
        return (self.rec +
            f', ({self.min_follow}) {{total: {self.total_time}}} {{consumed: {self.consumed}}}' +
            (' glider' + self.glider))

seen = set()
types = [(i[0]+j[0]+k[0], j[1]+' '+i[1]+' '+k[1]) for j in [('⬀', 'NE'), ('⬃', 'SW')]
                   for i in [('♗', 'black'), ('♝', 'white')]
                   for k in [('⓪', 'even'), ('①', 'odd')]]
recs = dict((i[0], []) for i in types)
with args.recipes.open() as results_file:
    for line in results_file:
        if not line.strip():
            continue
        m = re.match(
            r"""^\((\d+(?:, \d+)*,?)\)\s*\[('[^']*'(?:, '[^']*')*)?\]$""",
            line.strip()
        )
        if not m:
            raise SyntaxError(f"Invalid line: {line}")
        stream = tuple(map(int, filter(bool, m.group(1).split(','))))
        info = parse_objects(m.group(2) or '')
        if len(info['objects']) == 0 or len(info['objects']) == 1 \
                                        and info['objects'][0]['name'] == 'glider' \
                                        and 'd' in info['objects'][0]['info']:
            if len(info['objects']) == 1:
                sig = (len(stream), info['consumed'], str(info['objects']))
                if sig in seen:
                    continue
                seen.add(sig)
                minimum_follow = find_minimum_follow(m.group(1), info['consumed'])
                if not minimum_follow: continue
                total_time = sum(stream[1:]) + minimum_follow
                desc = Result(
                    m.group(1),
                    minimum_follow,
                    total_time,
                    info['consumed'],
                    info['objects'][0]['info'] if info['objects'] else ''
                )
                print(desc)
                recs[info['objects'][0]['info'].split('(')[-1][:-1]].append(desc)

print()
print(args.toolkit.name)
for a, b in types:
    print()
    print(b)
    for i in sorted(recs[a], key=lambda a: (a.total_time, a.consumed)):
        print(i)