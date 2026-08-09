import math
import sys

from components import pattern_components
from lifetree import lt

glider = lt.pattern('''ooo$o$bo''')
all_gliders = []
for o in ["identity", "rot270", "rot180", "rot90"]:
    for parity in range(0, 4):
        all_gliders.append(glider(o)[parity].centre())

def rewind_glider(p, n):
    for g in all_gliders:
        m = p.match(g, halo='')
        if m.nonempty():
            m = m.convolve(g)
            break
    else:
        raise Exception(f'no glider to rewind: {p.rle_string()}')

    glider = m
    p = p - glider

    x1, y1, _, _ = glider.getrect()
    x2, y2, _, _ = glider[4].getrect()

    dx = x2 - x1
    dy = y2 - y1

    shift = math.ceil((n+1)/4)

    return p + glider(-shift * dx, -shift * dy)[4 - (n % 4)]

with open('../tandem-19/all-block-h.rle') as f:
    p = lt.pattern(f.read())

x, y, w, h = p.getrect()
print(f"{x=} {y=} {w=} {h=}")

h_block = lt.pattern('''x = 14, y = 4, rule = B3/S23
11bo$11bobo$2o9b3o$2o11bo!''')

simkin_gun = lt.pattern('''x = 33, y = 13, rule = B3/S23
24b2o5b2o$24b2o5b2o2$27b2o$27b2o4$4b2o$4b2o12bo$18bobo$2o5b2o9b3o$2o5b
2o11bo!''')

h_blocks = []
for o in ["identity", "rot270", "rot180", "rot90", "flip_x", "flip_y", "swap_xy", "swap_xy_flip"]:
    oriented = h_block(o).centre()
    simkin = simkin_gun(o)
    x, y, _, _ = simkin.match(oriented).getrect()
    h_blocks.append((oriented, simkin(-x, -y)))

results = []

print(f"Searching {w//64} seeds")

for x in range(0, w, 64):
    subp = p[x:x+64, 0:h]

    it = subp
    for i in range(0, 257):
        it = it[1]
        centred = it.centre()
        for hb, simkin in h_blocks:
            if centred == hb:
                break
        else:
            continue
        break

    if i == 256:
        print(f"Didn't turn into h? {x=}")
        continue

    x1, y1, _, _ = hb.getrect()
    x2, y2, _, _ = it.getrect()

    dx = x2 - x1
    dy = y2 - y1

    additions = simkin - hb

    seed_trial = rewind_glider(subp, 256) + additions(dx, dy)

    def is_simkin_gun(p):
        pop = p.population
        for _ in range(0, 10):
            p = p[120]
            if p.population != pop + 10:
                return False
            pop = p.population
        return True

    if is_simkin_gun(seed_trial[1024]):
        print(x // 64, i)
        print(subp.rle_string(), seed_trial.rle_string())
        print('\n\n')
        results.append(seed_trial.centre())

results.sort(key=lambda p: (len(pattern_components(p)), p.population))
results_patt = lt.pattern()
for i, p in enumerate(results):
    results_patt += p(i * 128, 0)

print(results_patt.rle_string())