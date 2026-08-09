import sys
import re
import os
from collections import defaultdict
from dataclasses import dataclass

from gliders import single_channel_stream, mk_glider
from lifetree import lt
from life_history import write_life_history
from font import write_text

@dataclass
class GliderInfo:
    lane: int
    depth: int
    phase: int
    direction: str

@dataclass
class Obj:
    name: str
    info: str
    parsed: GliderInfo|None

    def __repr__(self):
        return f"{self.name}{self.info}"

@dataclass
class RecipeResult:
    stream: tuple[int]
    objs: list[Obj]

def parse_object(obj):
    m = re.match(r"^'([\w ]+)((?:\([^)]*\))*)'$", obj.strip())
    if not m:
        raise SyntaxError(f"Invalid object: {obj}")
    name = m.group(1)
    info = m.group(2)

    parsed = None
    if name == 'glider':
        m2 = re.match(r"^\(([dl])(-?[0-9]+)\)\(ph([0-3])\)\(.(.).\)$", info.strip())
        if not m2:
            raise SyntaxError(f"Invalid glider info: {info}")
        dl = m2.group(1)
        val = int(m2.group(2))
        phase = int(m2.group(3))
        dir = m2.group(4)
        parsed = GliderInfo(
            lane=val if dl == 'l' else 0,
            depth=val if dl == 'd' else 0,
            phase=phase,
            direction=dir
        )
    return Obj(
        name,
        info,
        parsed
    )

def parse_objects(objs):
    results = []
    for o in re.split(r"('[^']*')", objs):
        o = o.strip()
        if not o or o == ',':
            continue
        obj = parse_object(o)
        results.append(obj)        
    return results

if __name__ == '__main__':
    by_glider_lane = defaultdict(list)
    total_size = os.path.getsize(sys.argv[1]) or 1
    print(total_size)

    fake_gun = sum(
        [mk_glider(0, 46 * x) for x in range(0, 24)], start=lt.pattern("")
    )
    fake_gun = fake_gun('rot90')(5, -5)
    eater = lt.pattern('2.2A$3.A$3A$A!')(-53, 50)

    print((fake_gun + eater).rle_string())

    with open(sys.argv[1], 'rb') as f:
        bytes_read = 0
        for i, bline in enumerate(f):
            line = bline.decode('utf-8')
            if not line.strip():
                continue
            m = re.match(
                r"""^\((\d+(?:, \d+)*,?)\)\s*\[('[^']*'(?:, '[^']*')*)?\]$""",
                line.strip()
            )
            if not m:
                raise SyntaxError(f"Invalid line: {line}")
            stream = tuple(map(int, filter(bool, m.group(1).split(','))))
            info = parse_objects(m.group(2) or '')
            recipe_result = RecipeResult(stream, info)
            for obj in info:
                if obj.name == 'glider' and obj.parsed.direction == '⬁':
                    by_glider_lane[(obj.parsed.lane,obj.parsed.phase % 2)].append(recipe_result)
                    # print(f'found lane {obj.parsed.lane}')

            bytes_read += len(bline)
            if i % 10000 == 0:
                print(f"Progress: {bytes_read / total_size * 100:.2f}")

    def object_cost(obj):
        if obj.name == 'glider':
            return 5
        elif re.match(r"^g[0-9]+$", obj.name):
            return 0
        else:
            return 1

    def recipe_score(recipe):
        n_objects = sum(recipe_score(o) for o in recipe.objs)
        total_time = sum(recipe.stream[1:])
        return (n_objects, total_time)

    full_patt = lt.pattern()
    red_patt = lt.pattern()

    for i, ((lane, parity), recipes) in enumerate(sorted(by_glider_lane.items(), key=lambda a: a[0])):
        best = min(recipes, key=recipe_score)
        print(lane, best)
        patt = single_channel_stream(best.stream) + fake_gun + eater

        is_clean = recipe_score(best)[0] == 5

        full_patt += patt((i % 32) * 128, (i // 32) * 768)
        red_patt += write_text(f"lane {lane} parity {parity} {'*' if is_clean else ''}")((i % 32) * 128, (i // 32) * 1024)

    for i in range(0, )

    print(write_life_history(
        green = full_patt,
        red = red_patt
    ))