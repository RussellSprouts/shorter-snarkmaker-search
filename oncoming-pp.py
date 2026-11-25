import sqlite3
import sys
import argparse
import re
import itertools
import functools
import pathlib
import math
from collections import defaultdict, namedtuple

from arg_parser import range_str_to_list
from components import pattern_components
from font import write_text
from life_history import write_life_history
from lifetree import lt
from gliders import mk_glider, single_channel_stream, rewind_glider, offset_based_on_glider

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
argparser.add_argument(
    "--tandem-delay",
    "--tandem-distance",
    type=int,
    default=0
)
argparser.add_argument(
    "--tandem-offset",
    type=int,
    default=0
)
argparser.add_argument(
    "--echo",
    type=int,
    default=0
)
argparser.add_argument(
    "--process-objects",
    default=False,
    action=argparse.BooleanOptionalAction
)
argparser.add_argument(
    "--debris-combinations",
    type=str,
    default="",
)
argparser.add_argument(
    "--valid-debris-combinations",
    type=str,
    help="Which combinations of debris to check. E.g., '0,a,ab'"
)
argparser.add_argument(
    "--accept-min-follow-distance",
    default=False,
    action=argparse.BooleanOptionalAction
)
argparser.add_argument(
    "--relaxed-glider-envelope",
    default=False,
    action=argparse.BooleanOptionalAction
)
argparser.add_argument(
    "--presort",
    default=False,
    action=argparse.BooleanOptionalAction
)
argparser.add_argument(
    "--accept-all-less-than",
    type=int,
    default=0
)
argparser.add_argument(
    "--include-kickforward-glider",
    default=True,
    action=argparse.BooleanOptionalAction
)

args = argparser.parse_args()
simulate_gens = args.simulate_gens or args.toolkit.period * args.n_gun_gliders
gun_period = args.toolkit.period
def mk_fake_gun(n):
    trailing = n != int(n)
    n = int(n)
    fake_gun = sum(
        [mk_glider(0, gun_period * x) for x in range(0, n - trailing)], start=lt.pattern("")
    )
    fake_gun = fake_gun('rot180')(-10 + args.toolkit.lane_offset, -11)
    if args.tandem_delay or args.tandem_offset:
        shift = math.ceil(args.tandem_delay / 4)
        phase = (4 - (args.tandem_delay % 4)) % 4
        if args.tandem_offset >= 0:
            tandem_gliders = fake_gun(-shift, -shift - args.tandem_offset)[phase]
        else:
            tandem_gliders = fake_gun(-shift + args.tandem_offset, -shift)[phase]

        fake_gun = fake_gun + tandem_gliders
    if trailing:
        fake_gun += mk_glider(0, gun_period * (n - 1))
    return fake_gun

fake_gun = mk_fake_gun(args.n_gun_gliders)
expected_incoming_gliders = pattern_components(fake_gun[simulate_gens])


debris_combinations = []
if args.debris_combinations:
    debris = []
    for i, d in enumerate(args.debris_combinations.split(';')):
        debris.append((offset_based_on_glider(lt.pattern(d)), 'abcdefghijklmnopqrstuvwxyz'[i]))
    for r in range(0, len(debris) + 1):
        for combo in itertools.combinations(debris, r):
            patt = lt.pattern()
            description = ''
            for p, desc in combo:
                patt += p
                description += desc
            if not description:
                description = '0'
            debris_combinations.append((patt, description))

    if args.valid_debris_combinations:
        valid_combos = set(args.valid_debris_combinations.split(','))
        debris_combinations = list(filter(lambda a: a[1] in valid_combos, debris_combinations))



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

def find_glider_timing_inner(r, consumed, debris):
    if args.tandem_offset or args.tandem_delay:
        consumed /= 2
    delays = recipe_stream_to_delays(r)
    pattern = mk_fake_gun(consumed) + single_channel_stream(delays) + debris
    if args.echo:
        pattern += single_channel_stream((delays[0] + args.echo,) + tuple(delays[1:]))
    pattern = pattern[2048]
    components = pattern_components(pattern)
    # remove kickforward glider if present
    components = list(filter(lambda c: c[4] != c(1, 1), components))
    if len(components) != 1:
        return None
    c = components[0]
    # not a glider
    if c[4] == c or c[4].centre() != c.centre(): return None
    # escaping gun glider?
    if c[4] == c(1, 1): return None
    x, y, w, h = c.getrect()
    # spaceship?
    if w != 3 or h != 3: return None
    
    lane = x - y

    rewind = 2 * abs(lane) - 8
    
    for i in range(0, 128):
        new_glider = rewind_glider(c, rewind + i)
        nx, ny, _, _ = new_glider.getrect()
        new_lane = nx - ny
        if new_lane == 0:
            return rewind + i

    return None

def find_glider_timing(r, consumed):
    if debris_combinations:
        for d, _ in debris_combinations:
            if res := find_glider_timing_inner(r, consumed, d):
                return res
        return None
    else:
        return find_glider_timing_inner(r, consumed, lt.pattern())

class BlockingLane(Exception):
    pass

envelope = lt.pattern('b3o$5o$5o$5o$b3o' if args.relaxed_glider_envelope else '5o$5o$5o$5o$5o').centre()

def find_minimum_follow_inner(r, consumed, debris):
    if args.tandem_offset or args.tandem_delay:
        consumed /= 2
    delays = recipe_stream_to_delays(r)
    total = sum(delays)
    pattern = mk_fake_gun(consumed) + single_channel_stream(delays) + debris
    if args.echo:
        pattern += single_channel_stream((delays[0] + args.echo,) + tuple(delays[1:]))
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
        return float('inf')
    while lower != upper:
        mid = (lower + upper) // 2
        if valid_spacing(mid):
            upper = mid
        else:
            lower = mid + 1
    return lower

def find_minimum_follow(r, consumed):
    if debris_combinations and args.accept_min_follow_distance:
        return min(find_minimum_follow_inner(r, consumed, d) for d, _ in debris_combinations)
    elif debris_combinations:
        return max(find_minimum_follow_inner(r, consumed, d) for d, _ in debris_combinations)
    else:
        return find_minimum_follow_inner(r, consumed, lt.pattern())

def parse_object(obj):
    m = re.match(r"^'([\w:, ]+)((?:\([^)]*\))*)'$", obj.strip())
    if not m:
        raise SyntaxError(f"Invalid object: {obj}")
    name = m.group(1)
    info = m.group(2)
    return {
        'name': name,
        'info': info
    }

n_gun_gliders = 2 * args.n_gun_gliders if args.tandem_offset or args.tandem_delay else args.n_gun_gliders

gun_glider_names = set()
for i in range(0, n_gun_gliders):
    gun_glider_names.add(f"g{i}")

def parse_objects(objs):
    results = []
    gun_gliders = set()
    bonus = []
    for o in re.split(r"('[^']*')", objs):
        o = o.strip()
        if not o or o == ',':
            continue
        obj = parse_object(o)
        if obj['name'] in gun_glider_names:
            gun_gliders.add(obj['name'])
        elif not args.include_kickforward_glider and obj['info'] == '(l0)(ph3)(♗⬂①)':
            bonus.append(obj)
        else:
            results.append(obj)        
    for i in range(0, n_gun_gliders):
        if not f"g{i}" in gun_gliders:
            break
    if i != len(gun_gliders):
        return {'objects': [], 'consumed': 0}
    consumed = n_gun_gliders - i
    return {
        'consumed': consumed,
        'objects': results,
        'bonus': bonus
    }

class Result:
    def __init__(self, rec, min_follow, total_time, consumed, glider, object='glider',obj_info=None):
        self.rec = rec
        self.min_follow = min_follow
        self.total_time = total_time
        self.consumed = consumed
        self.glider = glider
        self.object = object
        self.obj_info = obj_info

    def __repr__(self):
        return (self.rec +
            f', ({self.min_follow}) {{total: {self.total_time}}} {{consumed: {self.consumed}}}' +
            (f' {self.object}' + self.glider))

class RecipeStore:
    def __init__(self):
        self.recipes = []
        self.best = float('inf')

    def could_beat(self, min_possible, depth):
        if min_possible < args.accept_all_less_than:
            return True
        for r in self.recipes:
            if r.obj_info.depth <= depth:
                wait = (depth - r.obj_info.depth) * 4
                if r.total_time + wait <= min_possible:
                    return False

        return True

    def append(self, recipe):
        if not self.could_beat(recipe.total_time, recipe.obj_info.depth):
            return
        self.recipes.append(recipe)
        if recipe.total_time < self.best:
            self.best = recipe.total_time

    def __iter__(self):
        covering_set = set()
        for r in sorted(self.recipes, key=lambda a: a.total_time):
            self.recipes.remove(r)
            self.append(r)

        return self.recipes.__iter__()

Info = namedtuple('Info', ['lane', 'depth', 'orientation', 'phase'])

def parse_object_info(info):
    if info == '(l0)(ph3)(♗⬂①)':
        return Info(0, 0, 0, 0)
    m = re.match(r"""^\(l([-0-9]+),d([-0-9]+),o([0-9]+)(?:,p([0-9]+))?\)$""", info)
    if not m:
        raise SyntaxError(f"Invalid info: {info}")
    lane, depth, orientation, phase = m.group(1), m.group(2), m.group(3), m.group(4) or '0'
    return Info(int(lane), int(depth), int(orientation), int(phase))

def recipe_ordering(line):
    m = re.match(
        r"""^\((\d+(?:, \d+)*,?)\)\s*\[('[^']*'(?:, '[^']*')*)?\]$""",
        line.strip()
    )
    if not m:
        raise SyntaxError(f"Invalid line: {line}")
    stream = tuple(map(int, filter(bool, m.group(1).split(','))))
    return sum(stream[1:]), stream

seen = set()

if __name__ == '__main__':

    if args.process_objects:
        types = []
        recs = defaultdict(RecipeStore)
    else:
        types = [(i[0]+j[0]+k[0], j[1]+' '+i[1]+' '+k[1]) for j in [('⬀', 'NE'), ('⬃', 'SW')]
                    for i in [('♗', 'black'), ('♝', 'white')]
                    for k in [('⓪', 'even'), ('①', 'odd')]]
        recs = defaultdict(list)
    with args.recipes.open() as results_file:
        lines = results_file
        if args.presort:
            lines = sorted(lines, key=recipe_ordering)

        for line in lines:
            try:
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
                if args.process_objects and len(info['objects']) == 1:
                    obj_info = parse_object_info(info['objects'][0]['info'])
                    item = f"{info['objects'][0]['name']}(l{obj_info.lane},o{obj_info.orientation},p{obj_info.phase})"
                    recipe_store = recs[item]
                    if not recipe_store.could_beat(sum(stream[1:]) + args.toolkit.min_spacing, obj_info.depth):
                        continue
                    minimum_follow = find_minimum_follow(m.group(1), info['consumed'])
                    if not math.isfinite(minimum_follow): continue
                    total_time = sum(stream[1:]) + minimum_follow
                    type_desc = (item, item)
                    if type_desc not in types:
                        types.append(type_desc)

                    desc = Result(
                        m.group(1),
                        minimum_follow,
                        total_time,
                        info['consumed'],
                        info['objects'][0]['info'] if info['objects'] else '',
                        object=info['objects'][0]['name'],
                        obj_info=obj_info
                    )
                    recs[item].append(desc)
                    print(desc)
                elif len(info['objects']) == 1 and 'glider' in info['objects'][0]['name'] \
                                                and 'd' in info['objects'][0]['info']:
                    sig = (len(stream), info['consumed'], str(info['objects']))
                    if sig in seen:
                        continue
                    seen.add(sig)
                    minimum_follow = find_minimum_follow(m.group(1), info['consumed'])
                    if not math.isfinite(minimum_follow): continue
                    timing = find_glider_timing(m.group(1), info['consumed'])
                    if timing is None: continue
                    total_time = sum(stream[1:]) + minimum_follow
                    info_str = re.sub(r'ph[0-9]', f'ph{timing}', info['objects'][0]['info']) if info['objects'] else ''
                    desc = Result(
                        m.group(1),
                        minimum_follow,
                        total_time,
                        info['consumed'],
                        info_str + ' ' + ''.join(str(info['bonus'])),
                        object=info['objects'][0]['name']
                    )
                    print(desc)
                    recs[info['objects'][0]['info'].split('(')[-1][:-1]].append(desc)
                elif len(info['objects']) == 1 and info['objects'][0]['name'] in ('lwss', 'xq4_27dee6', 'xq4_27deee6'):
                    # an xwss
                    minimum_follow = find_minimum_follow(m.group(1), info['consumed'])
                    if not minimum_follow: continue
                    total_time = sum(stream[1:]) + minimum_follow
                    type_desc = (info['objects'][0]['name'], info['objects'][0]['name'])
                    if type_desc not in types:
                        types.append(type_desc)
                    desc = Result(
                        m.group(1),
                        minimum_follow,
                        total_time,
                        info['consumed'],
                        info['objects'][0]['info'] if info['objects'] else '',
                        object=info['objects'][0]['name']
                    )
                    recs[info['objects'][0]['name']].append(desc)
                    print(desc)
            except Exception as e:
                print(f"Error processing line {line}: {e}", file=sys.stderr)


    print()
    print(args.toolkit.name)
    for a, b in sorted(types, key=lambda a: a[0][2:]):
        print()
        print(b)
        for i in sorted(recs[a], key=lambda a: (a.total_time, a.consumed)):
            print(i)
