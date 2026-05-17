# Compiles a slow salvo to the p120 arm, processes nearly instantly
# but may have slight inefficiencies.

import itertools
import collections
import math
import sys
import re
import argparse
import pathlib

from recipe_intermediates import RecipeDag
from gliders import extract_recipe_lanes
from lifetree import lt

argparser = argparse.ArgumentParser(
    prog="compile_p120_fast.py", description="Compile slow salvos to the p120 arm"
)
argparser.add_argument("salvo", type=pathlib.Path)
argparser.add_argument(
    "--period",
    type=int,
    default=120
)
argparser.add_argument(
    "--toolkit-file",
    type=pathlib.Path,
    default=pathlib.Path("recipes/sc90b5p120-gliders.txt")
)
argparser.add_argument(
    "--direction",
    type=str,
    choices = ["SW", "NE"],
    default = 'NE'
)
argparser.add_argument(
    "--color",
    type=int,
    choices = [0, 1],
    default=1
)
argparser.add_argument(
    "--parity",
    type=int,
    choices=[0, 1],
    default=0
)

args = argparser.parse_args()

PERIOD = args.period
TOOLKIT_FILE = args.toolkit_file
DIRECTION = args.direction

Recipe = collections.namedtuple("Recipe", ["offset", "consumed", "recipe", "min_follow"])
Partial = collections.namedtuple("Partial", ["nextgl", "time", "emits", "emits_str"])

chunks = {}
with open(TOOLKIT_FILE, 'r', encoding='utf-8') as f:
    header = True
    chunk = []
    name = ""
    for line in f:
        line = line.strip()
        if header:
            name = line
            header = False
        elif not line:
            header = True
            chunks[name] = chunk
            chunk = []
        else:
            recipe = tuple(map(int, line[:line.index('(')-2].split(',')))
            min_follow = int(re.search(r'\((\d+)\)', line).group(1))
            consumed = int(re.search(r'\{consumed:\s*(\d+)\}', line).group(1))
            offset = int(re.search(r'glider\(d(-?\d+)\)', line).group(1))
            chunk.append(Recipe(offset, consumed, recipe, min_follow))
    if chunk: chunks[name] = chunk
library = {
    (1, 1): chunks[DIRECTION + " black even"],
    (1, 0): chunks[DIRECTION + " black odd"],
    (0, 1): chunks[DIRECTION + " white even"],
    (0, 0): chunks[DIRECTION + " white odd"]
}

with open(args.salvo, 'r') as file:
    rle = file.read()
    recipe, starting_block = extract_recipe_lanes(lt.pattern(rle), enforce_signed_byte=False, relative_to='first')

    def adjust_recipe(a):
        lane, phase = a
        lane = lane + args.color
        if args.direction == 'SW':
            lane = lane * -1 + 1
        phase = phase + args.parity
        return (lane, phase)
    
    recipe = tuple(map(adjust_recipe, recipe))

Recipe = collections.namedtuple("Recipe", ["offset", "consumed", "recipe", "min_follow"])
Partial = collections.namedtuple("Partial", ["nextgl", "time", "emits", "emits_str"])

def score(pos):
    # return pos.time     # for minimum time
    return len(pos.emits) # for minimum gliders

beam = [Partial(0, -float('inf'), [], [])]
for gli in recipe:
    color = gli[0] % 2
    phase = gli[1] % 2
    gli_lane = gli[0]
    newbeam = []
    for rec in library[(color, phase)]:
        best = None
        for pos in beam:
            time = pos.time
            orig_time = time
            recipe_parity, *recipe_rest = rec.recipe

            delay = pos.nextgl + (gli_lane - rec.offset) * 4 + recipe_parity
            parity_offset = (delay - recipe_parity) % 8
            emits = list(pos.emits)
            emits_str = list(pos.emits_str)
            nextgl = pos.nextgl
            while delay < time + (recipe_parity - ((time + parity_offset) % 8)) % 8:
                if delay + PERIOD >= time + (0 - ((time + parity_offset) % 8)) % 8 + 90:
                    nextgl += PERIOD
                    delay += PERIOD
                    # send a 0, (90) glider
                    time += (0 - ((time + parity_offset) % 8)) % 8
                    emits.append(time)
                    emits_str.extend(('0', '(90)'))
                    time += 90
                elif delay + PERIOD >= time + (4 - (time % 4)) % 8 + 90:
                    nextgl += PERIOD
                    delay += PERIOD
                    # send a 4, (90) glider
                    time += (4 - ((time + parity_offset) % 8)) % 8
                    emits.append(time)
                    emits_str.extend(('4', '(90)'))
                    time += 90
                else:
                    nextgl += PERIOD * 2
                    delay += PERIOD * 2
                    # send a 2, (90) glider
                    time += (2 - ((time + parity_offset) % 8)) % 8
                    emits.append(time)
                    emits_str.extend(('2', '(90)'))
                    time += 90

            time += (recipe_parity - ((time + parity_offset) % 8)) % 8
            wait = ((delay - time) // 8) * 8
            if wait != 0 and math.isfinite(wait):
                emits_str.append(f'wait {wait}')
            emits.append(delay)
            for i in itertools.accumulate(recipe_rest):
                emits.append(delay + i)
            emits_str.extend(tuple(map(str, rec.recipe)) + (f'({rec.min_follow})',))
            nextgl += PERIOD * rec.consumed
            time = emits[-1] + rec.min_follow
            new = Partial(nextgl, time, emits, emits_str)
            if best is None or score(new) < score(best):
                best = new
        if best is not None:
            newbeam.append(best)
    beam = newbeam

beam.sort(key=score)
timings = []
ctime = 0
for i in beam[0].emits:
    timings.append(i - ctime)
    ctime = i
print("gliders =", len(timings))
print("duration =", beam[0].time)
print(timings)
print(', '.join(beam[0].emits_str))