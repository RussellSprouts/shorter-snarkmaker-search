# Logic

The oncoming glider construction arm allows you to cheaply create reactions
close to the lane. We can look for recipes that detect gliders to create
still lives, convert those still lives into gliders, or perform other logical
operations. We can use the length of the construction arm as data storage.

# Incoming 90 degree glider

```
uv run oncoming.py --toolkit=sc90b5p120 --subtree='0-36' --depth=1 --with-debris-rle='5bo$5bobo$5b2o25$3o$o$bo!' --and-without-debris --without-debris-max-population=0

# Glider was too far away

for i in {0..36}; do
echo "Checking $i"
uv run oncoming.py --toolkit=sc90b5p120 --subtree='0-36' --depth=1 --with-debris-rle='$13bo$13bobo$13b2o15$b3o$bo$2bo!' --and-without-debris --without-debris-max-population=0 --evolve-debris-gens="$i"
done

uv run oncoming.py --toolkit=sc90b5p120 --with-debris-rle='$13bo$13bobo$13b2o15$b3o$bo$2bo!' --and-without-debris --evolve-debris-gens=30 --print-rle='17(mod 120)'

```

## Detect an incoming 90 degree glider, convert to block at l16

uv run oncoming.py --toolkit=sc90b5p120 --with-debris-rle='$13bo$13bobo$13b2o15$b3o$bo$2bo!' --and-without-debris --evolve-debris-gens=18 --print-rle='advance_debris 18, 16 (mod 120);'

The detected glider hits a gun glider to make a bi-block, and the recipe glider
turns it into the block, so the recipe glider can be delayed by multiples of
4 ticks.

x = 227, y = 31, rule = LifeHistory
5$6.A13.A185.A$7.A11.A187.A$5.3A11.3A183.3A11$213.D2.3D$212.2D2.D$
213.D2.3D$213.D2.D.D$16.3C193.3D.3E$16.C199.A$17.C199.A!


uv run oncoming.py --toolkit=sc90b5p120 --with-debris-rle='3o14b2o$o16b2o$bo!' --and-without-debris --depth=3 --subtree='0-256'


for i in {0..120}; do
echo "Checking $i"
uv run oncoming.py --toolkit=sc90b5p120 --subtree='0-120' --depth=1 --with-debris-rle='25bo$25bobo$25b2o25$3o$o$bo!' --and-without-debris --without-debris-max-population=0 --evolve-debris-gens="$i"
done

The most useful results put a beehive at l15,o1. The reaction is adjustable, because it catches the glider with a kickback glider.


# Catch it with a recipe glider

3o$o$bo55$69bo$69bobo$69b2o!

uv run oncoming.py --toolkit=sc90b5p120 --subtree='256-292' --depth=1 --with-debris-rle='3o$o$bo55$69bo$69bobo$69b2o!' --and-without-debris --without-debris-max-population=0

# Not gate

 uv run oncoming.py --print-rle="27(mod 120),211,137,167,165" --with-debris-rle='3o9b2o$o11b2o$bo!' --and-without-debris 

# Tubs

Tubs have a good symmetry to use for snarks.

```
uv run oncoming.py --subtree="0-256" --with-debris-rle='3o10bo$o11bobo$bo11bo!' --depth=3 --and-without-debris --without-debris-max-population=24 --max-population=24 --concurrent --without-debris-same-gliders-consumed > results/logic/tub-l12.txt

uv run oncoming.py --subtree="0-256" --with-debris-rle='b3o$bo$2bo3$bo$obo$bo!' --depth=3 --and-without-debris --without-debris-max-population=24 --max-population=24 --concurrent --without-debris-same-gliders-consumed > results/logic/tub-l-6.txt
```

31, 162, 104, 176, 92, 217

105, 120, 135
31, 162, 104

90, 134;83, 99;89, 109

90;134;256-263
83;99;256-263
89;109;256-263


--subtree="47;135;256-263"

315 (75, 195, 91, 253, 93, 129, 119, 93, 190) ['block(l-3,d7,o0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'glider(l0)(ph3)(♗⬂①)', 'w/o:', 'block(l-9,d37,o0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'glider(l-6)(ph1)(♗⬁①)', 'diff:', '+block(l-3,d7,o0)', '+glider(l0)(ph3)(♗⬂①)', '-block(l-9,d37,o0)', '-glider(l-6)(ph1)(♗⬁①)']


block l-3
75, 195, 91, 253, 93, 129, 183, 93, 165

# Langton's ant logic

1. If there is a tub present, then:
  - Push the sc elbow block to flip the snark
  - Push the snark target by one to flip the output
2. Build a crabstretcher/corderpush to start going to the
    next square
3. Build copying circuitry to copy the second copy of the dna
4. Flip whether there was a tub present

# Block census results

l-6:
75, 97, 154 ; 123, 99, 160: extra glider without debris

l-7:

- 75, 208, 197

  NE Black Even (w/ block)

  - (75, 208, 197, 259, 102, 91) ['block(l-7,d23,o0)', 'g0', 'g1', 'g2', 'glider(d59)(ph2)(♝⬀⓪)', 'w/o:', 'g0', 'g1', 'g2', 'diff:', '+block(l-7,d23,o0)', '+glider(d59)(ph2)(♝⬀⓪)']

  NW Black Odd (w/ block)
  

  SW White Even (w/ block)
  
  - (75, 208, 197, 263, 111, 146) ['block(l-7,d23,o0)', 'g0', 'g1', 'g2', 'g3', 'w/o:', 'g0', 'g1', 'g2', 'g3', 'glider(d78)(ph2)(♗⬃⓪)', 'diff:', '+block(l-7,d23,o0)', '-glider(d78)(ph2)(♗⬃⓪)']

  SW Black Odd (w/ block)

  - (75, 208, 197, 261, 138, 143) ['block(l-7,d23,o0)', 'g0', 'g1', 'g2', 'glider(d63)(ph1)(♝⬃①)', 'w/o:', 'g0', 'g1', 'g2', 'diff:', '+block(l-7,d23,o0)', '+glider(d63)(ph1)(♝⬃①)']

  NE White Even (w/o block)
  
  - (75, 208, 197, 259, 104, 201) ['block(l-7,d23,o0)', 'g0', 'g1', 'w/o:', 'g0', 'g1', 'glider(d80)(ph2)(♗⬀⓪)', 'diff:', '+block(l-7,d23,o0)', '-glider(d80)(ph2)(♗⬀⓪)']

  NE White Odd (w/o block)
  
  - (75, 208, 197, 263, 126, 103) ['block(l-7,d23,o0)', 'g0', 'g1', 'g2', 'g3', 'w/o:', 'g0', 'g1', 'g2', 'g3', 'glider(d92)(ph1)(♗⬀①)', 'diff:', '+block(l-7,d23,o0)', '-glider(d92)(ph1)(♗⬀①)']

  SW Black Even (w/o block)
  
  - (75, 208, 197, 263, 178, 120) ['block(l-7,d23,o0)', 'g0', 'g1', 'g2', 'w/o:', 'g0', 'g1', 'g2', 'glider(d69)(ph0)(♝⬃⓪)', 'diff:', '+block(l-7,d23,o0)', '-glider(d69)(ph0)(♝⬃⓪)']


'+glider(d49)(ph2)(♝⬃⓪)'
'+glider(d63)(ph1)(♝⬃①)'
'+glider(d54)(ph0)(♗⬃⓪)'

'+glider(d54)(ph2)(♗⬀⓪)'
'+glider(d59)(ph2)(♝⬀⓪)'


'-glider(d100)(ph0)(♗⬃⓪)'
'-glider(d78)(ph2)(♗⬃⓪)'
'-glider(d80)(ph0)(♗⬃⓪)'
'-glider(d88)(ph3)(♗⬃①)'

'-glider(d69)(ph0)(♝⬃⓪)'
'-glider(d75)(ph2)(♝⬃⓪)'
'-glider(d83)(ph1)(♝⬃①)'
'-glider(d83)(ph3)(♝⬃①)'

'-glider(d83)(ph2)(♝⬀⓪)'
'-glider(d63)(ph2)(♝⬀⓪)'
'-glider(d79)(ph0)(♝⬀⓪)'
'-glider(d85)(ph1)(♝⬀①)'
'-glider(d85)(ph2)(♝⬀⓪)'
'-glider(d111)(ph1)(♝⬀①)'
'-glider(d99)(ph3)(♝⬀①)'

'-glider(d78)(ph2)(♗⬀⓪)'
'-glider(d80)(ph2)(♗⬀⓪)'
'-glider(d82)(ph2)(♗⬀⓪)'
'-glider(d84)(ph2)(♗⬀⓪)'
'-glider(d86)(ph2)(♗⬀⓪)'
'-glider(d88)(ph2)(♗⬀⓪)'
'-glider(d90)(ph2)(♗⬀⓪)'
'-glider(d92)(ph2)(♗⬀⓪)'
'-glider(d94)(ph2)(♗⬀⓪)'
'-glider(d96)(ph2)(♗⬀⓪)'
'-glider(d92)(ph1)(♗⬀①)'




75, 207, 198
75, 222, 183

l-9:
67, 208, 197

l-10:
