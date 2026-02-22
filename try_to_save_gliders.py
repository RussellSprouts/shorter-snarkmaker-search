
from gliders import mk_glider
from recipe_intermediates import RecipeGraph

def try_to_save_gliders(recipe_graph: RecipeGraph, min_lane=-40, max_lane=40):
    """
    Given an explored RecipeGraph, checks each node
    to see if a single glider can skip ahead more than
    one step.
    """
    all_items = {}
    for k, r in recipe_graph.all_recipes():
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
