from lifetree import lt

def mk_font():
    font_pattern = lt.pattern(
        """x = 187, y = 5, rule = B3/S23
3ob2o2b3ob2o2b3ob3ob3obobob3ob3obobobo3bo3bobo2bob3ob3ob3o2b3ob3ob3obo
bobobobo3bobobobobob3ob3o2bo2b3ob3obobob3ob3ob3ob3ob3o8bo7bo$obobobobo
3bobobo3bo3bo3bobo2bo3bo2bobobo3b2ob2ob2obobobobobobobo2bobobo4bo2bobo
bobobo3bobobobobo3bobobob2o4bo3bobobobo3bo5bobobobobo7b3o6bo3b3ob3o2bo
7bo$obob3obo3bobob3ob3obobob3o2bo3bo2b2o2bo3bobobobob2obobob3obobo2b3o
b3o2bo2bobobobobobobo2bo2bobo2bo2bobo2bo2b3ob3ob3ob3ob3o3bob3ob3ob3o4b
o7bo4b2ob2o4bobobobo$3obobobo3bobobo3bo3bobobobo2bo3bo2bobobo3bo3bobo
2bobobobo3bobo2b2o4bo2bo2bobobobobobobobobo2bo2bo3bobo2bo2bo5bo3bo3bob
obo2bo2bobo3bo7bobo5bo4bobobobo4b2ob2o$obob3ob3ob3ob3obo3b3obobob3ob2o
2bobob3obo3bobo2bob3obo3b2obobobob3o2bo2b3o2bo3bobo2bobo2bo2b3ob3ob3ob
3ob3o3bob2o2b3o2bo2b3ob3o5bo5b3obo3bo7bo2b3ob3o!
        """
    )
    components = font_pattern.components()
    # sort by x value
    components.sort(key=lambda x: x.getrect()[0])
    letters = "abcdefghijklmnopqrstuvwxyz0123456789-.*_/⬀⬁⬂⬃"

    font_pattern_y = font_pattern.getrect()[1]
    # map of character to
    font = {
        " ": (lt.pattern(), 4),
    }

    for letter, pattern in zip(letters, components):
        (x, y, w, _) = pattern.getrect()
        pattern = pattern(-x, -font_pattern_y)
        font[letter] = (pattern, w + 1)

    return font

font = mk_font()

def write_text(text: str):
    result = lt.pattern()
    x = 0
    for c in text.lower():
        p, w = font[c]
        result = result + p(x, 0)
        x += w
    return result
