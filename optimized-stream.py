from snark import *
import time
from typing import Tuple
import functools


def mk_glider_interaction_envelopes():
    neighbors = lt.pattern("5o$5o$5o$5o$5o")(-2, -2)
    dot = lt.pattern("o")
    dot_envelope = lt.pattern("")
    for i in range(0, 64):
        dot_envelope += dot
        dot = dot(1, 1)
    dot_envelope = dot_envelope.convolve(neighbors)
    gliders = [mk_glider(0, 0), mk_glider(0, 1), mk_glider(0, 2), mk_glider(0, 3)]
    return [g.convolve(dot_envelope) for g in gliders]

glider_envelopes = mk_glider_interaction_envelopes()

def get_envelope(gens):
    phase = gens % 4
    shift = gens // 4
    return glider_envelopes[phase](shift, shift)

@functools.lru_cache(maxsize=2**20)
def just_before_interaction_recursive(total_gens, stream, shortest_gap=90):
    if not len(stream):
        return PI_BLOCKS[0], 0
    else:
        pattern, skipped = just_before_interaction_recursive(total_gens - stream[-1], stream[0:-1])
        pattern = pattern + mk_glider(0, total_gens - skipped)
        gen = skipped
        while gen < total_gens + shortest_gap:
            envelope = get_envelope(total_gens + shortest_gap - gen)
            if (envelope & pattern).nonempty():
                break
            pattern = pattern[1]
            gen += 1

        return pattern, gen

def optimized_stream_simulation(stream):
    """Returns the stream at gen sum(stream)"""
    total_gens = sum(stream) - stream[-1]
    pattern, skipped = just_before_interaction_recursive(total_gens, stream[0:-1])
    pattern = pattern + mk_glider(0, total_gens - skipped + stream[-1])
    return pattern[total_gens - skipped + stream[-1]]

# Returns the pattern state and number of generations simulated
# to the point where it would interact with a glider 90 ticks
# afterward
def just_before_interaction(stream):
    total = sum(stream)
    pattern = single_channel_stream(stream) + PI_BLOCKS[0]
    gens = total + 90
    while gens > 0:
        envelope = get_envelope(gens)
        if (envelope & pattern).nonempty():
            break
        pattern = pattern[1]
        gens -= 1

    return pattern, total - gens + 90


def verify(s):
    total = sum(s)
    pattern, skipped = just_before_interaction(s)
    shortcut = pattern + mk_glider(0, total - skipped + 90)
    longway = single_channel_stream(s + [90]) + PI_BLOCKS[0]

    recursive, skipped2 = just_before_interaction_recursive(sum(s), tuple(s))
    recursive = recursive + mk_glider(0, total - skipped2 + 90)

    print('values', total, skipped, skipped2)
    print('shortcut', shortcut.rle_string())
    print('long', longway[skipped].rle_string())
    print('recursive', recursive.rle_string())
    print(shortcut == longway[skipped] == recursive)

verify([0, 90, 100, 110])

def verify2(s):
    longway = single_channel_stream(s) + PI_BLOCKS[0]
    longway = longway[sum(s)]

    shortcut = optimized_stream_simulation(s)

    return longway == shortcut
    

for i in range(90, 100):
    for j in range(90, 100):
        for k in range(90, 100):
            matches = verify2((i, j, k))
            if not matches:
                raise ValueError(f"not equal {i} {j} {k}")
