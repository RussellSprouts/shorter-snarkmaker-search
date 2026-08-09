"""Helpers for working with gliders and recipes"""

from lifetree import lt

canonical_glider = lt.pattern("ooo$o$bo!")

canonical_glider_info = canonical_glider.oscar()
if canonical_glider_info['displacement'] != (-1, -1):
    raise ValueError("Glider must travel NW")
canonical_glider_period = canonical_glider_info['period']

halo = lt.pattern("3o$3o$3o!")

def mk_glider(lane, delay):
    """Makes a glider with the given
    lane and generations of delay"""
    offset = (delay + canonical_glider_period - 1) // canonical_glider_period
    rem = (canonical_glider_period - delay % canonical_glider_period) % canonical_glider_period
    return canonical_glider[rem](offset - lane + (lane // 2), offset + (lane // 2))


def offset_based_on_glider(p, glider=mk_glider(0, 0)):
    """Removes the glider in the SPEBOE pattern
    and offsets the pattern based on the standard
    glider
    """
    g = p.match(glider, halo=halo)
    x, y, _, _ = g.getrect()
    return (p - g.convolve(glider))(-x, -y)

def depth(patt):
    x, y, w, h = patt.getrect()
    return x + y + w + h

def flip_pattern_as_if_other_pi_block(pattern):
    """Flips the pattern as if it were generated from the
    opposite pi block."""
    return pattern("swap_xy", 1, 0)

def extract_recipe_lanes(pattern, enforce_signed_byte = True, relative_to='last'):
    """Extracts a slow-salvo recipe from the given pattern.
    The gliders should travel to the NW and the initial target
    should be a block. If relative_to is last, there should be
    one extra glider at the end, which defines lane 0.

    Returns the recipe as Tuple[(lane, phase)], and the starting
    target block in the correct place.
    """
    starting_block = lt.pattern("")
    gliders = []
    for c in pattern.components():
        if c.population == 4:
            # remove the target starting_block
            starting_block += c
            continue
        gliders.append(c)

    # make sure the gliders are in order
    gliders.sort(key=lambda c: c.getrect()[1])

    recipe = []
    for g in gliders:
        m1 = g.match(canonical_glider, halo=halo)
        m2 = g[1].match(canonical_glider, halo=halo)
        m3 = g[2].match(canonical_glider, halo=halo)
        m4 = g[3].match(canonical_glider, halo=halo)
        phase = 1 if (m1.population or m3.population) else 0
        canonical = (
            m1
            if m1.population
            else (
                m2
                if m2.population
                else m3 if m3.population else m4 if m4.population else None
            )
        )
        if canonical is None:
            print(g.rle_string())
            raise ValueError("Recipe contained unexpected pattern. Does the recipe travel NW and use a block as the starting target?")

        x, y, _, _ = canonical.getrect()

        recipe.append((y - x, phase))

    if relative_to == 'last':
        relative_to_glider, _ = recipe.pop()
    elif relative_to == 'first':
        relative_to_glider, _ = recipe[0]
    else:
        raise ValueError(f'relative_to must be one of "first", "last". Got {relative_to}')

    shifted = tuple((l - relative_to_glider, p) for l, p in recipe)

    if enforce_signed_byte:
        for lane, phase in shifted:
            if lane > 127 or lane < -128:
                raise ValueError(f"Not supported: Recipe contains a glider on {lane}, which is out of range of a signed byte")

    return shifted, starting_block(relative_to_glider, 0)


def reconstruct(recipe, starting_block, spacing):
    start = starting_block
    for i, (lane, phase) in enumerate(recipe):
        start = start + mk_glider(lane, spacing * 4 * (i + 1) - phase)

    return start


def single_channel_stream(distances, lane=0):
    p = lt.pattern()
    total_distance = 0
    for d in distances:
        p += mk_glider(lane, d + total_distance)
        total_distance += d
    return p
