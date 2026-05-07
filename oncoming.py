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

    def __init__(self, str):
        m = re.match(r'sc(\d+)b(\d+)p(\d+)', str)
        if not m:
            raise ValueError(f'Toolkit {str} is invalid. Expected something like sc90b5p120')
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
    '--depth',
    type=int,
    help="The number of gliders to include in salvos"
)
argparser.add_argument(
    '--print-rle',
    type=str,
    default='',
    help="Prints a rle showing the given recipes. Skips processing anything else."
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
class SubtreeDef:
    options: tuple[tuple[int]]

    def __init__(self, str):
        depths = ()
        for d in str.split(';'):
            options = range_str_to_list(d)
            depths = depths + (tuple(options),)
        self.options = depths

argparser.add_argument(
    '--subtree',
    default=[],
    type=SubtreeDef,
    action="append",
    help="Search range. E.g. '1;90-255' to search the glider 1 followed by any glider in [90,255], or '1,3,5,7' to search the starting gliders 1,3,5 and 7. Use comma to separate at the same depth, then semicolon to separate depths. Ranges are inclusive.",
)
argparser.add_argument(
    '--max-delay',
    type=int,
    default=255,
    help='Maximum delay for a glider.'
)
argparser.add_argument(
    '--check-for-shutoff',
    type=str,
    help='Checks if the given sequences shut off the glider stream by sending 120 extra gun gliders and comparing the state'
)
argparser.add_argument(
    '--find-minimum-follow',
    type=str,
    help="Finds the minimum follow distance for the given recipes"
)
argparser.add_argument(
    '--use-gun-rle',
    type=str,
    help="Uses the rle as the gun"
)
argparser.add_argument(
    '--extract-recipes',
    type=pathlib.Path,
    help="Extracts the recipes from the given file. Outputs a JSON."
)
argparser.add_argument(
    '--to-apgluxe',
    action=argparse.BooleanOptionalAction,
    default=False
)

args = argparser.parse_args()
simulate_gens = args.simulate_gens or args.toolkit.period * args.n_gun_gliders

simkin_gun =lt.pattern("""x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!
""")(-490, -501)

gun_period = args.toolkit.period

def mk_fake_gun(n):
    fake_gun = sum([mk_glider(0, gun_period*x) for x in range(0, n)], start=lt.pattern(''))
    fake_gun = fake_gun('rot180')(-10 + args.toolkit.lane_offset, -11)
    return fake_gun

fake_gun = mk_fake_gun(args.n_gun_gliders)
expected_incoming_gliders = pattern_components(fake_gun[simulate_gens])

# phase 0 gliders
canonical_se = mk_glider(0, 0)('rot180').centre()
canonical_nw = mk_glider(0, 0).centre()
canonical_ne = mk_glider(0, 0)('rot270').centre()
canonical_sw = mk_glider(0, 0)('rot90').centre()

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

if args.find_minimum_follow:
    expected_incoming_gliders = pattern_components(fake_gun[simulate_gens])
    recipes = args.find_minimum_follow.split(';')
    for i, r in enumerate(recipes):
        if not r.strip():
            continue
        delays = recipe_stream_to_delays(r)
        total = sum(delays)

        p = fake_gun + single_channel_stream(delays)
        p = p[simulate_gens]

        escaping_gliders = []
        for c in pattern_components(p):
            for i, e in enumerate(expected_incoming_gliders):
                if c == e:
                    # this is one of the escaping gliders
                    escaping_gliders.append(i)
        n_escaping = max(escaping_gliders) + 1

        # now we know which gliders participate. Remove the rest.
        envelope = lt.pattern('5o$5o$5o$5o$5o').centre()

        pattern = mk_fake_gun(args.n_gun_gliders - n_escaping) + single_channel_stream(delays)

        @functools.lru_cache(maxsize=None)
        def pattern_at_gen(n):
            if n == 0:
                return pattern
            return pattern_at_gen(n-1)[1]

        for i in range(args.toolkit.min_spacing, args.toolkit.min_spacing + 1000):
            follow_up_glider = mk_glider(0, total + i)
            glider_envelope = lt.pattern()
            for j in range(0, simulate_gens + i):
                follow_up_glider = follow_up_glider[1]
                glider_envelope += follow_up_glider.convolve(envelope)
                if (pattern_at_gen(j+1) & glider_envelope).nonempty():
                    break
            else:
                # the envelope doesn't overlap with the reaction!
                print(','.join(map(str,delays)) + f',({i})')
                break
        else:
            print(','.join(map(str,delays)) + f',({1000 + args.toolkit.min_spacing}+???)')


    sys.exit(0)

if args.use_gun_rle:
    def remove_gliders(p):
        p = p + lt.pattern() # copy
        for c in pattern_components(p):
            cc = c.centre()
            if cc == canonical_se.centre() or cc == canonical_se[1].centre() or cc == canonical_se[2].centre() or cc == canonical_se[3].centre():
                p -= c
        return p

    gun = lt.pattern(args.use_gun_rle.strip())
    gun_without_gliders = remove_gliders(gun)

    glider_appears = gun
    # now, let's fast forward the gun until we see an output glider.
    for i in range(0, args.toolkit.period):
        if remove_gliders(glider_appears) != glider_appears:
            # there's a glider
            break
        glider_appears = glider_appears[1]

    glider_appears = glider_appears[(args.n_gun_gliders - 1) * args.toolkit.period]

    # and make the gliders canonical
    rect = (-float('inf'), 0, 0, 0)
    for i in range(0, 4):
        found = False
        for c in pattern_components(glider_appears):
            if c.centre() == canonical_se.centre():
                rect = max(rect, tuple(c.getrect()))
                found = True
        if found:
            break
        glider_appears = glider_appears[1]
    else:
        raise Exception("Couldn't find gliders?")

    # shift the gun so that it lines up with the fake gun.
    (fx, fy, _, _) = mk_fake_gun(1).getrect()
    (x, y, _, _) = rect
    fake_gun = glider_appears(fx - x, fy - y)


if args.extract_recipes:
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
        if i != len(gun_gliders):
            results.append('!skipped glider')
        if i == 0:
            results.append('!consumed all')

        return {
            'consumed': consumed,
            'objects': results
        }
    with open(args.extract_recipes) as results_file:
        for line in results_file:
            m = re.match(
                r"""^\((\d+(?:, \d+)*,?)\)\s*\[('[^']*'(?:, '[^']*')*)?\]$""",
                line.strip()
            )
            if not m:
                raise SyntaxError(f"Invalid line: {line}")
            stream = tuple(map(int, filter(bool, m.group(1).split(','))))
            info = parse_objects(m.group(2) or '')
            if info['consumed'] < 10 and len(info['objects']) == 1:
                print(stream, info)

    sys.exit(0)

if args.print_rle:
    green_patt = lt.pattern('')
    red_patt = lt.pattern('')
    recipes = args.print_rle.split(';')
    for i, r in enumerate(recipes):
        if not r.strip():
            continue
        gliders_int = recipe_stream_to_delays(r)
        print(gliders_int)
        green_patt += fake_gun(200 * i, 0) + single_channel_stream(gliders_int)(200 * i, 0)
        red_patt += write_text(' '.join(map(str, gliders_int)))(200 * i, 0)
    print(write_life_history(green=green_patt, red=red_patt))

    sys.exit(0)

if args.check_for_shutoff:
    print("Checking if patterns shut off the stream.")

    recipes = args.check_for_shutoff.split(';')

    for i, r in enumerate(recipes):
        gliders_int = recipe_stream_to_delays(r)
        original = fake_gun + single_channel_stream(gliders_int)
        extended_fake_gun = mk_fake_gun(args.n_gun_gliders + 120)
        extended = extended_fake_gun + single_channel_stream(gliders_int)

        original = original[simulate_gens]

        extended_simulate_gens = simulate_gens + args.toolkit.period * 120 * 4
        extended = extended[extended_simulate_gens]
        # allow the first n+20 gliders to possibly escape, but the rest should be absorbed.
        expected_gun_positions = mk_fake_gun(args.n_gun_gliders + 20)[extended_simulate_gens]

        if original == extended:
            print("Confirmed shutoff!")
            print(gliders_int)
        elif (original - expected_gun_positions) == (extended - expected_gun_positions):
            print("Possible shutoff with escaping gun gliders")
            print(gliders_int)

    sys.exit(0)

friendly_names = {
    'xq4_153': 'glider',
    'xs4_33': 'block',
    'xp2_7': 'blinker',
    'xs6_696': 'beehive',
    'xs7_2596': 'loaf',
    'xs5_253': 'boat',
    'xs6_356': 'ship',
    'xs8_6996': 'pond',
    'xs4_252': 'tub',
    'xs7_25ac': 'long boat',
    'xs12_g8o653z11': 'ship tie',
    'xp2_7e': 'toad',
    'xp2_318c': 'beacon',
    'xs14_g88m952z121': 'half bakery',
    'xs7_178c': 'eater 1',
    'xs6_25a4': 'barge',
    'xs6_bd': 'snake',
    'xs11_g8o652z11': 'boat tie ship',
    'xq4_6frc': 'lwss'
}

if __name__ == "__main__":
    """
    p = lt.pattern('')
    for d1 in range(0, 8):
        p += (fake_gun + mk_glider(0, d1) + mk_glider(0, d1 + 90))(100*(d1), 0)

    print(p.rle_string())

    Results:
    0 - delete
    1 - block on gun side
    2 - backwards kickback
    3 - pond on gun side
    4 - delete
    5 - pond on recipe side
    6 - forwards kickback
    7 - block on recipe side
    """

    # Only keep the interesting first gliders.
    # The deletes are too fast to follow-up.
    # The kickbacks will just delete the next glider from that side.
    # Those are useful for pushing upstream, but won't act as elbows.
    valid_first_gliders = (1, 3, 5, 7)

    def component_info(c, alt = False):
        if c == c[120]:
            # still life or oscillator
            code = c.apgcode
            name = friendly_names.get(code, code)
            (x, y, w, h) = c.getrect()
            lane = x - y
            depth = x + y + w + h
            return f'{name}(l{lane},d{depth})'
        elif c.centre() == c[4].centre():
            # spaceship
            code = c.apgcode
            name = friendly_names.get(code, code)

            (x, y, w, h) = c.getrect()
            (x4, y4, _, _) = c[4].getrect()

            if x4-x == 0 or y4-y == 0:
                # xWSS, need to process even if alt is true.
                return f'{name}({x},{y})({x4-x},{y4-y})'
            elif alt:
                # ignore gliders in alt -- we've already got them.
                return None

            # give the incoming gliders the names g0, g1, etc.
            for i, e in enumerate(expected_incoming_gliders):
                if c == e:
                    return f'g{i}'

            # glider phase/color info
            match (x4-x, y4-y):
                case (1,1):
                    # same direction as gun
                    canonical = canonical_se
                    direction = '⬂'
                case (1,-1):
                    # gun side 90 degree
                    canonical = canonical_ne
                    direction = '⬀'
                case (-1,1):
                    # recipe side 90 degree
                    canonical = canonical_sw
                    direction = '⬃'
                case (-1,-1):
                    # same direction as recipe
                    canonical = canonical_nw
                    direction = '⬁'

            if c.centre() == canonical:
                phase = 0
                phase_mod2 = '⓪'
            elif c[1].centre() == canonical:
                phase = 1
                phase_mod2 = '①'
            elif c[2].centre() == canonical:
                phase = 2
                phase_mod2 = '⓪'
            elif c[3].centre() == canonical:
                phase = 3
                phase_mod2 = '①'

            (lx, ly, lw, lh) = c[phase].getrect()
            lane = lx - ly
            depth = lx + ly + lw + lh

            match (x4-x, y4-y):
                case (1,1):
                    location = f'l{lane}'
                    color = '♗♝'[lane % 2]
                case (1,-1):
                    location = f'd{depth}'
                    color = '♗♝'[depth % 2]
                case (-1,1):
                    location = f'd{depth}'
                    color = '♗♝'[depth % 2]
                case (-1,-1):
                    location = f'l{lane}'
                    color = '♗♝'[lane % 2]

            return f'{name}({location})(ph{phase})({color}{direction}{phase_mod2})'
        else:
            # not an object
            return None

    def evaluate(s, patt):
        if patt.population > 150:
            # print(s, 'too big')
            # return
            pass

        components = pattern_components(patt)
        components1 = pattern_components(patt[1])

        infos = set()
        for c in components:
            infos.add(component_info(c, False))
        for c in components1:
            infos.add(component_info(c, True))

        print(s, sorted(filter(lambda a: a is not None, infos)))

    def recurse(s, depth=0):
        patt = fake_gun + single_channel_stream(s)

        if not args.to_apgluxe:
            patt_n = patt[simulate_gens]
            evaluate(s, patt_n)
        else:
            print(patt.rle_string()[len('#CLL state-numbering golly\n'):])

        if depth > 0:
            for n in range(args.toolkit.min_spacing, args.max_delay + 1):
                recurse(s + (n,), depth - 1)

    if not args.subtree:
        args.subtree = [SubtreeDef('0-7')]
    for subtree in args.subtree:
        for starting_point in itertools.product(*subtree.options):
            recurse(starting_point, depth=args.depth - len(starting_point))