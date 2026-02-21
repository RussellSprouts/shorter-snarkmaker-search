from collections import defaultdict
from dataclasses import dataclass, field
from typing import List, Any, Tuple
import json
import heapq
import sys
import argparse
from functools import cache, cached_property
import weakref
import numpy
import re
import math
from multiprocessing import Pool, connection
import multiprocessing
import functools

from speedometer import Speedometer
from font import write_text
from lifetree import lt
from gliders import canonical_glider
from optimized_stream_simulation import optimized_stream_simulation

halo = lt.pattern("3o$3o$3o!")

# Snark slow salvo recipe
# Includes the initial target block and
# a sample glider which will travel down the track
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


def preprocess_snark_recipe(snark_recipe):
    blocks = lt.pattern("")
    gliders = []
    for c in snark_recipe.components():
        if c.population == 4:
            # remove the target blocks
            blocks = blocks + c
            continue
        gliders.append(c)

    # make sure the gliders are in order
    gliders.sort(key=lambda c: c.getrect()[0])

    # remove the demo glider which travels through the snark
    snark_glider = gliders.pop()
    (snark_glider_x, snark_glider_y, _, _) = snark_glider.getrect()
    snark_glider_offset = snark_glider_y - snark_glider_x

    recipe = []
    for g in gliders:
        m1 = g.match(canonical_glider, halo=halo)
        m2 = g[1].match(canonical_glider, halo=halo)
        m3 = g[2].match(canonical_glider, halo=halo)
        m4 = g[3].match(canonical_glider, halo=halo)
        phase = m1.population or m3.population
        canonical = (
            m1
            if m1.population
            else m2 if m2.population else m3 if m3.population else m4
        )

        (x, y, _, _) = canonical.getrect()

        # offset so that the single-channel lane that the
        # snark reflects will be 0.
        recipe.append((y - x - snark_glider_offset, phase))

    return recipe, snark_glider_offset, blocks


# recipe is the sequence of glider lanes and phases
# snark_glider_offset is the x offset to make the snark input
#   lane equal 0
# blocks is the initial elbow
# elbow_depth_offset is the offset to make the starting elbow
#   block depth equal 0
recipe, snark_glider_offset, blocks = preprocess_snark_recipe(snark_recipe_73)


def mk_glider(lane, delay):
    """Makes a glider with the given
    lane and generations of delay"""
    offset = (delay + 3) // 4
    shift = snark_glider_offset + lane
    rem = (4 - delay % 4) % 4
    return canonical_glider[rem](offset - shift + (shift // 2), offset + (shift // 2))


def offset_based_on_glider(p):
    """Removes the glider in the SPEBOE pattern
    and offsets the pattern based on the standard
    glider
    """
    standard_glider = mk_glider(0, 0)
    g = p.match(standard_glider, halo=halo)
    (x, y, _, _) = g.getrect()
    return (p - g.convolve(standard_glider))(-x, -y)


PI_BLOCKS = list(
    map(
        offset_based_on_glider,
        [lt.pattern("2o$2o2b3o$4bo$5bo!"), lt.pattern("2o$2o3$3o$o$bo!")],
    )
)


def find_elbow_depth_offset():
    (blocks_x, blocks_y, _, _) = PI_BLOCKS[0].getrect()
    return blocks_x + blocks_y


elbow_depth_offset = find_elbow_depth_offset()
print("elbow depth offset", elbow_depth_offset)


def find_pattern_flip_offset():
    option1 = PI_BLOCKS[0] + mk_glider(0, 0) + mk_glider(0, 97)
    option1 = option1[1024]
    option2 = PI_BLOCKS[1] + mk_glider(0, 0) + mk_glider(0, 97)
    option2 = option2[1024]("swap_xy")

    (x1, y1, _, _) = option1.getrect()
    (x2, y2, _, _) = option2.getrect()

    return (x1 - x2, y1 - y2)


pattern_flip_offset = find_pattern_flip_offset()


def flip_pattern_to_other_side(pattern):
    """Flips the pattern as if it started with the other pi block"""
    return pattern.transform("swap_xy")(pattern_flip_offset[0], pattern_flip_offset[1])


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
    result = f"x = {min_x}, y = {min_y}, rule = LifeHistory\n"
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


# https://conwaylife.com/wiki/Most_common_objects_on_Catagolue
# Very simple heuristic to see how unlikely a constellation
# of objects is. Use log probabilities so they can be summed.
probabilities = {
    lt.pattern("2o$2o").octodigest(): math.log(1 / 3.24),  # block
    lt.pattern("3o").octodigest(): math.log(1 / 3.49),  # blinker
    lt.pattern("boo$obbo$boo").octodigest(): math.log(1 / 6.11),  # beehive
    lt.pattern("b2o$o2bo$bobo$2bo!").octodigest(): math.log(1 / 20.7),  # loaf
    lt.pattern("bo$obo$2o!").octodigest(): math.log(1 / 22.4),  # boat
    lt.pattern("b2o$obo$2o!").octodigest(): math.log(1 / 32.5),  # ship
    lt.pattern("bo$obo$bo!").octodigest(): math.log(1 / 103),  # tub
    lt.pattern("b2o$o2bo$o2bo$b2o!").octodigest(): math.log(1 / 106),  # pond
    lt.pattern("2o$obo$2bo$2b2o!").octodigest(): math.log(1 / 6407),  # eater 1
}


def get_pattern_frequency(pattern: PatternRef):
    return probabilities.get(pattern.octodigest, float("-inf"))


def recipe_str(recipe):
    """Writes the recipe as a string"""
    res = []
    for lane, phase in recipe:
        res.append(f"{lane}{'a' if phase else 'b'}")
    return ",".join(res)


def reconstruct(recipe, spacing):
    start = blocks
    for i, (lane, phase) in enumerate(recipe):
        start = start + mk_glider(lane, spacing * 4 * (i + 1) - phase)

    return start


snark = reconstruct(recipe, 100)[50000]


@cache
def recipe_from_json(so_far, remaining):
    pattern = reconstruct(so_far, 100)[400 * len(so_far) + 1024]
    (x, y, _, _) = pattern.getrect()
    return Recipe(
        so_far=so_far,
        remaining=remaining,
        digest=pattern.digest(),
        x=x,
        y=y,
        pattern=pattern,
    )


@dataclass(eq=True, unsafe_hash=True)
class Recipe:
    # The slow gliders we've sent so far
    so_far: tuple
    # The slow gliders still remaining to send
    remaining: tuple
    digest: int
    x: int
    y: int
    pattern: Any = field(compare=False)

    def rle_string(self):
        p = reconstruct(self.so_far, 100)
        p = p[400 * len(self.so_far)]
        return p.rle_string()

    def to_json(self):
        return {
            "so_far": self.so_far,
            "remaining": self.remaining,
        }

    def from_json(j):
        return recipe_from_json(
            tuple(map(tuple, j["so_far"])), tuple(map(tuple, j["remaining"]))
        )

    @cached_property
    def score(self):
        """How much to weight a chance of partially
        acheiving this pattern
        """
        return 1.1 ** len(self.so_far)

    @cached_property
    def total_probability(self):
        """Estimated relative log probability of all of the components
        appearing randomly."""
        prob = 0
        for c in self.pattern.components():
            d = c.octodigest()
            prob = prob + probabilities.get(d, float("-inf"))
        return prob


# At first, we only have the starting block, with
# all gliders to go.
first_recipe = Recipe(
    so_far=(),
    remaining=tuple(recipe),
    digest=blocks.digest(),
    x=blocks.getrect()[0],
    y=blocks.getrect()[1],
    pattern=blocks,
)


def recipe_cache_from_json():
    pass


class RecipeGraph:
    """We have one known snark recipe with 73 gliders.
    However, the order is not strict. At many we points,
    we have options for which glider to send next. This
    class lazily computes possible recipes based on what
    we've discovered so far. It's possible we get lucky
    and find a reaction which does the work of multiple
    gliders, so we might explore ahead multiple steps.
    """

    def __init__(self):
        # a map of recipe to list of possible next recipes
        self.cache = {}
        self.end_target = reconstruct(recipe, 100)[30000]

    def explore(self, recipe: Recipe, depth=1, width=1):
        """
        Explores {depth} steps from the given recipe.
        Tries re-arranging the remaining gliders in the
        recipe to find which gliders could possibly come next.
        To do this, it grabs a section of 1 to {width} gliders
        from later in remaining and tries a new recipe with
        those gliders coming first, then the rest of the
        remaining gliders, in order. If the recipe is still
        successful, then we say that the first grabbed glider
        is a possible next glider, and insert a new recipe.
        Once we've shown that a next glider is possible, we
        don't try larger widths.
        """
        if recipe in self.cache:
            return self.cache[recipe]
        self.cache[recipe] = []
        # try grabbing up to width gliders from later in
        # the recipe and bring them forward
        r = recipe.remaining
        for g in range(0, len(r)):
            for w in range(1, width + 1):
                # grab w gliders starting at index g in remaining,
                # and move them to the start of remaining.
                new_so_far = (*recipe.so_far, r[g])
                new_remaining = (*r[g + 1 : g + w], *r[0:g], *r[g + w :])
                if len(new_remaining) != len(r) - 1:
                    raise Exception("Hello")
                lane, phase = r[g]
                p = recipe.pattern + mk_glider(lane, 400 - phase)
                p = p[1024]
                new_pattern = p

                for lane, phase in new_remaining:
                    p = p + mk_glider(lane, 400 - phase)
                    p = p[1024]
                    if p != p[2]:
                        # didn't settle, failed
                        break
                if p == self.end_target:
                    new_digest = new_pattern.digest()
                    (x, y, _, _) = new_pattern.getrect()
                    self.cache[recipe].append(
                        Recipe(
                            so_far=new_so_far,
                            remaining=new_remaining,
                            digest=new_digest,
                            x=x,
                            y=y,
                            pattern=new_pattern,
                        )
                    )
                    break

        if depth > 1:
            for r in self.cache[recipe]:
                self.explore(r, depth - 1)

        return self.cache[recipe]

    def stamp_collection(self, include_glider=False):
        """Returns a pattern showing the different
        intermediate steps possible in the RecipeGraph"""
        all_items = {}
        for k, r in self.cache.items():
            all_items[(k.digest, k.x, k.y)] = k
            for ri in r:
                all_items[(ri.digest, ri.x, ri.y)] = ri

        groups = defaultdict(list)
        for r in all_items.values():
            groups[len(r.remaining)].append(r)

        best_p = None
        best_p_score = (1000, 1000)

        patt = lt.pattern("")
        for k, v in groups.items():
            v.sort(key=lambda p: p.pattern.population)
            for i, p in enumerate(v):
                if (k, p.pattern.population) < best_p_score:
                    best_p = p
                    best_p_score = (k, p.pattern.population)
                if len(p.remaining):
                    lane, phase = p.remaining[0]
                    patt = patt + (
                        p.pattern
                        + (
                            mk_glider(lane, 128 - phase)
                            if include_glider
                            else lt.pattern()
                        )
                    )(i * 100, -k * 100)
                else:
                    patt = patt + p.pattern(i * 100, -k * 100)

        patt = patt + best_p.pattern
        for i, (lane, phase) in enumerate(best_p.remaining):
            patt = patt + mk_glider(lane, 400 - phase)(i * 100, i * 100)

        return patt

    def all_recipes(self):
        return set(
            list(self.cache.keys()) + [item for l in self.cache.values() for item in l]
        )

    def to_json(self):
        all_recipes = self.all_recipes()
        recipe_ids = {}
        next_id = 0
        for x in all_recipes:
            recipe_ids[x] = next_id
            next_id += 1
        return {
            "recipes": [
                {"id": recipe_ids[x], "recipe": x.to_json()} for x in all_recipes
            ],
            "transitions": {
                recipe_ids[k]: [recipe_ids[r] for r in v] for k, v in self.cache.items()
            },
        }

    def from_json(j):
        result = RecipeGraph()
        recipes = j["recipes"]
        recipes_by_id = {}
        for r in recipes:
            id = r["id"]
            recipe = Recipe.from_json(r["recipe"])
            recipes_by_id[id] = recipe

        transitions = j["transitions"]
        for k, vs in transitions.items():
            k = int(k)
            recipe = recipes_by_id[k]
            result.cache[recipe] = [recipes_by_id[v] for v in vs]
        return result

    def unique_patterns(self):
        recipes_by_digest_xy = {}
        for r in self.all_recipes():
            recipes_by_digest_xy[(r.digest, r.x, r.y)] = r
        return recipes_by_digest_xy.values()


def relative_probability(pattern):
    """
    Calculate a score for how unlikely a constellation
    of objects is. A log probability.
    """
    prob = 1
    for c in pattern.components():
        digest = c.octodigest()
        c_prob = probabilities.get(digest, -10000000)
        prob += c_prob
    return prob


def explore_common_precursors(recipe_cache, first_recipe, depth, width, max_pool):
    """
    Does a small beam search of the recipe cache, starting from
    the first recipe, expanding branches that have common objects
    and low population. This helps seed the search with precursors
    that might be found from crashing gliders.
    """

    # Explore for intermediates with small population.
    pool = {(first_recipe.digest, first_recipe.x, first_recipe.y): first_recipe}

    def sort_pool():
        return sorted(
            pool.values(),
            key=lambda r: (
                len(r.remaining),
                relative_probability(r.pattern),
                r.pattern.population,
            ),
        )

    for i in range(0, depth):
        print("Searching depth", i, file=sys.stderr, flush=True)
        sample = sort_pool()[0:max_pool]
        for s in sample:
            next_results = recipe_cache.explore(s, depth=1, width=width)
            for n in next_results:
                pool[(n.digest, n.x, n.y)] = n

    print(recipe_cache.stamp_collection(include_glider=True).rle_string())


def mk_recipe_graph():
    """Explores the RecipeGraph to find possible
    precursors for the snark, printing out the unique
    intermediate patterns."""
    recipe_cache = RecipeGraph()
    explore_common_precursors(
        recipe_cache, first_recipe, depth=73, width=72, max_pool=65536
    )
    print(json.dumps([r.to_json() for r in recipe_cache.unique_patterns()]))


print("Loading recipe intermediates", file=sys.stderr)
with open("recipe-intermediates.json", "r") as recipe_intermediates_file:
    recipe_intermediates = [
        Recipe.from_json(r) for r in json.loads(recipe_intermediates_file.read())
    ]


def try_to_save_gliders(recipe_cache, min_lane=-40, max_lane=40):
    """
    Given an explored RecipeGraph, checks each node
    to see if a single glider can skip ahead more than
    one step.
    """
    all_items = {}
    for k, r in recipe_cache.cache.items():
        all_items[(k.digest, k.x, k.y)] = k
        for ri in r:
            all_items[(ri.digest, ri.x, ri.y)] = ri

    for r in all_items.values():
        for lane in range(min_lane, max_lane + 1):
            for phase in (0, 1):
                p = r.pattern + mk_glider(lane, 400 - phase)
                p = p[1024]
                digest = p.digest()
                (x, y, _, _) = p.getrect() or (0, 0, 0, 0)
                k = (digest, x, y)
                if k in all_items:
                    new_pattern = all_items[k]
                    if len(new_pattern.remaining) < len(r.remaining) - 1:
                        print("SAVED!", r.so_far, new_pattern.remaining)
                    else:
                        print("REDISCOVERED")


@dataclass(eq=True, unsafe_hash=True)
class PatternRef:
    """
    A reference to a pattern, with a unique ID
    for JSON storage.
    """

    pattern: Any = field(compare=False)
    id: int

    def __repr__(self):
        return f"pat{self.id}"

    def to_json(self):
        return self.id

    def from_json(j, pattern_cache):
        return pattern_cache.by_int(j)

    @cached_property
    def population(self):
        return self.pattern.population

    @cached_property
    def octodigest(self):
        return self.pattern.octodigest()


class PatternCache:
    """
    Caches patterns with a unique ID object based
    on the digest and position.
    """

    def __init__(self):
        self.next_id = 0
        # Map of (digest, x, y) to PatternRef
        # Weak values, so the cache will only keep
        # references if someone is holding the PatternRef
        # This should prevent leaking Pattern objects,
        # which slows the C API to a crawl.
        self.cache = weakref.WeakValueDictionary()

    def id(self, pattern):
        digest = pattern.digest()
        (x, y, _, _) = pattern.getrect()
        key = (digest, x, y)
        existing = self.cache.get(key, None)
        if existing:
            return existing
        self.next_id = self.next_id + 1
        r = PatternRef(pattern, self.next_id)
        self.cache[key] = r
        return r

    # Keep references from JSON alive until
    # after all JSON objects are deserialized.
    forced_id_to_ref = {}

    def by_int(self, n):
        return self.forced_id_to_ref[n]

    def json_loading_done(self):
        """
        After JSON is done loading, clear the forced
        IDs so they can be garbage collected"""
        self.forced_id_to_ref.clear()

    def _set_id(self, pattern, id):
        """
        Stores the pattern and sets the ID
        """
        stored_id = self.id(pattern)
        self.forced_id_to_ref[id] = stored_id
        stored_id.id = id

    def to_json(self):
        return {
            "next_id": self.next_id,
            "cache": {
                pattern_ref.id: pattern_ref.pattern.rle_string()
                for pattern_ref in self.cache.values()
            },
        }

    def from_json(j):
        r = PatternCache()
        for id, rle_string in j["cache"]:
            id = int(id)
            pattern = lt.pattern(rle_string)
            r.force_keep[id] = r._set_id(pattern, id)
        r.next_id = j["next_id"]


class ComponentSearch:
    """Class to help search for partial matches of
    recipes in glider results.
    """

    def __init__(self, pattern_cache):
        self.pattern_cache = pattern_cache
        # map of PatternRef to set of Recipes which contain
        # the pattern
        self.component_to_recipe = defaultdict(set)
        # Map of Recipe to set of PatternRef components
        self.recipe_to_components = {}

    def add_recipe(self, recipe: Recipe):
        """Adds the recipe as a target to
        search."""
        if recipe in self.recipe_to_components:
            # avoid double counting
            return
        components = set(map(self.pattern_cache.id, recipe.pattern.components()))
        self.recipe_to_components[recipe] = components
        for pr in components:
            self.component_to_recipe[pr].add(recipe)

    def overlapping_recipes(self, components: List[PatternRef]):
        """Given a list of components, returns a map of
        recipe to set of components that are overlapping"""
        result = defaultdict(set)
        for c in components:
            recipes = self.component_to_recipe.get(c, set())
            for r in recipes:
                result[r].add(c)
        return result

    def recipe_components(self, recipe):
        """Given a recipe, returns the set of components
        in that recipe"""
        return self.recipe_to_components[recipe]


pattern_cache = PatternCache()
component_search = ComponentSearch(pattern_cache)
for r in recipe_intermediates:
    component_search.add_recipe(r)


def pattern_components(cache, pattern):
    return set(map(cache.id, pattern.components()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="snark.py",
        description="Finds an optimized single-channel recipe for the snark.",
    )

    parser.add_argument(
        "--target-depth",
        default=2,
        type=int,
        help="How many steps to look ahead in the slow salvo recipe. A lucky reaction could theoretically do the work of multiple slow salvo gliders.",
    )

    parser.add_argument(
        "--salvo-size",
        default=4,
        type=int,
        help="How many gliders to send in each salvo to find",
    )

    args = parser.parse_args()

    print(args)


def single_channel_stream(distances, lane=0):
    p = lt.pattern()
    total_distance = 0
    for d in distances:
        p += mk_glider(lane, d + total_distance)
        total_distance += d
    return p


def recursive_priority_process_wrapper(queue, pipe, f):
    while True:
        id = None
        try:
            s = queue.get()
            if not s:
                print(f"S is {s}")
                continue
            id = s[0]
            args = s[1]
            if id == "stop":
                return
            new_jobs = []

            def add_to_queue(cost, data):
                new_jobs.append((cost, data))

            res = f(args, queue=add_to_queue)
            pipe.send((id, "ok", res, new_jobs))
        except Exception as e:
            pipe.send((id, "err", e, []))
            raise
        finally:
            queue.task_done()


class PendingTracker:
    """
    Keeps track of the number of tasks of a specific
    generation cost that are pending in the pool.
    """

    def __init__(self):
        # a heap of [cost, n_pending]
        # only one entry for each cost
        self.pending_heap = []
        # a dict of cost -> heap entry
        self.pending_items = {}
        # the total number of pending tasks
        self.n_pending = 0

    def mark_pending(self, cost):
        self.n_pending += 1
        if cost in self.pending_items:
            pend = self.pending_items[cost]
            pend[1] = pend[1] + 1
        else:
            pend = [cost, 1]
            self.pending_items[cost] = pend
            heapq.heappush(self.pending_heap, pend)

    def mark_done(self, cost):
        if cost not in self.pending_items:
            raise KeyError(f"{cost} marked done but not pending")
        self.n_pending -= 1
        pend = self.pending_items[cost]
        pend[1] = pend[1] - 1
        if pend[1] == 0:
            # clear out the zero entries.
            while len(self.pending_heap) and self.pending_heap[0][1] == 0:
                p = heapq.heappop(self.pending_heap)
                to_delete = p[0]
                del self.pending_items[to_delete]

    def min_cost_pending(self):
        if len(self.pending_heap):
            return self.pending_heap[0][0]
        return float("inf")


def recursive_priority_imap_unordered(fn, initial_items, n_processes=20):
    """Given a function and a list of (priority, data) pairs, applies
    fn to data in priority order across multiple processes. Yields
    (data, fn(data)) pairs in an arbitrary order.
    fn will also receive a keyword argument queue, which is a callback
    which accepts a (priority, data) pair, and adds it to the queue
    to be processed. To maintain the priority order, the priority must
    be strictly greater than the current priority.
    """
    with multiprocessing.Manager() as manager:
        next_id = 0
        id_to_args = {}
        local_queue = list(initial_items)
        heapq.heapify(local_queue)
        pending_tracker = PendingTracker()
        pending_queue = manager.JoinableQueue()
        readers = []
        processes = []
        for i in range(0, n_processes):
            r, w = multiprocessing.Pipe()
            readers.append(r)
            p = multiprocessing.Process(
                target=recursive_priority_process_wrapper,
                args=(pending_queue, w, fn),
            )
            processes.append(p)
            p.start()

        def send_tasks(max_val):
            nonlocal next_id
            while len(local_queue) and local_queue[0][0] < max_val:
                item = heapq.heappop(local_queue)
                priority, args = item
                pending_tracker.mark_pending(priority)
                id_to_args[next_id] = item
                pending_queue.put((next_id, args))
                next_id = next_id + 1

        # start the first tasks.
        send_tasks(local_queue[0][0] + 1)

        while pending_tracker.n_pending:
            for r in connection.wait(readers):
                id, status, result, new_jobs = r.recv()
                priority, args = id_to_args[id]
                del id_to_args[id]
                pending_tracker.mark_done(priority)

                def queue(new_jobs=new_jobs):
                    for j in new_jobs:
                        heapq.heappush(local_queue, j)
                    send_tasks(pending_tracker.min_cost_pending() + 1)

                yield (args, result, new_jobs, queue, pending_tracker, local_queue)

        for i in range(0, n_processes):
            pending_queue.put(("stop", None))
        pending_queue.join()
        for p in processes:
            p.join()


@dataclass(order=True)
class StreamJob:
    stream: bytes
    starting_block: int
    next_possibilities: bytes


@dataclass(order=True)
class StreamResult:
    next_possibility: int
    digest: int
    before_hit_digest: int
    x: int
    y: int
    max_lane: int
    next_highest_lane: int
    population: int


@dataclass(order=True)
class StreamJobResult:
    stream: bytes
    valid_children: List[StreamResult]


gen_options = bytes(range(90, 256))
max_gens = 1200

before_hit_digests_seen = set()

# Patterns that work as offset elbow to be used after
# the snark.
offset_elbows = set(
    lt.pattern(rle).digest()
    for rle in [
        "oo$oo",  # block
        "boo$obbo$boo",  # beehive horizontal
        "bo$obo$obo$bo",  # beehive vertical
        "2o$obo$b2o!",  # ship nw<->se
        "2o$obo$bo!",  # boat nw
        "bo$obo$b2o!",  # boat se
        "b2o$o2bo$o2bo$b2o!",  # pond
    ]
)

elbow_offsets_even = {
    lt.pattern(rle).digest(): v
    for rle, v in {
        "oo$oo": -20,  # block
        "boo$obbo$boo": -17,  # beehive horizontal
        "bo$obo$obo$bo": -21,  # beehive vertical
        "2o$obo$b2o!": -21,  # ship nw<->se
        "2o$obo$bo!": -21,  # boat nw
        "b2o$o2bo$o2bo$b2o!": -17,  # pond
    }.items()
}
elbow_offsets_odd = {
    lt.pattern(rle).digest(): v
    for rle, v in {
        "oo$oo": -16,
        "boo$obbo$boo": None,  # beehive horizontal
        "bo$obo$obo$bo": None,  # beehive vertical
        "2o$obo$b2o!": None,  # ship nw<->se
        "2o$obo$bo!": None,  # boat nw
        "bo$obo$b2o!": -16,  # boat se
        "b2o$o2bo$o2bo$b2o!": -21,  # pond
    }.items()
}


def offset_snark_for_elbow(elbow_digest, depth):
    if depth % 2 == 0:
        r = elbow_offsets_even[elbow_digest]
        if r is None:
            return None
        return r + depth // 2
    else:
        r = elbow_offsets_odd[elbow_digest]
        if r is None:
            return None
        return r + depth // 2


@dataclass
class PatternComponent:
    digest: int
    x: int
    y: int
    w: int
    h: int

    def lane(self):
        return max(
            self.x - self.y - snark_glider_offset,
            (self.x + self.w) - (self.y + self.h) - snark_glider_offset,
            key=abs,
        )

    def depth(self):
        return self.x + self.y + self.w + self.h - elbow_depth_offset

    def offset_elbow(self):
        if self.digest not in offset_elbows:
            return None
        return offset_snark_for_elbow(self.digest, self.depth())


def extract_offset_elbow(components: List[PatternComponent]):
    extreme_lane = 0
    extreme_component = None
    for c in components:
        lane = c.lane()
        if abs(lane) >= abs(extreme_lane):
            extreme_lane = lane
            extreme_component = c
    if extreme_component is None:
        return None
    offset = extreme_component.offset_elbow()
    if offset is None:
        return None
    return extreme_component, extreme_lane, offset


def score_offset_elbow(pattern):
    components = [
        PatternComponent(c.digest(), *c.getrect()) for c in pattern.components()
    ]
    offset_elbow = extract_offset_elbow(components)
    if offset_elbow is None:
        return 0
    extreme_component, extreme_lane, offset = offset_elbow


def find_p2_output(job, queue):
    initial_gens = sum(job.stream)
    result = StreamJobResult(job.stream, [])
    for next_possibility in job.next_possibilities:
        stream = job.stream + bytes((next_possibility,))
        gens = initial_gens + next_possibility

        before_hit = optimized_stream_simulation(stream)
        before_hit_digest = before_hit.digest()
        if before_hit_digest in before_hit_digests_seen:
            # we've reached a state we've seen before with
            # a shorter glider sequence. No need to explore further.
            break

        before_hit_digests_seen.add(before_hit_digest)

        # snapshots
        just_after_hit = before_hit[20]
        just_after_hit1 = just_after_hit[1]
        just_after_hit2 = just_after_hit1[1]
        end_pattern = just_after_hit2[512 - 22]
        end_pattern2 = end_pattern[2]

        if end_pattern == end_pattern2:
            # the pattern settles into a p1 or p2. It could be a valid
            # result! We need to get statistics about it for scoring.
            lanes = []
            depths = {}
            for c in end_pattern.components():
                (x, y, w, h) = c.getrect()
                is_pi_equivalent = c.digest() in offset_elbows
                lanes.append(
                    (
                        max(
                            x - y - snark_glider_offset,
                            (x + w) - (y + h) - snark_glider_offset,
                            key=abs,
                        ),
                        is_pi_equivalent,
                        c,
                    )
                )
                depths[c] = x + w + y + h

            if len(lanes) > 1:
                lanes.sort(key=lambda x: abs(x[0]))
                (max_lane, is_pi_equivalent) = lanes[-1]
                if is_pi_equivalent:
                    # the most extreme edge is a possible
                    # offset block
                    (x, y, _, _) = end_pattern.getrect()
                    result.valid_children.append(
                        StreamResult(
                            next_possibility=next_possibility,
                            digest=end_pattern.digest(),
                            before_hit_digest=before_hit_digest,
                            x=x,
                            y=y,
                            max_lane=max_lane,
                            next_highest_lane=lanes[-2][0],
                            population=end_pattern.population,
                        )
                    )

        if gens <= max_gens - gen_options[0]:
            if just_after_hit == just_after_hit1:
                # the pattern very quickly stabilized to p1,
                # only queue the fastest possible next glider
                queue(
                    gens,
                    StreamJob(
                        stream=stream,
                        starting_block=job.starting_block,
                        next_possibilities=gen_options[0:1],
                    ),
                )
            elif just_after_hit == just_after_hit2:
                queue(
                    gens,
                    StreamJob(
                        stream=stream,
                        starting_block=job.starting_block,
                        next_possibilities=bytes(
                            [x for x in gen_options[0:2] if x + gens <= max_gens]
                        ),
                    ),
                )
            else:
                queue(
                    gens,
                    StreamJob(
                        stream=stream,
                        starting_block=job.starting_block,
                        next_possibilities=bytes(
                            [x for x in gen_options if x + gens <= max_gens]
                        ),
                    ),
                )

    return result


starting_candidates = [(0,)]

sys.exit(0)

if __name__ == "__main__":
    pass


def search():
    speedo = Speedometer(interval_s=10)
    starting_jobs = [
        (
            sum(c),
            StreamJob(
                stream=bytes(c), starting_block=0, next_possibilities=gen_options
            ),
        )
        for c in starting_candidates
    ]

    already_seen_results = set()

    for (
        stream_job,
        stream_result,
        new_jobs,
        queue,
        pending_tracker,
        local_queue,
    ) in recursive_priority_imap_unordered(
        find_p2_output, starting_jobs, n_processes=20
    ):
        if isinstance(stream_result, Exception):
            raise ChildProcessError("error in child process") from stream_result
        if speedo.tick(len(stream_job.next_possibilities)):
            print(
                f"{speedo.get_current_speed_and_reset():.2f}/s, {speedo.overall_speed():.2f} avg/s, {speedo.n_finished} done, {pending_tracker.n_pending}Q/{len(local_queue)}L queued, {pending_tracker.min_cost_pending()} gens ({pending_tracker.pending_items.get(pending_tracker.min_cost_pending(), [float('inf'),0])[1]} remaining)",
                file=sys.stderr,
            )

        valid_new_streams = set()
        for c in stream_result.valid_children:
            key = (c.before_hit_digest, c.x, c.y)
            if key in already_seen_results:
                # Skip exploring patterns we've already
                # seen, based on the before_hit_digest
                continue
            already_seen_results.add(key)
            new_stream = stream_job.stream + bytes((c.next_possibility,))
            valid_new_streams.add(new_stream)
            score = (
                c.max_lane
                * (abs(c.max_lane) - abs(c.next_highest_lane)) ** 2
                / math.sqrt(c.population)
            )
            print(
                score,
                c.digest,
                c.max_lane,
                c.next_highest_lane,
                c.population,
                stream_job.starting_block,
                tuple(new_stream),
                flush=True,
            )

        valid_new_jobs = [
            (cost, job) for cost, job in new_jobs if job.stream in valid_new_streams
        ]
        queue(valid_new_jobs)

    print(
        f"Finished with {speedo.overall_speed():.2f} jobs/s, {speedo.n_finished} total",
        file=sys.stderr,
    )
