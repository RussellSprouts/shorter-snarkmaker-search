
from lifetree import lt
from gliders import mk_glider
import sys

if __name__ == "__main__":

    four_in_a_row_cordership = lt.pattern("""x = 70, y = 70, rule = B3/S23
    48bobo$39bob3o4bobo$37b2obo4bo5bo$39b2o4bo2bo2bo$45bo2bo2bo$44bo4bo$40b
    o2bo16b2o$41b2o17b2o3$32bo$33bob2obobo$27b3o3b4o3bo$33bo2b2ob2o$32bo35b
    2o$30b3o35b2o$30b3o22bobo2b2o$41bo4bobo6bo2b2o2bo$40bobo2b2o2b2o7b2o2b
    o$40bob4o2bobo5b2o2bobo$41bo6bobo$45bob3o5$46b4o$12bo37bo$12bo19bob2o
    b2o7bo4bo$12bo18b5o2b2o7b2obo$15b2o14bo2b3obo10bo$15b2o12b2o6bo$10bo3b
    3o11b2o$11b3o15bo$12bo15b3o$11b2o15b3o$11b3o16bo19b3o$2bo10bo14bo2bo$
    2bo8bo16b3o12b2o3bo5bo$bobo9bo15bo12bo2bo2bo5bo$2b2o2bo4b3o4b2o23b2o3b
    o5bo$bo5bo9bo2bo$bo5bo10b2o19bo10b3o$bo4bo12bo18bobo$5bo13bo18bobo$2b
    3o13b2obo17bo$17b2o7bobo$21bo4bo2bo$2ob2o12bob3o4bo2bo8b3o$5bo12bo2bo
    4bo3bo$2o16b3o6bobo6bo5bo$2b3o23bo7bo5bo$36bo5bo2$38b3o$16b2o$19bo$16b
    o2bo$17b2o$17b2o$6b2o8bo2bo$6b2o8bo$17b3o6$14b2o$14b2o!""")

    two_engine_cordership = lt.pattern("""x = 57, y = 49, rule = B3/S23
4$19b3o2$23bo$19bo3b2o12bo$21bobo13b2o$18b3o16bobo$20bo$36b2o$19b2o16b
2o$20b2o14bo2bo$20bo15b3o5b2o$20b2o22b2o$19b2o5$5b3o$5b3o27b2o$4bo3bo
25bo2bo14b2o$5b2ob3o23bo2b2o9bo2bob2o$5b2o4bo23bo3bo8bo5b2o$8bo2bo23bo
12bobob3o$9b2o25bo2b2o11b2o$37bo3bo10b2o$39bobo$38bo$38bo$33b3obo$31b
2o8bo$31bo6b3o$32b2o3bo$33bob2o$31b4o$31b3o$11b2o13b2o$11b2o13b2o2$23b
o$23bo2bo$25b2o3$19b2o$19b2o!
    """)('rot90')

    centered = two_engine_cordership.centre()
    print(centered[192].centre() == centered)

    se_glider = mk_glider(0, 0)('rot180')
    ne_glider = mk_glider(0, 0)('rot270')
    sw_glider = mk_glider(0, 0)('rot90')

    p = centered

    print((centered + mk_glider(13, 200 + 91)).rle_string())
    print((centered + mk_glider(13, 200 + 91 + 96)).rle_string())

    for lane in range(-32, 50):
        print(lane)
        for delay in range(0, 96):
            p = centered + mk_glider(lane, delay + 200)
            op = p
            
            p = p[192*12]

            if p == p[2]:
                print("stopped!", lane, delay)
                # print(op.rle_string())
            if p.population == centered.population + 5:
                print("good pop", lane, delay)
                for phase in range(0, 4):
                    for g, desc in ((se_glider, 'se'), (ne_glider, 'ne'), (sw_glider, 'sw')):
                        has_glider = p.match(g[phase], halo='ooo$ooo$ooo')
                        if has_glider.nonempty():
                            p = p - has_glider.convolve(g[phase])
                            p = p.centre()
                            if p == centered:
                                print("reflected!", desc,  lane, delay)
                                print(op.rle_string())

            elif p.population == centered.population:
                p = p.centre()
                if p == centered:
                    print("eaten", lane, delay)
