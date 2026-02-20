from lifetree import lt

def mk_font():
    font_pattern = lt.pattern(
        """
    3ob2o2b3ob2o2b3ob3ob3obobob3ob3obobobo3bo3bobo2bob3ob3ob3o2b3ob3ob3obo
    bobobobo3bobobobobob3ob3o2bo2b3ob3obobob3ob3ob3ob3ob3o$obobobobo3bobob
    o3bo3bo3bobo2bo3bo2bobobo3b2ob2ob2obobobobobobobo2bobobo4bo2bobobobobo
    3bobobobobo3bobobob2o4bo3bobobobo3bo5bobobobobo$obob3obo3bobob3ob3obob
    ob3o2bo3bo2b2o2bo3bobobobob2obobob3obobo2b3ob3o2bo2bobobobobobobo2bo2b
    obo2bo2bobo2bo2b3ob3ob3ob3ob3o3bob3ob3o$3obobobo3bobobo3bo3bobobobo2bo
    3bo2bobobo3bo3bobo2bobobobo3bobo2b2o4bo2bo2bobobobobobobobobo2bo2bo3bo
    bo2bo2bo5bo3bo3bobobo2bo2bobo3bo$obob3ob3ob3ob3obo3b3obobob3ob2o2bobob
    3obo3bobo2bob3obo3b2obobobob3o2bo2b3o2bo3bobo2bobo2bo2b3ob3ob3ob3ob3o
    3bob2o2b3o2bo2b3ob3o!
    """
    )
    components = font_pattern.components()
    # sort by x value
    components.sort(key=lambda x: x.getrect()[0])
    letters = "abcdefghijklmnopqrstuvwxyz0123456789"

    # map of character to
    font = {
        " ": (lt.pattern(), 4),
    }

    for letter, pattern in zip(letters, components):
        (x, y, w, _) = pattern.getrect()
        pattern = pattern(-x, -y)
        font[letter] = (pattern, w + 1)

    return font

font = mk_font()

def write_text(pattern, text: str):
    result = pattern
    x = 0
    for c in text.lower():
        p, w = font[c]
        result = result + p(x, 0)
        x += w
    return result
