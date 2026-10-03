import sys

import heapq
import math
from multiprocessing import Pool
import os
from dataclasses import dataclass

@dataclass(frozen=True)
class SerializedPattern:
    x: int
    y: int
    rle_string: str

def score(p):
    from components import pattern_components

    if p.population == 0:
        return 0
    xs = []
    ys = []
    comps = pattern_components(p)
    for c in comps:
        x, y, _, _ = c.getrect()
        xs.append(x)
        ys.append(y)

    s = 0
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)
    for x, y in zip(xs, ys):
        s += math.sqrt((x - cx)**2 + (y - cy)**2)

    s = s / len(comps)

    return s + p.population

def explore(args):
    from lifetree import lt
    from gliders import mk_glider

    pattern, so_far = args
    pattern = lt.pattern(pattern.rle_string)(pattern.x, pattern.y)
    stable_results = []
    tested_digests = set()
    def minimize(pattern, so_far, depth):
        px, py, pw, ph = pattern.getrect()
        min_lane = px - py - ph
        max_lane = px - py + pw

        for i in range(min_lane - 8, max_lane + 9):
            for parity in (255, 256):
                test = pattern + mk_glider(i, parity)
                result = test[512]
                if result == result[2]:
                    digest = result.digest() + result[1].digest() + len(so_far)
                    if digest in tested_digests:
                        continue

                    tested_digests.add(digest)
                    new_so_far = so_far + ((i, parity),)
                    x, y, _, _ = result.getrect() or (0, 0, 0, 0)
                    stable_results.append((score(result), new_so_far, SerializedPattern(x, y, result.rle_string())))
                    if depth > 0 and result.population > 0:
                        minimize(result, new_so_far, depth - 1)
    minimize(pattern, so_far, 2)
    return stable_results


if __name__ == '__main__':
    from lifetree import lt
    from gliders import mk_glider

    with open(sys.argv[1]) as f:
        rle = f.read()

    p = lt.pattern(rle)

    with Pool(processes=os.cpu_count() - 1) as pool:
        BEAM_WIDTH=32
        best = score(p)
        beam = [(best, (), SerializedPattern(p.getrect()[0], p.getrect()[1], p.rle_string()))]

        while best > 0:
            stable_results = []

            args = ((result, so_far) for sc, so_far, result in beam)
            for i, sr in enumerate(pool.imap_unordered(explore, args)):
                print(f"Processed beam {i=}")
                stable_results += sr

            stable_results.sort(key=lambda a: (a[0], len(a[1])))
            patterns = set()
            filtered_results = []
            for sc, so_far, result in stable_results:
                if result in patterns:
                    continue
                patterns.add(result)
                filtered_results.append((sc, so_far, result))

            beam = filtered_results[0:BEAM_WIDTH]
            best = filtered_results[0][0]

            for sc, so_far, result in beam[0:1]:
                pattern = p
                for i, (lane, parity) in enumerate(so_far):
                    pattern = pattern + mk_glider(lane, 256*i + parity)
                print("BEST!!!!!!!", sc, so_far, pattern.rle_string())

    print(len(stable_results))