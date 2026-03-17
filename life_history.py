import lifelib

from lifetree import lt

session = lifelib.load_rules('sixstate.rule')
lht = session.lifetree()

EMPTY = lt.pattern()

def write_life_history(
    green=EMPTY,  # on
    blue=EMPTY,  # was on
    white=EMPTY,  # marked, on
    red=EMPTY,  # marked, off
    yellow=EMPTY,  # temp mark
    grey=EMPTY,  # boundary, always dead
):
    patterns = [
        lht.pattern(grey.rle_string().replace('A', 'F'))(*(grey.getrect() or (0, 0))[0:2]),
        lht.pattern(yellow.rle_string().replace('A', 'E'))(*(yellow.getrect() or (0, 0))[0:2]),
        lht.pattern(red.rle_string().replace('A', 'D'))(*(red.getrect() or (0, 0))[0:2]),
        lht.pattern(white.rle_string().replace('A', 'C'))(*(white.getrect() or (0, 0))[0:2]),
        lht.pattern(blue.rle_string().replace('A', 'B'))(*(blue.getrect() or (0, 0))[0:2]),
        lht.pattern(green.rle_string())(*green.getrect()[0:2]),
    ]

    p = sum(patterns, start=lht.pattern())

    return p.rle_string().replace('x3xsixstate', 'LifeHistory')
