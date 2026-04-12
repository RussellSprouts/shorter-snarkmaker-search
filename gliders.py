"""Helpers for working with gliders and recipes"""

from lifetree import lt

canonical_glider = lt.pattern("ooo$o$bo!")
halo = lt.pattern("3o$3o$3o!")


def mk_glider(lane, delay):
    """Makes a glider with the given
    lane and generations of delay"""
    offset = (delay + 3) // 4
    rem = (4 - delay % 4) % 4
    return canonical_glider[rem](offset - lane + (lane // 2), offset + (lane // 2))


def offset_based_on_glider(p, glider=mk_glider(0, 0)):
    """Removes the glider in the SPEBOE pattern
    and offsets the pattern based on the standard
    glider
    """
    g = p.match(glider, halo=halo)
    (x, y, _, _) = g.getrect()
    return (p - g.convolve(glider))(-x, -y)


PI_BLOCKS = list(
    map(
        offset_based_on_glider,
        [lt.pattern("2o$2o3$3o$o$bo!"), lt.pattern("2o$2o2b3o$4bo$5bo!")],
    )
)


def depth(patt):
    (x, y, w, h) = patt.getrect()
    return x + y + w + h


if depth(PI_BLOCKS[0]) != 0:
    raise "PI_BLOCKS[0] should be at depth 0 by definition"


def flip_pattern_as_if_other_pi_block(pattern):
    """Flips the pattern as if it were generated from the
    opposite pi block."""
    return pattern("swap_xy", 1, 0)

def test():
    option1 = mk_glider(0, 0) + PI_BLOCKS[0]
    option1 = option1[1024]
    option2 = mk_glider(0, 0) + PI_BLOCKS[1]
    option2 = option2[1024]

    if flip_pattern_as_if_other_pi_block(option2) != option1:
        raise "flip pattern mismatch"
test()

def extract_recipe_lanes(pattern):
    """Extracts a slow-salvo recipe from the given pattern.
    The gliders should travel to the NW and the initial target
    should be a block. There should be one extra glider at the
    end, which defines lane 0.

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
    gliders.sort(key=lambda c: c.getrect()[0])

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
            raise "Recipe contained unexpected pattern. Does the recipe travel NW and use a block as the starting target?"

        (x, y, _, _) = canonical.getrect()

        recipe.append((y - x, phase))

    last_glider, _ = recipe.pop()

    shifted = tuple((l - last_glider, p) for l, p in recipe)

    for lane, phase in shifted:
        if lane > 127 or lane < -128:
            raise f"Not supported: Recipe contains a glider on {lane}, which is out of range of a signed byte"

    return shifted, starting_block(
        last_glider, 0
    )


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


if __name__ == "__main__":
    # Builds a snark with 73 gliders
    snark_recipe_73 = lt.pattern(
        """
        2o$2o63$68b3o$68bo$69bo126$195b3o$195bo$196bo125$336bo$335b2o$335bobo
        127$455b3o$455bo$456bo124$574bo$573b2o$573bobo126$696bo$695b2o$695bobo
        127$833b3o$833bo$834bo125$959bo$958b2o$958bobo127$1084b3o$1084bo$1085b
        o126$1209b3o$1209bo$1210bo125$1348bo$1347b2o$1347bobo128$1495b3o$1495b
        o$1496bo126$1626b3o$1626bo$1627bo125$1763bo$1762b2o$1762bobo127$1881b
        3o$1881bo$1882bo126$2014b3o$2014bo$2015bo126$2112b3o$2112bo$2113bo124$
        2245bo$2244b2o$2244bobo127$2376b3o$2376bo$2377bo125$2499bo$2498b2o$
        2498bobo127$2631b3o$2631bo$2632bo125$2771bo$2770b2o$2770bobo126$2883bo
        $2882b2o$2882bobo127$3017b3o$3017bo$3018bo126$3128b3o$3128bo$3129bo
        126$3269b3o$3269bo$3270bo127$3407b3o$3407bo$3408bo126$3532b3o$3532bo$
        3533bo126$3660b3o$3660bo$3661bo126$3795b3o$3795bo$3796bo126$3913b3o$
        3913bo$3914bo126$4035b3o$4035bo$4036bo125$4163bo$4162b2o$4162bobo125$
        4269bo$4268b2o$4268bobo126$4394bo$4393b2o$4393bobo126$4516bo$4515b2o$
        4515bobo127$4656bo$4655b2o$4655bobo125$4784bo$4783b2o$4783bobo127$
        4910bo$4909b2o$4909bobo126$5025bo$5024b2o$5024bobo127$5161b3o$5161bo$
        5162bo124$5294bo$5293b2o$5293bobo127$5422b2o$5421b2o$5423bo127$5603b3o
        $5603bo$5604bo125$5708bo$5707b2o$5707bobo127$5850b3o$5850bo$5851bo125$
        5975b3o$5975bo$5976bo126$6106b3o$6106bo$6107bo126$6227b3o$6227bo$6228b
        o126$6353b3o$6353bo$6354bo126$6486b3o$6486bo$6487bo126$6613b3o$6613bo$
        6614bo126$6737b3o$6737bo$6738bo126$6865bo$6864b2o$6864bobo127$7001b3o$
        7001bo$7002bo126$7118b3o$7118bo$7119bo126$7249b3o$7249bo$7250bo126$
        7381b3o$7381bo$7382bo126$7500b3o$7500bo$7501bo125$7633bo$7632b2o$7632b
        obo126$7742b3o$7742bo$7743bo126$7880b3o$7880bo$7881bo126$8005b3o$8005b
        o$8006bo125$8130bo$8129b2o$8129bobo126$8262bo$8261b2o$8261bobo126$
        8395bo$8394b2o$8394bobo127$8517b3o$8517bo$8518bo126$8666b3o$8666bo$
        8667bo125$8800bo$8799b2o$8799bobo127$8935b3o$8935bo$8936bo126$9054b3o$
        9054bo$9055bo126$9189b3o$9189bo$9190bo126$9301b3o$9301bo$9302bo126$
        9419b2o$9418b2o$9420bo!
        """
    )
    recipe, starting_block = extract_recipe_lanes(snark_recipe_73)

    print(recipe, starting_block)

    patt = starting_block
    for i, (lane, phase) in enumerate(recipe):
        patt = patt + mk_glider(lane, 400 * i - phase)

    print(patt.rle_string())

    single_channel=[240,135,93,105,107,115,91,105,102,118,101,96,92,138,151,147,129,108,91,116,154,149,128,114,202,128,128,120,110,113,162,115,90,91,146,127,103,118,135,176,124,180,96,108,218,91,90,111,111,99,104,202,174,135,111,214,116,94,182,91,93,190,103,106,95,96,117,91,122,110,147,117,91,120,92,105,149,108,119,102,106,126,124,106,128,150,130,132,134,90,197,99,132,91,161,146,100,108,145,97,138,100,101,167,91,183,140,90,94,99,93,100,105,102,153,105,92,121,92,90,99,96,97,116,91,193,94,91,117,100,103,122,121,90,109,205,90,105,110,93,232,108,100,93,145,118,106,90,101,151,134,113,141,96,91,123,91,111,90,102,95,198,107,122,162,90,114,96,92,114,127,109,126,98,135,95,141,114,98,124,102,148,129,91,92,136,107,249,181,93,141,106,109,98,113,95,128,108,250,105,98,109,100,96,170,94,95,102,101,206,98,100,170,111,152,169,97,141,186,100,101,94,96,95,110,95,134,111,98,115,91,91,96,102,98,98,101,175,156,238,100,99,172,116,122,212,146,96,138,152,101,104,96,98,131,138,127,103,94,129,96,120,147,98,142,128]
    single_channel = single_channel + [240,109,91,94,91,90,96,90,91,146] * 21 + single_channel * 2

    patt = single_channel_stream(single_channel) + PI_BLOCKS[1]

    print(patt.rle_string())

    single_channel_recovering_block=[240,135,93,105,107,115,91,105,102,118,101,96,92,138,151,147,129,108,91,116,154,149,128,114,202,128,128,120,110,113,162,115,90,91,146,127,103,118,135,176,124,180,96,108,218,91,90,111,111,99,104,202,174,135,111,214,116,94,182,91,93,190,103,106,95,96,117,91,122,110,147,117,91,120,92,105,149,108,119,102,106,126,124,106,128,150,130,132,134,90,197,99,132,91,161,146,100,108,145,97,138,100,101,167,91,183,140,90,94,99,93,100,105,102,153,105,92,121,92,90,99,96,97,116,91,193,94,91,117,100,103,122,121,90,109,205,90,105,110,93,232,108,100,93,145,118,106,90,101,151,134,113,141,96,91,123,91,111,90,102,95,198,107,122,162,90,114,96,92,114,127,109,126,98,135,95,141,114,98,124,102,148,129,91,92,136,107,249,181,93,141,106,109,98,113,95,128,108,250,105,98,109,100,96,170,94,95,102,101,206,98,100,170,111,152,169,97,141,186,100,101,94,96,95,110,95,134,111,98,115,91,91,96,102,98,98,101,175,156,238,100,99,172,116,122,212,146,96,138,152,101,104,96,98,131,138,127,103,94,129,96,120,144,91,110,90,96,100,232]

    move_minus_10=[255,109,91,94,91,91,96,90,97,91,91,130,94,90,105,90,95,111]
    move_minus_9=[90,109,91,94,91,91,179,90,91,94,91,102,91,105,91,108,90,91,91,120,90]

    stack_snarks = single_channel_recovering_block + move_minus_10 * 5 + move_minus_9 + single_channel_recovering_block

    patt = single_channel_stream(stack_snarks) + PI_BLOCKS[1]

    print(patt.rle_string())