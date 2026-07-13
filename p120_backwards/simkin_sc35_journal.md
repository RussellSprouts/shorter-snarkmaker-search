# Simkin Glider Gun Building Journal

We're going to build the simkin gun assuming that we have 4 merge circuits based on the SW25T179 shown [here](https://conwaylife.com/wiki/Scorbie_Splitter). This lets us send up to 4 gliders with a minimum spacing of 35. If we send a glider with a spacing of at least 67, we've reset and can send another set of 4.

```bash
$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search1.sqlite -n 600 --partial-range=42 --depth-range=-100-0 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
2100.33/s, 2933.79 avg/s, 11,495,094 done, 218-438 gens, 141,661/1,748,935,309 pending, 0x0, -17.07x2, 12x15 A (1), inf overlap (0), 13 pop (1)
...
129.63/s, 261.90 avg/s, 3,231,883 done, 242-462 gens, 3,476,330/8,778,130,159 pending, 0x0, -10.11x2, 0x0 A (230), inf overlap (0), 0 pop (13)
```

This processed many millions of streams before finally finding results that included the eater 1 in the right spot. Out of 4.6 million results (streams that reach a p2 stable state), two include the eater 1 in the right position. I still haven't implemented searching for partial matches by lane instead of exact x,y, so the initial search with 101 depth values to try is much slower.

Both results are based on the same reaction -- (0, 42, 50, 40, 75, 65) and (0, 42, 50, 40, 141). To better explore, let's use --truncate-n-gliders=1 to start with (0, 42, 50, 40, 75).

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search1.sqlite -o results/35/simkin-search2.sqlite -q 'select * from r order by partial_intermediate_log_prob desc limit 2' --truncate-n-gliders=1

Filtered 1 duplicate results
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search2.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
1408.20/s, 1176.99 avg/s, 5,313,419 done, 195-415 gens, 514,930/1,361,458,979 pending, 0x0, -8.94x2, 6x7 A (1), inf overlap (0), 8 pop (1)
```

There were a few results which added an extra block to the eater, but it found ones in front, so we'll skip those.

At this point, there were 800k results, but only 10k kept the eater 1 in place. The truncate-n-gliders option probably contributed to this. To speed it up, we'll filter to just the ones that lead to the eater 1 being placed.
Using --no-reset-costs, we'll keep the same costs as we continue searching deeper.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search2.sqlite -o results/35/simkin-search3.sqlite -q 'select * from r where partial_intermediate_log_prob > -11' --no-reset-costs

Filtered 2300 duplicate results
Transferred 8637 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search3.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
2067.13/s, 1842.10 avg/s, 13,174,291 done, 162-382 gens, 2,431/1,886,428,148 pending, 0x0, -8.30x4, 25x9 A (1), inf overlap (0), 10 pop (1)
```

There is one result with partial_intermediate_digest=1585696544348514143, which adds the far back block, but it's very messy with a population of 239 and a depth from -56 to 95. There are also results with better log_prob which place the beehive and blinker, but those would block the lane so we don't want to pursue them until we have the back 3 blocks done.

```
...
2038.05/s, 2081.35 avg/s, 8,522,218 done, 180-400 gens, 619,684/5,412,622,595 pending, 0x0, -7.69x1, 13x15 A (1), inf overlap (0), 11 pop (4)
```

Now there are 5 results which place the back block. Let's try those quickly.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search3.sqlite -o results/35/simkin-search4.sqlite -q 'partial_intermediate_digest=1585696544348514143'
...
Transferred 5 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search4.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
2147.80/s, 1834.78 avg/s, 11,726,414 done, 188-408 gens, 19,448/1,647,573,562 pending, 0x0, -7.13x2, 22x35 A (4), inf overlap (0), 20 pop (1)
```

There is one results with partial_intermediate_digest=954146300907376725, but once again it's pretty messy.

```
2364.86/s, 2038.78 avg/s, 15,899,337 done, 201-421 gens, 1,925,131/3,804,042,998 pending, 0x0, -7.13x2, 14x26 A (1), inf overlap (0), 14 pop (1)
```

Now we also found partial_intermediate_digest=5753209004553313824, which places the other remaining block in the back. There are three total results, and 

```
3906.83/s, 2065.38 avg/s, 71,301,259 done, 219-439 gens, 2,736,864/12,723,551,855 pending, 0x0, -7.05x1, 13x33 A (5), inf overlap (0), 16 pop (1)
```

Now there are 11 results which place one of the back blocks. Let's search from those.

```
$ uv run snark.py setup-next-search -i results/35/simkin-search4.sqlite -o results/35/simkin-search5.sqlite -q 'partial_intermediate_digest in (954146300907376725, 5753209004553313824)'
...
Transferred 11 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search5.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
1101.20/s, 1258.56 avg/s, 21,022,236 done, 178-398 gens, 188,955/3,216,095,446 pending, 0x0, -5.41x1, 39x62 A (3), inf overlap (0), 44 pop (1)
```

There's one result which places two of the blocks in the front. Getting the last block in the back might be hard but I think it possible. Let's try it.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search5.sqlite -o results/35/simkin-search6.sqlite -q 'select * from r order by partial_intermediate_log_prob desc limit 1'
...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search6.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
1380.15/s, 1441.94 avg/s, 11,487,138 done, 208-428 gens, 656,812/2,296,111,043 pending, 0x0, -4.24x2, 44x109 A (1), inf overlap (0), 100 pop (1)
```

There are three results which place the last block in the front. The back block is still going to be tough, so let's keep going. That block is between the eater and the other block, so we might need to go all the way back to the result which places that block before the other back block.

```
1272.75/s, 1501.65 avg/s, 43,744,530 done, 228-448 gens, 1,109,641/7,835,977,150 pending, 0x0, -4.24x72, 44x97 A (1), inf overlap (0), 99 pop (1)
```

Now there is a result which places the last back block, but it clobbers the front two. At this point, I think it's better to go back to simkin-search5 and search deeper for a result which places the last back block.

```
$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search5.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255
...
2050.17/s, 1161.15 avg/s, 17,077,562 done, 188-408 gens, 2,552,329/5,803,539,772 pending, 0x0, -5.95x1, 39x62 A (220), inf overlap (0), 39 pop (1)
```

There is one result which places all of the back blocks. Let's continue with that.

```
$ uv run snark.py setup-next-search -i results/35/simkin-search5.sqlite -o results/35/simkin-search7.sqlite -q 'partial_intermediate_digest=8475441342317800377'

Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search7.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
2243.99/s, 1455.29 avg/s, 30,283,843 done, 250-470 gens, 401,999/8,453,026,788 pending, 0x0, -5.95x6, 59x121 A (1), inf overlap (0), 102 pop (1)
```

There are still no results which keep the back three blocks and add another -- the reaction that places the back two blocks takes a while. Let's use a few gliders to do some cleanup while that reaction happens, then we can search further from there.

```
$ uv run snark.py setup-next-search -i results/35/simkin-search7.sqlite -o results/35/simkin-search8.sqlite \
  -q 'partial_intermediate_digest=8475441342317800377 order by population limit 100' \
  -q 'partial_intermediate_digest=8475441342317800377 order by lane_width limit 100' \
  -q 'partial_intermediate_digest=8475441342317800377 order by depth limit 100'

...
Filtered 82 duplicate results
Transferred 198 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search8.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255
```

There are 7 results which add the beehive. Let's try continuing with those and finding results that clean it up.

```
$ uv run snark.py setup-next-search -i results/35/simkin-search8.sqlite -o results/35/simkin-search9.sqlite -q 'select * from r order by partial_intermediate_log_prob desc limit 7'

...
Transferred 7 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search9.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
306.77/s, 386.18 avg/s, 3,068,165 done, 161-381 gens, 210,834/467,027,552 pending, 0x0, -3.60x1, 71x112 A (1), inf overlap (0), 150 pop (1)
```

There are 6 results which clean up the long boat and have the lowest partial_intermediate_overlapping_population. Let's pick the best of those.

```
$ uv run snark.py setup-next-search -i results/35/simkin-search9.sqlite -o results/35/simkin-search10.sqlite -q 'partial_intermediate_overlapping_digest = 1512258518775863282 and partial_intermediate_log_prob > -4.8 order by population+depth limit 1'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search10.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
437.52/s, 554.47 avg/s, 905,666 done, 163-383 gens, 221/140,114,977 pending, 0x0, -3.60x4, 67x175 A (1), inf overlap (0), 218 pop (1)
```

There are results which clear the whole SW side of the gun from ash that would interfere, leaving just two beehives to clear.

```
$ uv run snark.py setup-next-search -i results/35/simkin-search10.sqlite -o results/35/simkin-search11.sqlite -q 'partial_intermediate_overlapping_digest = 4499978174598477964 and partial_intermediate_log_prob > -4.8 order by population+depth limit 5'

...
Transferred 5 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search11.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
642.26/s, 672.21 avg/s, 1,943,916 done, 155-375 gens, 49,725/336,830,330 pending, 0x0, -3.60x136, 71x169 A (2), inf overlap (0), 225 pop (1)
```

Now we've found some results which clean up the entire area around the intermediate results very nicely. Let's continue from there



```
$ uv run snark.py setup-next-search -i results/35/simkin-search11.sqlite -o results/35/simkin-search12.sqlite -q 'partial_intermediate_overlapping_digest = -905921443007483322 and partial_intermediate_log_prob > -4.8 order by population+depth'

...
Transferred 4 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search12.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
219.83/s, 327.82 avg/s, 4,608,292 done, 179-399 gens, 152,711/955,494,531 pending, 0x0, -3.53x16, 70x162 A (1), inf overlap (0), 223 pop (1)

```

There are 4 results which place the back block of the front 3 blocks, which is probably the best next item to place. Of those, one has the cleanest set of overlapping items.

partial_intermediate_digest=-4861072044468114049 and partial_intermediate_overlapping_digest=-9117069071120457350

There's also a result which places the blinker and has the surrounding area completely clear. Let's take that as well.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search12.sqlite -o results/35/simkin-search13.sqlite -q 'partial_intermediate_digest=-4861072044468114049 and partial_intermediate_overlapping_digest=-9117069071120457350' -q 'partial_intermediate_digest=695521621877188254 order by partial_intermediate_overlapping_population limit 1'
...
Transferred 2 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search13.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
260.68/s, 315.76 avg/s, 11,481,666 done, 218-438 gens, 1,647,555/4,032,133,891 pending, 0x0, -2.35x1, 80x161 A (1), inf overlap (0), 204 pop (2)
```

There is a result which has the back block + blinker, and another which has the first two blocks.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search13.sqlite -o results/35/simkin-search14.sqlite -q 'partial_intermediate_digest in (-4844308016031593667, -861303193338872548)'
...
Transferred 2 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search14.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
719.74/s, 650.90 avg/s, 42,467,880 done, 231-451 gens, 5,898,490/15,445,541,312 pending, 0x0, -2.35x128, 64x176 A (1), inf overlap (0), 228 pop (1)
```

Even after all of that, there are no results which improve on the previous.

There are 419 results which keep the back block + blinker (-4844308016031593667),
and 192k results which keep the back two blocks (-861303193338872548).

Of the 192k, there are three which clean up the partial_intermediate_overlapping_digest to give enough clearance on the SW side, but they are large.
-6589263458846144438, 5701102026080860447, -3601778584558429576

Let's focus instead on the 419 results. There are 4 unique partial_intermediate_overlapping_digests. Two of them have good clearance.
-8674394527424676069 (6 results), -1117485727613482492 (410 results).

Let's take those and transfer them using --no-reset-costs. There are two results with cost 64 and 68 which we've already explored deeply, so let's remove those.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search14.sqlite -o results/35/simkin-search15.sqlite -q 'partial_intermediate_digest=-4844308016031593667 and partial_intermediate_overlapping_digest in (-8674394527424676069, -1117485727613482492)' --no-reset-costs
...
Filtered 136 duplicate results
Transferred 280 results as starting_points.

$ sqlite3 results/35/simkin-search15.sqlite
> delete from queue where cost=64;
> delete from queue where cost=68;

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search15.sqlite -n 700 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
438.16/s, 444.37 avg/s, 15,537,087 done, 198-418 gens, 1,239,147/6,496,061,168 pending, 0x0, -1.18x4, 64x170 A (1), inf overlap (0), 221 pop (1)
```

There is one result which places the next block. partial_intermediate_digest=2043155643089006004. There's just one block to go!

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search15.sqlite -o results/35/simkin-search16.sqlite -q 'partial_intermediate_digest=2043155643089006004'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search16.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
342.87/s, 471.41 avg/s, 23,318,275 done, 255-475 gens, 478,686/2,730,829,136 pending, 0x0, -1.18x1012053, 80x155 A (1), inf overlap (0), 232 pop (1)
```

The reaction that adds the last pieces takes a while to complete, so we might not find results which add the last block yet. Let's run autoshrink but add a `sys.exit` before it starts running optimize, so we get what autoshrink picks as the best candidates for next time. Later I'll add support for the merged-stream-gen-options to autoshrink.

```bash
$ uv run snark.py autoshrink -r results/simkin-stages.sqlite -i results/35/simkin-search16.sqlite -o results/35/simkin-search17.sqlite -n 600 --partial-range=42 --depth-range=-21 -q 'partial_intermediate_digest=2043155643089006004' -c 32

...
Filtered 53 duplicate results
Transferred 163 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search17-round1.sqlite -n 600 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255

...
191.59/s, 338.60 avg/s, 2,861,143 done, 114-334 gens, 73,151/467,707,825 pending, 42x1, -1.18x422523, 82x150 A (1), 62 overlap (1), 252 pop (8)
```

Now we have a completion! It has a loaf in the way that we should clean up. Let's look for results which remove that.

```bash
$ uv run snark.py setup-next-search -i results/35/simkin-search17-round1.sqlite -o results/35/simkin-search18.sqlite -q 'full_intermediate is not null'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/simkin-stages.sqlite -o results/35/simkin-search18.sqlite -n 300 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255
```

Turns out the loaf is not overlapping technically so it will be cleaned up by the full_intermediate_non_overlapping_depth_separation, but we don't have a good way to clean it up otherwise. Let's run autoshrink.

```bash
$ while true; do uv run snark.py autoshrink -r results/simkin-stages.sqlite -i results/35/simkin-search18.sqlite -o results/35/simkin-search19.sqlite -n 256 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255 -c 32 -q 'full_intermediate is not null' --n-results-limit=1000000; done
```

This finished round11, but with only 1 million per round there were pretty much only two gliders per round. Let's try again with more.

```bash
while true; do uv run snark.py autoshrink -r results/simkin-stages.sqlite -i results/35/simkin-search18.sqlite -o results/35/simkin-search20.sqlite -n 256 --partial-range=42 --depth-range=-21 --merged-stream-gen-options="4x35-255;67-255" --gen-options=35-255 -c 32 -q 'full_intermediate is not null' --n-results-limit=5000000; done
```

with rs as (select * from r where full_intermediate is not null) select * from (select * from rs order by population limit 1) union all select * from (select * from rs order by depth, population limit 1) union all select * from (select * from rs order by lane_width, population limit 1) union all select * from (select * from rs order by full_intermediate_overlapping_population, population limit 1) union all select * from (select * from rs order by full_intermediate_non_overlapping_depth_separation desc, population limit 1)