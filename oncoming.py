import sqlite3
import sys
import argparse
import re
import itertools

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
    default='0-7',
    type=SubtreeDef,
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

args = argparser.parse_args()

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

if args.find_minimum_repeat:
    expected_incoming_gliders = pattern_components(fake_gun[120 * args.n_gun_gliders])
    recipes = args.find_minimum_repeat.split(';')
    for i, r in enumerate(recipes):
        if not r.strip():
            continue
        delays = recipe_stream_to_delays(r)
        total = sum(delays)
        for i in range(args.toolkit.min_spacing, args.toolkit.min_spacing + 1000):
            p = fake_gun + single_channel_stream(delays)
            p = p[120 * args.n_gun_gliders]

            escaping_gliders = []
            for c in pattern_components(p):
                for i, e in enumerate(expected_incoming_gliders):
                    if c == e:
                        # this is one of the escaping gliders
                        escaping_gliders.append(i)
            n_escaping = max(escaping_gliders)
            follow_up_glider = mk_glider(total + i)



if args.print_rle:
    green_patt = lt.pattern('')
    red_patt = lt.pattern('')
    recipes = args.print_rle.split(';')
    for i, r in enumerate(recipes):
        if not r.strip():
            continue
        gliders_int = recipe_stream_to_delays(r)
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
        extended = mk_fake_gun(args.n_gun_gliders + 120) + single_channel_stream(gliders_int)

        original = original[120 * args.n_gun_gliders]
        extended = extended[120 * args.n_gun_gliders + 120 * 120 * 4]

        if original == extended:
            print("Confirmed shutoff!")
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

    expected_incoming_gliders = pattern_components(fake_gun[120 * args.n_gun_gliders])

    # phase 0 gliders
    canonical_se = mk_glider(0, 0)('rot180').centre()
    canonical_nw = mk_glider(0, 0).centre()
    canonical_ne = mk_glider(0, 0)('rot270').centre()
    canonical_sw = mk_glider(0, 0)('rot90').centre()

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
            elif c[1].centre() == canonical:
                phase = 1
            elif c[2].centre() == canonical:
                phase = 2
            elif c[3].centre() == canonical:
                phase = 3

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

            return f'{name}({location})(ph{phase})({color}{direction})'
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

        patt_n = patt[120 * args.n_gun_gliders]

        evaluate(s, patt_n)

        if depth > 0:
            for n in range(args.toolkit.min_spacing, args.max_delay + 1):
                recurse(s + (n,), depth - 1)

    for starting_point in itertools.product(*args.subtree.options):
        recurse(starting_point, depth=args.depth - len(starting_point))