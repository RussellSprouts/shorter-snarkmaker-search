"""Given a slow salvo recipe, finds possible intermediate steps."""

import sys
from collections import defaultdict

from db import ProcessingDatabase, Recipe
from lifetree import lt
from gliders import extract_recipe_lanes, mk_glider, reconstruct


class RecipeGraph:
    """We have one known snark recipe with 73 gliders.
    However, the order is not strict. At many we points,
    we have options for which glider to send next. This
    class lazily computes possible recipes based on what
    we've discovered so far. It's possible we get lucky
    and find a reaction which does the work of multiple
    gliders, so we might explore ahead multiple steps.
    """

    def __init__(self, end_target):
        # a map of recipe to list of possible next recipes
        self.cache = {}
        self.end_target = end_target

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
                            id=None,
                            so_far=new_so_far,
                            remaining=new_remaining,
                            digest=new_digest,
                            x=x,
                            y=y,
                            rle_string=new_pattern.rle_string(),
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


if __name__ == "__main__":
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
    first_recipe = Recipe(
        id=None,
        so_far=(),
        remaining=recipe,
        digest=starting_block.digest(),
        x=starting_block.getrect()[0],
        y=starting_block.getrect()[1],
        rle_string=starting_block.rle_string(),
    )

    end_target = reconstruct(recipe, starting_block, 100)[73 * 512]

    recipe_cache = RecipeGraph(end_target)

    explore_common_precursors(recipe_cache, first_recipe, 10, 1, 2048)

    db = ProcessingDatabase("new-db.sqlite")
    db.add_recipe_intermediates(recipe_cache.unique_patterns())
    db.commit()
    db.close()
