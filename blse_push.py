
from lifetree import lt
from gliders import mk_glider, offset_based_on_glider, single_channel_stream

import multiprocessing
from multiprocessing import Pool
import os

mode = 2

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

def process_repeated_stream(s):
    results = []
    for delay in range(90, 128):
        p = seed + single_channel_stream((0, 122, 99) + (delay,) + (s * 12)[1:])
        p2 = p[4096]
        x1, _, _, _ = p2.getrect()
        x2, _, _, _ = p2[288].getrect()

        if x1 - x2 != 24:
            # broke the blse
            continue
        if p2.population < 359:
            print(p2.population, delay, s, p.rle_string())
        results.append((p2.population, delay, s))
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
    print(start.rle_string())

    def streams_summing_to(n, so_far=(), total=0, min=90, max=10000):
        for i in range(min, max):
            if i + total == n:
                yield so_far + (i,)
            elif i + total > n:
                break

            if i + total + min <= n:
                yield from streams_summing_to(n, so_far + (i,), total + i, min, max)

    multiprocessing.set_start_method('spawn')
    with Pool(processes=os.cpu_count() - 1) as pool:
        results = []
        best = float('inf')
        for r in pool.imap_unordered(process_repeated_stream, streams_summing_to(384)):
            for a in r:
                if a[0] < best:
                    best = a[0]
                    print(a)
            results.extend(r)

    results.sort(key=lambda a: a[0], reverse=True)
    for pop, delay, stream, p in results:
        print(pop, delay, stream, p.rle_string())
    print(list(streams_summing_to(192)))