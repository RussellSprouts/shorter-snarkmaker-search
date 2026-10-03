
from lifetree import lt
from gliders import mk_glider, offset_based_on_glider, single_channel_stream

import functools
import multiprocessing
from multiprocessing import Pool
import os
from dataclasses import dataclass
import heapq
import sys
import re

from speedometer import Speedometer

mode = 3

seed = offset_based_on_glider(lt.pattern('$8bo$8bo$8bo2$9b3o$bo4bo2bo$bo4bo3bo$bo4bo!'))
block = lt.pattern('oo$oo')
block_pattern = lt.pattern('15b2o$15b2o5$12b2o$12b2o3$8b2o$8b2o5$31b2o$31b2o3$3b2o$3b2o16b2o$21b2o3$17b2o$17b2o2$11b2o$11b2o!')

def remove_block_patterns(p):
    locations = p.match(block_pattern)
    return p - locations.convolve(block_pattern)

def process(p):
    p = p[96 * 100]
    if p[288].population != p.population + 8*4:
        # not a blse!
        return None
    return remove_block_patterns(p).population

@dataclass(frozen=True, order=True)
class Result:
    population: int
    delay: int
    stream: tuple[int]

def process_repeated_stream(s):
    results = []
    for delay in range(90, 128):
        p = seed + single_channel_stream((0, 122, 99) + (delay,) + (s * 8)[1:])
        p2 = p[8192]
        x1, y1, w1, h1 = p2.getrect()
        x2, y2, w2, h2 = p2[288].getrect()

        if x1 - x2 != 24 or y1 - y2 != 24:
            # broke the blse
            continue
        if abs((x1 + w1) - (x2 + w2)) > 24:
            # escaping gliders
            continue
        if abs((y1 + h1) - (y2 + h2)) > 24:
            # escaping gliders
            continue
        results.append(Result(p2.population, delay, s))
    return results

if mode == 1:
    results = []
    for x in range(0, 1):
        for y in range(90, 255):
            print(x, y)
            for g in range(90, 255):
                p = seed + mk_glider(0, 128) + mk_glider(0, 128+y) + mk_glider(0, 128+y+g) # + block(x, y)
                gens = process(p)

                if gens is not None:
                    results.append((gens, p))

    results.sort(key=lambda a:a[0])
    for gens, p in results[0:10]:
        print(gens, p.rle_string())

elif mode == 2 and __name__ == '__main__':
    start = seed + single_channel_stream([0, 122, 99])
    print(start.rle_string(),file=sys.stderr)

    @functools.lru_cache(maxsize=None)
    def n_streams_summing_to(n, total=0, min=90, max=10000):
        num = 0
        for i in range(min, max):
            if i + total == n:
                num += 1
            elif i + total > n:
                break

            if i + total + min <= n:
                num += n_streams_summing_to(n, total + i, min, max)

        return num

    def streams_summing_to(n, so_far=(), total=0, min=90, max=10000):
        temp_min = min
        temp_max = max
        if len(so_far) == 0:
            temp_min = 91
            temp_max = 92
        for i in range(temp_min, temp_max):
            if i + total == n:
                yield so_far + (i,)
            elif i + total > n:
                break

            if i + total + min <= n:
                yield from streams_summing_to(n, so_far + (i,), total + i, min, max)

    multiprocessing.set_start_method('spawn')
    with Pool(processes=os.cpu_count() - 1) as pool:
        speedo = Speedometer()
        results = []
        best = float('inf')
        best_result = None
        TARGET_SUM = 384
        total = n_streams_summing_to(TARGET_SUM)
        for r in pool.imap_unordered(process_repeated_stream, streams_summing_to(TARGET_SUM)):
            for a in r:
                heapq.heappush(results, a)
                if a.population < best:
                    best = a.population
                    best_result = a
                    print('new best', a, file=sys.stderr)
            if r:
                batch_best = min(r)
                print(batch_best.population, batch_best.stream, batch_best.delay)
            if speedo.tick(1):
                current_per_s = speedo.get_current_speed_and_reset()
                avg_per_s = speedo.overall_speed()
                done = speedo.n_finished

                for a in sorted(results, reverse=True):
                    pop = a.population
                    delay = a.delay
                    stream = a.stream
                    p = seed + single_channel_stream((0, 122, 99) + (delay,) + (stream * 12)[1:])
                    print(' ', pop, delay, stream, file=sys.stderr)
                print(f'{current_per_s=} {avg_per_s=} {done=} {total=} most recent: {a.stream}',file=sys.stderr)

            while len(results) > 100:
                results.pop()

    for a in sorted(results, reverse=True):
        pop = a.population
        delay = a.delay
        stream = a.stream
        p = seed + single_channel_stream((0, 122, 99) + (delay,) + (stream * 18)[1:])
        print(pop, delay, stream, p.rle_string())
elif mode == 3:
    full_pattern = lt.pattern()
    for i, recipe in enumerate(sys.argv[1:]):
        m = re.fullmatch(r'\s*\((\d+(?:, \d+)*)\) (\d+)\s*', recipe.strip())
        if not m:
            raise SyntaxError('not a valid recipe like "(90, 91, 92) 93"')
        delay = int(m.group(2))
        stream = tuple(int(a.strip()) for a in m.group(1).split(','))
        p = seed + single_channel_stream((0, 122, 99) + (delay,) + (stream * 12)[1:])
        full_pattern += p(i * 128, 0)

    print(full_pattern.rle_string())
