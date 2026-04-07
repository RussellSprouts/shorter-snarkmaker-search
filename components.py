import lifelib
from lifetree import lt

halo = lt.pattern('ooo$ooo$ooo').centre()

def pattern_components(p: lifelib.Pattern):

    ccs = []
    x = p.__copy__()

    while (x.nonempty()):

        cc = x.component_containing(halo=halo)
        x -= cc
        ccs.append(cc)

    return ccs
