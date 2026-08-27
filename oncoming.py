import sqlite3
import sys
import argparse
import re
import itertools
import functools
import pathlib
import os
from multiprocessing import Pool
import multiprocessing
import math

import lifelib

from arg_parser import range_str_to_list
from components import pattern_components
from font import write_text
from life_history import write_life_history
from lifetree import lt
from gliders import extract_single_channel_recipe, mk_glider, offset_based_on_glider, single_channel_stream
from parse_p120_recipes import parse_p120_recipe
from speedometer import Speedometer

argparser = argparse.ArgumentParser(
    prog="oncoming.py", description="Search for glider patterns"
)


class ToolkitDef:
    min_spacing: int
    lane_offset: int
    period: int
    name: str

    def __init__(self, str):
        m = re.match(r"sc(\d+)b(\d+)p(\d+)", str)
        if not m:
            raise ValueError(
                f"Toolkit {str} is invalid. Expected something like sc90b5p120"
            )
        self.min_spacing = int(m.group(1))
        self.lane_offset = int(m.group(2))
        self.period = int(m.group(3))
        self.name = str


argparser.add_argument(
    "--toolkit",
    default="sc90b5p120",
    type=ToolkitDef,
    help="The oncoming gliders to search. Format sc[min spacing]b[lane_offset]p[period]. E.g., sc90b5p120",
)
argparser.add_argument(
    "--depth", type=int, help="The number of gliders to include in salvos"
)
argparser.add_argument(
    "--print-rle",
    type=str,
    default="",
    help="Prints a rle showing the given recipes. Skips processing anything else.",
)
argparser.add_argument(
    "--n-gun-gliders", type=int, default=10, help="How many gun gliders to simulate"
)
argparser.add_argument(
    "--simulate-gens", type=int, default=None, help="How many generations to simulate"
)
argparser.add_argument(
    "--max-population", type=int, default=float('inf'), help="The maximum population results to report"
)

class SubtreeDef:
    options: tuple[tuple[int]]

    def __init__(self, str):
        depths = ()
        for d in str.split(";"):
            options = range_str_to_list(d)
            depths = depths + (tuple(options),)
        self.options = depths


argparser.add_argument(
    "--subtree",
    default=[],
    type=SubtreeDef,
    action="append",
    help="Search range. E.g. '1;90-255' to search the glider 1 followed by any glider in [90,255], or '1,3,5,7' to search the starting gliders 1,3,5 and 7. Use comma to separate at the same depth, then semicolon to separate depths. Ranges are inclusive.",
)
argparser.add_argument(
    "--subtree-file",
    default=None,
    type=pathlib.Path,
    help="A path to a file, with each line containing a subtree. Overrides the subtree param."
)
argparser.add_argument(
    "--max-delay", type=int, default=255, help="Maximum delay for a glider."
)
argparser.add_argument(
    "--check-for-shutoff",
    type=str,
    help="Checks if the given sequences shut off the glider stream by sending 120 extra gun gliders and comparing the state",
)
argparser.add_argument(
    "--find-minimum-follow",
    type=str,
    help="Finds the minimum follow distance for the given recipes",
)
argparser.add_argument("--use-gun-rle", type=str, help="Uses the rle as the gun")
argparser.add_argument(
    "--extract-recipes",
    type=pathlib.Path,
    help="Extracts the recipes from the given file. Outputs a JSON.",
)
argparser.add_argument(
    "--to-apgluxe",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Just print out the rles, don't simulate anything.",
)
argparser.add_argument(
    "--only-gliders",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Only process glider recipes",
)
argparser.add_argument(
    "--only-90-degree-gliders",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Only process glider recipes at 90 degrees",
)
argparser.add_argument(
    "--swim-upstream-after",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Send 2,96,96,96... after each part of the subtree"
)
argparser.add_argument(
    "--concurrent",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Use multiple threads for searching."
)
argparser.add_argument(
    "--view-orientations",
    type=str,
    default=None
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
    "--actually-not-oncoming",
    action=argparse.BooleanOptionalAction,
    default=False,
    help="Check 90 degree gliders",
)
argparser.add_argument(
    "--evaluate",
    default=False,
    help="Evaluates the pattern, offset based on the recipe glider present in the pattern."
)
argparser.add_argument(
    "--recipe-label",
    default=True,
    action=argparse.BooleanOptionalAction,
    help="If true, use LifeHistory to print the recipe label in --print-rle mode."
)
argparser.add_argument(
    "--with-debris-rle",
    default=None,
    type=str,
    help="Extra items to place alongside the construction lane. Include a NW glider indicating the location of the 0 glider."
)
argparser.add_argument(
    "--evolve-debris-gens",
    default=0,
    type=int,
    help="How many generations to evolve the debris before combining it with the pattern"
)
argparser.add_argument(
    "--and-without-debris",
    default=False,
    action=argparse.BooleanOptionalAction,
    help="Also include results for the pattern without the debris"
)
argparser.add_argument(
    "--without-debris-max-population",
    default=float('inf'),
    type=int,
    help="The max population to consider for the pattern without debris"
)
argparser.add_argument(
    "--without-debris-same-gliders-consumed",
    default=False,
    action=argparse.BooleanOptionalAction,
    help="If true, the with and without debris results must consume the same number of gliders"
)
argparser.add_argument(
    "--without-debris-must-differ",
    default=True,
    action=argparse.BooleanOptionalAction,
    help="If true, the end pattern for the result with debris cannot be the same, just with the original debris."
)
argparser.add_argument(
    "--delays-from-rle",
    type=str,
)    

args = argparser.parse_args()

if args.delays_from_rle:
    p = lt.pattern(args.delays_from_rle)
    print(extract_single_channel_recipe(p))
    sys.exit(0)


simulate_gens = args.simulate_gens or args.toolkit.period * args.n_gun_gliders

simkin_gun = lt.pattern("""x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!
""")(-490, -501)

gun_period = args.toolkit.period


def mk_fake_gun(n):
    fake_gun = sum(
        [mk_glider(0, gun_period * x) for x in range(0, n)], start=lt.pattern("")
    )
    if args.actually_not_oncoming:
        fake_gun = fake_gun('rot90')(5, -5)
    else:
        fake_gun = fake_gun('rot180')(-10 + args.toolkit.lane_offset, -11)
    if args.tandem_delay or args.tandem_offset:
        shift = math.ceil(args.tandem_delay / 4)
        phase = (4 - (args.tandem_delay % 4)) % 4
        if args.tandem_offset >= 0:
            tandem_gliders = fake_gun(-shift, -shift - args.tandem_offset)[phase]
        else:
            tandem_gliders = fake_gun(-shift + args.tandem_offset, -shift)[phase]

        fake_gun = fake_gun + tandem_gliders
    return fake_gun


fake_gun = mk_fake_gun(args.n_gun_gliders)
expected_incoming_gliders_pattern = fake_gun[simulate_gens]
expected_incoming_gliders = pattern_components(expected_incoming_gliders_pattern)
expected_incoming_gliders.sort(key=lambda p: sum(p.getrect()))

# phase 0 gliders
canonical_se = mk_glider(0, 0)("rot180").centre()
canonical_nw = mk_glider(0, 0).centre()
canonical_ne = mk_glider(0, 0)("rot270").centre()
canonical_sw = mk_glider(0, 0)("rot90").centre()


def recipe_stream_to_delays(stream):
    gliders = stream.split(",")
    result = []
    total = 0
    for g in gliders:
        m = re.match(r"^\(\s*(\d+)\s*\)\s*(?:\s*(\d+)\s*\+\s*)?(\d+)$", g.strip())
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
    recipes = args.find_minimum_follow.split(";")
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
        envelope = lt.pattern("5o$5o$5o$5o$5o").centre()

        pattern = mk_fake_gun(args.n_gun_gliders - n_escaping) + single_channel_stream(
            delays
        )

        @functools.lru_cache(maxsize=None)
        def pattern_at_gen(n):
            if n == 0:
                return pattern
            return pattern_at_gen(n - 1)[1]

        for i in range(args.toolkit.min_spacing, args.toolkit.min_spacing + 1000):
            follow_up_glider = mk_glider(0, total + i)
            glider_envelope = lt.pattern()
            for j in range(0, simulate_gens + i):
                follow_up_glider = follow_up_glider[1]
                glider_envelope += follow_up_glider.convolve(envelope)
                if (pattern_at_gen(j + 1) & glider_envelope).nonempty():
                    break
            else:
                # the envelope doesn't overlap with the reaction!
                print(",".join(map(str, delays)) + f",({i})")
                break
        else:
            print(
                ",".join(map(str, delays)) + f",({1000 + args.toolkit.min_spacing}+???)"
            )

    sys.exit(0)

if args.use_gun_rle:

    def remove_gliders(p):
        p = p + lt.pattern()  # copy
        for c in pattern_components(p):
            cc = c.centre()
            if (
                cc == canonical_se.centre()
                or cc == canonical_se[1].centre()
                or cc == canonical_se[2].centre()
                or cc == canonical_se[3].centre()
            ):
                p -= c
        return p

    if args.use_gun_rle == '120':
        args.use_gun_rle = '''x = 83, y = 50, rule = B3/S23
13b3o17$2o$obo$bo64b3o2$17bo6b2o38bo5bo$16bobo5b2o38bo5bo$16bobo45bo5b
o$17bo$34bo31b3o$9b2o23b3o$8bobo26bo$9bo26b2o5$25b2o5b2o$25b2o5b2o46b
2o$79bo2bo$29b2o49b2o$24bo4b2o$5b2o16bobo8b2o$5b2o16bobo7bo2bo$24bo7b
2o$33b2o3bo13b2o$34bo4bo12b2o$37b3o$49b2o5b2o$49b2o5b2o$12bo$6b2o3bobo
$5bo2bo2b2o$6b2o!'''
    elif args.use_gun_rle == '46':
        args.use_gun_rle = '''x = 37, y = 15, rule = B3/S23
24b2o$24b2o$36bo$10b2o22b3o$2o7bobo13b2o6bo$2o7bo15b2o6b2o$9b3o4$9b3o
21b3o$2o7bo20b2o$2o7bobo13bo4b2o$10b2o11bobo4bobo$24b2o!
'''

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
    rect = (-float("inf"), 0, 0, 0)
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
    fx, fy, _, _ = mk_fake_gun(1).getrect()
    x, y, _, _ = rect
    fake_gun = glider_appears(fx - x, fy - y)

debris_pattern = lt.pattern()
if args.with_debris_rle:
    debris_pattern = offset_based_on_glider(lt.pattern(args.with_debris_rle))[args.evolve_debris_gens]
    fake_gun = fake_gun + debris_pattern


if args.extract_recipes:

    def parse_object(obj):
        m = re.match(r"^'([\w ]+)((?:\([^)]*\))*)'$", obj.strip())
        if not m:
            raise SyntaxError(f"Invalid object: {obj}")
        name = m.group(1)
        info = m.group(2)
        return {"name": name, "info": info}

    gun_glider_names = set()
    for i in range(0, args.n_gun_gliders):
        gun_glider_names.add(f"g{i}")

    def parse_objects(objs):
        results = []
        gun_gliders = set()
        for o in re.split(r"('[^']*')", objs):
            o = o.strip()
            if not o or o == ",":
                continue
            obj = parse_object(o)
            if obj["name"] in gun_glider_names:
                gun_gliders.add(obj["name"])
            else:
                results.append(obj)

        for i in range(0, args.n_gun_gliders):
            if not f"g{i}" in gun_gliders:
                break

        consumed = args.n_gun_gliders - i
        if i != len(gun_gliders):
            results.append("!skipped glider")
        if i == 0:
            results.append("!consumed all")

        return {"consumed": consumed, "objects": results}

    with open(args.extract_recipes) as results_file:
        for line in results_file:
            m = re.match(
                r"""^\((\d+(?:, \d+)*,?)\)\s*\[('[^']*'(?:, '[^']*')*)?\]$""",
                line.strip(),
            )
            if not m:
                raise SyntaxError(f"Invalid line: {line}")
            stream = tuple(map(int, filter(bool, m.group(1).split(","))))
            info = parse_objects(m.group(2) or "")
            if info["consumed"] < 10 and len(info["objects"]) == 1:
                print(stream, info)

    sys.exit(0)

if args.print_rle:

    PI_BLOCKS = list(
        map(
            offset_based_on_glider,
            [lt.pattern("2o$2o3$3o$o$bo!"), lt.pattern("2o$2o2b3o$4bo$5bo!")],
        )
    )

    macros = {
        'sc90b5p120': {
            'construct_arm': 'mode sc, 0, 126, 102, 100, 195, 90, 91, 95, 98, 105, 90, 101, 141, 94, 159, 92, 146, 99, 90, 152, 139, 144, 92, 161, 131, 116, 101, 114, 111, 112, 93, 127, 98, 102, 114, 107, 157, 90, 90, 90, 91, 91, 243, 113, 139, 108, 95, 127, 121, 99, 257, 144, 94, 218, 148, 226, 111, 119, 100, 95, 91, 138, 201, 221, 216, 138, 125, mode p120, set 28 (mod 120), (90)',
            'snarkmaker': 'mode sc, 0,135,93,105,107,115,91,105,102,118,101,96,92,138,151,147,129,108,91,116,154,149,128,114,202,128,128,120,110,113,162,115,90,91,146,127,103,118,135,176,124,180,96,108,218,91,90,111,111,99,104,202,174,135,111,214,116,94,182,91,93,190,103,106,95,96,117,91,122,110,147,117,91,120,92,105,149,108,119,102,106,126,124,106,128,150,130,132,134,90,197,99,132,91,161,146,100,108,145,97,138,100,101,167,91,183,140,90,94,99,93,100,105,102,153,105,92,121,92,90,99,96,97,116,91,193,94,91,117,100,103,122,121,90,109,205,90,105,110,93,232,108,100,93,145,118,106,90,101,151,134,113,141,96,91,123,91,111,90,102,95,198,107,122,162,90,114,96,92,114,127,109,126,98,135,95,141,114,98,124,102,148,129,91,92,136,107,249,181,93,141,106,109,98,113,95,128,108,250,105,98,109,100,96,170,94,95,102,101,206,98,100,170,111,152,169,97,141,186,100,101,94,96,95,110,95,134,111,98,115,91,91,96,102,98,98,101,175,156,238,100,99,172,116,122,212,146,96,138,152,101,104,96,98,131,138,127,103,94,129,96,120,147,98,142,128,(156)',
            'sc_destroy': 'mode sc, 0, 109, 90, 93, 91, 90, 90, 90, (90)',
            'sc_paren_left': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 91, 90, 91, 91, 90, 90, 91, 90, 90, 99, 90, 90, 91, 90, 94, 90, 90, 109, 91, 94, 91, 91, 189, 91, 90, 91, 92, 90, 91, 158, 91, 90, 90, 90, 91, 116, 91, 137, 91, 90, 91, 90, 90, 149, 200, 90, 90, 154, 90, 91, (256)',
            'sc_paren_right': 'mode sc, 0, 109, 90, 93, 91, 90, 90, 90, 90, 121, 91, 91, 90, (256)',
            'sc_push44': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 91, 91, 138, 157, 96, 90, 120, 91, 97, 107, 90, 90, 93, (188)',
            'sc_pull38': 'mode sc, 0, 109, 90, 93, 91, 90, 100, 131, 101, 90, 113, (95)',
            'sc_pull32': 'mode sc, 0, 109, 91, 93, 91, 155, 106, 91, 90, 139, 91, 104, 91, 90, 93, 104, 91, 91, 143, 91, 110, 153, 162, 90, 91, 93, (163)',
            'sc_push22': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 97, 91, 90, 91, 90, 161, 91, 91, 91, 91, 91, 103, (130)',
            'sc_push20': 'mode sc, 0, 109, 91, 93, 91, 145, 215, 106, 90, 90, 91, 91, 174, 90, 158, 90, 90, 90, 91, 137, 90, 91, 127, (90)',
            'sc_push18': 'mode sc, 0, 109, 91, 93, 91, 113, 91, 132, 91, 91, 133, 91, 90, 98, 91, 90, 131, 90, 112, 132, 90, (90)',
            'sc_push16': 'mode sc, 0, 109, 91, 94, 91, 91, 96, 90, 97, 91, 91, 130, 94, 90, 105, 90, 95, 143, (99)',
            'sc_push14': 'mode sc, 0, 109, 91, 93, 90, 140, 150, 113, 90, 90, 90, 90, 91, 136, 119, 127, 90, 154, 142, 132, 91, 91, (90)',
            'sc_push12': 'mode sc, 0, 109, 91, 93, 91, 92, 90, 97, 91, 116, 91, 93, 115, 90, 91, 127, 90, 124, 112, (90)',
            'sc_push10': 'mode sc, 0, 109, 91, 93, 91, 129, 149, 91, 90, 90, 105, 90, 90, 90, 90, 114, 91, 100, 90, (90)',
            'sc_push8': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 119, 90, (90)',
            'sc_push6': 'mode sc, 0, 109, 91, 93, 91, 145, 215, 104, 90, 90, 90, 90, 90, 102, 92, 90, 90, 90, 106, 155, 150, (90)',
            'sc_push4': 'mode sc, 0, 109, 91, 93, 91, 92, 90, 90, 90, 151, 93, 90, 143, 134, 94, 90, 90, 90, 109, 91, (90)',
            'sc_push2': 'mode sc, 0, 109, 90, 93, 91, 91, 90, 90, 91, 91, 90, 90, 91, 90, 90, 94, 90, (90)',
            'sc_push0': 'mode sc, 0, 109, 91, 93, 91, 129, 148, 90, 93, 90, 93, 90, 161, 153, 155, 90, 107, 90, 90, (90)',
            'sc_pull2': 'mode sc, 0, 109, 91, 94, 91, 91, 136, 90, 90, 91, 171, 100, 118, 90, (90)',
            'sc_pull4': 'mode sc, 0, 109, 90, 93, 91, 91, 90, 90, 92, 90, 95, 91, 170, 90, 90, 91, 91, 98, 91, 91, (90)',
            'sc_pull6': 'mode sc, 0, 109, 91, 93, 91, 156, 91, 91, 94, 90, 91, 140, 91, 103, 91, 91, 132, (90)',
            'sc_pull8': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 91, 90, 91, 91, 90, 90, 91, 90, 90, 99, 90, 90, 91, 90, 94, 90, (90)',
            'sc_pull10': 'mode sc, 0, 109, 91, 94, 91, 91, 96, 90, 97, 91, 91, 130, 94, 90, 105, 90, 95, 111, (90)',
            'sc_pull12': 'mode sc, 0, 109, 91, 93, 91, 137, 91, 91, 125, 172, 108, 90, 109, 91, 101, 120, 90, (90)',
            'sc_pull14': 'mode sc, 0, 109, 91, 93, 91, 155, 106, 91, 91, 145, 90, 90, 91, 91, 90, 91, 90, 90, 118, (90)',
            'sc_pull16': 'mode sc, 0, 109, 90, 93, 91, 91, 128, 91, 91, 90, 100, 90, 90, 176, 94, 153, 90, 145, (115)',
            'sc_pull18': 'mode sc, 0, 109, 91, 94, 91, 91, 136, 91, 90, 91, 120, 90, 144, 90, 90, 90, 90, 102, 90, (90)',
            'sc_pull20': 'mode sc, 0, 109, 91, 94, 91, 91, 93, 90, 103, 120, 105, 101, 91, 106, 90, 90, 125, 90, 107, 91, 101, 90, 130, 91, 90, (90)',
            'sc_pull22': 'mode sc, 0, 109, 91, 93, 90, 118, 91, 90, 90, 91, 120, 132, 90, 101, 91, 125, 179, 91, 116, 108, 128, (90)',
            'sc_pull24': 'mode sc, 0, 109, 91, 93, 90, 129, 149, 91, 90, 90, 108, 91, 90, 113, 97, 167, 90, 91, 105, 94, (90)',
            'sc_pull26': 'mode sc, 0, 109, 91, 93, 90, 156, 90, 90, 95, 138, 91, 90, 96, 122, 91, 90, 95, 91, 90, 90, 91, 110, 130, 90, 131, (128)',
            'sc_pull28': 'mode sc, 0, 109, 91, 93, 90, 118, 91, 90, 90, 90, 97, 91, 90, 90, 129, 90, 164, 91, 94, 91, 91, 90, 96, 91, 111, (172)',
            'sc_push21': 'mode sc, 0, 109, 91, 93, 91, 92, 90, 128, 90, 91, 138, 99, 118, 91, 90, 91, 91, 169, 90, 91, 95, 91, 131, (90)',
            'sc_push19': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 113, 90, 91, 101, 90, 91, 93, 90, 90, 90, 106, 90, 91, 91, 91, 90, 109, 90, 90, 90, (90)',
            'sc_push17': 'mode sc, 0, 109, 90, 93, 91, 91, 90, 90, 100, 90, 90, 174, 90, 90, 90, 90, 105, 90, 130, 90, (90)',
            'sc_push15': 'mode sc, 0, 109, 91, 93, 91, 97, 91, 90, 90, 94, 91, 118, 90, 91, 99, 213, 102, 90, 90, 90, (90)',
            'sc_push13': 'mode sc, 0, 109, 91, 93, 91, 92, 90, 97, 91, 116, 91, 93, 115, 90, 91, 130, (90)',
            'sc_push11': 'mode sc, 0, 109, 91, 93, 91, 117, 90, 91, 90, 163, 91, 163, 91, 90, 149, 109, 109, 162, 91, 162, 91, 90, (90)',
            'sc_push9': 'mode sc, 0, 109, 90, 93, 91, 91, 90, 90, 95, 90, 91, 90, 90, 140, 90, 90, 128, (93)',
            'sc_push7': 'mode sc, 0, 109, 91, 94, 91, 90, 96, 90, 91, 146, 240, 109, 91, 94, 91, 91, 92, 90, 119, 90, (90)',
            'sc_push5': 'mode sc, 0, 109, 91, 93, 91, 92, 90, 110, 90, 152, 90, 90, 91, 91, 91, 90, 90, 90, 90, 175, 119, 115, (193)',
            'sc_push3': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 143, 90, 90, 90, 129, 101, 102, (90)',
            'sc_push1': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 143, 90, 91, 156, 90, 104, (164)',
            'sc_pull1': 'mode sc, 0, 109, 91, 94, 91, 90, 96, 90, 91, 146, (240)',
            'sc_pull3': 'mode sc, 0, 109, 91, 94, 91, 90, 96, 90, 91, 92, 90, 217, 90, 103, (90)',
            'sc_pull5': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 173, 100, 90, 141, 91, 90, 90, 90, 147, 90, 117, (192)',
            'sc_pull7': 'mode sc, 0, 109, 91, 93, 91, 118, 90, 91, 91, 91, 90, 90, 156, 114, 90, 90, 90, 90, 141, (90)',
            'sc_pull9': 'mode sc, 0, 109, 91, 94, 91, 91, 179, 90, 91, 94, 91, 102, 91, 105, 91, 108, 90, 91, 91, 120, 90, (90)',
            'sc_pull11': 'mode sc, 0, 109, 91, 93, 91, 92, 90, 90, 90, 151, 93, 90, 137, 113, 112, 90, 121, (90)',
            'sc_pull13': 'mode sc, 0, 109, 91, 94, 91, 91, 114, 94, 90, 106, 90, 91, 107, 233, 118, 90, 90, (90)',
            'sc_pull15': 'mode sc, 0, 109, 91, 94, 91, 90, 152, 91, 90, 91, 145, 90, 90, 139, 91, 90, 92, (90)',
            'sc_pull17': 'mode sc, 0, 109, 91, 93, 90, 97, 91, 91, 93, 91, 90, 90, 91, 123, 114, 92, 90, 90, 154, 90, 117, 126, 141, 90, 92, 106, (90)',
            'sc_pull19': 'mode sc, 0, 109, 91, 93, 90, 171, 90, 90, 91, 154, 110, 169, 107, 91, 90, 99, 91, 122, 90, 90, 159, 90, (90)',
            'sc_pull21': 'mode sc, 0, 109, 91, 93, 91, 132, 115, 102, 90, 91, 91, 91, 90, 90, 154, (98)',
            'sc_pull23': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 173, 100, 90, 141, 91, 90, 90, 90, 145, 98, 107, (90)',
            'sc_pull25': 'mode sc, 0, 109, 91, 93, 91, 129, 148, 91, 93, 154, 91, 91, 91, 90, 90, 90, 90, 143, 91, 90, 90, 107, (90)',
            'sc_pull27': 'mode sc, 0, 109, 91, 93, 91, 145, 215, 97, 91, 91, 90, 91, 158, 95, 90, 112, 90, 91, 97, 90, 100, 91, 90, 91, 107, (90)',
            'sc_pull29': 'mode sc, 0, 109, 91, 94, 91, 91, 92, 90, 169, 91, 90, 116, 90, 113, (90)',
            'sc_pull31': 'mode sc, 0, 109, 91, 93, 90, 140, 150, 113, 90, 90, 90, 90, 91, 136, 119, 127, 90, 103, 91, 99, (116)',
            'sc_push12': 'mode sc, 0, 109, 90, 95, 245, 90, 126, 211, 91, 90, 120, 90, 91, 91, 90, 91, 90, 118, 90, 90, 91, 90, 113, 91, 105, 90, 90, 90, 90, (90)',
            'sc_push10': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 91, 91, 139, 90, 163, 90, 91, 148, 104, 98, 91, 91, 90, 90, 92, 91, 173, 93, 136, 90, 100, 90, 92, 90, 91, (90)',
            'sc_push8': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 91, 91, 118, 90, 93, 91, 90, 91, 91, 90, 113, 91, 90, 91, 91, 149, 91, 90, 90, 96, 91, 142, 91, 134, (197)',
            'sc_push6': 'mode sc, 0, 93, 90, 90, 90, 90, 90, 90, 91, 105, 159, 92, 90, 115, 100, 231, 99, 91, 90, 90, 91, 130, 91, 90, 90, 90, 91, 97, 91, 116, 90, 99, (174)',
            'sc_push0': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 90, 90, 91, 90, 90, 151, 91, 91, 90, 93, 90, 90, 90, 100, 91, 90, 90, 90, 91, 90, 90, 97, 90, (90)',
            'sc_pull2': 'mode sc, 0, 109, 90, 95, 245, 90, 126, 211, 91, 90, 113, 90, 90, 90, 92, 91, 90, 98, 165, 91, 125, 90, 90, 110, 112, 90, 90, 100, (90)',
            'sc_pull34': 'mode sc, 0, 109, 90, 93, 91, 90, 95, 91, 91, 139, 90, 157, 90, 91, 93, 90, 109, 90, 123, 119, 135, 94, 90, 161, 91, 90, 90, 90, 91, 91, 90, 139, (90)',
        }
    }
    green_patt = lt.pattern("")
    red_patt = lt.pattern("")
    recipes = args.print_rle.split(";")

    if args.and_without_debris:
        stride = 400
    else:
        stride = 200

    for i, r in enumerate(recipes):
        if not r.strip():
            continue
        parse = parse_p120_recipe(r, macros.get(args.toolkit.name, {}))
        gliders_int = parse.delays
        print(gliders_int)
        if parse.start_mode == "p120":
            fg = fake_gun
            if parse.advance_debris:
                fg = fake_gun - debris_pattern + debris_pattern[parse.advance_debris]
            green_patt += fg(stride * i, 0) + single_channel_stream(gliders_int)(
                stride * i, 0
            )
            red_patt += write_text(" ".join(map(str, gliders_int)))(stride * i, 0)

            if args.and_without_debris:
                green_patt += (fake_gun - debris_pattern)(stride * i + stride // 2, 0) + single_channel_stream(gliders_int)(
                    stride * i + stride // 2, 0
                )
                red_patt += write_text(" ".join(map(str, gliders_int)))(stride * i + stride // 2, 0)

        elif parse.start_mode == "sc":
            green_patt += PI_BLOCKS[1](stride * i, 0) + single_channel_stream(gliders_int)(stride*i, 0)
            red_patt += write_text(" ".join(map(str, gliders_int)))(stride * i, 0)
    if not args.recipe_label:
        red_patt = lt.pattern()
    print(write_life_history(green=green_patt, red=red_patt))

    sys.exit(0)

if args.check_for_shutoff:
    print("Checking if patterns shut off the stream.")

    recipes = args.check_for_shutoff.split(";")

    for i, r in enumerate(recipes):
        gliders_int = recipe_stream_to_delays(r)
        original = fake_gun + single_channel_stream(gliders_int)
        extended_fake_gun = mk_fake_gun(args.n_gun_gliders + 120)
        extended = extended_fake_gun + single_channel_stream(gliders_int)

        original = original[simulate_gens]

        extended_simulate_gens = simulate_gens + args.toolkit.period * 120 * 4
        extended = extended[extended_simulate_gens]
        # allow the first n+20 gliders to possibly escape, but the rest should be absorbed.
        expected_gun_positions = mk_fake_gun(args.n_gun_gliders + 20)[
            extended_simulate_gens
        ]

        if original == extended:
            print("Confirmed shutoff!")
            print(gliders_int)
        elif (original - expected_gun_positions) == (extended - expected_gun_positions):
            print("Possible shutoff with escaping gun gliders")
            print(gliders_int)

    sys.exit(0)

friendly_names = {
    "xq4_153": "glider",
    "xs4_33": "block",
    "xp2_7": "blinker",
    "xs6_696": "beehive",
    "xs7_2596": "loaf",
    "xs5_253": "boat",
    "xs6_356": "ship",
    "xs8_6996": "pond",
    "xs4_252": "tub",
    "xs7_25ac": "long boat",
    "xs12_g8o653z11": "ship tie",
    "xp2_7e": "toad",
    "xp2_318c": "beacon",
    "xs14_g88m952z121": "half bakery",
    "xs7_178c": "eater 1",
    "xs6_25a4": "barge",
    "xs6_bd": "snake",
    "xs11_g8o652z11": "boat tie ship",
    "xq4_6frc": "lwss",
}

class HashablePattern:
    def __init__(self, c: lifelib.Pattern, digest: int):
        self.c = c
        self.digest = digest
    
    def __hash__(self):
        return self.digest

    def __eq__(self, other):
        return self.digest == other.digest

@functools.lru_cache(maxsize=None)
def pattern_orientation(c):
    c = c.c
    orientations = [c.digest()]
    for o in ["rot270", "rot180", "rot90", "flip_x", "flip_y", "swap_xy", "swap_xy_flip"]:
        orientations.append(c(o).digest())
    orientations = sorted(set(orientations))
    return orientations.index(c.digest())

def component_info(c, alt=False):
    if c == c[1]:
        # still life
        code = c.apgcode
        name = friendly_names.get(code, code)
        x, y, w, h = c.getrect()
        lane = x - y
        depth = x + y + w + h
        orientation = pattern_orientation(HashablePattern(c, c.digest()))
        return f"{name}(l{lane},d{depth},o{orientation})"
    elif c == c[120]:
        # oscillator
        code = c.apgcode
        name = friendly_names.get(code, code)
        x, y, w, h = c.getrect()
        lane = x - y
        depth = x + y + w + h
        orientation = pattern_orientation(HashablePattern(c, c.digest()))
        if name == 'blinker' and alt:
            # skip blinkers when processing the alt.
            return None
        return f"{name}(l{lane},d{depth},o{orientation},p{int(alt)})"
    elif c.centre() == c[4].centre():
        # spaceship
        code = c.apgcode
        name = friendly_names.get(code, code)

        x, y, w, h = c.getrect()
        x4, y4, _, _ = c[4].getrect()

        if x4 - x == 0 or y4 - y == 0:
            orientation = pattern_orientation(HashablePattern(c, c.digest()))
            # xWSS, need to process even if alt is true.
            canonical = c
            if pattern_orientation(HashablePattern(c[2], c[2].digest())) < orientation:
                canonical = c[2]
            cx, cy, _, _ = canonical.getrect()
            # record the parity and color of the xWSS.
            return f"{name}({x4-x},{y4-y},p{int(alt) + (2 if c == canonical else 0)},c{(cx+cy) % 2})({cx},{cy})"
        elif alt:
            # ignore gliders in alt -- we've already got them.
            return None

        # give the incoming gliders the names g0, g1, etc.
        for i, e in enumerate(expected_incoming_gliders):
            if c == e:
                return f"g{i}"

        # glider phase/color info
        match (x4 - x, y4 - y):
            case (1, 1):
                # same direction as gun
                canonical = canonical_se
                direction = "⬂"
            case (1, -1):
                # gun side 90 degree
                canonical = canonical_ne
                direction = "⬀"
            case (-1, 1):
                # recipe side 90 degree
                canonical = canonical_sw
                direction = "⬃"
            case (-1, -1):
                # same direction as recipe
                canonical = canonical_nw
                direction = "⬁"

        phase = 5
        if c.centre() == canonical:
            phase = 0
            phase_mod2 = "⓪"
        elif c[1].centre() == canonical:
            phase = 1
            phase_mod2 = "①"
        elif c[2].centre() == canonical:
            phase = 2
            phase_mod2 = "⓪"
        elif c[3].centre() == canonical:
            phase = 3
            phase_mod2 = "①"

        lx, ly, lw, lh = c[phase].getrect()
        lane = lx - ly
        depth = lx + ly + lw + lh

        match (x4 - x, y4 - y):
            case (1, 1):
                location = f"l{lane}"
                color = "♗♝"[lane % 2]
            case (1, -1):
                location = f"d{depth}"
                color = "♗♝"[depth % 2]
            case (-1, 1):
                location = f"d{depth}"
                color = "♗♝"[depth % 2]
            case (-1, -1):
                location = f"l{lane}"
                color = "♗♝"[lane % 2]

        return f"{name}({location})(ph{phase})({color}{direction}{phase_mod2})"
    else:
        # not an object
        return None

if args.view_orientations:
    if args.view_orientations in friendly_names.values():
        args.view_orientations = next(k for k,v in friendly_names.items() if v == args.view_orientations)
    p = lt.pattern(args.view_orientations)
    results = {}
    orientations = [p]
    for o in ["rot270", "rot180", "rot90", "flip_x", "flip_y", "swap_xy", "swap_xy_flip"]:
        orientations.append(p(o))
    for oriented in orientations:
        x, y, w, h = oriented.getrect()
        oriented = oriented(-x + 1, -y + 1)
        data = ['.'] * (w+2) * (h*2)
        for (cx, cy) in oriented.coords():
            data[cy*(w+2) + cx] = '#'
        data = ''.join(data)
        lines = []
        for i in range(0, h+2):
            lines.append(data[i*(w+2):(i+1)*(w+2)])
        lines = '\n'.join(lines)
        results[pattern_orientation(HashablePattern(oriented, oriented.digest()))] = lines
    
    for orientation, view in sorted(results.items()):
        print()
        print(f'o{orientation}')
        print('==========================')
        print(view)

    sys.exit(0)

def evaluate(s, patt, stream_to_check_patt = None):
    if args.actually_not_oncoming:
        # if we are trying 90 degree recipes,
        # ignore results where a recipe glider escapes without
        # interacting.
        expected_recipe_gliders = stream_to_check_patt[simulate_gens]
        escaped_patt = patt & expected_recipe_gliders
        for p in pattern_components(escaped_patt):
            if p.population == 5:
                return (s, ['prune'])

    if (patt - expected_incoming_gliders_pattern).population > args.max_population:
        return (s, ['too big'])

    infos = set()

    if args.only_gliders:
        if patt.population % 5:
            return
        diff = patt - expected_incoming_gliders_pattern
        if diff.population % 5 or diff.population < 5:
            return
        if diff.centre() != diff[4].centre() or diff == diff[4]:
            return
        if args.only_90_degree_gliders:
            a = tuple(patt.getrect())
            b = tuple(patt[4].getrect())
            if (a[0] - b[0], a[1] - b[1]) in ((-1, -1), (1, 1)):
                return
        components = pattern_components(patt)
        for c in components:
            info = component_info(c, False)
            if info is not None:
                infos.add(info)
    else:
        components = pattern_components(patt)
        has_unidentified = False
        for c in components:
            info = component_info(c, False)
            if info is not None:
                infos.add(info)
            else:
                has_unidentified = True
        if has_unidentified:
            components1 = pattern_components(patt[1])
            for c in components1:
                info = component_info(c, True)
                if info is not None:
                    infos.add(info)

    return (s, sorted(infos))

def process_concurrent(s):
    stream_to_check = s
    if args.swim_upstream_after:
        stream_to_check = parse_p120_recipe(','.join(map(str, s)) + ',(90), 2, 96, 96, 96, 96, 96, 96, 96, 96', {}).delays
    stream_to_check_patt = single_channel_stream(stream_to_check)
    patt = fake_gun + stream_to_check_patt

    patt_n = patt[simulate_gens]

    if args.and_without_debris:
        patt_n_without_debris = (patt - debris_pattern)[simulate_gens]

        if (patt_n_without_debris - expected_incoming_gliders_pattern).population > args.without_debris_max_population:
            return

        if args.without_debris_must_differ and patt_n_without_debris == patt_n - debris_pattern:
            return

        if args.without_debris_same_gliders_consumed:
            if (patt_n & expected_incoming_gliders_pattern) != (patt_n_without_debris & expected_incoming_gliders_pattern):
                return

        _, without_result = evaluate(s, patt_n_without_debris, stream_to_check_patt)

        _, with_result = evaluate(s, patt_n, stream_to_check_patt)

        if with_result and with_result[0] == 'too big':
            return

        a = set(without_result)
        b = set(with_result)

        diff_plus = sorted(map(lambda x: f'+{x}', b - a))
        diff_minus = sorted(map(lambda x: f'-{x}', a - b))

        return (s, with_result + ['w/o:'] + without_result + ['diff:'] + diff_plus + diff_minus)


    result = evaluate(s, patt_n, stream_to_check_patt)
    return result

def recurse(s, depth=0):
    stream_to_check = s
    if args.swim_upstream_after:
        stream_to_check = parse_p120_recipe(','.join(map(str, s)) + ',(90), 2, 96, 96, 96, 96, 96, 96, 96, 96', {}).delays

    stream_to_check_patt = single_channel_stream(stream_to_check)
    patt = fake_gun + stream_to_check_patt

    if not args.to_apgluxe:
        patt_n = patt[simulate_gens]
        v = evaluate(s, patt_n, stream_to_check_patt)
        if v:
            print(*v)
    else:
        print(patt.rle_string()[len("#CLL state-numbering golly\n") :])

    if depth > 0:
        for n in range(args.toolkit.min_spacing, args.max_delay + 1):
            recurse(s + (n,), depth - 1)


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

    if args.evaluate:
        patt = offset_based_on_glider(lt.pattern(args.evaluate))
        s, result = evaluate((), patt)
        print(result)

        sys.exit(0)

    if args.subtree_file:
        with open(args.subtree_file) as f:
            args.subtree = list(SubtreeDef(line) for line in f if line.strip())

    if args.concurrent:
        print("Generating jobs...", file=sys.stderr)
        if not args.subtree:
            args.subtree = [SubtreeDef("0-7")]
        len_all_options = 0
        for subtree in args.subtree:
            for depth in range(0, args.depth - len(subtree.options) + 1):
                deeper = (tuple(range(args.toolkit.min_spacing, args.max_delay + 1)),) * depth
                len_all_options += math.prod(map(len, subtree.options + deeper))

        print('Total:', len_all_options, file=sys.stderr)

        def all_options():
            for subtree in args.subtree:
                for depth in range(0, args.depth - len(subtree.options) + 1):
                    for starting_point in itertools.product(*subtree.options):
                        deeper = (tuple(range(args.toolkit.min_spacing, args.max_delay + 1)),) * depth
                        for d in itertools.product(*map(lambda a: (a,), starting_point), *deeper):
                            yield d

        multiprocessing.set_start_method('spawn')
        with Pool(processes=os.cpu_count() - 1) as pool:
            speedo = Speedometer()
            print("Starting...", file=sys.stderr)
            for result in pool.imap_unordered(process_concurrent, all_options(), chunksize=256):
                if speedo.tick(1):
                    current_per_s = speedo.get_current_speed_and_reset()
                    avg_per_s = speedo.overall_speed()
                    done = speedo.n_finished
                    percent = done/len_all_options*100
                    estimate_s = int((len_all_options - done)/avg_per_s)
                    estimate_min = estimate_s // 60
                    estimate_hr = estimate_min // 60
                    if estimate_hr > 0:
                        estimate = f"{estimate_hr}h {estimate_min % 60}m {estimate_s % 60}s"
                    elif estimate_min > 0:
                        estimate = f"{estimate_min % 60}m {estimate_s % 60}s"
                    else:
                        estimate = f"{estimate_s}s"
                    print(f"{current_per_s:.2f}/s, {avg_per_s:.2f}/s avg, {done}/{len_all_options} ({percent:0.2f}%), {estimate} left", file=sys.stderr)
                if result:
                    print(*result)
        pool.join()
    else:
        if not args.subtree:
            args.subtree = [SubtreeDef("0-7")]
        for subtree in args.subtree:
            for starting_point in itertools.product(*subtree.options):
                recurse(starting_point, depth=args.depth - len(starting_point))
