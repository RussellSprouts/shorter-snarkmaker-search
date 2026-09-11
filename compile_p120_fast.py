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
    "--min-follow",
    type=int,
    default=90
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
argparser.add_argument(
    "--max-stabilization-gens",
    type=int,
    default=2048
)

args = argparser.parse_args()

PERIOD = args.period
TOOLKIT_FILE = args.toolkit_file
DIRECTION = args.direction

Recipe = collections.namedtuple("Recipe", ["offset", "consumed", "recipe", "min_follow", "to_state", "requires_state", "symbol"])
SwimResult = collections.namedtuple("SwimResult", ["first_possible_time", "target", "next_glider", "emits", "emits_str"])

symbol_names = {
    'SW black even': 'g1',
    'SW black odd': 'g2',
    'SW white even': 'g3',
    'SW white odd': 'g4',
    'NE black even': 'g5',
    'NE black odd': 'g6',
    'NE white even': 'g7',
    'NE white odd': 'g8',
    'Swim': 's'
}
letters = 'abcdefghijklmnopqrstuvwxyz'
def get_letter(i):
    l = len(letters)
    if i < l:
        return letters[i]
    else:
        return letters[i % l] * (i // len(letters))

chunks = {}
with open(TOOLKIT_FILE, 'r', encoding='utf-8') as f:
    header = True
    chunk = []
    name = ""
    recipe_in_chunk = 0
    for line in f:
        line = line.strip()
        if header:
            name = line
            header = False
            recipe_in_chunk = 0
        elif not line:
            header = True
            chunks[name] = chunk
            chunk = []
        else:
            recipe = tuple(map(int, line[:line.index('(')-2].split(',')))
            min_follow = int(re.search(r'\((\d+)\)', line).group(1))
            consumed = int(re.search(r'\{consumed:\s*(\d+)\}', line).group(1))
            glider_match = re.search(r'glider\(d(-?\d+)\)', line)
            offset = int(glider_match.group(1)) if glider_match else 0
            to_state_match = re.search(r'\{to state: (\d+)\}', line)
            to_state = int(to_state_match.group(1)) if to_state_match else 0
            requires_state_match = re.search(r'\{requires state: (\d+)\}', line)
            requires_state = int(requires_state_match.group(1)) if requires_state_match else 0 
            symbol = symbol_names.get(name, '') + get_letter(recipe_in_chunk)
            recipe_in_chunk += 1
            chunk.append(Recipe(offset, consumed, recipe, min_follow, to_state, requires_state, symbol))
    if chunk: chunks[name] = chunk
library = {
    (1, 1): chunks[DIRECTION + " black even"],
    (1, 0): chunks[DIRECTION + " black odd"],
    (0, 1): chunks[DIRECTION + " white even"],
    (0, 0): chunks[DIRECTION + " white odd"],
    'swim': chunks['Swim']
}

with open(args.salvo, 'r') as file:
    rle = file.read()
    recipe, starting_block = extract_recipe_lanes(lt.pattern(rle), enforce_signed_byte=False, relative_to='first')
    starting_block = starting_block[1]

    print("Calculating recipe dag, this may take a few seconds...")
    dag = RecipeDag(recipe, starting_block, keep_order=True, max_gens=args.max_stabilization_gens)

def adjust_recipe(a):
    lane, phase = a
    lane = lane + args.color
    if args.direction == 'SW':
        lane = lane * -1 + 1
    phase = phase + args.parity
    return (lane, phase)

@dataclass
class Partial:
    nextgl: int
    time: int
    emits: list[int]
    emits_str: list[str]
    emits_symbols: list[str]
    emits_recipes: dict[str,str]
    state: int

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
        possibilities = dag.get_next(tuple(so_far), max_gens=args.max_stabilization_gens)
        filtered_possibilities = list(filter(
            lambda a: a.kind != 'rephase',
            possibilities
        ))
        # append one of the possibilities since this is a static version
        so_far.append(filtered_possibilities[0])
        possible_gliders.append(filtered_possibilities)
    return possible_gliders


class Beam:
    def __init__(self):
        self.beams_by_end_state = collections.defaultdict(list)

    def add(self, partial):
        beam = self.beams_by_end_state[partial.state]
        heapq.heappush(beam, partial)
        if len(beam) > args.beam_width:
            beam.pop()

    def __iter__(self):
        return heapq.merge(*self.beams_by_end_state.values())

    def best(self, state=None):
        if state is not None:
            return self.beams_by_end_state[state][0]
        return next(self.__iter__())

beam = [Partial(0, -float('inf'), [], [], [], {}, 0)]

recipe_steps = get_possible_gliders()
for step_no, step in enumerate(recipe_steps):
    print(f"Step {step_no}")
    newbeam = Beam()
    for possible_glider in step:
        gli = adjust_recipe((possible_glider.lane, possible_glider.parity))
        color = gli[0] % 2
        phase = gli[1] % 2
        gli_lane = gli[0]
        print(f"  {color=} {phase=} {gli_lane=}")

        for rec in library[(color, phase)]:
            # the mod 8 timing of the first glider
            # and the rest
            recipe_parity, *recipe_rest = rec.recipe

            # try each recipe on each position in the beam
            for pos in beam:
                if rec.requires_state != pos.state:
                    continue
                first_possible_time = pos.time
                next_glider = pos.nextgl
                target = pos.nextgl + (gli_lane - rec.offset) * 4 + recipe_parity
                offset = (target - recipe_parity) % 8
                emits = list(pos.emits)
                emits_str = list(pos.emits_str)
                emits_symbols = list(pos.emits_symbols)
                emits_recipes = dict(pos.emits_recipes)

                if pos.state != 0 and target < first_possible_time:
                    # we can't use swim recipes except in state 0
                    continue

                while target < first_possible_time:
                    swim_results = []

                    for swimrec in library['swim']:
                        swim_parity = swimrec.recipe[0]
                        swim_recipe_start = first_possible_time + (swim_parity - first_possible_time + offset) % 8
                        swim_emits = [swim_recipe_start]
                        swim_emits_str = (tuple(map(str, swimrec.recipe)) + (f'swim {swimrec.consumed}', f'({swimrec.min_follow})'))
                        for i in itertools.accumulate(swimrec.recipe[1:]):
                            swim_emits.append(swim_recipe_start + i)
                        swim_results.append(SwimResult(
                            first_possible_time=swim_emits[-1] + swimrec.min_follow,
                            target=target + PERIOD * swimrec.consumed,
                            next_glider=next_glider + PERIOD * swimrec.consumed,
                            emits=swim_emits,
                            emits_str=swim_emits_str,
                        ))

                    solutions = list(filter(lambda r: r.target > r.first_possible_time, swim_results))

                    if solutions:
                        # if there are recipes that move us far enough,
                        # take the fastest one
                        solutions.sort(key=lambda r: r.first_possible_time)
                        best = solutions[0]
                    else:
                        # otherwise take the one that brings us closest.
                        swim_results.sort(key=lambda r: r.first_possible_time - r.target)
                        best = swim_results[0]

                    first_possible_time = best.first_possible_time
                    target = best.target
                    offset = (target - recipe_parity) % 8
                    next_glider = best.next_glider
                    emits.extend(best.emits)
                    emits_str.extend(best.emits_str)

                wait = ((target - first_possible_time) // 8) * 8
                if wait != 0 and math.isfinite(wait):
                    emits_str.append(f'wait {wait}')
                emits.append(target)
                for i in itertools.accumulate(recipe_rest):
                    emits.append(target + i)
                emits_str.extend(tuple(map(str, rec.recipe)) + (f'swim {rec.consumed}', f'({rec.min_follow})'))
                emits_symbols.append(f'{rec.symbol}(d{gli_lane})')
                rec_desc = f'let {rec.symbol}(d{rec.offset + int(args.direction == 'SW')}) = {recipe_parity}, {', '.join(map(str, recipe_rest))}, swim {rec.consumed}, ({rec.min_follow}) in'
                if rec.requires_state > 0:
                    rec_desc += f' # (requires state {rec.requires_state})'
                if rec.to_state > 0:
                    rec_desc += f' # (to state {rec.to_state})'
                emits_recipes[rec.symbol] = rec_desc

                next_glider += PERIOD * rec.consumed
                time = emits[-1] + rec.min_follow
                new = Partial(next_glider, time, emits, emits_str, emits_symbols, emits_recipes, rec.to_state)
                newbeam.add(new)
    beam = newbeam

timings = []
ctime = 0
for i in beam.best(0).emits:
    timings.append(i - ctime)
    ctime = i
print("gliders =", len(timings))
print("duration =", beam.best(0).time)
print(timings)
print(', '.join(beam.best(0).emits_str))
print("#######################################################")
print('\n'.join(sorted(beam.best(0).emits_recipes.values())))
emits_symbols = beam.best(0).emits_symbols
max_width = max(len(a) for a in emits_symbols)
for group in itertools.batched(beam.best(0).emits_symbols, 10):
    print(''.join(f'{a}, '.ljust(max_width+2) for a in group))
