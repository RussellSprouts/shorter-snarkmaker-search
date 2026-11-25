import sqlite3
import sys
import re
from collections import namedtuple, defaultdict
from dataclasses import dataclass
import dataclasses
from functools import lru_cache, wraps

friendly_names = {
    "glider":"xq4_153",
    "block":"xs4_33",
    "blinker":"xp2_7",
    "beehive":"xs6_696",
    "loaf":"xs7_2596",
    "boat":"xs5_253",
    "ship":"xs6_356",
    "pond":"xs8_6996",
    "tub":"xs4_252",
    "long boat":"xs7_25ac",
    "ship tie":"xs12_g8o653z11",
    "toad":"xp2_7e",
    "beacon":"xp2_318c",
    "half bakery":"xs14_g88m952z121",
    "eater 1":"xs7_178c",
    "barge":"xs6_25a4",
    "snake":"xs6_bd",
    "boat tie ship":"xs11_g8o652z11",
    "lwss":"xq4_6frc",
}

@dataclass(frozen=True)
class ObjectName:
    id: int
    name: str
    apgcode: str

    @lru_cache(maxsize=None)
    def mk(id, name, apgcode):
        return ObjectName(id, name, apgcode)

    def of(name):
        if name in friendly_names:
            apgcode = friendly_names[name]
        else:
            apgcode = name
        return ObjectName.mk(None, name, apgcode)

@dataclass(frozen=True)
class Object:
    id: int
    name: ObjectName
    lane: int
    phase: int
    orientation: int

    @lru_cache(maxsize=None)
    def mk(id, name, lane, phase, orientation):
        return Object(id, name, lane, phase, orientation)

    def of(obj):
        """Returns the object and its depth"""
        if re.match(r"g[0-9]+", obj):
            return Object.mk(None, ObjectName.of(obj), 0, 0, 0), 0
        if m := re.match(r"([a-z0-9_ ]*)\(l([0-9-]+),d([0-9-]+)(?:,o([0-9-]+))?(?:,p([0-9-]+))?\)", obj):
            name = m.group(1)
            lane = int(m.group(2) or 0)
            depth = int(m.group(3) or 0)
            orientation = int(m.group(4) or 0)
            phase = int(m.group(5) or 0)
            return Object.mk(None, ObjectName.of(name), lane, phase, orientation), depth
        if m := re.match(r"glider\(([dl])([0-9-]+)\)\(ph([0-9-]+)\)\(.(.).\)", obj):
            dorl = m.group(1)
            dorl_mag = int(m.group(2))
            phase = int(m.group(3))
            direction = m.group(4)
            if dorl == 'd':
                return Object.mk(None, ObjectName.of('glider'), 0, phase, '⬁⬀⬂⬃'.index(direction)), dorl_mag
            else:
                return Object.mk(None, ObjectName.of('glider'), dorl_mag, phase, '⬁⬀⬂⬃'.index(direction)), 0
        if m := re.match(r"([a-z0-9_ ]*)\(([0-9-]+,[0-9-]+),p([0-9-]+),c([0-9-]+)\)\(([0-9-]+),([0-9-]+)\)", obj):
            name = m.group(1)
            direction = m.group(2)
            phase = int(m.group(3))
            color = m.group(4)
            x = m.group(5)
            y = m.group(6)
            if direction == '0,-2':
                direction = 0
                depth = x
            elif direction == '2,0':
                direction = 1
                depth = y
            elif direction == '0,2':
                direction = 2
                depth = x
            elif direction == '-2,0':
                direction = 3
                depth = y

            return Object.mk(None, ObjectName.of(name), 0, phase, direction), depth

        raise Exception(obj)

@dataclass
class Recipe:
    id: int
    recipe: bytes
    gliders_consumed: int

    @lru_cache(maxsize=None)
    def mk(id, recipe, gliders_consumed):
        return Recipe(id, recipe, gliders_consumed)

@dataclass
class RecipeObject:
    id: int
    recipe: Recipe
    object: Object
    depth: int

    @lru_cache(maxsize=None)
    def mk(id, recipe, object, depth):
        return RecipeObject(id, recipe, object, depth)

schema = [
# 1 byte for total length
# 3 bytes for field lengths
# 1 byte for id
# n bytes for name
# n bytes for apgcode
"""
CREATE TABLE object_names (
    id INTEGER PRIMARY KEY,
    name TEXT,
    apgcode TEXT
);
""",
# 1 byte for total length
# 4 bytes for field lengths
# 1-3 bytes for id
# 1 byte for name
# 1 byte for lane
# 1 byte for phase orientation
"""
CREATE TABLE objects (
    id INTEGER PRIMARY KEY,
    name INTEGER REFERENCES object_names (id),
    lane INTEGER NOT NULL,
    phase_orientation INTEGER NOT NULL
);
""",
# 1 byte for total length
# 3 bytes for field lengths
# 1-4 bytes for id
# 5 bytes for recipe
# 1 byte for gliders consumed
"""
CREATE TABLE recipes (
    id INTEGER PRIMARY KEY,
    recipe BLOB NOT NULL,
    gliders_consumed INTEGER NOT NULL
);
""",
# 1 byte for total length
# 4 bytes for field lengths
# 1-4 bytes for id
# 1-4 bytes for recipe
# 1-3 bytes for object
# 1 byte for depth
"""
CREATE TABLE recipe_objects (
    id INTEGER PRIMARY KEY,
    recipe INTEGER REFERENCES recipes (id),
    object INTEGER REFERENCES objects (id),
    depth INTEGER NOT NULL
);"""
]

def recipe_to_blob(recipe):
    """Converts a recipe to a blob.
    Uses a single byte if possible, otherwise a 0 followed by
    two bytes."""
    b = bytearray()
    for r in recipe:
        if 0 < r < 256:
            b.append(r)
        else:
            b.append(0)
            b.append(r & 255)
            b.append(r >> 8)
    return bytes(b)

def blob_to_recipe(blob):
    r = []
    it = iter(blob)
    for b in it:
        if b == 0:
            lo = next(it)
            hi = next(it)
            r.append(lo | (hi << 8))
        else:
            r.append(b)
    return tuple(r)

def to_positive_int(n):
    if n >= 0:
        return n * 2
    return -n * 2 - 1

N_GUN_GLIDERS = 10

if __name__ == '__main__':
    conn = sqlite3.connect('results/depth-5.sqlite', timeout=10)
    conn.autocommit = False
    conn.row_factory = sqlite3.Row
    for s in schema:
        conn.execute(s)
    conn.commit()

    all_objects = defaultdict(lambda: 0)
    all_object_names = defaultdict(lambda: 0)

    def parse_line(line):
        m = re.match(r"^\((\d+(?:, \d+)*),?\) \[(.*)\]$", line)
        if not m:
            print("WARNING: unknown line", line)
            return
        recipe, objects_str = m.group(1), m.group(2)
        recipe = recipe_to_blob(map(int, recipe.split(',')))
        objects = []
        expected_gun_glider = 0
        for o in re.split(r"'([^']*)'", objects_str):
            o = o.strip()
            if not o or o == ',':
                continue

            if o == f"g{expected_gun_glider}":
                expected_gun_glider += 1
                continue

            obj, depth = Object.of(o)
            objects.append((obj, depth))
            all_objects[obj] += 1
            all_object_names[obj.name] += 1

        n_consumed = N_GUN_GLIDERS - expected_gun_glider
        return recipe, objects, n_consumed

    with open(sys.argv[1]) as f:
        for line in f:
           info = parse_line(line)
           if not info:
               continue
           recipe, objects, n_consumed = info

    name_ids = {}
    for name, n in sorted(all_object_names.items(), key=lambda a: a[1], reverse=True):
        name_ids[name] = len(name_ids)

    conn.executemany(
        """INSERT INTO object_names(id, name, apgcode) VALUES (?, ?, ?)""",
        ((id, name.name, name.apgcode) for name, id in name_ids.items())
    )
    conn.commit()

    object_ids = {}
    for object, n in sorted(all_objects.items(), key=lambda a: a[1], reverse=True):
        object_ids[object] = len(object_ids)

    conn.executemany(
        """INSERT INTO objects(id, name, lane, phase_orientation) VALUES (?, ?, ?, ?)""",
        ((id, name_ids[object.name], to_positive_int(object.lane), object.phase * 8 | object.orientation) for object, id in object_ids.items())
    )
    conn.commit()

    print(f"{len(all_object_names)=}, {len(all_objects)=}")

    with open(sys.argv[1]) as f:
        all_objects = defaultdict(lambda: 0)
        all_object_names = defaultdict(lambda: 0)
        recipe_id = 0
        for line in f:
            info = parse_line(line)
            if not info:
                continue
            recipe, objects, n_consumed = info
            conn.execute(
                """INSERT INTO recipes(id, recipe, gliders_consumed) VALUES (?, ?, ?)""",
                (recipe_id, recipe, n_consumed)
            )
            conn.executemany(
                """INSERT INTO recipe_objects(recipe, object, depth) VALUES (?, ?, ?)""",
                ((recipe_id, object_ids[object], depth) for object, depth in objects)
            )
            if recipe_id % 10000 == 0:
                print(f"Finished {blob_to_recipe(recipe)}")
                conn.commit()
            recipe_id += 1
        conn.commit()