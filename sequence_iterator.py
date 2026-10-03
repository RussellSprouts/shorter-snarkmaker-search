import functools
import itertools

from arg_parser import range_str_to_list

class SubtreeDef:
    options: tuple[tuple[int]]

    def __init__(self, str):
        depths = ()
        for d in str.split(";"):
            options = range_str_to_list(d)
            depths = depths + (tuple(options),)
        self.options = depths

class TreeIterator:
    def __init__(self, options_per_glider: tuple[tuple[int]], min_depth, depth, max_total):
        self.options_per_glider = options_per_glider
        self.min_depth = min_depth
        self.depth = depth
        self.max_total = max_total

    def __len__(self):
        return self.n_possibilities(0, 0)

    @functools.lru_cache(maxsize=None)
    def n_possibilities(self, gliders_so_far, gens_so_far):
        if gliders_so_far >= self.depth:
            return 0        
        total = 0
        for o in self.options_per_glider[gliders_so_far]:
            if gens_so_far + o <= self.max_total:
                if gliders_so_far + 1 >= self.min_depth:
                    total += 1
                total += self.n_possibilities(gliders_so_far + 1, gens_so_far + o)
        return total

    def __iter__(self):
        return self.iter((), 0)

    def iter(self, so_far, total):
        gliders_so_far = len(so_far)
        if gliders_so_far >= self.depth:
            return
        for o in self.options_per_glider[gliders_so_far]:
            n = so_far + (o,)
            if total + o <= self.max_total:
                if gliders_so_far + 1 >= self.min_depth:
                    yield so_far + (o,)
                yield from self.iter(n, total + o)

class CompositeTreeIterator:
    def __init__(self, iterators, len_all_options):
        self.iterators = iterators
        self.len_all_options = len_all_options

    def __iter__(self):
        return itertools.chain(*self.iterators)

    def __len__(self):
        return self.len_all_options

def glider_sequence_iterator(subtree, max_depth, min_spacing, max_delay, max_total):
    len_all_options = 0
    default_glider = tuple(range(min_spacing, max_delay + 1))
    iterators = []
    for subtree in subtree:
        iterator = TreeIterator(
            options_per_glider=subtree.options + (default_glider,) * (max_depth - len(subtree.options)),
            min_depth=len(subtree.options),
            depth=max_depth,
            max_total=max_total
        )
        iterators.append(iterator)
        len_all_options += len(iterator)

    return CompositeTreeIterator(iterators, len_all_options)
