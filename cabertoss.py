
import lifelib

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree()

canonical_glider = lt.pattern("ooo$o$bo!")

def mk_glider(lane, delay):
    """Makes a glider with the given
    lane and generations of delay"""
    offset = (delay + 3) // 4
    rem = (4 - delay % 4) % 4
    return canonical_glider[rem](offset - lane + (lane // 2), offset + (lane // 2))

if __name__ == "__main__":

    two_engine_cordership = lt.pattern("""x = 57, y = 49, rule = B3/S23
4$19b3o2$23bo$19bo3b2o12bo$21bobo13b2o$18b3o16bobo$20bo$36b2o$19b2o16b
2o$20b2o14bo2bo$20bo15b3o5b2o$20b2o22b2o$19b2o5$5b3o$5b3o27b2o$4bo3bo
25bo2bo14b2o$5b2ob3o23bo2b2o9bo2bob2o$5b2o4bo23bo3bo8bo5b2o$8bo2bo23bo
12bobob3o$9b2o25bo2b2o11b2o$37bo3bo10b2o$39bobo$38bo$38bo$33b3obo$31b
2o8bo$31bo6b3o$32b2o3bo$33bob2o$31b4o$31b3o$11b2o13b2o$11b2o13b2o2$23b
o$23bo2bo$25b2o3$19b2o$19b2o!
    """)

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
