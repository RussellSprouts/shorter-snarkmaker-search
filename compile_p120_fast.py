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

args = argparser.parse_args()

PERIOD = args.period
TOOLKIT_FILE = args.toolkit_file
DIRECTION = args.direction

Recipe = collections.namedtuple("Recipe", ["offset", "consumed", "recipe", "min_follow", "to_state", "requires_state"])
SwimResult = collections.namedtuple("SwimResult", ["first_possible_time", "target", "next_glider", "emits", "emits_str"])

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
            glider_match = re.search(r'glider\(d(-?\d+)\)', line)
            offset = int(glider_match.group(1)) if glider_match else 0
            to_state_match = re.search(r'\{to state: (\d+)\}', line)
            to_state = int(to_state_match.group(1)) if to_state_match else 0
            requires_state_match = re.search(r'\{requires state: (\d+)\}', line)
            requires_state = int(requires_state_match.group(1)) if requires_state_match else 0 
            chunk.append(Recipe(offset, consumed, recipe, min_follow, to_state, requires_state))
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

    print("Calculating recipe dag, this may take a few seconds...")
    dag = RecipeDag(recipe, starting_block, keep_order=True)

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
        possibilities = dag.get_next(tuple(so_far))
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

beam = [Partial(0, -float('inf'), [], [], 0)]

recipe_steps = get_possible_gliders()
for step_no, step in enumerate(recipe_steps):
    print(f"Step {step_no}")
    newbeam = Beam()
    for possible_glider in step:
        gli = adjust_recipe((possible_glider.lane, possible_glider.parity))
        color = gli[0] % 2
        phase = gli[1] % 2
        gli_lane = gli[0]
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
                        swim_results.sort(key=lambda r: r.first_possible_time - r.target, reverse=True)
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
                next_glider += PERIOD * rec.consumed
                time = emits[-1] + rec.min_follow
                new = Partial(next_glider, time, emits, emits_str, rec.to_state)
                newbeam.add(new)
    beam = newbeam

"""
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
            recipe_parity, *recipe_rest = rec.recipe
            for pos in beam:
                # first available time we can send a glider
                time = pos.time
                # timing of the next unconsumed glider
                nextgl = pos.nextgl
                # actual time we want to send a glider
                delay = nextgl + (gli_lane - rec.offset) * 4 + recipe_parity
                emits = list(pos.emits)
                emits_str = list(pos.emits_str)
                print(gli_lane - rec.offset)

                while delay < time:
                    bestdiff = float('-inf')
                    bestnextgl = float('-inf')
                    bestdelay = float('-inf')
                    besttime = float('-inf')
                    bestemits = []
                    bestemits_str = []
                    foundvalid = False

                    for swimrec in library['swim']:
                        time2 = time + ((swimrec.recipe[0] - ((time + nextgl) % 8)) % 8)
                        emits2 = [time2]
                        for i in itertools.accumulate(swimrec.recipe[1:]):
                            emits2.append(time2 + i)
                        emits_str2 = (tuple(map(str, swimrec.recipe)) + (f'swim {swimrec.consumed}', f'({swimrec.min_follow})'))
                        time2 += sum(swimrec.recipe[1:]) + swimrec.min_follow

                        nextgl2 = nextgl + PERIOD * swimrec.consumed
                        delay2 = delay + PERIOD * swimrec.consumed

                        diff2 = delay2 - time2
                        if diff2 >= 0:
                            # this swims far enough
                            if not foundvalid or diff2 < bestdiff:
                                bestdiff = diff2
                                bestnextgl = nextgl2
                                bestdelay = delay2
                                besttime = time2
                                bestemits = emits2
                                bestemits_str = emits_str2
                                foundvalid = True
                        elif not foundvalid and diff2 > bestdiff:
                            bestdiff = diff2
                            bestnextgl = nextgl2
                            bestdelay = delay2
                            besttime = time2
                            bestemits = emits2
                            bestemits_str = emits_str2

                    nextgl = bestnextgl
                    delay = bestdelay
                    time = besttime
                    emits.extend(bestemits)
                    emits_str.extend(bestemits_str)

                time += (recipe_parity - ((time + nextgl) % 8)) % 8
                wait = ((delay - time) // 8) * 8
                if wait != 0 and math.isfinite(wait):
                    emits_str.append(f'wait {wait}')
                emits.append(delay)
                for i in itertools.accumulate(recipe_rest):
                    emits.append(delay + i)
                emits_str.extend(tuple(map(str, rec.recipe)) + (f'swim {rec.consumed}', f'({rec.min_follow})'))
                nextgl += PERIOD * rec.consumed
                time = emits[-1] + rec.min_follow
                new = Partial(nextgl, time, emits, emits_str)
                heapq.heappush(newbeam, new)
                if len(newbeam) > args.beam_width:
                    newbeam.pop()

    beam = newbeam
"""
timings = []
ctime = 0
for i in beam.best(0).emits:
    timings.append(i - ctime)
    ctime = i
print("gliders =", len(timings))
print("duration =", beam.best(0).time)
print(timings)
print(', '.join(beam.best(0).emits_str))