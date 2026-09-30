import itertools
import functools
import collections

from lifetree import lt
from gliders import single_channel_stream, offset_based_on_glider, mk_glider
from life_history import write_life_history
from font import write_text

PI_BLOCK = offset_based_on_glider(lt.pattern("2o$2o3$3o$o$bo!"))

NORMALIZE = (0, 109, 91, 94, 91, 90, 96, 90, 91, 146, 240, 109, 91, 94, 91, 91, 92, 90, 143, 90, 91, 156, 90, 104)

with open('results/block-pushes.txt') as f:
    recipes = f.read()

unique_recipes = collections.defaultdict(set)
for r in recipes.splitlines():
    gliders = [int(''.join(glider), 16) for glider in itertools.batched(r, 2)]
    while (PI_BLOCK + single_channel_stream(gliders[0:-1]))[10000].population == 55:
        gliders.pop()

    gliders = tuple(gliders)
    unique_recipes[gliders[0:-1]].add(gliders)

final_recipes = []

for group, options in unique_recipes.items():
    best = sorted(map(lambda a: a[-1], options))[0]

    if best != 90:
        continue

    normalized_p = PI_BLOCK + single_channel_stream(group + (best,) + NORMALIZE[1:])
    normalized_p = normalized_p[20000]

    x, y, _, _ = normalized_p.getrect()
    ox, oy, _, _ = PI_BLOCK.getrect()
    depth = x + y
    odepth = ox + oy
    push = odepth - depth
    total_cost = sum(group) + best
    efficiency_score = total_cost / push

    final_recipes.append((
        efficiency_score,
        f'# {efficiency_score:0.2f} gens/depth\nlet sc_push{push} = {', '.join(map(str, group))}, ({best}) in',
        group
    ))

group = (0, 109, 90, 93, 91, 90, 95, 91, 91, 138, 157, 96, 90, 120, 91, 97, 107, 90, 90, 93)
best = 188
total_cost = sum(group) + best
push=44
efficiency_score = total_cost / push
final_recipes.append((
    efficiency_score,
    f'# {efficiency_score:0.2f} gens/depth\nlet sc_push{push} = {', '.join(map(str, group))}, ({best}) in',
    group
))


green = lt.pattern()
red = lt.pattern()
white = lt.pattern()
n_results = 0

for score, recipe, group in sorted(final_recipes):
    print(recipe)

    p = PI_BLOCK + single_channel_stream(group)
    green += p(n_results * 128, 0)

    normalized_p = PI_BLOCK + single_channel_stream(group + (best,) + NORMALIZE[1:])
    normalized_p = normalized_p[20000]

    red += (PI_BLOCK | normalized_p)(n_results * 128, 0)
    n_results += 1

print(write_life_history(
    green=green,
    red=red,
))
