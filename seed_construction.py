"""
"""
from lifetree import lt
from life_history import write_life_history
from components import pattern_components

import pathlib

seeds_path = pathlib.Path('./recipes/seeds')


def minimize_seed(p):
    result = p[2048]
    for c in pattern_components(p):
        if (p - c)[2048] == result - c:
            return minimize_seed(p - c)
    return p

green = lt.pattern()
red = lt.pattern()
i = 0

for file in seeds_path.iterdir():
    if not file.is_file():
        continue
    # print(file.name)
    with open(file, 'r') as f:
        for seed in f:
            seed = seed.strip()
            p = lt.pattern(seed)
            r = p[2048]

            green += p(i * 100, 0)
            red += r(i*100, 0)

            i += 1

print(write_life_history(
    green=green,
    red=red
))
