import functools
import multiprocessing
from multiprocessing import Pool
import os
from dataclasses import dataclass
import heapq
import sys
import re
import argparse
import itertools
import collections

from lifetree import lt
from gliders import mk_glider, offset_based_on_glider, single_channel_stream
from speedometer import Speedometer
from components import pattern_components
from sequence_iterator import glider_sequence_iterator, SubtreeDef


argparser = argparse.ArgumentParser(
    prog="active_region_push.py", description="Search for glider recipes that push an active region forward through space"
)

argparser.add_argument(
    '-a', '--active-region',
    help="The active region to use as a target",
    type=str,
    required=True
)
argparser.add_argument(
    '-d', '--depth',
    help="The depth to search",
    type=int,
    required=True
)
argparser.add_argument(
    '--require-'
)

argparser.add_argument(
    "--subtree",
    default=[SubtreeDef('0-255')],
    type=SubtreeDef,
    action="append",
    help="Search range. E.g. '1;90-255' to search the glider 1 followed by any glider in [90,255], or '1,3,5,7' to search the starting gliders 1,3,5 and 7. Use comma to separate at the same depth, then semicolon to separate depths. Ranges are inclusive.",
)

args = argparser.parse_args()

print((single_channel_stream((0,), -100) + single_channel_stream((0,), 100)).rle_string())

def safe_rect(p):
    return p.getrect() or (None, None, None, None)

def populate_evolution(active_region):
    result = {}
    for i in itertools.count():
        x, y, _, _ = safe_rect(active_region)
        signature = (x, y, active_region.digest())
        if signature in result:
            break

        for c in pattern_components(active_region):
            if c[4] != c and c[4].centre() == c.centre():
                # spaceship
                cx, cy, _, _ = safe_rect(c)
                if abs(cx) + abs(cy) > 512:
                    # remove far-away escaping ships
                    active_region = active_region - c

        result[signature] = i
        flipped_region = active_region("swap_xy", 1, 0)
        x, y, _, _ = safe_rect(flipped_region)
        signature2 = (x, y, flipped_region.digest())
        result[signature2] = i

        active_region = active_region[1]

    return result

evolution_map = None
digests = set()
locations = {}

def init_concurrent(p):
    global evolution_map
    evolution_map = p
    for k in p.keys():
        x, y, digest = k
        digests.add(digest)
        locations[digest] = (x, y)

@functools.lru_cache()
def rle_to_pattern(p):
    return lt.pattern(p)

def process_concurrent(p):
    active_region_rle, lane, s = p

    active_region = rle_to_pattern(active_region_rle)

    stream = single_channel_stream(s, lane)
    
    if (stream & active_region).nonempty():
        # overlapping
        return None
    
    p = stream + active_region
    p = p[sum(s) + 90]

    digest = p.digest()
    if digest in digests:
        x, y, _, _ = safe_rect(p)
        if (x, y, digest) not in evolution_map:
            x2, y2 = locations[digest]
            dx = x-x2
            dy = y-y2
            if dx < 0 and dy < 0:
                return active_region_rle, lane, s, x-x2, y-y2

    return None

if __name__ == '__main__':
    print('Calculating evolutionary sequence...')
    active_region = lt.pattern(args.active_region)
    evolution = populate_evolution(active_region)
    print(evolution)

    interaction_envelope = lt.pattern('5o$5o$5o$5o$5o').centre()
    print(interaction_envelope.getrect())
    
    def jobs():
        for active_region in (args.active_region,):
            for lane in sorted(range(-100, 100), key=abs):
                print(f"{lane=}")
                for stream in glider_sequence_iterator(subtree=args.subtree, max_depth=args.depth, min_spacing=90, max_delay=255, max_total=512):
                    yield (active_region, lane, stream)

    with Pool(processes=os.cpu_count() - 1, initializer=init_concurrent, initargs=(evolution,)) as pool:
        speedo = Speedometer()
        print("Starting...", file=sys.stderr)
        for result in pool.imap_unordered(process_concurrent, jobs(), chunksize=256):
            if result is not None:
                active_region_rle, lane, s, x, y = result
                print(result)
                active_region = rle_to_pattern(active_region_rle)
                print((active_region + single_channel_stream(s, lane)).rle_string())

            if speedo.tick(1):
                speed = speedo.get_current_speed_and_reset()
                print(speed, '/s')