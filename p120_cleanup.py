
from life_history import lht
from lifetree import lt
from gliders import mk_glider
import sys

cleanup_problem = lht.pattern("""x = 70, y = 81, rule = x3xsixstate
$19.9D$16.14D$11.20D$8.25D$7.28D$6.30D$5.10D5B17D$5.10D6B16D$4.11D2BA
4B16D$3.12D2B3A4B15D$2.13D5BA4B15D$2.13D4B2A5B15D$2.5D20B14D$.6D27B9D
$.5D29B9D$.5D9B2A18B9D$.5D2B2A3B2A2BA17B10D$6D2B2A8BA18B9D$6D6BA4BA
20B9D$6D6BA3BA21B9D$7D6BABA22B10D$9D30B9D$10D29B9D$10D6BA23B8D$11D3BA
BA18B2A5B7D$11D4BA19B2A6B6D$11D32B6D$.11D20B2A5B2A2B5D$.13D11BA6B2A5B
2A2B5D$.13D9BABA17B5D$.13D10B2A17B5D$2.13D27B6D$2.20D20B6D$3.19D18B8D
$4.19D17B8D$4.22D14B8D$6.20DB2A12B7D$8.18DBABA12B5D$10.16DBA11B.B$17.
9D13B$19.6D.12B$27.12B$28.12B$29.12B$30.12B$31.12B$32.13B$33.13B$33.
14B$34.14B$36.13B$36.14B$37.14B$38.14B$40.13B$41.13B$42.13B$43.13B$
44.13B$45.13B$46.13B$47.13B$48.13B$49.13B$50.13B$51.13B$52.13B$53.12B
$54.12B$55.12B$56.12B$57.12B$58.12B$59.11B$60.9B$61.7B$62.5B$63.3B$
64.2B!
""")

glider_pattern = lht.pattern("AA$A.A$A!")

blue = lht.pattern("3B$3B$3B!")

glider_location = cleanup_problem.match(glider_pattern, halo='.')
glider = glider_location.convolve(glider_pattern)

print('blue', glider.convolve(blue).rle_string())

(gx, gy, _, _) = glider.getrect()
cleanup_problem = cleanup_problem - glider + blue(gx, gy)

directory = sys.argv[1]

for i in range(0, 140):
    new_glider = mk_glider(0, i)(gx, gy)
    p = cleanup_problem + new_glider.convolve(lht.pattern('A'))
    with open(f"{directory}/{i}.rle", 'w') as f:
        f.write(p.rle_string().replace('x3xsixstate', 'LifeHistory'))