import itertools
import math
import more_itertools
import multiprocessing
from multiprocessing import connection
import ctypes
import heapq
import random
import time
from typing import Callable
from collections import defaultdict

def part_n(x, n, minval, maxval):
    if not n * minval <= x <= n * maxval:
        return
    elif n == 0:
        yield []
    else:
        for val in range(minval, maxval + 1):
            for p in part_n(x - val, n - 1, val, maxval):
                yield [val] + p


def part(x, minval, maxval):
    min = x // maxval
    max = math.ceil(x / minval)
    return itertools.chain(*[part_n(x, n, minval, maxval) for n in range(min, max)])


def ordered_partitions(x, minval, maxval):
    return itertools.chain(
        *map(more_itertools.distinct_permutations, part(x, minval, maxval))
    )