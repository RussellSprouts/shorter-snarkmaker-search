
```bash
$ uv run snark.py recipe-intermediates -i ../demonoid/sc35/p46-seed-salvo.rle -o results/35/p46-stages.sqlite 

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-1.sqlite -n 600 --partial-range=74 --depth-range=-100-0 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='3bo$b3o$o$2o!'

...

# From speedydelete's search:
$ uv run snark.py custom-starting-point -o results/35/p46-try2.sqlite -s '0,54,53,43,51,77'

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-try2.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='3bo$b3o$o$2o!' --must-contain='2o$2o$12bo$10b3o$9bo$9b2o!|2$38bo$36b3o$35bo$35b2o6$2b2o$2b2o!'

1645.00/s, 1606.39 avg/s, 2,701/3,507,212 done, 197-417 gens, 442/463,529,772 pending, 0x0, -16.99x1, 47x115 A (1), inf overlap (0), 141 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-try2.sqlite -o results/35/p46-3.sqlite -q 'partial_intermediate_digest = -7834883841845249356'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-3.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='2$38bo$36b3o$35bo$35b2o6$2b2o$2b2o!' --must-contain='11$43bo$41b3o$40bo$40b2o2$16b2o$16b2o3$7b2o$7b2o!|14$48bo$46b3o$45bo$45b2o6$12b2o6bo$12b2o5bobo$19bobo$20bo!|20$49b2o$49b2o$61bo$59b3o$58bo$58b2o6$25b2o$25b2o!'

...
852.84/s, 1008.62 avg/s, 1/834,717 done, 189-409 gens, 23,868/119,692,593 pending, 0x0, -15.82x1, 47x121 A (1), inf overlap (0), 161 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-3.sqlite -o results/35/p46-4.sqlite -q '1=1'

...
Transferred 1 results as starting_points.

# There's a boat behind the blocks that we need to clean up
$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-4.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='15$44bo$42b3o$41bo$41b2o2$17b2o$17b2o3$8b2o$8b2o!'

...
1011.86/s, 1032.52 avg/s, 24,532/148,733 done, 175-395 gens, 221/9,470,677 pending, 0x0, -14.64x4, 46x101 A (1), inf overlap (0), 105 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-4.sqlite -o results/35/p46-5.sqlite -q '1=1 order by far_depth desc limit 1'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-5.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='13$39bo$37b3o$36bo$36b2o2$12b2o$12b2o3$3b2o$3b2o!' --must-contain='12$33b2o$33b2o$45bo$43b3o$42bo$42b2o2$18b2o$18b2o3$9b2o$9b2o!|10$50bo$48b3o$47bo$47b2o2$23b2o$23b2o3$14b2o6bo$14b2o5bobo$21bobo$22bo!|10$60bo$58b3o$57bo$57b2o$40bo$33b2o4bobo$33b2o4bobo$40bo2$24b2o$24b2o!'

...
689.79/s, 815.21 avg/s, 1/41,548 done, 158-378 gens, 221/6,814,480 pending, 0x0, -14.01x1, 51x118 A (1), inf overlap (0), 171 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-5.sqlite -o results/35/p46-6.sqlite -q '1=1'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-6.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='11$45bo$43b3o$42bo$42b2o$25bo$18b2o4bobo$18b2o4bobo$25bo2$9b2o$9b2o!' --must-contain='9$35b2o$35b2o$47bo$45b3o$44bo$44b2o$27bo$20b2o4bobo$20b2o4bobo$27bo2$
11b2o$11b2o!|11$46bo$44b3o$43bo$43b2o$26bo$19b2o4bobo$19b2o4bobo$26bo2$10b2o6bo$10b
2o5bobo$17bobo$18bo!'

# I went back to p46-3.sqlite and found more results.

$ uv run snark.py setup-next-search -i results/35/p46-3.sqlite -o results/35/p46-4-2.sqlite -q 'partial_intermediate is not null'

...
Transferred 246 results as starting_points.

# There's still a boat behind to clean up.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-4.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='6$41bo$39b3o$38bo$38b2o6$5b2o6bo$5b2o5bobo$12bobo$13bo!|13$52bo$50b3o$49bo$49b2o2$25b2o$25b2o3$16b2o$16b2o!'

...
1552.93/s, 1327.91 avg/s, 322,129/3,046,478 done, 227-447 gens, 116,246/178,142,331 pending, 0x0, -13.32x2, 46x83 A (1), -39 (121) fd, inf overlap (0), 94 pop (1)

# ^ that found 121 results which remove the boat from the original p46-4.sqlite.
# Let's also check p46-4-2.sqlite.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-4-2.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='6$41bo$39b3o$38bo$38b2o6$5b2o6bo$5b2o5bobo$12bobo$13bo!|13$52bo$50b3o$49bo$49b2o2$25b2o$25b2o3$16b2o$16b2o!'

# ^ that found several results that remove the boat, including ones that

$ uv run snark.py setup-next-search -i results/35/p46-4.sqlite -o results/35/p46-5-part1.sqlite -q 'partial_intermediate is not null and far_depth > -43'

...
Filtered 2 duplicate results
Transferred 121 results as starting_points.

$ uv run snark.py setup-next-search -i results/35/p46-4-2.sqlite -o results/35/p46-5-part2.sqlite -q 'partial_intermediate is not null and far_depth > -43'

...
Transferred 11 results as starting_points.

$ uv run snark.py combine-starting-points -i results/35/p46-5-part1.sqlite -i results/35/p46-5-part2.sqlite -o results/35/p46-5-2.sqlite

...
Tranferred 132 starting points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-5-2.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='6$41bo$39b3o$38bo$38b2o6$5b2o6bo$5b2o5bobo$12bobo$13bo!|13$52bo$50b3o$49bo$49b2o2$25b2o$25b2o3$16b2o$16b2o!' --must-contain='17$53bo$51b3o$50bo$50b2o2$26b2o$26b2o3$17b2o6bo$17b2o5bobo$24bobo$25bo!|12$40b2o$40b2o$52bo$50b3o$49bo$49b2o6$16b2o6bo$16b2o5bobo$23bobo$24bo!|4$33b2o$33b2o$45bo$43b3o$42bo$42b2o2$18b2o$18b2o3$9b2o$9b2o!|8$40bo$38b3o$37bo$37b2o$20bo$13b2o4bobo$13b2o4bobo$20bo2$4b2o$4b2o!'

# There's one result from running p46-try2 for a while longer which places the difficult back block.

$ uv run snark.py setup-next-search -i results/35/p46-try2.sqlite -o results/35/p46-back-block-1.sqlite -q 'partial_intermediate_digest=-8517427714706585302'

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-1.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='2o$2o$12bo$10b3o$9bo$9b2o!'

# There's one result which clears much of the debris that would interfere with the reaction.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-1.sqlite -o results/35/p46-back-block-2.sqlite -q 'partial_intermediate_overlapping_population = 85'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-2.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='2o$2o$12bo$10b3o$9bo$9b2o!'

$ uv run snark.py setup-next-search -i results/35/p46-try2.sqlite -o results/35/p46-back-block-best-1.sqlite -q 'r.digest=-6656395336763488385'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-1.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='2o$2o$12bo$10b3o$9bo$9b2o!' --must-contain='16$39b2o$39b2o$51bo$49b3o$48bo$48b2o6$15b2o$15b2o!|6$2b2o$2b2o$14bo$12b3o$3b2o6bo$3b2o6b2o!'

...
1429.59/s, 1507.86 avg/s, 92,151/1,161,134 done, 199-319 gens, 8,833/38,964,178 pending, 0x0, -14.49x1, 36x92 A (1), -26 (7) fd, inf overlap (0), 54 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-1.sqlite -o results/35/p46-back-block-best-2.sqlite -q 'partial_intermediate_digest=-7716977956632074662'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-2.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='3$b2o$b2o$13bo$11b3o$2b2o6bo$2b2o6b2o!'

...
1763.30/s, 1706.85 avg/s, 13,064/28,175,965 done, 237-357 gens, 459,679/1,080,814,955 pending, 0x0, -14.64x2, 37x149 A (1), -48 (2) fd, inf overlap (0), 160 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-2.sqlite -o results/35/p46-back-block-best-3.sqlite -q 'partial_intermediate_digest =-4795386547392832430'

...
Transferred 2 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-3.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o6$2o$2o!'

...
1026.73/s, 1054.67 avg/s, 306,571/946,101 done, 167-287 gens, 52,393/58,985,443 pending, 0x0, -14.64x149350, 37x115 A (1), -43 (5) fd, inf overlap (0), 104 pop (1)

# There are several results which separate the block from the bi block.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-3.sqlite -o results/35/p46-back-block-best-4.sqlite -q 'partial_intermediate_overlapping_digest in (3525166929334274753, 5565747590025878660)'

...
Filtered 17 duplicate results
Transferred 21 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-4.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o6$2o$2o!'

# ^ Those results separated the bi block using recipe gliders, which left the center lane empty and was hard to recover from. Let's go back to p46-back-block-best-3.sqlite and look for more results.


$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-3.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o6$2o$2o!'

...
2212.42/s, 2363.58 avg/s, 3,661,557/59,650,331 done, 220-340 gens, 808,643/1,328,603,474 pending, 0x0, -10.89x4, 37x115 A (5), -43 (210) fd, inf overlap (0), 99 pop (1)

# There were the 4 results which placed the traffic light correctly, but none that placed any of the components in the back which we should find next. Instead, let's take the results which clean up the debris that will be a problem when we activate the seed.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-3.sqlite -o results/35/p46-back-block-best-5.sqlite -q 'partial_intermediate_overlapping_digest in (-8592021874893328463, 2193059085553206319, 7192494522526623559, -2347119336435635957, -8159052946573997904, -7201514928430881584, -5626584095067936541, 8945156716543295453, 2857296542224393783, 712970560282915865, 3217030953054209394, -8361844669889289274, -1944986172592249435, -1269579691009731524, -160865320173527766)'

...
Filtered 77 duplicate results
Transferred 151 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-5.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o6$2o$2o!'

...
507.75/s, 810.65 avg/s, 314,129/2,627,483 done, 121-241 gens, 110,352/119,467,656 pending, 0x0, -11.53x1, 40x127 A (1), -39 (14) fd, inf overlap (0), 109 pop (3)

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-5.sqlite -o results/35/p46-back-block-best-6.sqlite -q 'partial_intermediate_digest=916236986069170144'

...
Filtered 2 duplicate results
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-6.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o$2o!'

...
652.76/s, 773.59 avg/s, 1,600,287/11,955,823 done, 149-269 gens, 464,761/674,564,836 pending, 0x0, -11.53x1, 37x115 A (3), -39 (4) fd, inf overlap (0), 105 pop (1)

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-5.sqlite -o results/35/p46-back-block-best-7.sqlite -q 'r.digest = -2080942547926822647'

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-7.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o$2o!'

# ^ I ran this for a bit, and found results as low as 280 population (-100),
# but went back to 5 and ran it overnight. It found a new class of results which
# is much cleaner.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-5.sqlite -o results/35/p46-back-block-best-8.sqlite -q 'partial_intermediate_digest = 916236986069170144 order by lane_width limit 3'

...
Transferred 3 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-8.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o$2o!'

# This found some results which remove the blinker in the back.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-8.sqlite -o results/35/p46-back-block-best-9.sqlite -q 'r.digest = -1578095558570826349'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-9.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o$2o!' --max-allowed-population=314 --must-contain='not 3o3$28bo$26b3o$25bo$25b2o!' --must-contain='not o$o$o2$27bo$25b3o$24bo$24b2o!'

...
1353.96/s, 1616.04 avg/s, 67,052/20,193,980 done, 208-328 gens, 83,490/861,278,847 pending, 0x0, -13.46x62766, 68x168 A (2), -39 (1) fd, inf overlap (0), 208 pop (1)

# There were three results which remove the extra block from the bi block 

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-9.sqlite -o results/35/p46-back-block-best-10.sqlite -q 'partial_intermediate_overlapping_digest in (-533415218630714179, -3072008839902628384, 5533622547071292622)'

...
Transferred 3 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-10.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o$2o!' --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o6bo$2o5bobo$7b
obo$8bo!|24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=311 --must-contain='not 3o3$28bo$26b3o$25bo$25b2o!' --must-contain='not o$o$o2$27bo$25b3o$24bo$24b2o!' --must-contain='not 2b2o$2b2o$14bo$12b3o$2ob2o6bo$2ob2o6b2o!'

# TO INVESTIGATE: select * from r where partial_intermediate_overlapping_digest = 731635527154440752 (does a difficult cleanup) + ONE added beehive.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-10.sqlite -o results/35/p46-back-block-best-11.sqlite -q 'partial_intermediate_overlapping_digest = 731365527154440752'

...
Filtered 8 duplicate results
Transferred 2 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-11.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o$2o!' --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o2$9b2o$9b2o3$2o6bo$2o5bobo$7b
obo$8bo!|24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=311 --must-contain='not 24b2o$24b2o$36bo$34b3o$33bo$33b2o2$9b2o$9b2o3$2o$2o2$3bo$2bobo$bo2bo$
2b2o!'

...
1586.09/s, 2124.43 avg/s, 0/7,263,345 done, 202-322 gens, 127,897/271,425,748 pending, 0x0, -infx0, infxinf A (0), -inf (0) fd, inf overlap (0), inf pop (0)

# Since we know that the loaf can be cleaned up, let's search with the best
# log prob result.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-10.sqlite -o results/35/p46-back-block-best-12.sqlite -q '1=1 order by partial_intermediate_log_prob desc limit 1'

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-12.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=311

...
2034.84/s, 1943.18 avg/s, 15,041/104,896,585 done, 234-354 gens, 3,176,008/4,328,331,414 pending, 0x0, -11.65x15041, 91x187 A (2), -48 (15041) fd, inf overlap (0), 285 pop (1)

# We only found 15k results out of 100 million that preserved the result.
# Let's filter to just those.

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-12.sqlite -o results/35/p46-back-block-best-13.sqlite -q '1=1'

...
Filtered 10433 duplicate results
Transferred 4608 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-13.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=311

...
1218.29/s, 1400.36 avg/s, 1,548,930/26,971,735 done, 131-251 gens, 1,217,502/2,400,098,525 pending, 0x0, -11.65x608064, 91x180 A (1), -46 (3) fd, inf overlap (0), 247 pop (1)

# No better results here, let's try running the setup-next-search portion of an autoshrink command, which will pick the best compact patterns of the 1.5 million we've found.

$ uv run snark.py autoshrink -r results/35/p46-stages.sqlite -i results/35/p46-back-block-best-13.sqlite -o results/35/p46-back-block-best-14.sqlite -n 600 --n-results-limit=1 --full-or-partial=partial --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 

...
Filtered 41 duplicate results
Transferred 197 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-14-round1.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=300

...
1530.97/s, 1106.10 avg/s, 2,128,649/64,883,994 done, 159-279 gens, 1,783,540/3,297,548,507 pending, 0x0, -8.55x1, 91x166 A (1), -39 (26) fd, inf overlap (0), 196 pop (1)

# This found a few new partial intermediate patterns, but none of the beehive we need. The previous beehive reaction does take a while to settle, so it makes sense that we aren't finding alternate options yet. Let's run autoshrink again with a n-results-limit of 2 million, so that it generates the round2 file.

$ uv run snark.py autoshrink -r results/35/p46-stages.sqlite -i results/35/p46-back-block-best-13.sqlite -o results/35/p46-back-block-best-14.sqlite -n 600 --n-results-limit=1 --full-or-partial=partial --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --n-results-limit=2000000

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-14-round2.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=275

...
1275.76/s, 1069.80 avg/s, 371,889/6,827,733 done, 117-237 gens, 179,806/307,184,757 pending, 0x0, -9.15x2, 68x180 A (4), -39 (1031) fd, inf overlap (0), 179 pop (1)

# There's one result which removes the extra loaf. Let's search from there:

$ uv run snark.py setup-next-search -i results/35/p46-back-block-best-14-round2.sqlite -o results/35/p46-back-block-best-15.sqlite -q 'partial_intermediate_overlapping_digest=7391967363082790543'

...
Transferred 1 results as starting_points.

$ uv run snark.py optimize -r results/35/p46-stages.sqlite -o results/35/p46-back-block-best-15.sqlite -n 600 --partial-range=74 --depth-range=-20 --merged-stream-gen-options="4x35-155;67-155" --gen-options=35-155 --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o!' --max-allowed-population=272 --must-contain='not 24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16b
o2$2o$2o2$3bo$2bobo$bo2bo$2b2o!' --must-contain='24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16bo2$2o6bo$2o5bobo$7bobo$8bo!|24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16bo$27b3o3b3o$2o$2o29bo$31bo$31bo!|24b2o$24b2o$36bo$34b3o$25b2o6bo$25b2o6b2o$16bo$9b2o4bobo$9b2o4bobo$16bo11bo5bo$28bo5bo$2o26bo5bo$2o$30b3o!'

# Added a must contain so that this searches faster.

```

