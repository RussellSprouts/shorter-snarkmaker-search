# Search log

First, push the block back a bit to give us more free space to work with.

```bash
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first.sqlite -l 0 -n 450
```

Push some more

```bash
> uv run snark.py setup-next-search -i results/push-first.sqlite -o results/push-first2.sqlite -q '1=1 ORDER BY depth LIMIT 200'
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first2.sqlite -l 0 -n 450 # (stopped early ~419)
```

Search for offset block that will become the target after the snark is
complete.

```bash
> uv run snark.py setup-next-search -i results/push-first2.sqlite -o results/push-first3.sqlite -q '1=1 ORDER BY depth LIMIT 200'
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first3.sqlite -l 0 -n 450 # (stopped early ~423)
```

Take the best candidate which has low depth and an offset block at lane 101,
to try to shrink the lane width without affecting the offset block.

```rle
x = 420, y = 417, rule = LifeHistory
2A$2A2.3A$4.A$5.A31$39.A$38.2A$38.A.A22$61.3A$61.A$62.A24$88.2A$87.2A$89.A25$114.3A$114.A$115.A26$144.A$143.2A$143.A.A21$166.2A$166.A.A$166.A24$193.A$192.2A$192.A.A24$218.2A$217.2A$219.A27$248.A$247.2A$247.A.A24$272.3A$272.A$273.A22$296.3A$296.A$297.A21$319.3A$319.A$320.A26$348.2A$348.A.A$348.A31$382.A$381.2A$381.A.A34$416.3A$416.A$417.A!
```

```bash
> uv run snark.py setup-next-search -i results/push-first3.sqlite -o results/push-first4.sqlite -q 'offset_block_lane > 100 ORDER BY depth LIMIT 1'
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first4.sqlite -l 100 -n 450
```

Take the pool of best candidates and try to lower the lane width further.

```bash
> uv run snark.py setup-next-search -i results/push-first4.sqlite -o results/push-first5.sqlite -q 'depth <= 0 ORDER BY lane_width LIMIT 100'
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first5.sqlite -l 100 -n 400
```

Repeat several times.

```bash
for i in 5 6 7 8 9; do
  uv run snark.py setup-next-search -i "results/push-first${i}.sqlite" -o results/"push-first$(($i + 1)).sqlite" -q 'depth <= 0 ORDER BY lane_width LIMIT 100'
  uv run snark.py optimize -r results/snark.sqlite -o "results/push-first$(($i + 1)).sqlite" -l 100 -n 400
done
```

This was able to reduce the lane width signficantly:

- 4: lane_width 87
- 5: lane_width 77
- 6: lane_width 66
- 7: lane_width 58
- 8: lane_width 44
- 9: lane_width 38
- 10: lane_width 24

However, this takes many gliders -- for the 10 result we're already at 34.
Instead, let's try to combine the search for partial_intermediates with
shrinking the lane size, starting with 5. Having a partial_intermediate also
lets us bound the depth using partial_intermediate_depth_separation on one end,
and depth on the other. Limit the search to partials with 13 gliders so far, which has simple intermediates like

```rle
x = 38, y = 42, rule = B3/S23
21b2o$21b2o3$13bo$13bo$13bo2$9b3o15$4bo$4bo$4bo2$3o3b3o2$4bo$4bo$4bo8$
35b3o$35bo$36bo!
```

```
> uv run snark.py setup-next-search -i results/push-first5.sqlite -o results/partial_search1.sqlite -q 'depth <= 0 ORDER BY lane_width LIMIT 10'
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search1.sqlite -l 100 -n 512 --partial-range=13 # (stopped early ~433)
```

This found partial matches for these recipe intermediates:
```
23|2317
103|1
108|216
188|807
619|216
684|132
692|878
798|1887
821|416
955|14
```

Continue search with samples of two types:

- The 50 patterns that are closest to complete
- Up to 10 of the most compact results from each recipe intermediate

```bash
> uv run snark.py setup-next-search \
  -i results/partial_search1.sqlite \
  -o results/partial_search2.sqlite \
  -q 'depth <= 0 and partial_intermediate is not null ORDER BY partial_intermediate_log_prob DESC LIMIT 50' \
  -q 'depth <= 0 and partial_intermediate = 23 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 103 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 108 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 188 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 619 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 684 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 692 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 798 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 821 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10' \
  -q 'depth <= 0 and partial_intermediate = 955 ORDER BY lane_width * partial_intermediate_overlapping_population LIMIT 10'
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search2.sqlite -l 100 -n 512 --partial-range=13 # (stopped early ~306)
```

There's a promising candidate here. It's missing a block and half of a traffic light.

```rle
x = 734, y = 722, rule = LifeHistory
20.2D$20.2D4$11.3D2$9.D$9.D$9.D15$2.3D2$D5.D$D5.D$D5.D2$2.3D16$55.2A$55.2A2.3A$59.A$60.A31$94.A$93.2A$93.A.A22$116.3A$116.A$117.A24$143.2A$142.2A$144.A25$169.3A$169.A$170.A26$199.A$198.2A$198.A.A21$221.2A$221.A.A$221.A24$248.A$247.2A$247.A.A24$273.2A$272.2A$274.A27$303.A$302.2A$302.A.A24$327.3A$327.A$328.A22$351.3A$351.A$352.A21$374.3A$374.A$375.A32$409.2A$409.A.A$409.A36$447.2A$446.2A$448.A35$483.3A$483.A$484.A30$516.2A$515.2A$517.A25$543.2A$542.2A$544.A21$565.3A$565.A$566.A27$594.3A$594.A$595.A36$633.2A$633.A.A$633.A35$671.A$670.2A$670.A.A30$703.A$702.2A$702.A.A27$731.2A$730.2A$732.A!
```

```bash
> uv run snark.py setup-next-search -i results/partial_search2.sqlite -o results/partial_search3.sqlite -q 'depth >= 0 and partial_intermediate_log_prob > -10 order by lane_width limit 1' # (this was a typo, should be <= 0)
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search3.sqlite -l 100 -n 512 --partial-range=13
```

Even with depth 512, we didn't find a better match for the partial, but we now
have 30,000 results which are variations that might be good starting points.

Maybe we're really close? Try just up to 255 gen follow-up.

```bash
> uv run snark.py setup-next-search -i results/partial_search3.sqlite -o results/partial_search3.5.sqlite -q 'depth <= 0 and partial_intermediate_log_prob > -9.7'
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search3.5.sqlite -l 100 -n 255 --partial-range=13
```

With this, there are 223 results with a partial_intermediate_log_prob better than
-9.7. Let's search from there.

```bash
> uv run snark.py setup-next-search -i results/partial_search3.5.sqlite -o results/partial_search4.sqlite -q 'depth <= 0 and partial_intermediate_log_prob > -9.6'
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search4.sqlite -l 100 -n 400 --partial-range=13
```
