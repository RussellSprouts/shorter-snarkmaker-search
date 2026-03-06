import numpy
import re
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
    """Outputs a life history RLE with
    the given patterns as the different colored
    states."""
    min_x = 10000000
    min_y = 10000000
    max_x = -10000000
    max_y = -10000000
    all = [green, blue, white, red, yellow, grey]
    states = [1, 2, 3, 4, 5, 6]
    for p in all:
        rect = p.getrect()
        if rect is None:
            continue
        (x, y, w, h) = rect
        max_x = max(max_x, x + w)
        min_x = min(min_x, x)
        max_y = max(max_y, y + h)
        min_y = min(min_y, y)

    W = max_x - min_x + 1
    H = max_y - min_y + 1

    data = numpy.zeros(shape=(W, H), dtype=numpy.uint8)

    for p, state in reversed(list(zip(all, states))):
        for x, y in p.coords():
            data[x - min_x, y - min_y] = state

    states = ".ABCDEF"
    result = f"x = {W}, y = {H}, rule = LifeHistory\n"
    for y in range(0, H):
        all_zeros = True
        row = ""
        for x in range(0, W):
            v = data[x, y]
            if v != 0:
                all_zeros = False
            row += states[v]
        if not all_zeros:
            result += row
        result += "$"

    # clean up trailing zeros and empty lines
    result = re.sub("\\.+\\$", "$", result)
    result = re.sub("\\$+$", "!", result)
    # apply rle
    result = re.sub("(.)\\1+", lambda x: f"{len(x.group(0))}{x.group(1)}", result)
    return result

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
