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