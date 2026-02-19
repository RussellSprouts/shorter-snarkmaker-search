"""
The snarkmaker recipe first creates a block that
is far offset from the rest of the pattern. This block
will become the elbow after the stream passes through the
snark. However, we can also consider constellations which
become an elbow after we send a glider through the snark.
This expands our search space.

Uses results from the octo3obj database.
"""

import lifelib
from dataclasses import dataclass, field
from typing import List, Any
import json
import heapq
import time
import sys

sess = lifelib.load_rules("b3s23")
lt = sess.lifetree()

nw_glider1 = lt.pattern('2o$obo$o!')
nw_glider2 = nw_glider1[1]
nw_glider3 = nw_glider1[2]
nw_glider4 = nw_glider1[3]

pi = lt.pattern('3o$obo$obo!')
pi_ash = pi[256].octodigest()
pi_ash2 = pi[257].octodigest()

def process(filename):
    with open(filename, 'r') as f:
        halo = lt.pattern('3o$3o$3o!')
        cell = lt.pattern('o')
        beeg = lt.pattern(f.read())
        print(beeg.population)
        (x, y, w, h) = beeg.getrect()
        print(w, h)
        slice = beeg[0:0, 64:64]
        for i in range(0, w//64, 64):
            center_x = i + x
            patt = beeg[center_x-20:center_x+20, y-1:y+h+1]

            matches = [
                patt.match(nw_glider1, halo=halo),
                patt.match(nw_glider2, halo=halo),
                patt.match(nw_glider3, halo=halo),
                patt.match(nw_glider4, halo=halo),
            ]
            m = (matches[0] if matches[0].population else
                matches[1] if matches[1].population else
                matches[2] if matches[2].population else
                matches[3])
            
            phase = (nw_glider1 if matches[0].population else
                    nw_glider2 if matches[1].population else
                    nw_glider3 if matches[2].population else
                    nw_glider4)

            (mx, my, _, _) = m.getrect()

            m = m + cell(mx + 23, my + 23)

            patt_with_follow_up = patt + m.convolve(phase)

            result = patt_with_follow_up[512]
            digest = result.octodigest()
            if digest == pi_ash or digest == pi_ash2:
                info = {
                    'file': filename,
                    'rle': patt_with_follow_up.rle_string(),
                }
                print(json.dumps(info))

process('all-block.mc')
process('all-beehive.mc')
process('all-boat.mc')
process('all-fishhook.mc')
process('all-pond.mc')
process('all-ship.mc')