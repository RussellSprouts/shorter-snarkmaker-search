from dataclasses import dataclass, field
import itertools
import collections
import heapq
import sys

from recipe_intermediates import RecipeDag, RecipeStep
from gliders import extract_recipe_lanes
from lifetree import lt

recipe = "-5:1 -2:5 -7:5 -12:0 -1:1 3:1 -16:1 -17:1 -44:1 -42:5 -40:1 -45:1 -32:1 -34:5 -40:1 -42:5 -43:5 -43:5 -46:5 -61:1 -50:4 -65:0 -57:1 -56:1 -44:0 -52:0 -45:1 -42:5 -42:5 -61:0 -70:5 -70:4 -65:1 -71:5 -66:4 -55:4 -38:5 -24:1 -25:1 -26:5 -34:4 -32:1 -47:4 -46:5 -49:0 -47:5 -47:4 -34:5 -35:5 -20:1 -25:0 -33:1 -50:4 -38:5 -27:4 -27:5 -37:1 -22:5 -27:4 -30:5 -41:0 -38:5 -38:4 -42:4 -30:4 -35:5 -31:4 -27:4 -24:1 -27:5 -29:1 -29:1 -15:4 -12:0 -14:5 -29:0 -38:5 -34:5 -34:5 -33:1 -35:5 -42:5 -42:5 -46:4 -40:1 -49:1 -48:1 -39:5 -30:5 -40:0 -34:5 -26:5 -43:5 -38:4 -42:5 -17:1 -10:5 -12:1 -12:1 -20:1 -8:1 -15:5 -9:0 -2:5 -5:1 -1:0 -20:0 -34:4 -55:5 -62:5 -58:5 -64:1 -62:5 -65:1 -74:5 -69:0 -63:4 -67:5 -71:5 -66:4 -88:0 -64:1 -75:5 -64:1 -98:5 -88:1 -90:5 -105:1 -95:5 -106:5 -103:5 -108:1 -103:5 -112:0 -114:5 -114:4 -93:1 -101:1 -103:4 -76:1 -73:1 -75:5 -69:1 -58:5 -60:0 -58:4 -74:4 -74:5 -91:5 -88:1 -96:1 -99:4 -80:0 -93:1 -91:5 -82:4 -78:5 -68:1 -64:0 -73:1 -60:1 -62:5 -89:0 -88:1 -88:0 -86:5 -94:4 -91:5 -78:4 -80:1 -86:5 -83:5 -83:5 -82:5 -98:4 -100:1 -108:1 -104:1 -90:4 -97:1 -103:5 -95:5 -96:1 -92:1 -80:1 -60:1 -61:1 -62:5 -70:4 -68:1 -83:4 -82:5 -95:4 -108:1 -105:0 -106:5 -105:1 -86:5 -70:5 -67:5 -62:4 -71:5 -83:5 -83:5 -86:5 -84:1 -101:0 -106:5 -101:0 -93:1 -86:5 -79:5 -91:5 -82:5 -72:1 -74:4 -79:4 -77:0 -87:4 -88:0 -79:5 -72:1 -70:5 -89:1 -78:4 -65:1 -72:1 -77:1 -84:1 -86:5 -75:5 -71:5 -72:1 -78:5 -71:5 -67:5 -77:1 -81:1 -72:1 -72:0 -81:0 -83:4 -71:4 -54:5 -44:1 -46:5 -76:1 -116:1 -113:1 -120:1 -117:1 -116:1 -131:5 -130:5 -120:1 -115:5"
recipe = [(int(i.split(":")[0])+1, int(i.split(":")[1])) for i in recipe.split(" ")]

Recipe = collections.namedtuple("Recipe", ["offset", "consumed", "time", "recipe"])
Partial = collections.namedtuple("Partial", ["nextgl", "time", "emits"])

library = {
    (1, 1): [Recipe( -5, 3, 288, (3, 102, 90)),
             Recipe(+11, 4, 472, (7, 158, 144))],
    (1, 0): [Recipe(+21, 4, 416, (3, 212, 96)),
             Recipe( -3, 4, 432, (3, 105, 233)),
             Recipe( +7, 4, 456, (7, 170, 94, 92))],
    (0, 1): [Recipe( +6, 3, 352, (7, 148, 106)),
             Recipe(-10, 4, 376, (3, 201)),
             Recipe(+20, 4, 512, (7, 132, 126, 156))],
    (0, 0): [Recipe(+12, 4, 472, (3, 159, 122, 95)),
             Recipe( +8, 4, 536, (3, 217, 129, 93))]
}

@dataclass
class Candidate:
    n_emitted: int
    next_glider: int
    time: int
    so_far: tuple[RecipeStep, ...]
    emits: tuple[int]

    def __lt__(self, other: Candidate):
        # Estimate 2 gliders per slow glider as the cost to finish, since that's
        # the minimum
        a = (self.n_emitted - len(self.so_far) * 2, self.time - 288*len(self.so_far))
        b = (other.n_emitted - len(other.so_far) * 2, self.time - 288*len(self.so_far))
        return a < b

def main():
    f = sys.argv[1]
    with open(f, "r") as file:
        contents = file.read()
        lanes, starting_block = extract_recipe_lanes(lt.pattern(contents), enforce_signed_byte=False)

        print(lanes)

        dag = RecipeDag(lanes, starting_block, keep_order=True)

        candidates = [
            Candidate(
                n_emitted=0,
                next_glider=0,
                time=0,
                so_far=(),
                emits=()
            )
        ]

        def hash_value(candidate):
            return (
                candidate.n_emitted,
                candidate.next_glider,
                candidate.time,
                candidate.so_far[-1].digest if candidate.so_far else 0
            )

        open_candidates = set(map(hash_value, candidates))

        n_considered = 0

        while candidates:
            candidate = heapq.heappop(candidates)
            open_candidates.remove(hash_value(candidate))
            if len(candidate.so_far) == len(lanes):
                break
            
            n_considered += 1
            if n_considered % 100 == 0:
                print(len(candidate.so_far), hash_value(candidate))

            follow_ups = dag.get_next(candidate.so_far)
            for gli in follow_ups:
                if gli.kind == 'rephase':
                    continue
                color = gli.lane % 2
                phase = gli.parity % 2
                for recipe in library[(color, phase)]:
                    delay = candidate.next_glider + (gli.lane - recipe.offset) * 4
                    time = candidate.time
                    emits = list(candidate.emits)
                    next_glider = candidate.next_glider
                    while delay < time:
                        next_glider += 240
                        delay += 240
                        emits.append(time+2)
                        time += 96
                    for i in itertools.accumulate(recipe.recipe):
                        emits.append(delay + i)
                    next_glider += 120 * recipe.consumed
                    time = delay + recipe.time
                    new_candidate = Candidate(
                        n_emitted=len(emits),
                        next_glider=next_glider,
                        time=time,
                        so_far=candidate.so_far + (gli,),
                        emits=tuple(emits)
                    )
                    h = hash_value(new_candidate)
                    if h not in open_candidates:
                        heapq.heappush(candidates, new_candidate)
                        open_candidates.add(h)

        print(candidate)

        timings = []
        ctime = 0
        for i in candidate.emits:
            timings.append(i - ctime)
            ctime = i
        print(len(timings))
        print(timings)

if __name__ == "__main__":
    main()

"""
beam = [Partial(0, -float("inf"), [])]
for gli in recipe:
    color = gli[0] % 2
    phase = gli[1] % 2
    newbeam = []
    for rec in library[(color, phase)]:
        best = None
        for pos in beam:
            delay = pos.nextgl + (gli[0] - rec.offset) * 4
            time = pos.time
            emits = list(pos.emits)
            nextgl = pos.nextgl
            while delay < time:
                nextgl += 240
                delay += 240
                emits.append(time+2)
                time += 96
            for i in itertools.accumulate(rec.recipe):
                emits.append(delay + i)
            nextgl += 120 * rec.consumed
            time = delay + rec.time
            if best is None or len(emits) < len(best.emits):
                best = Partial(nextgl, time, emits)
        if best is not None:
            newbeam.append(best)
    beam = newbeam

beam.sort(key=lambda x:len(x.emits))
timings = []
ctime = 0
for i in beam[0].emits:
    timings.append(i - ctime)
    ctime = i
print(len(timings))
print(timings)

"""