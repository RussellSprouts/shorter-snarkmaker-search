from lifetree import lt

def mk_font():
    font_pattern = lt.pattern(
        """
x = 155, y = 5, rule = B3/S23
3A.2A2.3A.2A2.3A.3A.3A.A.A.3A.3A.A.A.A3.A3.A.A2.A.3A.3A.3A2.3A.3A.3A.
A.A.A.A.A3.A.A.A.A.A.3A.3A2.A2.3A.3A.A.A.3A.3A.3A.3A.3A$A.A.A.A.A3.A.
A.A3.A3.A3.A.A2.A3.A2.A.A.A3.2A.2A.2A.A.A.A.A.A.A.A2.A.A.A4.A2.A.A.A.
A.A3.A.A.A.A.A3.A.A.A.2A4.A3.A.A.A.A3.A5.A.A.A.A.A$A.A.3A.A3.A.A.3A.
3A.A.A.3A2.A3.A2.2A2.A3.A.A.A.A.2A.A.A.3A.A.A2.3A.3A2.A2.A.A.A.A.A.A.
A2.A2.A.A2.A2.A.A2.A2.3A.3A.3A.3A.3A3.A.3A.3A.3A$3A.A.A.A3.A.A.A3.A3.
A.A.A.A2.A3.A2.A.A.A3.A3.A.A2.A.A.A.A3.A.A2.2A4.A2.A2.A.A.A.A.A.A.A.A
.A2.A2.A3.A.A2.A2.A5.A3.A3.A.A.A2.A2.A.A3.A$A.A.3A.3A.3A.3A.A3.3A.A.A
.3A.2A2.A.A.3A.A3.A.A2.A.3A.A3.2A.A.A.A.3A2.A2.3A2.A3.A.A2.A.A2.A2.3A
.3A.3A.3A.3A3.A.2A2.3A2.A2.3A.3A5.A!
        """
    )
    components = font_pattern.components()
    # sort by x value
    components.sort(key=lambda x: x.getrect()[0])
    letters = "abcdefghijklmnopqrstuvwxyz0123456789-."

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
