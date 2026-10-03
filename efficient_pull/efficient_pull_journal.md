# Finding an efficient recipe for pulling an elbow block

Converting a backwards glider to a block:
```bash
for i in {1..6}; do
  echo "sc90b${i}p120"
  uv run oncoming.py --toolkit="sc90b${i}p120" --subtree="0-7" --depth=4 --max-population=4 --n-gun-gliders=1 --simulate-gens=512 | grep -P 'block\(l(-3|4)'
done
```

This found a good recipe at sc90b4 -- 7, 90, (90) converts a b4 glider to a SPEBOE.

Next, we want to find a recipe for the backwards glider. To handle even and odd pulls, we want to find the b4 glider on either side.

We can use snark.py with a bit of a hack. It doesn't allow for backwards gliders, so
we send the recipe first through a snark, and detect when the backwards glider hits the
snark.

```bash
$ uv run snark.py custom-starting-point -t 'x = 72, y = 63, rule = B3/S23
5$53b2o$52bobo$46b2o4bo$44bo2bo2b2ob4o$44b2obobobobo2bo$47bobobobo$47b
obob2o$48bo2$61b2o$52b2o7bo$52b2o5bobo$59b2o2$51b3o$51bo$52bo3$49b2o$
50bo$47b3o$47bo24$10b2o$10b2o!' -s 0 -o results/efficient-pull/1.sqlite
```

When b4 glider hits the snark, it will look like one of these, depending on which
side:

```
x = 75, y = 36, rule = B3/S23
5$19b2o$18bobo19bo$12b2o4bo21bo19bo$10bo2bo2b2ob4o17bo18bobo$10b2obobo
bobo2bo17bo19bo$13bobobobo20bo$13bobob2o21bo$14bo25bo$40bo19b2o$27b2o
11bo19b2o$18b2o7bo12bo$18b2o5bobo12bo$25b2o13bo27b2o$40bo27bo$17b3o20b
o25bobo$17bo22bo25b2o$18bo21bo$40bo17b3o$40bo17bo$9b2o4b2o23bo18bo$8bo
2bo2bobo23bo$8bo2bo3bo24bo$9b2o29bo15b2o$40bo16bo$40bo13b3o$54bo!
```

```bash
uv run snark.py custom-intermediates -r results/efficient-pull/i.sqlite -i 'x = 75, y = 36, rule = B3/S23
5$19b2o$18bobo19bo$12b2o4bo21bo19bo$10bo2bo2b2ob4o17bo18bobo$10b2obobo
bobo2bo17bo19bo$13bobobobo20bo$13bobob2o21bo$14bo25bo$40bo19b2o$27b2o
11bo19b2o$18b2o7bo12bo$18b2o5bobo12bo$25b2o13bo27b2o$40bo27bo$17b3o20b
o25bobo$17bo22bo25b2o$18bo21bo$40bo17b3o$40bo17bo$9b2o4b2o23bo18bo$8bo
2bo2bobo23bo$8bo2bo3bo24bo$9b2o29bo15b2o$40bo16bo$40bo13b3o$54bo!'
```

Now, we run optimize, with must-contain including either of the backwards glider options, or a full snark.

```bash
$ uv run snark.py optimize -r results/efficient-pull/i.sqlite -o results/efficient-pull/1.sqlite -n 1024 --depth-range=0 --must-contain='11b2o$10bobo$4b2o4bo$2bo2bo2b2ob4o$2b2obobobobo2bo$5bobobobo$5bobob2o$6bo2$19b2o$10b2o7bo$10b2o5bobo$17b2o7$b2o4b2o$o2bo2bobo$o2bo3bo$b2o!|7bo$6bobo$7bo4$7b2o$7b2o3$15b2o$15bo$13bobo$13b2o7$3b2o$4bo$b3o$bo!|9b2o$8bobo$2b2o4bo$o2bo2b2ob4o$2obobobobo2bo$3bobobobo$3bobob2o$4bo2$17b2o$8b2o7bo$8b2o5bobo$15b2o7$5b2o$6bo$3b3o$3bo!' --max-allowed-population=100
```
