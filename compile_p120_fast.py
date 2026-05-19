# Compiles a slow salvo to the p120 arm, processes nearly instantly
# but may have slight inefficiencies.

import itertools
import collections
import math
import sys
import re
import argparse
import pathlib
from dataclasses import dataclass
import heapq

from recipe_intermediates import RecipeDag
from gliders import extract_recipe_lanes
from lifetree import lt

argparser = argparse.ArgumentParser(
    prog="compile_p120_fast.py", description="Compile slow salvos to the p120 arm"
)
argparser.add_argument(
    "salvo",
    type=pathlib.Path,
    help="The rle file for the slow salvo."
)
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
argparser.add_argument(
    "--optimize",
    type=str,
    choices=["time", "population"],
    default="time",
)
argparser.add_argument(
    "--beam-width",
    type=int,
    default=100
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

    print("Calculating recipe dag, this may take a few seconds...")
    dag = RecipeDag(recipe, starting_block, keep_order=True)

def adjust_recipe(a):
    lane, phase = a
    lane = lane + args.color
    if args.direction == 'SW':
        lane = lane * -1 + 1
    phase = phase + args.parity
    return (lane, phase)


Recipe = collections.namedtuple("Recipe", ["offset", "consumed", "recipe", "min_follow"])

@dataclass
class Partial:
    nextgl: int
    time: int
    emits: list[int]
    emits_str: list[str]

    def __lt__(self, other):
        match args.optimize:
            case 'time':
                return (self.time, len(self.emits)) < (other.time, len(other.emits))
            case 'population':
                return (len(self.emits), self.time) < (len(other.emits), other.time)


def get_possible_gliders():
    """Finds the list of simple agnosticizations for each recipe step.
    It's a static list -- alternate gliders that are guaranteed to work
    no matter what we've sent so far"""
    possible_gliders = []
    so_far = []
    for i in range(0, len(recipe)):
        possibilities = dag.get_next(tuple(so_far))
        filtered_possibilities = list(filter(
            lambda a: a.kind != 'rephase',
            possibilities
        ))
        # append one of the possibilities since this is a static version
        so_far.append(filtered_possibilities[0])
        possible_gliders.append(filtered_possibilities)
    return possible_gliders


beam = [Partial(0, -float('inf'), [], [])]

recipe_steps = get_possible_gliders()
for step_no, step in enumerate(recipe_steps):
    print(f"Step {step_no}")
    newbeam = []
    for possible_glider in step:
        gli = adjust_recipe((possible_glider.lane, possible_glider.parity))
        color = gli[0] % 2
        phase = gli[1] % 2
        gli_lane = gli[0]
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
                heapq.heappush(newbeam, new)
                if len(newbeam) > args.beam_width:
                    newbeam.pop()

    beam = newbeam

timings = []
ctime = 0
for i in beam[0].emits:
    timings.append(i - ctime)
    ctime = i
print("gliders =", len(timings))
print("duration =", beam[0].time)
print(timings)
print(', '.join(beam[0].emits_str))