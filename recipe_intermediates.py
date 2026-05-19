"""Given a slow salvo recipe, finds possible intermediate steps."""

import sys
from collections import defaultdict, namedtuple
import functools

from db import ProcessingDatabase, Recipe
from lifetree import lt
from gliders import extract_recipe_lanes, mk_glider, reconstruct
from components import pattern_components

RecipeStep = namedtuple("RecipeStep", ("lane", "parity", "kind", "i", "digest"))

class RecipeDag:

    def __init__(self, lanes, starting_block, keep_order=False):
        birthdays = {}
        periodic_birthdays = {}
        dependencies = defaultdict(set)
        dependencies[0] = set([-1])
        should_create = {}
        should_delete = {}
        periodic_dependencies = defaultdict(set)
        flight_paths = {}

        def coords(patt):
            return map(lambda c: (int(c[0]), int(c[1])), patt.coords())

        for c in coords(starting_block):
            birthdays[c] = -1

        debug = lt.pattern()
        pattern = starting_block
        for i, (lane, parity) in enumerate(lanes):
            old = pattern
            # cells that were periodic
            old_periodic = old[1] ^ old

            new = pattern + mk_glider(lane, 400 - parity)
            debug += new(i * 400, 0)
            flight_path = lt.pattern()
            for _ in range(0, 1024):
                next = new[2]
                flight_path |= (next - new)
                flight_path |= (new - next)
                if new == next:
                    break
                new = next
            else:
                print(debug.rle_string())
                print(i, lane, parity)
                raise Exception("Slow salvo didn't stabilize in 2048 gens!")

            flight_path -= old
            flight_path -= old_periodic
            flight_paths[i] = flight_path

            deleted = old - new
            created = new - old

            should_delete[i] = deleted
            should_create[i] = created

            for c in coords(deleted):
                dependencies[i].add(birthdays[c])
                del birthdays[c]

            for c in coords(created):
                birthdays[c] = i

            # calculate which glider's phases affect the
            # phase of what this glider touched.
            new_periodic = new[1] ^ new
            deleted_periodic = old_periodic - new_periodic
            created_periodic = new_periodic - old_periodic
            shared_periodic = old_periodic & new_periodic
            rephased_periodic = shared_periodic & (old_periodic ^ new_periodic)
            
            for c in coords(deleted_periodic):
                periodic_dependencies[i].add(periodic_birthdays[c])
                del periodic_birthdays[c]

            for c in coords(created_periodic):
                periodic_birthdays[c] = i

            for c in coords(rephased_periodic):
                # we changed the phase of this periodic
                # cell, so we depend on the original phase
                # and set a new phase.
                periodic_dependencies[i].add(periodic_birthdays[c])
                periodic_birthdays[c] = i

            pattern = new

        # Any remaining birthdays are cells that are
        # live and remain live until the very end.
        # If they are in the flight path of a previous
        # glider, then they would block it. Add deps to
        # handle that case.
        for coord, creator in birthdays.items():
            p = lt.pattern('o')(coord[0], coord[1])
            for flight, path in flight_paths.items():
                if flight >= creator:
                    continue
                if (p & path).nonempty():
                    dependencies[creator].add(flight)

        if keep_order:
            for i in dependencies.keys():
                dependencies[i].add(i - 1)

        # compute the transitive closure of dependencies
        transitive_dependencies = defaultdict(set)
        for i in dependencies.keys():
            dependencies[i].add(i)

        for k in dependencies.keys():
            for i in dependencies.keys():
                for j in dependencies.keys():
                    if j in dependencies[i] or ((k in dependencies[i]) and (j in dependencies[k])):
                        transitive_dependencies[i].add(j)

        reduced_dependencies = transitive_dependencies
        for i in reduced_dependencies.keys():
            reduced_dependencies[i].discard(i)

        for j in reduced_dependencies.keys():
            for i in reduced_dependencies.keys():
                if j in reduced_dependencies[i]:
                    for k in reduced_dependencies.keys():
                        if k in reduced_dependencies[j]:
                            reduced_dependencies[i].discard(k)

        # Any periodic cells that are present at the end
        # must keep their phase
        last_glider = len(lanes) - 1
        for coord, creator in periodic_birthdays.items():
            periodic_dependencies[last_glider].add(creator)

        # Compute transitive closure
        transitive_periodic_dependencies = defaultdict(set)
        all_deps = set()
        for i, deps in periodic_dependencies.items():
            periodic_dependencies[i].add(i)
            all_deps.update(deps)
        for i in all_deps:
            periodic_dependencies[i].add(i)
        for k in periodic_dependencies.keys():
            for i in periodic_dependencies.keys():
                for j in periodic_dependencies.keys():
                    if j in periodic_dependencies[i] or ((k in periodic_dependencies[i]) and (j in periodic_dependencies[k])):
                        transitive_periodic_dependencies[i].add(j)

        reachable_from_end = set(transitive_periodic_dependencies[last_glider])

        # remove reflexive edges
        for i in transitive_dependencies.keys():
            transitive_periodic_dependencies[i].discard(i)
            if not transitive_periodic_dependencies[i]:
                del transitive_periodic_dependencies[i]
        for i in periodic_dependencies.keys():
            periodic_dependencies[i].discard(i)

        periodic_depended_on = set()
        has_periodic_dependencies = set()
        for i, deps in transitive_periodic_dependencies.items():
            if not deps:
                continue
            has_periodic_dependencies.add(i)
            periodic_depended_on.update(deps)

        rephasable_gliders = periodic_depended_on - has_periodic_dependencies - reachable_from_end
        p1_gliders = set(dependencies.keys()) - periodic_depended_on - has_periodic_dependencies

        self.lanes = lanes
        self.starting_block = starting_block
        self.dependencies = reduced_dependencies
        self.periodic_dependencies = periodic_dependencies
        self.should_create = should_create
        self.should_delete = should_delete
        self.rephasable_gliders = rephasable_gliders
        self.p1_gliders = p1_gliders

    @functools.lru_cache(2**12)
    def _simulate(self, lanes):
        """Simulates the results of the given tuple of glider numbers. Cached.
        Returns 'unstable' if the result is not stable."""
        if not lanes:
            return self.starting_block
        lane, parity, kind = lanes[-1]
        p = self._simulate(lanes[:-1]) + mk_glider(lane, 400 - parity)
        p = p[2048]
        if kind == 'rephase':
            p = p[1]
        if p[2] != p:
            return "unstable"
        return p

    def get_possible_gliders(self, i):
        lane, parity = self.lanes[i]
        possibilities = [
            (lane, parity, 'orig')
        ]
        if i in self.rephasable_gliders:
            possibilities.append(
                (lane,  1 - parity, 'rephase')
            )
        elif i in self.p1_gliders:
            possibilities.append(
                (lane, 1 - parity, 'p1-rephase')
            )
            for i in range(-10, 10):
                if i == 0:
                    continue
                possibilities.append(
                    (lane + i, parity, f'shift{i}')
                )
                possibilities.append(
                    (lane + i, 1 - parity, f'shift{i}-rephase')
                )

        return possibilities

    def get_next(self, so_far: tuple[RecipeStep]) -> list[RecipeStep]:
        so_far_set = set(s[3] for s in so_far)
        so_far_set.add(-1)

        lanes = tuple((s[0], s[1], s[2]) for s in so_far)
        before = self._simulate(lanes)

        results = []

        for i, dependencies in self.dependencies.items():
            if i in so_far_set:
                # we've already sent this glider
                continue
            if any(d not in so_far_set for d in dependencies):
                # we don't have the dependencies for this glider
                continue

            for lane, parity, kind in self.get_possible_gliders(i):
                after = self._simulate(lanes + ((lane, parity, kind),))
                if isinstance(after, str) and after == 'unstable':
                    continue
                deleted = before - after
                if deleted != self.should_delete[i]:
                    continue
                created = after - before
                if created != self.should_create[i]:
                    continue
                
                # glider is likely valid!
                results.append(RecipeStep(lane, parity, kind, i, after.digest()))

        return results


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
                    x, y, _, _ = new_pattern.getrect()
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


def dot_string(recipe_dag):
    result = 'digraph recipe_dag {\nrankdir="BT"\n'

    for glider in recipe_dag.rephasable_gliders:
        result += f'{glider} [color="blue"]\n'

    for glider in recipe_dag.p1_gliders:
        result += f'{glider} [color="red"]\n'

    for glider, dependencies in recipe_dag.dependencies.items():
        non_periodic = [d for d in dependencies if d not in recipe_dag.periodic_dependencies[glider] and d != -1]
        result += f'{glider} -> {{{' '.join(map(str, non_periodic))}}}\n'

    result += 'edge [style=dashed]\n'
    for glider, dependencies in recipe_dag.periodic_dependencies.items():
        real_dependencies = [d for d in dependencies if d != -1]
        if real_dependencies:
            result += f'{glider} -> {{{' '.join(map(str, real_dependencies))}}}\n'

    result += '}\n'
    return result

if __name__ == "__main__":
    f = sys.argv[1]
    with open(f, "r") as file:
        contents = file.read()
        lanes, starting_block = extract_recipe_lanes(lt.pattern(contents))

        dag = RecipeDag(lanes, starting_block)

        def explore(so_far, depth):
            next = dag.get_next(so_far)
            for n in next:
                new_so_far = so_far + (n,)
                if depth > 1:
                    explore(new_so_far, depth - 1)
                else:
                    print(new_so_far)
        explore((), 10)

        print(dag.periodic_dependencies)
        # print(dot_string(dag))