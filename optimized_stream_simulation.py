import functools

from gliders import mk_glider, PI_BLOCKS, offset_based_on_glider
from lifetree import lt

def mk_glider_interaction_envelopes():
    """Makes a set of patterns showing the envelope of
    possible interactions with gliders"""
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
    """Gets the interaction envelope of a glider on lane 0
    with gens of delay."""
    phase = gens % 4
    shift = gens // 4
    return glider_envelopes[phase](shift, shift)

@functools.lru_cache(maxsize=None)
def target_rle_to_pattern(target_rle: str):
    return offset_based_on_glider(lt.pattern(target_rle))

@functools.lru_cache(maxsize=2**20)
def just_before_interaction_recursive(total_gens, stream, target_rle, shortest_gap):
    """Cached function which returns the resulting pattern and gens
    skipped for the last possible generation before a glider with delay shortest_gap
    would interact with the results from stream.
    """
    if not len(stream):
        return target_rle_to_pattern(target_rle), 0
    else:
        pattern, skipped = just_before_interaction_recursive(
            total_gens - stream[-1], stream[0:-1], target_rle, shortest_gap
        )
        pattern = pattern + mk_glider(0, total_gens - skipped)
        gen = skipped
        while gen < total_gens + shortest_gap:
            envelope = get_envelope(total_gens + shortest_gap - gen)
            if (envelope & pattern).nonempty():
                break
            pattern = pattern[1]
            gen += 1

        return pattern, gen


def optimized_stream_simulation(stream, target_rle, shortest_gap):
    """Returns the stream at gen sum(stream)"""
    total_gens = sum(stream) - stream[-1]
    pattern, skipped = just_before_interaction_recursive(total_gens, stream[0:-1], target_rle, shortest_gap)
    pattern = pattern + mk_glider(0, total_gens - skipped + stream[-1])
    return pattern[total_gens - skipped + stream[-1]]
