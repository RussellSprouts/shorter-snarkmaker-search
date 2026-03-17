from dataclasses import dataclass, field
from functools import cached_property
from typing import Any, Set
import weakref
from collections import defaultdict

from db import Recipe

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

    @cached_property
    def population(self):
        return self.pattern.population

    @cached_property
    def octodigest(self):
        return self.pattern.octodigest()
    
    @cached_property
    def depth(self):
        return sum(self.pattern.getrect())


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

    def overlapping_recipes(self, components: Set[PatternRef]) -> Set[Recipe]:
        """Given a list of components, returns a map of
        recipe to set of components that are overlapping"""
        result = defaultdict(set)
        for c in components:
            recipes = self.component_to_recipe.get(c, None)
            if recipes:
                for r in recipes:
                    result[r].add(c)
        return result

    def recipe_components(self, recipe: Recipe) -> Set[PatternRef]:
        """Given a recipe, returns the set of components
        in that recipe"""
        return self.recipe_to_components[recipe]
