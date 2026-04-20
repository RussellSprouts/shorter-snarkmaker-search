from gliders import single_channel_stream, PI_BLOCKS

if __name__ == "__main__":
    simkin_recipe = (0, 126, 102, 100, 195, 90, 91, 95, 98, 105, 90, 101, 141, 94, 159, 92, 146, 99, 90, 152, 139, 144, 92, 161, 131, 116, 101, 114, 111, 112, 93, 127, 98, 102, 114, 107, 157, 90, 90, 90, 91, 91, 243, 113, 139, 108, 95, 127, 121)
    """
    def is_gun_active(p):
        cycles = 30
        pn = p[120*cycles]
        if pn.population == p.population + 5*cycles:
            return True
        return False

    for i in range(90, 255):
        print("Trying", i)
        p = single_channel_stream(simkin_recipe + (i,)) + PI_BLOCKS[0]
        pn = p[6000]
        if is_gun_active(pn):
            print("Activates gun at", i)
            print(p.rle_string())
            break
    """
    # ^ finds 99 as the first activation
                                      # 254, 123 can be replaced with 257.
    simkin_recipe = simkin_recipe + (99,254 ,123, 144, 94, 218, 148, 226, 111, 119, 100, 95, 91, 138, 201, 221, 216, 138, 125, 94, 240, 240, 240, 96)
    p = (single_channel_stream(simkin_recipe) + PI_BLOCKS[0])('swap_xy', 1, 0)
    print(p.rle_string())

    """
    x = 124, y = 99, rule = B3/S23
2$19b2o$19bobo$20bo3$40b2o8bo$40b2o7bobo$49bobo$29bo20bo$28bobo$28b2o$
49b2o$48bobo$49bo$b3o2$24b2o$23bo2bo$24b2o5$40b2o$23b2o14bo2bo$23b2o
10b2o3b2o$35b2o3$38b2o$38b2o2$35b2o$35b2o$27b2o$28bo$28bobo34b3o$29b2o
14b3o$46bo$44b3o50b2o$97b2o4$63b2o$63b2o$113bo9bo$71b2o40bo9bo$71b2o
27b3o10bo9bo$46b2o$46b2o23b2o$71b2o$43b2o$43b2o3$46b2o$46b2o2$102bo$
101bobo$101b2o2$24bo$24bo$24bo2$20b3o3b3o2$24bo$24bo$24bo8$37bo$36bobo
$36bobo$37bo11$50b2o$50bobo$51bo!
    """
    

