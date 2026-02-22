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

    def unique_patterns(self):
        recipes_by_digest_xy = {}
        for r in self.all_recipes():
            recipes_by_digest_xy[(r.digest, r.x, r.y)] = r
        return recipes_by_digest_xy.values()


def explore_common_precursors(recipe_graph, first_recipe, depth, width, max_pool):
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
            next_results = recipe_graph.explore(s, depth=1, width=width)
            for n in next_results:
                pool[(n.digest, n.x, n.y)] = n

    print(recipe_graph.stamp_collection(include_glider=True).rle_string())


def recipe_intermediates(input_recipe, output_db, search_depth, search_width, max_pool):
    with open(input_recipe) as f:
        rle = f.read()
    db = ProcessingDatabase(output_db)
    if len(db.recipe_intermediates):
        raise Exception(f"Error: {output_db} already exists and contains recipes.")
    pattern = lt.pattern(rle)
    recipe, starting_block = extract_recipe_lanes(pattern)
    first_recipe = Recipe(
        id=None,
        so_far=(),
        remaining=recipe,
        digest=starting_block.digest(),
        x=starting_block.getrect()[0],
        y=starting_block.getrect()[1],
        rle_string=starting_block.rle_string(),
    )

    if search_depth == -1:
        search_depth = len(recipe)

    end_target = reconstruct(recipe, starting_block, 100)[len(recipe) * 512]
    recipe_graph = RecipeGraph(end_target)

    print(f"Exploring common precursors\nsearch depth:{search_depth}")

    explore_common_precursors(
        recipe_graph=recipe_graph,
        first_recipe=first_recipe,
        depth=search_depth,
        width=search_width,
        max_pool=max_pool,
    )

    db.add_recipe_intermediates(recipe_graph.unique_patterns())
    db.commit()
    db.close()
