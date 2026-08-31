# Snarks with Seeds of Destruction

Finding alternate versions of the snarkmaker recipe that
include seeds of destruction, so that a reverse glider will
cleanly remove it.

E.g.:

1. Remove the snark and send a chained reverse glider
```
x = 64, y = 72, rule = LifeHistory
18$33.A$33.A.A$33.2A7$12.2A$13.A$11.A$11.5A14.2A$16.A13.A$13.3A12.A.A
$12.A15.2A$12.4A$10.2A3.A3.2A$9.A2.3A4.2A$9.2A.A$12.A$12.2A3$20.2A$
11.C9.A$10.C.C5.3A$10.C2.C4.A$11.2C$24.C$23.C.C$23.C2.C$24.2C2$10.2C$
9.C.C$10.C!
```

2. Remove the snark

```
x = 64, y = 173, rule = LifeHistory
25$51.A$51.A.A$51.2A14$23.2A$24.A$22.A$22.5A14.2A$27.A13.A$24.3A12.A.
A$23.A15.2A$23.4A$21.2A3.A3.2A$20.A2.3A4.2A$20.2A.A$23.A$23.2A3$31.2A
$21.2C9.A$21.2C6.3A$29.A$35.3C4$29.2C$28.C2.C$29.2C48$48.A$48.A.A$48.
2A14$20.2A$21.A$19.A$19.5A14.2A$24.A13.A$21.3A12.A.A$20.A15.2A$20.4A$
18.2A3.A3.2A$17.A2.3A4.2A$17.2A.A$20.A$20.2A3$28.2A$18.2C9.A$18.2C6.
3A$26.A2$14.2C$14.2C2$33.2C$25.2C6.2C$25.2C!
```

To set up, first create a custom intermediates DB:

```bash
$ uv run snark.py custom-intermediates -r results/sod_snark/intermediates.sqlite -i 'x = 435, y = 300, rule = B3/S23                                                                                                                                                                           94b2o$93bobo$87b2o4bo$85bo2bo2b2ob4o$85b2obobobobo2bo$88bobobobo$88bob
ob2o$89bo2$102b2o$93b2o7bo$93b2o5bobo$100b2o7$90b2o$91bo$88b3o$88bo21$
121b3o$121bo$122bo18$41b2o$41b2o39$117b26o117$307bo$307bo$307bo$307bo$
307bo$307bo$307bo$307bo$307bo$53b2o252bo$52bobo5b2o245bo$46b2o4bo7b2o
169b2o15bo58bo$44bo2bo2b2ob4o173bobo6b2o6bobo57bo108b2o$44b2obobobobo
2bo167b2o4bo7bo2bo5b2o58bo108b2o$47bobobobo168bo2bo2b2ob4o4bobo65bo$
47bobob2o169b2obobobobo2bo5bo66bo97b2o$48bo176bobobobo75bo96bobo5b2o$
68bo156bobob2o76bo90b2o4bo7b2o$61b2o4bobo156bo80bo88bo2bo2b2ob4o$52b2o
7bo5bobo237bo88b2obobobobo2bo$52b2o5bobo6bo170b2o158bobobobo$59b2o169b
2o7bo159bobob2o$230b2o5bobo160bo$237b2o181b2o$63bo349b2o5b2o$63bo179b
2o159b2o7bo$63bo178bo2bo158b2o5bobo$141bo101bobo165b2o$49b2o90bo102bo$
50bo90bo$47b3o91bo85b2o$47bo93bo86bo190b2o$141bo83b3o191b2o$141bo83bo$
141bo259b2o$141bo260bo$141bo257b3o$141bo257bo$141bo$141bo$141bo$141bo$
141bo$141bo9$80b3o$80bo$81bo176b3o$258bo$259bo2$432b3o$432bo$433bo12$
2o$2o$178b2o$178b2o3$352b2o$352b2o!
'
```

Then create a custom starting point which is the snarkmaker recipe minus the
last ~20 gliders

```bash
$ uv run snark.py custom-starting-point -o results/sod_snark/1.sqlite -s "0,135,93,105,107,115,91,105,102,118,101,96,92,138,151,147,129,108,91,116,154,149,128,114,202,128,128,120,110,113,162,115,90,91,146,127,103,118,135,176,124,180,96,108,218,91,90,111,111,99,104,202,174,135,111,214,116,94,182,91,93,190,103,106,95,96,117,91,122,110,147,117,91,120,92,105,149,108,119,102,106,126,124,106,128,150,130,132,134,90,197,99,132,91,161,146,100,108,145,97,138,100,101,167,91,183,140,90,94,99,93,100,105,102,153,105,92,121,92,90,99,96,97,116,91,193,94,91,117,100,103,122,121,90,109,205,90,105,110,93,232,108,100,93,145,118,106,90,101,151,134,113,141,96,91,123,91,111,90,102,95,198,107,122,162,90,114,96,92,114,127,109,126,98,135,95,141,114,98,124,102,148,129,91,92,136,107,249,181,93,141,106,109,98,113,95,128,108,250,105,98,109,100,96,170,94,95,102,101,206,98,100,170,111,152,169,97,141,186,100,101,94,96,95,110,95,134,111,98,115,91,91,96,102,98,98,101,175,156,238,100,99,172,116,122"
```

Now search for streams that add one of the viable missing pieces:

```bash
$ uv run snark.py optimize -r results/sod_snark/intermediates.sqlite -o results/sod_snark/1.sqlite -n 720 --depth-range="0" --partial-range=1 --must-contain='4$12b2o$11bobo$5b2o4bo$3bo2bo2b2ob4o$3b2obobobobo2bo$6bobobobo$6bobob
2o$7bo8$22bo$22bo$22bo!|9$17b2o$16bobo5b2o$10b2o4bo7b2o$8bo2bo2b2ob4o$8b2obobobobo2bo$11bobobo
bo$11bobob2o$12bo!|10$20b2o$19bobo6b2o$13b2o4bo7bo2bo$11bo2bo2b2ob4o4bobo$11b2obobobobo2b
o5bo$14bobobobo$14bobob2o$15bo!|13$27b2o$26bobo$20b2o4bo$18bo2bo2b2ob4o$18b2obobobobo2bo$21bobobobo$
21bobob2o$22bo7$39b2o$38bo2bo$39bobo$40bo!'
```

Partials for end snark
> select partial_intermediate_digest, count(*) from r where partial_intermediate_digest in (8938491844139237213, -94428361224738471, 5598193673153933675) group by partial_interme
diate_digest
Row(partial_intermediate_digest=-94428361224738471, count(*)=3)
Row(partial_intermediate_digest=5598193673153933675, count(*)=131)
Row(partial_intermediate_digest=8938491844139237213, count(*)=62)

There are no partials for the chain snark yet, and I've searched 548-713 gens deep. Let's come back and search that later. First, let's search deeper in the end snark.

```bash
$ uv run snark.py setup-next-search -i results/sod_snark/1.sqlite -o results/sod_snark/end1.sqlite -q 'partial_intermediate_digest in (8938491844139237213, -94428361224738471, 5598193673153933675)'

...
Filtered 7 duplicate results
Transferred 189 results as starting_points.

$ uv run snark.py optimize -r results/sod_snark/intermediates.sqlite -o results/sod_snark/end1.sqlite -n 720 --depth-range="0" --partial-range=1 --must-contain='5$17b2o$16bobo5b2o$10b2o4bo7b2o$8bo2bo2b2ob4o$8b2obobobobo2bo$11bobobo
bo$11bobob2o$12bo2$25b2o$16b2o7bo$16b2o5bobo$23b2o3$27bo$27bo$27bo2$
13b2o$14bo$11b3o$11bo!|8$20b2o$19bobo5b2o$13b2o4bo7b2o$11bo2bo2b2ob4o$11b2obobobobo2bo$14bobo
bobo$14bobob2o$15bo2$28b2o$19b2o7bo$19b2o5bobo$26b2o4$29b3o3$16b2o$17b
o$14b3o$14bo!|9$18b2o$17bobo5b2o$11b2o4bo7b2o$9bo2bo2b2ob4o$9b2obobobobo2bo$12bobobo
bo$12bobob2o$13bo$33bo$26b2o4bobo$17b2o7bo5bobo$17b2o5bobo6bo$24b2o7$
14b2o$15bo$12b3o$12bo!'

...
1888.25/s, 2086.90 avg/s, 1/10,747,914 done, 330-495 gens, 75,032/768,732,278 pending, 0x0, -1.91x1, 101x113 A (1), -72 (1) fd, inf overlap (0), 219 pop (1)
```

Let's try continuing from the one result.

```bash
$ uv run snark.py setup-next-search -i results/sod_snark/end1.sqlite -o results/sod_snark/end2.sqlite -q '1=1'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/sod_snark/intermediates.sqlite -o results/sod_snark/end2.sqlite -n 720 --depth-range="0" --partial-range=1 --must-contain='3$13b2o$12bobo5b2o$6b2o4bo7b2o$4bo2bo2b2ob4o$4b2obobobobo2bo$7bobobobo
$7bobob2o$8bo$28bo$21b2o4bobo$12b2o7bo5bobo$12b2o5bobo6bo$19b2o4$22b3o
3$9b2o$10bo$7b3o$7bo!|3$12b2o$11bobo5b2o$5b2o4bo7b2o$3bo2bo2b2ob4o$3b2obobobobo2bo$6bobobobo
$6bobob2o$7bo$27bo$20b2o4bobo$11b2o7bo5bobo$11b2o5bobo6bo$18b2o3$22bo$
22bo$22bo2$8b2o$9bo$6b3o$6bo!'

...
2297.42/s, 1859.98 avg/s, 2/14,517,296 done, 517-682 gens, 1,012,268/1,291,226,670 pending, 1x2, -3.63x2, 101x118 A (2), -72 (2) fd, 5 overlap (2), 249 pop (2)
```

This was successful! Just need to clean up.

```
$ uv run snark.py autoshrink -r results/sod_snark/intermediates.sqlite -i results/sod_snark/end2.sqlite -o results/sod_snark/end_shrink.sqlite -n 720 --depth-range="0" --partial-range=1 -q 'full_intermediate is not null' --must-contain='5$15b2o$14bobo5b2o$8b2o4bo7b2o$6bo2bo2b2ob4o$6b2obobobobo2bo$9bobobobo
$9bobob2o$10bo$30bo$23b2o4bobo$14b2o7bo5bobo$14b2o5bobo6bo$21b2o3$25bo
$25bo$25bo2$11b2o$12bo$9b3o$9bo!|15$19b2o$18bobo5b2o$12b2o4bo7b2o$10bo2bo2b2ob4o$10b2obobobobo2bo$13bob
obobo$13bobob2o$14bo$34bo$27b2o4bobo$18b2o7bo5bobo$18b2o5bobo6bo$25b2o
4$28b3o3$15b2o$16bo$13b3o$13bo!' --n-results-limit=1000000 --max-allowed-population=250
```

