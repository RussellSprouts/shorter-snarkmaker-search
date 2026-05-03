import sys
from collections import defaultdict
import math

from gliders import single_channel_stream
from lifetree import lt

with open(sys.argv[1], 'r') as file:
    rle = file.read()
    patt = lt.pattern(rle)
    _, _, w, _ = patt.getrect()

    glider = lt.pattern('bo$bbo$3o')
    d1 = (glider, glider[1], glider[2], glider[3])
    glider = glider('rot90')
    d2 = (glider, glider[1], glider[2], glider[3])
    glider = glider('rot90')
    d3 = (glider, glider[1], glider[2], glider[3])
    glider = glider('rot90')
    d4 = (glider, glider[1], glider[2], glider[3])
    halo = lt.pattern('3o$3o$3o').centre()

    def is_glider(patt):
        if patt.population != 5:
            return False
        for d in (d1, d2, d3, d4):
            for g in d:
                if g.centre() == patt.centre():
                    return True
        return False

    def direction(glider):
        if not glider.nonempty():
            return []
        for desc, d in [('d1', d1), ('d2', d2), ('d3', d3), ('d4', d4)]:
            for g in d:
                m = glider.match(g, halo='b')
                if m.nonempty():
                    match = m.convolve(g)
                    return [(desc, match)] + direction(glider - match)
        return []

    def is_tee(patt):
        dirs = defaultdict(list)
        for glider in patt.components():
            for d, g in direction(glider):
                dirs[d].append(g)
        if set(dirs.keys()) not in (set(('d1', 'd3')), set(('d2', 'd4'))):
            return False
        result = patt[512]
        if not is_glider(result):
            return False
        d, result_glider = direction(result)[0]
        if d not in dirs:
            double = None
            single = None
            for d, gliders in dirs.items():
                if len(gliders) == 2:
                    d, tandem_glider = direction(gliders[0])[0]
                    if d != 'd1':
                        return is_tee(patt('rot90'))
                    double = gliders[0] + gliders[1]
                elif len(gliders) == 1:
                    single = gliders[0]
            if not double or not single:
                print("fail", dirs, patt.rle_string())
            return (double, single)

    def has_kickback(double, single):
        dir1, d_glider_1 = direction(double[0])[0]

        p = double + single
        result = p[512]
        for c in result.components():
            if not is_glider(c):
                continue
            
            d, _ = direction(c)[0]
            if dir1 != d and ((dir1 in ('d1', 'd3') and d in ('d1', 'd3')) or (dir1 in ('d2', 'd4') and d in ('d2', 'd4'))):
                return True
        return False

    
    def is_vanish(patt):
        return patt[512].population == 0

    def is_eventual_vanish(double, single):
        for i in range(2, 20):
            p = single + double
            for j in range(1, i):
                p = p + rewind(double, 120*j)

            if p[20000].population == 0:
                print('found one')
                return i

        return False

    def rewind(glider, n):
        x1, y1, _, _ = glider.getrect()
        x2, y2, _, _ = glider[4].getrect()

        dx = x2 - x1
        dy = y2 - y1

        shift = math.ceil((n+1)/4)

        return glider(-shift * dx, -shift * dy)[4 - (n % 4)]

    all_results = lt.pattern()
    n_results = 0

    for x in range(0, w, 64):
        collision = patt[x:x+64,0:64].centre()
        dirs = defaultdict(list)
        
        tee = is_tee(collision)
        if not tee:
            continue
        double, single = tee
        all_results |= (double + single)(n_results*128, 128*0)
        has_tee = False
        for i in range(1, 8):
            s = rewind(single, i)
            other = double + s
            if has_kickback(double, s):
                pass
                # all_results |= (other + rewind(double, 120))(n_results*128, 128*i)
            elif is_vanish(other):
                pass
                # all_results |= other(n_results*128, 128*i)
            elif is_tee(other):
                pass
                # all_results |= other(n_results*128, 128*i)
            elif is_eventual_vanish(double, s):
                pass
                # all_results |= (other + rewind(double, 120) + rewind(double, 240) + rewind(single, 128))(n_results*128, 128*i)
                next_chance =  88+i if i > 1 else 96+i
                all_results |= (
                    double + single + rewind(single, next_chance) + rewind(single, 304) + rewind(double, 120) + rewind(double, 240) + rewind(double, 360) + rewind(double, 480)
                )(n_results*128, 128*i)
            else:
                pass
                # all_results |= (other + rewind(single, i + 90))(n_results*128, 128*i)

        n_results += 1


    print(all_results.rle_string())
