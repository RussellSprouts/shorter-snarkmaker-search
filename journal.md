# Search log

First, we need to generate the recipe intermediates database. This takes in the zero-degree slow glider snark recipe and does a search to find intermediate states with different permutations of the gliders.

```bash
> uv run snark.py recipe-intermediates -i snark.rle -o snark.sqlite
```

To start off the search, push the block back a bit to give us more free space to work with.

```bash
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first.sqlite -l 0 -n 450
> uv run snark.py setup-next-search -i results/push-first.sqlite -o results/push-first2.sqlite -q '1=1 ORDER BY depth LIMIT 200'
```

Push some more

```bash
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first2.sqlite -l 0 -n 450 # (stopped early ~419)
> uv run snark.py setup-next-search -i results/push-first2.sqlite -o results/push-first3.sqlite -q '1=1 ORDER BY depth LIMIT 200'
```

Search for offset block that will become the target after the snark is
complete.

```bash
> uv run snark.py optimize -r results/snark.sqlite -o results/push-first3.sqlite -l 0 -n 450 # (stopped early ~423)
```

Take the best candidate which has low depth and an offset block at lane 101, to try to shrink the lane width without affecting the offset block.

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

However, this takes many gliders -- for the 10 result we're already at 34. Instead, let's try to combine the search for partial_intermediates with shrinking the lane size, starting with 5. Having a partial_intermediate also lets us bound the depth using partial_intermediate_depth_separation on one end and depth on the other. Limit the search to partials at the step with 13 gliders so far, which has simple intermediates like

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
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search4.sqlite -l 100 -n 400 --partial-range=13 # (stopped early ~388)
```

There are 5 results with a full match and depth <= 0. If we were to remove the extra blocks, each of these patterns is 60 zero-degree gliders away from a complete snark.

```rle
x = 7513, y = 6186, rule = LifeHistory
188.2D298.2D298.2D298.2D298.2D$187.D2.D38.2D256.D2.D38.2D256.D2.D38.2D256.D2.D38.2D256.D2.D38.2D$188.2D39.2D257.2D39.2D257.2D39.2D257.2D39.2D257.2D39.2D3$180.2D298.2D298.2D298.2D298.2D$180.D.D16.2D279.D.D16.2D279.D.D16.2D279.D.D16.2D279.D.D16.2D$181.D.D14.D2.D279.D.D14.D2.D279.D.D14.D2.D279.D.D14.D2.D279.D.D14.D2.D$182.D16.2D281.D16.2D281.D16.2D281.D16.2D281.D16.2D$178.2D298.2D298.2D298.2D298.2D$177.D2.D296.D2.D296.D2.D296.D2.D296.D2.D$178.2D7.2D289.2D7.2D289.2D7.2D289.2D298.2D7.2D$163.2D22.2D274.2D22.2D274.2D22.2D274.2D298.2D22.2D$163.2D62.D235.2D62.D235.2D62.D235.2D62.D235.2D62.D$226.D.D297.D.D297.D.D297.D.D297.D.D$208.2D15.D2.D279.2D15.D2.D279.2D15.D2.D279.2D15.D2.D279.2D15.D2.D$207.D2.D15.2D279.D2.D15.2D279.D2.D15.2D279.D2.D15.2D279.D2.D15.2D$207.D2.D296.D2.D296.D2.D296.D2.D296.D2.D$208.2D298.2D298.2D275.2D21.2D298.2D$231.2D298.2D298.2D251.D2.D43.2D298.2D$231.2D298.2D264.D33.2D252.2D44.2D298.2D$796.D.D$234.D299.D261.D.D35.D299.D299.D$233.D.D297.D.D261.D35.D.D297.D.D297.D.D$233.D.D297.D.D297.D.D256.D40.D.D297.D.D$201.D32.D299.D299.D240.2D14.D.D40.D299.D$200.D.D871.D2.D12.D2.D$200.D.D25.D299.D299.D245.D.D8.D5.2D35.D299.D$201.D26.D299.D248.2D49.D246.D8.D.D41.D299.D$162.2D64.D299.D233.2D13.2D49.D233.2D5.D14.D.D41.D299.D$162.2D598.2D39.3D256.2D5.D15.D$183.2D884.D$183.2D47.2D298.2D298.2D298.2D298.2D$231.D.D244.2D16.D34.D.D297.D.D297.D.D262.D34.D.D$165.D31.2D33.D245.2D15.D.D34.D299.D272.2D25.D262.D.D34.D$20.2D143.D4.2A25.2D121.2D148.2A24.2D122.2D148.2A148.2D148.2A32.D2.D112.2D148.2A24.2D$20.2D143.D4.2A148.2D148.2A148.2D148.2A148.2D148.2A33.2D113.2D148.2A$217.D7.D291.D7.D291.D7.D291.D7.D291.D7.D$217.D6.D.D290.D6.D.D290.D6.D.D282.2D6.D6.D.D290.D6.D.D$217.D6.D.D290.D6.D.D290.D6.D.D241.2D20.2D17.2D6.D6.D.D290.D6.D.D$11.3D147.3A61.D85.3D147.3A61.D85.3D147.3A61.D85.3D147.3A4.2D20.2D33.D85.3D147.3A61.D$1080.3D$9.D149.A5.D38.D104.D149.A5.D143.D149.A8.2D139.D149.A5.D143.D149.A5.D$9.D149.A5.D38.D104.D149.A5.D143.D149.A7.D2.D10.2D126.D149.A5.D143.D149.A5.D$9.D149.A5.D38.D104.D149.A5.D143.D149.A8.2D11.2D126.D149.A5.D10.2D13.D117.D149.A5.D$1072.2D2.2D12.D.D$161.3D53.2D12.2D228.3D67.2D298.2D228.3D8.2D16.D.D38.2D228.3D67.2D$217.2D12.2D298.2D298.2D258.D39.2D248.2D48.2D$145.2D31.2D265.2D48.2D248.2D298.2D298.2D34.2D12.2D$144.D2.D30.2D264.D2.D47.2D247.D2.D68.2D226.D2.D296.D2.D47.2D$144.D2.D2.2D292.D2.D2.2D292.D2.D2.2D63.D2.D225.D2.D2.2D292.D2.D2.2D$145.2D3.2D293.2D3.2D293.2D3.2D6.2D46.2D8.2D227.2D3.2D293.2D3.2D$758.2D46.2D299.2D259.D16.2D$201.D3.D19.D5.D249.D43.D5.D293.D5.D274.D.D16.D5.D235.D.D14.D2.D37.D5.D$178.2D20.D.D.D.D18.D5.D249.D35.2D6.D5.D293.D5.D256.D4.2D10.D.D9.2D6.D5.D236.D16.D.D29.2D6.D5.D$178.2D20.D.D.D.D18.D5.D249.D35.2D6.D5.D293.D5.D255.D.D2.D2.D10.D10.2D6.D5.D254.D30.2D6.D5.D$201.D3.D564.2D18.2D295.D.D3.2D$227.3D297.3D240.2D10.D6.D2.D34.3D258.D38.3D297.3D$774.D7.D7.2D$2.3D147.3A28.2D38.3D76.3D147.3A68.3D76.3D147.3A18.D.D6.D40.3D76.3D147.3A68.3D76.3D147.3A26.D41.3D$183.D.D16.3D290.2D276.2D606.D9.3D$D5.D143.A5.A27.D115.D5.D143.A5.A38.2D103.D5.D143.A5.A53.2D88.D5.D143.A5.A143.D5.D143.A5.A24.D$D5.D143.A5.A143.D5.D143.A5.A143.D5.D143.A5.A53.2D88.D5.D143.A5.A4.2D137.D5.D143.A5.A38.D$D5.D143.A5.A143.D5.D143.A5.A48.D94.D5.D143.A5.A45.3D95.D5.D143.A5.A3.D2.D136.D5.D143.A5.A20.3D3.3D9.D9.D$505.D555.2D332.D9.D$2.3D147.3A147.3D147.3A10.D5.D33.D96.3D147.3A6.3D46.D91.3D147.3A22.D124.3D147.3A26.D23.D$465.D5.D337.D.D264.D.D302.D9.3D$465.D5.D29.3D305.D.D265.D303.D$161.D648.D247.2D9.D291.D$160.D.D304.3D587.D2.D7.D.D289.D.D$160.D.D610.D14.3D267.2D8.2D290.D.D$161.D12.2D596.D.D39.3D293.2D249.D$173.D2.D595.D.D335.2D$174.2D585.D11.D$760.D.D$760.2D2$796.2D278.3D17.D$196.3D597.2D298.D299.2D$1068.D27.D299.2D$1068.D$55.2A298.2A298.2A298.2A111.D4.2D180.2A$55.2A2.3A293.2A2.3A293.2A2.3A293.2A2.3A110.D2.D22.3D154.2A2.3A$59.A299.A299.A299.A113.2D184.A$60.A299.A299.A299.A299.A5$479.3D3$470.D$469.D.D$469.D.D$470.D20$94.A299.A299.A299.A299.A$93.2A298.2A298.2A298.2A298.2A$93.A.A297.A.A297.A.A297.A.A297.A.A22$116.3A297.3A297.3A297.3A297.3A$116.A299.A299.A299.A299.A$117.A299.A299.A299.A299.A24$143.2A298.2A298.2A298.2A298.2A$142.2A298.2A298.2A298.2A298.2A$144.A299.A299.A299.A299.A22$301.A299.A299.A299.A299.A$300.2A298.2A298.2A298.2A298.2A$300.A.A297.A.A297.A.A297.A.A297.A.A$169.3A297.3A297.3A297.3A297.3A$169.A299.A299.A299.A299.A$170.A299.A299.A299.A299.A26$199.A299.A299.A299.A299.A$198.2A298.2A298.2A298.2A298.2A$198.A.A297.A.A297.A.A297.A.A297.A.A21$221.2A298.2A298.2A298.2A298.2A$221.A.A297.A.A297.A.A297.A.A297.A.A$221.A299.A299.A299.A299.A24$248.A299.A299.A299.A299.A$247.2A298.2A298.2A298.2A298.2A$247.A.A297.A.A297.A.A297.A.A297.A.A4$416.A299.A299.A299.A299.A$415.2A298.2A298.2A298.2A298.2A$415.A.A297.A.A297.A.A297.A.A297.A.A18$273.2A298.2A298.2A298.2A298.2A$272.2A298.2A298.2A298.2A298.2A$274.A299.A299.A299.A299.A27$303.A299.A299.A299.A299.A$302.2A298.2A298.2A298.2A298.2A$302.A.A297.A.A297.A.A297.A.A297.A.A24$327.3A297.3A297.3A297.3A297.3A$327.A299.A299.A299.A299.A$328.A299.A299.A299.A299.A21$517.A299.A299.A299.A299.A$351.3A162.2A133.3A162.2A133.3A162.2A133.3A162.2A133.3A162.2A$351.A164.A.A132.A164.A.A132.A164.A.A132.A164.A.A132.A164.A.A$352.A299.A299.A299.A299.A21$374.3A297.3A297.3A297.3A297.3A$374.A299.A299.A299.A299.A$375.A299.A299.A299.A299.A32$409.2A298.2A298.2A298.2A298.2A$409.A.A297.A.A297.A.A297.A.A297.A.A$409.A299.A299.A299.A299.A36$447.2A298.2A298.2A298.2A298.2A$446.2A172.3A123.2A172.3A123.2A172.3A123.2A172.3A123.2A172.3A$448.A171.A127.A171.A127.A171.A127.A171.A127.A171.A$621.A299.A299.A299.A299.A34$483.3A297.3A297.3A297.3A297.3A$483.A299.A299.A299.A299.A$484.A299.A299.A299.A299.A30$516.2A298.2A298.2A298.2A298.2A$515.2A298.2A298.2A298.2A298.2A$517.A299.A299.A299.A299.A25$543.2A298.2A298.2A298.2A298.2A$542.2A298.2A298.2A298.2A298.2A$544.A299.A299.A299.A299.A7$717.A299.A299.A299.A299.A$716.2A298.2A298.2A298.2A298.2A$716.A.A297.A.A297.A.A297.A.A297.A.A12$565.3A297.3A297.3A297.3A297.3A$565.A299.A299.A299.A299.A$566.A299.A299.A299.A299.A27$594.3A297.3A297.3A297.3A297.3A$594.A299.A299.A299.A299.A$595.A299.A299.A299.A299.A36$633.2A298.2A298.2A298.2A298.2A$633.A.A297.A.A297.A.A297.A.A297.A.A$633.A299.A299.A299.A299.A14$819.A299.A299.A299.A299.A$818.2A298.2A298.2A298.2A298.2A$818.A.A297.A.A297.A.A297.A.A297.A.A19$671.A299.A299.A299.A299.A$670.2A298.2A298.2A298.2A298.2A$670.A.A297.A.A297.A.A297.A.A297.A.A30$703.A299.A299.A299.A299.A$702.2A298.2A298.2A298.2A298.2A$702.A.A297.A.A297.A.A297.A.A297.A.A27$731.2A298.2A298.2A298.2A298.2A$730.2A298.2A298.2A298.2A298.2A$732.A299.A299.A299.A299.A28$1361.2A$1360.2A$1362.A$904.A299.A299.A299.A299.A$903.2A298.2A298.2A298.2A298.2A$903.A.A297.A.A297.A.A297.A.A297.A.A13$1680.A$1679.2A$1082.A596.A.A300.A$1081.2A898.2A$1081.A.A897.A.A$785.A$784.2A$784.A.A10$1397.A$1396.2A$1396.A.A8$1705.3A$807.2A896.A$806.2A898.A$808.A4$1114.A899.A$1113.2A898.2A$1113.A.A897.A.A4$1419.2A$1419.A.A$1419.A10$831.2A$830.2A$832.A5$1738.2A$1737.2A$1739.A5$1146.A899.A$1145.2A898.2A$1145.A.A300.A596.A.A$1447.2A$1447.A.A7$856.2A$855.2A$857.A5$1006.3A297.3A297.3A297.3A297.3A$1006.A299.A299.A157.2A140.A299.A$1007.A299.A299.A156.A.A140.A299.A$1764.A9$1176.A899.A$1175.2A298.3A597.2A$1175.A.A297.A599.A.A$1476.A8$886.2A$886.A.A$886.A$1790.A$1789.2A$1789.A.A12$1203.2A898.2A$1202.2A898.2A$1204.A899.A6$1511.2A$1510.2A$914.A597.A$913.2A$913.A.A15$1830.2A$1830.A.A298.2A$1830.A300.A.A$2131.A$1234.2A$1233.2A$937.A297.A$936.2A$936.A.A2$1539.3A$1539.A$1540.A12$1855.A$1854.2A$1854.A.A$1257.2A$1257.A.A$1257.A$1109.A299.A299.A299.A299.A$1108.2A298.2A298.2A298.2A298.2A$1108.A.A297.A.A297.A.A297.A.A297.A.A$962.3A$962.A$963.A7$1572.2A597.3A$1572.A.A596.A$1572.A599.A6$1880.2A$1879.2A$1881.A$1284.A$1283.2A$1283.A.A5$990.2A$989.2A$991.A8$2201.A$2200.2A$2200.A.A6$1608.2A$1607.2A$1609.A54$1205.3A297.3A297.3A297.3A297.3A$1205.A299.A299.A299.A299.A$1206.A299.A299.A299.A299.A94$1308.A299.A299.A299.A299.A$1307.2A298.2A298.2A298.2A298.2A$1307.A.A297.A.A297.A.A297.A.A297.A.A94$1413.3A297.3A297.3A297.3A297.3A$1413.A299.A299.A299.A299.A$1414.A299.A299.A299.A299.A106$1505.3A297.3A297.3A297.3A297.3A$1505.A299.A299.A299.A299.A$1506.A299.A299.A299.A299.A93$1609.A299.A299.A299.A299.A$1608.2A298.2A298.2A298.2A298.2A$1608.A.A297.A.A297.A.A297.A.A297.A.A107$1701.A299.A299.A299.A299.A$1700.2A298.2A298.2A298.2A298.2A$1700.A.A297.A.A297.A.A297.A.A297.A.A91$1807.A299.A299.A299.A299.A$1806.2A298.2A298.2A298.2A298.2A$1806.A.A297.A.A297.A.A297.A.A297.A.A94$1912.A299.A299.A299.A299.A$1911.2A298.2A298.2A298.2A298.2A$1911.A.A297.A.A297.A.A297.A.A297.A.A99$2010.A299.A299.A299.A299.A$2009.2A298.2A298.2A298.2A298.2A$2009.A.A297.A.A297.A.A297.A.A297.A.A98$2110.A299.A299.A299.A299.A$2109.2A298.2A298.2A298.2A298.2A$2109.A.A297.A.A297.A.A297.A.A297.A.A95$2214.A299.A299.A299.A299.A$2213.2A298.2A298.2A298.2A298.2A$2213.A.A297.A.A297.A.A297.A.A297.A.A103$2309.A299.A299.A299.A299.A$2308.2A298.2A298.2A298.2A298.2A$2308.A.A297.A.A297.A.A297.A.A297.A.A101$2406.A299.A299.A299.A299.A$2405.2A298.2A298.2A298.2A298.2A$2405.A.A297.A.A297.A.A297.A.A297.A.A99$2504.3A297.3A297.3A297.3A297.3A$2504.A299.A299.A299.A299.A$2505.A299.A299.A299.A299.A108$2595.3A297.3A297.3A297.3A297.3A$2595.A299.A299.A299.A299.A$2596.A299.A299.A299.A299.A97$2695.3A297.3A297.3A297.3A297.3A$2695.A299.A299.A299.A299.A$2696.A299.A299.A299.A299.A100$2794.3A297.3A297.3A297.3A297.3A$2794.A299.A299.A299.A299.A$2795.A299.A299.A299.A299.A104$2887.3A297.3A297.3A297.3A297.3A$2887.A299.A299.A299.A299.A$2888.A299.A299.A299.A299.A93$2993.A299.A299.A299.A299.A$2992.2A298.2A298.2A298.2A298.2A$2992.A.A297.A.A297.A.A297.A.A297.A.A96$3094.3A297.3A297.3A297.3A297.3A$3094.A299.A299.A299.A299.A$3095.A299.A299.A299.A299.A98$3194.3A297.3A297.3A297.3A297.3A$3194.A299.A299.A299.A299.A$3195.A299.A299.A299.A299.A71$3322.A299.A299.A299.A299.A$3321.2A298.2A298.2A298.2A298.2A$3321.A.A297.A.A297.A.A297.A.A297.A.A111$3409.3A297.3A297.3A297.3A297.3A$3409.A299.A299.A299.A299.A$3410.A299.A299.A299.A299.A89$3517.A299.A299.A299.A299.A$3516.2A298.2A298.2A298.2A298.2A$3516.A.A297.A.A297.A.A297.A.A297.A.A99$3616.A299.A299.A299.A299.A$3615.2A298.2A298.2A298.2A298.2A$3615.A.A297.A.A297.A.A297.A.A297.A.A97$3718.A299.A299.A299.A299.A$3717.2A298.2A298.2A298.2A298.2A$3717.A.A297.A.A297.A.A297.A.A297.A.A101$3814.A299.A299.A299.A299.A$3813.2A298.2A298.2A298.2A298.2A$3813.A.A297.A.A297.A.A297.A.A297.A.A99$3913.A299.A299.A299.A299.A$3912.2A298.2A298.2A298.2A298.2A$3912.A.A297.A.A297.A.A297.A.A297.A.A96$4016.A299.A299.A299.A299.A$4015.2A298.2A298.2A298.2A298.2A$4015.A.A297.A.A297.A.A297.A.A297.A.A98$4115.A299.A299.A299.A299.A$4114.2A298.2A298.2A298.2A298.2A$4114.A.A297.A.A297.A.A297.A.A297.A.A100$4213.A299.A299.A299.A299.A$4212.2A298.2A298.2A298.2A298.2A$4212.A.A297.A.A297.A.A297.A.A297.A.A100$4311.3A297.3A297.3A297.3A297.3A$4311.A299.A299.A299.A299.A$4312.A299.A299.A299.A299.A93$4417.A299.A299.A299.A299.A$4416.2A298.2A298.2A298.2A298.2A$4416.A.A297.A.A297.A.A297.A.A297.A.A103$4511.A299.A299.A299.A299.A$4510.2A298.2A298.2A298.2A298.2A$4510.A.A297.A.A297.A.A297.A.A297.A.A97$4613.A299.A299.A299.A299.A$4612.2A298.2A298.2A298.2A298.2A$4612.A.A297.A.A297.A.A297.A.A297.A.A96$4715.A299.A299.A299.A299.A$4714.2A298.2A298.2A298.2A298.2A$4714.A.A297.A.A297.A.A297.A.A297.A.A102$4810.A299.A299.A299.A299.A$4809.2A298.2A298.2A298.2A298.2A$4809.A.A297.A.A297.A.A297.A.A297.A.A97$4911.3A297.3A297.3A297.3A297.3A$4911.A299.A299.A299.A299.A$4912.A299.A299.A299.A299.A106$5004.A299.A299.A299.A299.A$5003.2A298.2A298.2A298.2A298.2A$5003.A.A297.A.A297.A.A297.A.A297.A.A93$5109.A299.A299.A299.A299.A$5108.2A298.2A298.2A298.2A298.2A$5108.A.A297.A.A297.A.A297.A.A297.A.A99$5207.A299.A299.A299.A299.A$5206.2A298.2A298.2A298.2A298.2A$5206.A.A297.A.A297.A.A297.A.A297.A.A101$5304.3A297.3A297.3A297.3A297.3A$5304.A299.A299.A299.A299.A$5305.A299.A299.A299.A299.A96$5406.3A297.3A297.3A297.3A297.3A$5406.A299.A299.A299.A299.A$5407.A299.A299.A299.A299.A96$5509.3A297.3A297.3A297.3A297.3A$5509.A299.A299.A299.A299.A$5510.A299.A299.A299.A299.A99$5607.A299.A299.A299.A299.A$5606.2A298.2A298.2A298.2A298.2A$5606.A.A297.A.A297.A.A297.A.A297.A.A88$5718.A299.A299.A299.A299.A$5717.2A298.2A298.2A298.2A298.2A$5717.A.A297.A.A297.A.A297.A.A297.A.A96$5819.3A297.3A297.3A297.3A297.3A$5819.A299.A299.A299.A299.A$5820.A299.A299.A299.A299.A93$5924.A299.A299.A299.A299.A$5923.2A298.2A298.2A298.2A298.2A$5923.A.A297.A.A297.A.A297.A.A297.A.A103$6020.A299.A299.A299.A299.A$6019.2A298.2A298.2A298.2A298.2A$6019.A.A297.A.A297.A.A297.A.A297.A.A94$6123.A299.A299.A299.A299.A$6122.2A298.2A298.2A298.2A298.2A$6122.A.A297.A.A297.A.A297.A.A297.A.A106$6215.A299.A299.A299.A299.A$6214.2A298.2A298.2A298.2A298.2A$6214.A.A297.A.A297.A.A297.A.A297.A.A105$6309.3A297.3A297.3A297.3A297.3A$6309.A299.A299.A299.A299.A$6310.A299.A299.A299.A299.A!
```

The latest searches have been slow -- the search program does better when
running with a single starting point, for better caching.

```bash
> uv run snark.py setup-next-search -i results/partial_search4.sqlite -o results/zero_degree1.1.sqlite -q 'full_intermediate is not null and depth <= 0 order by full_intermediate_overlapping_population limit 1'
> uv run snark.py setup-next-search -i results/partial_search4.sqlite -o results/zero_degree1.2.sqlite -q 'full_intermediate is not null and depth <= 0 order by full_intermediate_overlapping_population limit 1 offset 1'
> uv run snark.py setup-next-search -i results/partial_search4.sqlite -o results/zero_degree1.3.sqlite -q 'full_intermediate is not null and depth <= 0 order by full_intermediate_overlapping_population limit 1 offset 2'
> uv run snark.py setup-next-search -i results/partial_search4.sqlite -o results/zero_degree1.4.sqlite -q 'full_intermediate is not null and depth <= 0 order by full_intermediate_overlapping_population limit 1 offset 3'
> uv run snark.py setup-next-search -i results/partial_search4.sqlite -o results/zero_degree1.5.sqlite -q 'full_intermediate is not null and depth <= 0 order by full_intermediate_overlapping_population limit 1 offset 4'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree1.1.sqlite -l 100 -n 512
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree1.2.sqlite -l 100 -n 512
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree1.3.sqlite -l 100 -n 512
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree1.4.sqlite -l 100 -n 512
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree1.5.sqlite -l 100 -n 512
```

Interestingly, for most of the intermediates, the searches ended early without ever reaching 512 generations. This can happen because the search skips processing patterns that are identical to earlier ones -- if the reactions settle quickly, then you might only need to send a 90 and 91 gen follow-up.

```bash
> uv run snark.py setup-next-search -i results/zero_degree1.1.sqlite -o /tmp/1.1.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.2.sqlite -o /tmp/1.2.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.3.sqlite -o /tmp/1.3.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.4.sqlite -o /tmp/1.4.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.5.sqlite -o /tmp/1.5.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py combine-starting-points -i /tmp/1.1.sqlite -i /tmp/1.2.sqlite -i /tmp/1.3.sqlite -i /tmp/1.4.sqlite -i /tmp/1.5.sqlite -o results/zero_degree2.sqlite
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree2.sqlite -l 100 -n 400 # (stopped early ~371)
```

select * from results join recipe_intermediates fi on fi.id=full_intermediate where length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 10;

There are many ways to improve from here, so let's explore each of those dimensions:

```bash
> uv run snark.py setup-next-search -i results/zero_degree2.sqlite -o results/zero_degree3.sqlite \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree3.sqlite -l 100 -n 512 # (stopped early ~391)
```

At this point, I added the full_intermediate_overlapping_digest code so that I could better track how removing the overlapping pieces was going. I had to reprocess the results to include this.

The results have an extra pond and block behind the full_intermediate match. I want to find reactions that remove this. I can group by full_intermediate_overlapping_digest and view the results to manually check.

```rle
x = 103, y = 111, rule = LifeHistory
3$33.B12.2B$32.3B5.7B2A37.3B$29.7B2.8BA2BA34.4B2A$29.7B.10B2AB33.5B2A
$28.23B22.3B6.9B$29.21B19.9B4.9B$30.18B11.2B6.12B4.9B$32.14B8.B3.2AB
6.13B5.7B$31.18B4.3B.A2BA2B3.14B3.8B$26.B5.19B.6B2A3B2.16B2.8B$24.67B
$15.2B6.71B$13.5B5.72B$11.B.5B4.73B$9.10B2.65BA9B$8.11B2.64BABA7B$4.
3B.12B.46B2A15BA2BA8B$3.63BA2BA15B2A11B$4.62BA2BA28B$4.63B2A30B$6.84B
2A8B$7.83B2A8B$9.90B$10.83BA2B$11.81BABAB$10.82BABAB$11.82BAB$12.13B.
5B.57B$12.75BAB$13.74BAB$14.73BA2B$13.77B$12.5B.74B$7.2B2.4B4.72B2A$
6.9B4.71BABA$6.11B2.72BA$4.25B2C59B$3.26B2C59B$2.74BA7BA5B$3.73BA6BAB
A4B$2.74BA6BABA5B$2.18B3C61BA6B$4.86B$7.11BC5BA65B$10.8BC5BA22B2A40B$
13.5BC5BA21BA2BA40B$10.3B.33B2A41B$10.10B3A67B2A$4.3B3.80B2A$4.2A85B$
3.A2BA29B2A52B$3.A2BA2B2A25B2A24B2A27B$2.2B2A3B2A51B2A27B$2.88B$3.29B
2A25BA24BA5BA$4.28B2A24BABA23BA5BAB$4.54BABA23BA5BA$6.53BA29B$7.79B3A
$10.55B3A20B$10.B3C68B3AB$10.75B$9.C5BC69B$8.BC5BC68B$9.C5BC68B$10.
76B$10.B3C74B$10.79B$11.77B$12.5B.24B2A17B2A23B$13.B2.26B2A17B2A23B$
16.33BA35B$18.30BABA34B$19.29BABA35B$20.29BA36B$21.65B$22.65B$22.64B$
22.64B$22.64B$22.66B$22.68B$23.68B$23.4B.62B$24.B3.28B2A30B$29.27B2A
30B$30.57B$30.56B$29.58B$29.57B$29.57B$28.17B3.37B$28.16B5.3B.31B$28.
BA14B10.29B$28.ABA10B.2B11.27B$28.ABA.9B15.27B$29.A3.B.3B19.B3.23B$
36.B25.B.B.5B3.2B2.2B.4B$68.B13.4B$83.4B$84.4B$85.4B$86.4B$87.4B$88.
4B$89.4B$90.4B$91.4B!
```

```bash
> uv run snark.py reprocess -i results/zero_degree3.sqlite -o results/zero_degree3_reprocessed.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree3_reprocessed.sqlite -l 100 -n 0
```

Next, I used this query in view-results to see a sample of each unique
full_intermediate_overlapping_digest. Note the use of `as label` to
print a label to identify each output by its digest.

```sql
SELECT *, full_intermediate_overlapping_digest as label FROM (SELECT *, ROW_NUMBER() OVER ( PARTITION BY full_intermediate_overlapping_digest ORDER BY length(r.stream) + length(sp.stream)) as row_num FROM results r JOIN starting_points sp ON sp.id = starting_point JOIN recipe_intermediates fi ON fi.id = full_intermediate WHERE depth <= 0 and length(fi.so_far) >= 26) WHERE row_num = 1 ORDER BY full_intermediate_overlapping_population LIMIT 100;
```

There's one very nice group of results `7471297537555870078` -- it cleans up a lot of the tricky still lives behind the intermediate pattern, and it makes progress on the intermediate by sending the next glider. In fact, the remaining pond could actually stay through the entire construction process without affecting the snark recipe. We still want to remove it, however, so that the full_intermediate_depth_separation gives us useful results.

```rle
x = 1332, y = 1326, rule = LifeHistory
24.D$23.D.D$23.D.D$24.D2$19.2D7.2D$18.D2.D5.D2.D$19.2D7.2D2$24.D$
23.D.D$11.3D9.D.D$24.D$9.D$9.D$9.D15$2.3D2$D5.D$D5.D$D5.D2$2.3D16$
55.2A$55.2A2.3A$59.A$60.A31$94.A$93.2A$93.A.A22$116.3A$116.A$117.A
24$143.2A$142.2A$144.A25$169.3A$169.A$170.A26$199.A$198.2A$198.A.A
21$221.2A$221.A.A$221.A24$248.A$247.2A$247.A.A24$273.2A$272.2A$
274.A27$303.A$302.2A$302.A.A24$327.3A$327.A$328.A22$351.3A$351.A$
352.A21$374.3A$374.A$375.A32$409.2A$409.A.A$409.A36$447.2A$446.2A$
448.A35$483.3A$483.A$484.A30$516.2A$515.2A$517.A25$543.2A$542.2A$
544.A21$565.3A$565.A$566.A27$594.3A$594.A$595.A36$633.2A$633.A.A$
633.A35$671.A$670.2A$670.A.A30$703.A$702.2A$702.A.A27$731.2A$730.
2A$732.A48$782.A$781.2A$781.A.A30$814.A$813.2A$813.A.A30$846.A$
845.2A$845.A.A28$876.A$875.2A$875.A.A26$903.2A$902.2A$904.A26$931.
2A$931.A.A$931.A39$971.3A$971.A$972.A26$1001.A$1000.2A$1000.A.A21$
1023.2A$1022.2A$1024.A21$1045.3A$1045.A$1046.A34$1082.2A$1082.A.A$
1082.A30$1114.2A$1113.2A$1115.A24$1139.3A$1139.A$1140.A27$1169.2A$
1169.A.A$1169.A32$1203.2A$1202.2A$1204.A42$1247.2A$1246.2A$1248.A
22$1271.2A$1270.2A$1272.A57$1330.2A$1329.2A$1331.A!
```

```bash
> uv run snark.py setup-next-search -i results/zero_degree3_reprocessed.sqlite -o results/zero_degree4.sqlite -q 'full_intermediate_overlapping_digest=7471297537555870078'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree4.sqlite -l 100 -n 512 # (stopped early ~372)
```

There is a group of results (`-4140205901904326681`) that turns the pond into a tub. I don't think a single glider can remove the pond from that position (based on trying in SeedsOfDestruction), so turning it into a tub is progress.

```
> uv run snark.py setup-next-search -i results/zero_degree4.sqlite -o results/zero_degree5.sqlite -q 'full_intermediate_overlapping_digest=-4140205901904326681 and depth <= 0'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree5.sqlite -l 100 -n 512
```

This search ran very quickly -- about 20 minutes for 104 patterns searching depth 512, where a normal 512 deep search takes hours for even one pattern. This indicates that there must be sections of the search where the pattern settles quickly and it doesn't need to branch.

The results mostly wanted to expand back towards the glider stream, including results with a max depth of 106! There is a group of 72 results which remove the tub (`-2756292488817558500`), but they have depths from 0 to 102. There are 4 with depth 0, followed by depths 17+.

```
> uv run snark.py setup-next-search -i results/zero_degree5.sqlite -o results/zero_degree6.sqlite -q 'full_intermediate_overlapping_digest=-2756292488817558500 and depth <= 0'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree6.sqlite -l 100 -n 512 # (stopped early ~412)
```

Let's try different improvements. The max_depth has been 14 since the beginning, so let's relax the depth limit to 14. Otherwise, there are very few results.

```
> uv run snark.py setup-next-search -i results/zero_degree6.sqlite -o results/zero_degree7.sqlite \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree7.sqlite -l 100 -n 512 # (stopped early ~396)
```

Stats:

- full_intermediate_overlapping_population: min 13
- full_intermediate_depth_separation: max -26
- lane_width: min 66
- length(fi.so_far): max 30

```bash
> uv run snark.py setup-next-search -i results/zero_degree7.sqlite -o results/zero_degree8.sqlite \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 28 and depth <= 14 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree8.sqlite -l 100 -n 512 # (stopped early ~313)
```

Stats:

- full_intermediate_overlapping_population: min 8
- full_intermediate_depth_separation: max -26
- lane_width: min 64
- length(fi.so_far): max 32

With progress on intermediate recipe (30 so far, 32 so far):

- full_intermediate_overlapping_population: min 10 (30), 29 (32)
- full_intermediate_depth_separation: max -27 (30), -40 (32)
- lane_width: 66 (30), 85 (32)

```bash
> uv run snark.py setup-next-search -i results/zero_degree8.sqlite -o results/zero_degree9.sqlite \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree9.sqlite -l 100 -n 400
> uv run snark.py setup-next-search -i results/zero_degree9.sqlite -o results/zero_degree10.sqlite \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 14 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree10.sqlite -l 100 -n 400
> uv run snark.py setup-next-search -i results/zero_degree10.sqlite -o results/zero_degree11.sqlite \
  -q 'length(fi.so_far) >= 32 and depth <= 14 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 32 and depth <= 14 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 32 and depth <= 14 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 32 and depth <= 14 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 32 and depth <= 14 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree11.sqlite -l 100 -n 400
```

- full_intermediate_overlapping_population: 7 (zero_degree9), 3 (zero_degree10), 3 (zero_degree11)
- full_intermediate_depth_separation: -27 (9), -27 (10), -27 (11)
- lane_width: 66 (9), 65 (10), 65 (11)

---

Gonna try to remove the last blinker. There are 23 results in zero_degree10,
but only 1 in zero_degree11, since they have a length so_far of 30, and we set
a cut-off of 32. I'll start with the zero_degree10 results.

```bash
> uv run snark.py setup-next-search -i results/zero_degree10.sqlite -o results/zero_degree_separate1.sqlite -q 'full_intermediate_overlapping_population=3 and depth <= 14'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate1.sqlite -l 100 -n 400
```

Now there are results that have 0 overlapping population. Let's increase the distance to ~30.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate1.sqlite -o results/zero_degree_separate2.sqlite -q 'length(fi.so_far) >= 30 and depth <= 40 and full_intermediate_overlapping_population = 0 order by full_intermediate_depth_separation desc limit 100'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate2.sqlite -l 100 -n 512 # (stopped early ~412)
```

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate2.sqlite -o results/zero_degree_separate3.sqlite \
  -q 'length(fi.so_far) >= 30 and depth <= 40 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 40 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 30 and depth <= 40 order by lane_width limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate3.sqlite -l 100 -n 512 # (stopped early ~406)
```

There's one result with full_intermediate_depth_separation >= 30. Let's explore that quickly to see if it's viable.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate3.sqlite -o results/zero_degree_separate4.sqlite -q 'depth <= 40 and length(fi.so_far) >= 30 and full_intermediate_depth_separation >= 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate4.sqlite -l 100 -n 270
```

This took ~10 seconds and gave ~100 stable results, many of which have items in the path of the gliders, so it looks like it's not a dead end.

```bash
> rm results/zero_degree_separate4.sqlite
> uv run snark.py setup-next-search -i results/zero_degree_separate3.sqlite -o results/zero_degree_separate4.sqlite -q 'depth <= 40 and length(fi.so_far) >= 30 and full_intermediate_depth_separation >= 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate4.sqlite -l 100 -n 512
```

This seems to have worked well, and we have 79 results which satisfy
`depth <= 40 and length(fi.so_far) >= 32 and full_intermediate_depth_separation > 20`. Let's try to just send zero degree gliders to continue incrementing the recipe.

This script will pick the best 100 candidates and search up to 400 generations for new patterns.

```bash
> for i in 4 5 6 7 8 9 10 11 12 13 14 15 16; do
    uv run snark.py setup-next-search -i results/zero_degree_separate${i}.sqlite -o results/zero_degree_separate$(($i + 1)).sqlite -q 'depth <= 40 and length(fi.so_far) >= 30 and full_intermediate_depth_separation > 20 order by length(fi.so_far) desc, length(stream), full_intermediate_depth_separation desc, lane_width limit 100'
  uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate$(($i + 1)).sqlite -l 100 -n 400 || break
done
```

select *, "progress " || (length(fi.so_far)/2) as label from results join recipe_intermediates fi on full_intermediate=fi.id where depth <= 40 and length(fi.so_far) >= 30 and full_intermediate_depth_separation > 0 order by length(fi.so_far) desc, length(stream), full_intermediate_depth_separation desc, lane_width limit 10

5: 82 gliders
6: 85 gliders
7: 88 gliders
8: 92 gliders

In zero_degree_separate10 it failed to find the next step, due to a bug in the full_intermediate calculation. The intermediate calculation preferred patterns that have more gliders so far. However, if step 22 involves removing a piece of the pattern, then it will report a match for step 23 with an overlapping population, rather than a match for step 22 with no overlapping population. I fixed it to consider the full_intermediate pattern with the most population instead. Eventually, it would be good to have the intermediate matches in a separate table joined with the results, so we can consider multiple matches at once.

select *, "progress " || cast(length(fi_so_far)/2 as text) || " gliders " || cast(length(full_stream) as text) as label from r where depth <= 40 and length(fi_so_far) >= 30 and full_intermediate_depth_separation > 20 order by length(fi_so_far) desc, length(stream), full_intermediate_depth_separation desc, lane_width limit 10;

```bash
> uv run snark.py reprocess -i results/zero_degree_separate10.sqlite -o results/zero_degree_separate10_reprocessed.sqlite -q 'full_intermediate=327 or full_intermediate=383'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate10_reprocessed.sqlite -l 100 -n 0
```

After reprocessing, we find that there's one result which makes progress on the recipe, but it has a depth separation of 15. Let's continue with that one. Since there's only one candidate, let's try a deep search to maybe get lucky with something that cleans up the depth_separation or leaps forward by multiple times. Trying depth 540 took a couple of hours, but the results were less useful since it included results from a previous run, where the starting points were mixed up. Trying again with depth 630, which will be by far the deepest I've tried.

```bash
>  uv run snark.py setup-next-search -i results/zero_degree_separate10_reprocessed.sqlite -o results/zero_degree_separate11.sqlite -q 'depth <= 40 and length(fi.so_far) >= 30 order by length(fi.so_far) desc, length(stream), full_intermediate_depth_separation desc, lane_width limit 1'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate11.sqlite -l 100 -n 630 # (stopped early ~600)
```

Searching to the 600-630 gens point took ~60 hours, and there are still >5 million jobs to search.

- Stable results: 14 million
- ...with full_intermediate match: 5.6 million
- ...with depth <= 40: 260 thousand
- ...with full_intermediate_depth_separation > 0: 230 thousand
- ...with full_intermediate_depth_separation > 10: 1178
- ...with full_intermediate_depth_separation > 20: 5
- With full_intermediate_match and depth <= 40 and lane_width < 80: 98
- ...with lane_width < 70: 6

There are definitely diminishing returns with deep searches. For example, a pattern might have an escaping glider that we can't catch, but the deep search will still explore all the follow ups to the max, in case it might turn out OK. We also have to limit the number of candidates to test, so we're stuck with how good the starting points are.

There are 1404 results that are at step 22 or 23 (and only 19 are step 23), and have full_intermediate_depth_separation > 0 and depth <= 40. Let's try all of them.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate11.sqlite -o results/zero_degree_separate12.sqlite -q 'depth <= 40 and full_intermediate_depth_separation > 0 and length(fi.so_far)/2 >= 22'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate12.sqlite -l 100 -n 400 # (stopped early ~334)
```

With this, I only found 4 results that made it to step 24, but there are many that made it to step 23. It seems like the wider search gives more consistent results -- we have almost 30,000 results that meet the criteria from the 1400 starting points.

There were a lot of duplicate results by before_hit_digest, so I used the partition query to allow me to select unique results more precisely. Otherwise, I could set a limit of 1500 in the query but only have 400 candidates. To support this, I expanded the `-q` option of setup-next-search to allow passing a full query (if it starts with `select `).

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate12.sqlite -o results/zero_degree_separate13.sqlite -q 'select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 23) where row_number = 1 order by length(fi_so_far)/2, length(full_stream), lane_width*population limit 1500'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate13.sqlite -l 100 -n 350
```

Calculating to 350 only took a couple of hours, but we ended up with only 38 results which reach step 24 and stay in bounds, and only 900 which reach step 24 at all. Let's try again with depth 400.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate12.sqlite -o results/zero_degree_separate13_depth400.sqlite -q 'select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 23) where row_number = 1 order by length(fi_so_far)/2, length(full_stream), lane_width*population limit 1500'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate13_depth400.sqlite -l 100 -n 400
```

Let's check on our pace, using the zero-degree separate results:

SELECT full_intermediate, COUNT(distinct before_hit_digest), LENGTH(fi_so_far)/2 as step, min(length(full_stream)) as gliders FROM r WHERE depth <= 40 and full_intermediate_depth_separation > 0 GROUP BY full_intermediate order by step desc, gliders asc;

SELECT full_intermediate, COUNT(distinct before_hit_digest), LENGTH(fi_so_far)/2 as step, min(length(full_stream)) as gliders FROM r GROUP BY full_intermediate order by step desc, gliders asc;


- zero_degree_separate1: step 15, 68 gliders
- zero_degree_separate2: step 16, 71 gliders
- zero_degree_separate3: step 16, 73 gliders
- zero_degree_separate4: step 16, 79 gliders
- zero_degree_separate5: step 17, 81 gliders (+1/+2)
- zero_degree_separate6: step 18, 84 gliders (+1/+3)
- zero_degree_separate7: step 19, 87 gliders (+1/+3)
- zero_degree_separate8: step 20, 90 gliders (+1/+3)
- zero_degree_separate9: step 21, 93 gliders (+1/+3)
- zero_degree_separate10_reprocessed: step 21, 94 gliders (+0/+1)
- zero_degree_separate11: step 23: 100 gliders (+2/+6)
- zero_degree_separate12: step 24: 103 gliders (+1/+3)

If this holds, we could reach step 73 in the 250-275 glider range, and then we just need to clean up. We could be on track to finish in less than 300 gliders.

The 400 deep search gave us 84+123 gliders which reach step 24 in-bounds, and over a million that reach step 23 in-bounds.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate13_depth400.sqlite -o results/zero_degree_separate14.sqlite -q 'select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 23) where row_number = 1 order by length(fi_so_far)/2, lane_width*population, length(full_stream) limit 1500'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate14.sqlite -l 100 -n 400 # (stopped early ~389-400)
```

There are now more results that make it to step 24.
Let's try continuing with the results we've found.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate14.sqlite -o results/zero_degree_separate15.sqlite -q 'select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 23) where row_number = 1 order by length(fi_so_far)/2, lane_width*population, length(full_stream) limit 1500'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate15.sqlite -l 100 -n 400
```

Finally, this finds one result which reaches step 25.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate15.sqlite -o results/zero_degree_separate16.sqlite -q 'select * from r where length(fi_so_far) = 50'
# remove the last 2 gliders from the stream and search from there.
> sqlite3 results/zero_degree_separate16.sqlite 'update starting_points set stream = cast(substr(stream, 1, length(stream)-2) as blob)'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate16.sqlite -l 100 -n 450
```

This expanded the results, but I also realized that my last few days of searches were flawed -- I forgot to use `desc` in `ORDER BY length(fi_so_far)`,
so I was ignoring the furthest candidates at each stage. Time to redo the searches starting at zero_degree_separate13!

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate12.sqlite -o results/zero_degree_separate13_redo.sqlite -q 'select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0) where row_number = 1 order by length(fi_so_far) DESC, length(full_stream), lane_width*population limit 1500'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate13_redo.sqlite -l 100 -n 375
```

This time, things worked as expected. zero_degree_separate12 had 4 distinct streams that reached 24 while staying in-bounds, and over 29k that reached step 23. zero_degree_separate13_redo has 5 that reached step 25, and 16k that reached step 24.

Now let's redo 14, 15, and 16. The 375 depth takes about ~12 hours, vs ~24 for depth 400, so if I continue to get good results that should save a lot of time.

```bash
for i in 13 14 15; do
  uv run snark.py setup-next-search -i "results/zero_degree_separate${i}_redo.sqlite" -o results/zero_degree_separate$(($i + 1))_redo.sqlite -q "select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0) where row_number = 1 order by length(fi_so_far) DESC, length(full_stream), lane_width*population limit 1500"
  uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate$(($i + 1))_redo.sqlite -l 100 -n 375 || break
done
```

select *, "progress " || cast(length(fi_so_far)/2 as text) || " gliders " || cast(length(full_stream) as text) as label from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 23) where row_number = 1 order by length(fi_so_far) DESC, lane_width*population, length(full_stream) limit 1500


select hex(stream), row_number() over (order by length(fi_so_far) DESC, length(full_stream)) as row from (select
*, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0) where row_number = 1 order by row limit 1500

```bash
> uv run snark.py setup-next-search -i "results/zero_degree_separate15_redo.sqlite" -o results/zero_degree_separate16_redo.sqlite -q "select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0) where row_number = 1 order by length(fi_so_far) DESC, length(full_stream), lane_width*population limit 1500"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate16_redo.sqlite -l 100 -n 375
```

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate16_redo_redo.sqlite -o results/zero_degree_separate17.sqlite -q "select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0) where row_number = 1 order by length(fi_so_far) DESC, length(full_stream), lane_width*population limit 1500"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate17.sqlite -l 100 -n 410
```


select "progress " || cast(length(fi_so_far)/2 as text) || " gliders " || cast(length(full_stream) as text) as label from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 23) where row_number = 1 order by length(fi_so_far) DESC, length(full_stream) limit 10


- zero_degree_separate1: step 15, 68 gliders
- zero_degree_separate2: step 16, 71 gliders
- zero_degree_separate3: step 16, 73 gliders
- zero_degree_separate4: step 16, 79 gliders
- zero_degree_separate5: step 17, 81 gliders (+1/+2)
- zero_degree_separate6: step 18, 84 gliders (+1/+3)
- zero_degree_separate7: step 19, 87 gliders (+1/+3)
- zero_degree_separate8: step 20, 90 gliders (+1/+3)
- zero_degree_separate9: step 21, 93 gliders (+1/+3)
- zero_degree_separate10_reprocessed: step 21, 94 gliders (+0/+1)
- zero_degree_separate11: step 23: 100 gliders (+2/+6)
- zero_degree_separate12: step 24: 103 gliders (+1/+3)

- zero_degree_separate13_redo: 5 candidates step 25, 106 gliders, 15k candidates step 24, 104 gliders
- zero_degree_separate14_redo: 1 candidate step 26, 110 gliders, 7k candidates step 25, 106 gliders
- zero_degree_separate15_redo: 700 candidates step 26, 110 gliders, 600k candidates to step 25, 107 gliders
- zero_degree_separate16_redo_redo: 400 candidates step 27, 113 gliders, 450k candidates step 26, 110 gliders
- zero_degree_separate17: 10 candidates step 28, 117 gliders, 520k candidates step 27, 113 gliders

step 44, 162 gliders

I want to find more candidates at step 28, so I'll run a wide shallow search:

```bash
> uv run snark.py setup-next-search -i "results/zero_degree_separate17.sqlite" -o results/zero_degree_separate18.sqlite -q "select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where (depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 27) or length(fi_so_far)/2 == 28) where row_number = 1"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate18.sqlite -l 100 -n 255
```

And in parallel run a search from zero_degree_separate16_redo_redo on the remaining candidates that reached 25.

```bash
> uv run snark.py setup-next-search -i "results/zero_degree_separate17.sqlite" -o results/zero_degree_separate18.sqlite -q "select * from (select *, row_number() over (partition by before_hit_digest order by length(full_stream), sp_cost) as row_number from r where (depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 >= 27) or length(fi_so_far)/2 == 28) where row_number = 1"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate18.sqlite -l 100 -n 255
```

I stopped the search early after 73 million streams were evaluated, with 13 million remaining to try every single glider follow-up to the 500k results.

Combined with the results from 17, I now have 173 more candidates at step 28.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate18.sqlite -o results/zero_degree_separate19.1.sqlite -q "depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 == 28"
> uv run snark.py setup-next-search -i results/zero_degree_separate17.sqlite -o results/zero_degree_separate19.2.sqlite -q "depth <= 40 and full_intermediate_depth_separation > 0 and length(fi_so_far)/2 == 28"
> uv run snark.py combine-starting-points -i results/zero_degree_separate19.1.sqlite -i results/zero_degree_separate19.2.sqlite -o results/zero_degree_separate19.sqlite
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate19.sqlite -l 100 -n 450 # (stopped early 400)
```

Now we have 183 starting points.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate19.sqlite -o results/zero_degree_separate20.sqlite -q "depth <= 40 and length(fi_so_far)/2 == 29"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate20.sqlite -l 100 -n 450 # (stopped early ~363)
```

There was one lucky result which goes straight from 29-32. It may not be viable -- there's a trough all the way through to the target. Let's explore it.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate20.sqlite -o results/zero_degree_separate21.sqlite -q "length(fi_so_far)/2 == 32"
# Rewind two gliders to explore related streams as well.
> sqlite3 results/zero_degree_separate21.sqlite 'update starting_points set stream = cast(substr(stream, 1, length(stream)-2) as blob)'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate21.sqlite -l 100 -n 512
```

This found 12 unique results at step 33 with depth <= 40, though there is a modest overlap. The depth 512 search finished with only 15 million total processed -- many branches were pruned early.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate21.sqlite -o results/zero_degree_separate22.sqlite -q "length(fi_so_far)/2 == 33 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate22.sqlite -l 100 -n 512
``` 

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate22.sqlite -o results/zero_degree_separate23.sqlite -q "length(fi_so_far)/2 == 34 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate23.sqlite -l 100 -n 450 # (stopped early 328)
```

This found two results at step 36 and 8 at step 35, though they are pretty messy. There are also 800k+ results at step 34.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate23.sqlite -o results/zero_degree_separate24.sqlite -q "length(fi_so_far)/2 >= 35" -q "length(fi_so_far)/2 = 34 and depth <= 40 and full_intermediate_depth_separation > 0 order by full_intermediate_depth_separation desc limit 10" -q "length(fi_so_far)/2 = 34 and depth <= 40 and full_intermediate_depth_separation > 0 order by lane_width limit 10"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate24.sqlite -l 100 -n 450 # (stopped early 413)
```

This found 3 results at step 37. Let's try them out.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate24.sqlite -o results/zero_degree_separate25.sqlite -q "length(fi_so_far)/2 = 37"
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree_separate25.sqlite -l 100 -n 512 # (stopped early ~352)
```

There is one result with a good depth that reaches step 38.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate25.sqlite -o results/sprint1.sqlite -q "length(fi_so_far)/2 = 38 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint1.sqlite -l 100 -n 512
```

That search didn't find anything at 39, so let's try to find more 38 candidates by resuming the search in zero_degree_separate25.sqlite. Stopping at 433, we have 19 results now.

```bash
> uv run snark.py setup-next-search -i results/zero_degree_separate25.sqlite -o results/sprint2.sqlite -q "length(fi_so_far)/2 = 38 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint2.sqlite -l 100 -n 512 # (stopped early ~388)
```

Even with hundreds of thousands at step 38, we have none at step 39. However, we did find lots of results which clean up area. Let's search from those.

```bash
> uv run snark.py setup-next-search -i results/sprint2.sqlite -o results/sprint3.sqlite -q "length(fi_so_far)/2 = 38 and depth <= 40 and full_intermediate_overlapping_population <= 6"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint3.sqlite -l 100 -n 450 # (stopped early ~400)
```

There are 44 results on step 39 with depth <= 40.

```bash
> uv run snark.py setup-next-search -i results/sprint3.sqlite -o results/sprint4.sqlite -q "length(fi_so_far)/2 = 39 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint4.sqlite -l 100 -n 450 # (stopped early 279)
```

There's one result on step 40 with depth <= 40. Let's try it quickly:

```bash
> uv run snark.py setup-next-search -i results/sprint4.sqlite -o results/sprint5.sqlite -q "length(fi_so_far)/2 = 40 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint5.sqlite -l 100 -n 450
```

That finished with only one result at 41, and it has a depth of 45, so let's continue searching in sprint4.sqlite.

Continuing to 380, we find 39 results at step 40 with depth <= 40.

```bash
> uv run snark.py setup-next-search -i results/sprint4.sqlite -o results/sprint6.sqlite -q "length(fi_so_far)/2 = 40 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint6.sqlite -l 100 -n 450 # (stopped early 302)
```

We found 1 with a good depth pretty quickly, let's try it.

```bash
> uv run snark.py setup-next-search -i results/sprint6.sqlite -o results/sprint7.sqlite -q "length(fi_so_far)/2 = 41 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint7.sqlite -l 100 -n 512 # (stopped early 418)
```

This found some candidates at step 44 (really 43, the 44 candidate is very messy).
None of them activated the LOM reaction.

Trying some more, we find another candidate with depth 31. Let's try that.

```bash
> uv run snark.py setup-next-search -i results/sprint6.sqlite -o results/sprint8.sqlite -q "length(fi_so_far)/2 = 41 and depth = 31"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint8.sqlite -l 100 -n 512
```

```bash
> uv run snark.py setup-next-search -i results/sprint7.sqlite -o results/sprint9.1.sqlite -q "length(fi_so_far)/2 > 41 and depth <= 40"
> uv run snark.py setup-next-search -i results/sprint8.sqlite -o results/sprint9.2.sqlite -q "length(fi_so_far)/2 > 41 and depth <= 40"
> uv run snark.py combine-starting-points -i results/sprint9.1.sqlite -i results/sprint9.2.sqlite -o results/sprint9.sqlite
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint9.sqlite -l 100 -n 375 # (stopped early ~192)
```

There is one result which does the first big reaction towards making the snark heart. It's on step 44.

```bash
> uv run snark.py setup-next-search -i results/sprint9.sqlite -o results/sprint10.sqlite -q "full_intermediate=311"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint10.sqlite -l 100 -n 450
```

No great results from this right away, went back to sprint9 and let it run overnight, stopping at 275 gens. It found 43 results which made it to step 44 and had depth <= 40.

```bash
> uv run snark.py setup-next-search -i results/sprint9.sqlite -o results/sprint11.sqlite -q "length(fi_so_far)/2 = 44 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint11.sqlite -l 100 -n 450 # (stopped early ~314)
```

There is one result which has very good separation at step 45, and it has already done the LOM reaction to create the first part of the snark heart. Let's try exploring this.

```bash
> uv run snark.py setup-next-search -i results/sprint11.sqlite -o results/sprint12.sqlite -q 'full_intermediate=302'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint12.sqlite -l 100 -n 450 # (stopped early 349)
```

This found 167 results at step 46.

```bash
> uv run snark.py setup-next-search -i results/sprint12.sqlite -o results/sprint13.sqlite -q 'length(fi_so_far)/2 = 46 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint13.sqlite -l 100 -n 450 # (stopped early ~285)
```

There are 32 results at step 47.

```bash
> uv run snark.py setup-next-search -i results/sprint13.sqlite -o results/sprint14.sqlite -q 'length(fi_so_far)/2 = 47 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint14.sqlite -l 100 -n 450 # (stopped early 375)
```

There are 723 results at depth 48, but many of them have an interesting pattern which puts a ship at lane width 90, opposite the offset block.

```
x = 138, y = 145, rule = LifeHistory
4$48.B12.2B$47.3B5.9B37.3B$44.7B2.12B9.B24.4B2A$44.7B.13B7.4B22.5B2A$
43.23B5.8B7.B.3B6.9B$44.21B6.9B.12B4.9B$45.19B7.23B4.9B$47.18B4.26B5.
7B$46.19B3.29B.8B$41.B5.19B.30B.8B$39.67B$30.2B6.71B$28.5B5.72B$26.B.
5B4.73B$24.10B2.75B$23.11B2.74B$19.3B.12B.75B$18.95B$19.94B$19.95B$
21.84B2A8B$22.83B2A8B$24.90B$25.83BA2B$26.81BABAB$25.76B3A3BABAB$26.
82BAB$27.13B.5B.52BA5BA$27.72BA5BAB$28.38B2A31BA5BA$29.37B2A39B$28.
67B3A3B3A5B$27.5B.77B$22.2B2.4B4.65BA10B$21.9B4.64BABA7B$21.11B2.64BA
BA7B$19.80BA5B.B$18.88B$17.25B2C19B2A41B$18.23BC2BC7B2C9B2A40B$17.25B
2C7BC2BC51B$17.18B3C14B2C52B$19.28BC44B2A11B$21.25BCBC42BA2BA10B$20.
12B2C12BCBC43B2A12B$19.5B.6BC2BC12BC58B$18.6B.6BC2BC3B2C66B$17.15B2C
3BC2BC2B2C22B3A30B2A5B$16.21BC2BC2BC56B2A5B$17.21B2C4B3C60B$17.30BC
57B$18.26B3C59B$17.26BC62B$17.26B4C60B$18.23B2C3BC61B$19.21BC2B3C62B$
19.21B2CBC64B$21.22BC66B$22.21B2C65B$25.85B$25.90B$23.94B$22.35BA60B$
22.34BABA49BA8B2A$24.32BABA48BABA7B2A$25.32BA3B2A44BABA10B$25.35BA2BA
44BA12B$25.36B2A51B2A5B$24.90B2A3BAB$23.95BABAB$22.96BABAB$21.4B2.92B
A4B$20.4B4.98B$19.4B6.97B$18.4B8.69B2A25B$17.4B10.8B2A58B2A25B$16.4B
11.7BA2BA83B$15.4B13.7B2A85B$14.7B13.93B$14.8B13.91B$13.10B11.92B$10.
13B9.93B$9.16B6.78BA10B2.3B$8.17B5.78BABA8B4.B$8.17B4.25B2A52BABA5B.B
$7.17B4.26B2A53BA6B$7.10B2A5B3.88B$6.11B2A5B2.4B.73B2A7B2AB$5.18B4.2B
4.70BA2BA5BA2BAB$6.23B5.26BA43B2A7B2AB$6.21B7.17B3A5BABA52B$7.20B9.
24B2A47BA2B$7.19B11.71BABAB$7.20B11.70BABA$7.22B9.34B2A35BAB$6.2A24B
2.2B.B.4B3A25BA2BA35B$5.BABA63B2A31B.2B$6.B2A32BA5BA57B$8.13B.19BA5BA
4B2A22B2A26B$8.12B2.19BA5BA3BA2BA21B2A26B$9.2B.9B2.28BA2BA49B$10.11B
9.4B.8B3A6B2A50B$9.13B9.4B4.B.53B3A8B$9.13B10.4B5.7B2.51B.4B$10.13B
10.4B3.8B.52B2.4B$10.14B10.4B2.7B2.2BA49B3.4B$11.13B11.4B.6B4.BA10BA
37B5.4B$11.13B12.4B2.2A2B4.BA9BABA35B7.4B$11.13B13.4BABAB6.10BABA29B
14.4B$12.11B15.3B2AB7.11BA29B16.4B$39.B13.40B16.4B$52.9BA31B17.4B$53.
7BABA30B18.4B$53.7B2A31B19.4B$53.40B20.4B$52.35B.4B22.4B$52.8B2A26B2.
B24.4B$52.8B2A26B28.4B$52.25B.11B28.4B$52.24B2.11B29.4B$53.22B4.B.8B
30.4B$55.20B6.7B32.4B$56.18B7.6B34.4B$57.17B7.5B36.4B$59.15B8.3B38.4B
$59.15B50.4B$59.15B51.4B$59.15B52.4B$59.13B55.4B$60.13B55.4B$62.10B
57.4B$64.8B58.4B$65.6B60.4B$66.6B60.4B$66.5B62.4B$66.5B63.4B$67.3B65.
3B$68.B67.2B$137.B!
```

Filtering these out, we only have 231, which should be easier to search.

```bash
> uv run snark.py setup-next-search -i results/sprint14.sqlite -o results/sprint16.sqlite -q 'length(fi_so_far)/2 = 48 and depth <= 40 and lane_width < 90'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint16.sqlite -l 100 -n 450 # (stopped early 302)
```

So far there's one result with a good depth at step 49. I also tried to search for anything that finished the snark heart with possible missing pieces, with no luck. I think the next stage might be good for this, though.

```bash
> uv run snark.py setup-next-search -i results/sprint16.sqlite -o results/sprint17.sqlite -q 'length(fi_so_far)/2 = 49 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint17.sqlite -l 100 -n 450 # (stopped early ~360)
```

There are 31 results with step 50 and depth <= 40.

```bash
> uv run snark.py setup-next-search -i results/sprint17.sqlite -o results/sprint18.sqlite -q 'length(fi_so_far)/2 = 50 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint18.sqlite -l 100 -n 375 # (stopped early 300)
```

There are 12 results with step 51 and depth <= 40.

```bash
> uv run snark.py setup-next-search -i results/sprint18.sqlite -o results/sprint19.sqlite -q 'length(fi_so_far)/2 = 51 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint19.sqlite -l 100 -n 512 #( stopped early 375)
```

This search didn't pan out well, so going back to sprint18.sqlite and letting it finish.

```bash
> uv run snark.py setup-next-search -i results/sprint18.sqlite -o results/sprint20.sqlite -q 'length(fi_so_far)/2 = 51 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint20.sqlite -l 100 -n 450 # (stopped early 400)
```

There was one result which made it to step 52 with depth <= 40.

```bash
> uv run snark.py setup-next-search -i results/sprint20.sqlite -o results/sprint21.sqlite -q 'length(fi_so_far)/2 = 52 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/sprint21.sqlite -l 100 -n 450 
```

This completed in a few minutes and found no interesting results. I will go all the way back to sprint16, since we branched from there with just one result. Letting it run overnight, stopping at 387, we find 58 results with a good depth.

```bash
> uv run snark.py setup-next-search -i results/sprint16.sqlite -o results/heart1.sqlite -q 'length(fi_so_far)/2 = 49 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart1.sqlite -l 100 -n 450 # (stopped early 357)
```

This found 4 results which finish the snark heart! They don't count as full_intermediates, since they are missing the pieces which will become the eaters and block in the slow salvo recipe. Hopefully with some searching we can just make those from random pieces.

If that doesn't pan out, we also found a lot of results that make it to step 50, so we can continue following the slow salvo recipe from here.

```bash
> uv run snark.py setup-next-search -i results/heart1.sqlite -o results/heart2.sqlite -q 'partial_intermediate=420'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart2.sqlite -l 100 -n 630 --partial-range=73 # (stopped early 412)
```

Searching to 412-577, this only finds 1 stream which places the block, not to mention the eaters which are ~2000x rarer and less symmetrical. So, I will try again with partial range increased to cover the whole range of intermediates which contain the snark heart.

```bash
> uv run snark.py setup-next-search -i results/heart1.sqlite -o results/heart3.sqlite -q 'partial_intermediate=420'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart3.sqlite -l 100 -n 630 --partial-range=53-73
```

I stopped this early at 493-630, which took about 48 hours. After that time, there were over 2 billion streams in the queue and rising. I have 17 million results, about 9 million of which preserve the snark heart.

The most promising candidates are the 4 which place a boat in the right place for a partial at step 64 and have depth <= 40, just missing a beehive and a blinker.

There might be even better matches, but the results only including the "best" partial match limits us. It would be good to implement saving all of the partial matches in a table we can join with the results.

```bash
> uv run snark.py setup-next-search -i results/heart3.sqlite -o results/heart4.sqlite -q 'length(pi_remaining)/2=9 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart4.sqlite -l 100 -n 450 --partial-range=64-73
```

This finished without any better partial matches, so let's take patterns that improve in other ways and search further:

```bash
> uv run snark.py setup-next-search -i results/heart4.sqlite -o results/heart5.sqlite \
  -q 'length(pi_remaining)/2 <= 9 and depth <= 40 order by lane_width*partial_intermediate_overlapping_population limit 30' \
  -q 'length(pi_remaining)/2 <= 9 and depth <= 40 order by partial_intermediate_depth_separation desc limit 30' \
  -q 'length(pi_remaining)/2 <= 9 and depth <= 40 order by partial_intermediate_overlapping_population limit 30' \
  -q 'length(pi_remaining)/2 <= 9 and depth <= 40 order by lane_width limit 30' \
  -q 'length(pi_remaining)/2 <= 9 and depth <= 40 order by length(pi_remaining), lane_width*partial_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart5.sqlite -l 100 -n 450 --partial-range=64-73
```

Even at 416 gens, this didn't have any useful results. Let's go back to heart4 and see if any of the 230k results can be improved with a short follow-up.

```bash
> uv run snark.py setup-next-search -i results/heart4.sqlite -o results/heart6.sqlite \
  -q 'length(pi_remaining)/2 <= 9 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart6.sqlite -l 100 -n 255 --partial-range=64-73
```

Stopping at 184 gens, this found 22 results with good depth which keep the boat and add another matching still life. Let's explore all of those:

```bash
> uv run snark.py setup-next-search -i results/heart6.sqlite -o results/heart7.sqlite \
  -q 'partial_intermediate_log_prob > -3.9 and depth <= 40'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart7.sqlite -l 100 -n 450 --partial-range=64-73
```

Stopping early at 374, we have a couple of options. There are 7 results which are full matches for step 64, and there are thousands of results which are only missing two blinkers for step 66. Both seem about equally good -- adding a blinker seems like a similar difficulty to finding a zero-degree glider, especially since the full match results are very messy with lots of overlapping areas.

```bash
> uv run snark.py setup-next-search -i results/heart7.sqlite -o results/heart8.sqlite \
  -q 'length(pi_remaining)/2=6 and partial_intermediate_log_prob > -4 and depth <= 40 order by partial_intermediate_overlapping_population*-partial_intermediate_depth_separation*lane_width limit 512'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart8.sqlite -l 100 -n 450 --partial-range=66-73
```

Stopping early at 279, there are three results which place one of the blinkers. Let's try exploring those really quick.

```bash
> uv run snark.py setup-next-search -i results/heart8.sqlite -o results/heart9.sqlite \
  -q 'partial_intermediate_log_prob > -2'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart9.sqlite -l 100 -n 450 --partial-range=66-73
```

This finished without finding any improvements. Letting heart8 continue overnight, I stopped it early at 366 gens (still 150 million queued streams), and found 87 results which improved on the partial match, including one which found a traffic light which is a partial match for a pattern with 5 gliders left and one blinker missing.

Let's start with that one, then continue with the rest later if needed.

```bash
> uv run snark.py setup-next-search -i results/heart8.sqlite -o results/heart10.sqlite \
  -q 'partial_intermediate_log_prob > -1.8'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart10.sqlite -l 100 -n 450 --partial-range=67-73
```

That didn't find any full matches, but let's continue anyway with patterns that make improvements in other areas.

```bash
> uv run snark.py setup-next-search -i results/heart10.sqlite -o results/heart11.sqlite \
  -q 'partial_intermediate_log_prob > -1.8 and depth <= 40 order by lane_width*partial_intermediate_overlapping_population limit 30' \
  -q 'partial_intermediate_log_prob > -1.8 and depth <= 40 order by partial_intermediate_depth_separation desc limit 30' \
  -q 'partial_intermediate_log_prob > -1.8 and depth <= 40 order by partial_intermediate_overlapping_population limit 30' \
  -q 'partial_intermediate_log_prob > -1.8 and depth <= 40 order by lane_width limit 30' \
  -q 'partial_intermediate_log_prob > -1.8 and depth <= 40 order by population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/heart11.sqlite -l 100 -n 450 --partial-range=67-73
```

Stopping early at 282, there are 9 results which are at 4 gliders from finishing, just missing one blinker (still)

```bash
> uv run snark.py setup-next-search -i results/heart11.sqlite -o results/heart12.sqlite -q "partial_intermediate_log_prob > -1.7 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart12.sqlite -l 100 -n 450 --partial-range=68-73
```

This finished with 772 results which are only 3 gliders from finishing, still missing the blinker.

```
> uv run snark.py setup-next-search -i results/heart12.sqlite -o results/heart13.sqlite -q "partial_intermediate_log_prob > -1.6 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart13.sqlite -l 100 -n 375 --partial-range=70-73
```

This finished with 55 results which are two gliders away from finishing, but still no blinker. We've now run out of other options -- we need to find the blinker to make progress, though we could do some cleanup as well.

```bash
> uv run snark.py setup-next-search -i results/heart13.sqlite -o results/heart14.sqlite -q "partial_intermediate_log_prob > -1.5 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart14.sqlite -l 100 -n 512 --partial-range=71-73
```

Stopping early at 398, there's one result with a good depth and complete match for step 71! Let's try it.

```bash
> uv run snark.py setup-next-search -i results/heart14.sqlite -o results/heart15.sqlite -q "depth <= 40 and full_intermediate is not null"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart15.sqlite -l 100 -n 512 --partial-range=71-73
```

Stopping at 386, this tended to explode in depth -- less than 1% of results which kept the full match at step 71 had a depth <= 40. Going back to heart14 for more results.

Stopping heart14 at 439, we haven't found a single extra result that completes the intermediate.

Let's take the 923 results which don't explode in depth from heart15 and continue with those.

```bash
> uv run snark.py setup-next-search -i results/heart15.sqlite -o results/heart16.sqlite -q "depth <= 40 and full_intermediate is not null"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart16.sqlite -l 100 -n 450 --partial-range=71-73
```

Stopping early at 218, there's a result which clears up the rest of the traffic light. It seems likely to get us to step 72.

```bash
> uv run snark.py setup-next-search -i results/heart16.sqlite -o results/heart17.sqlite -q "full_intermediate_overlapping_digest = -6527835380348743352 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart17.sqlite -l 100 -n 450 --partial-range=71-73
```

Stopping early at 384, there's one result with depth 41, let's explore it just to say we found the snark.

```bash
> uv run snark.py setup-next-search -i results/heart17.sqlite -o results/heart18.sqlite -q "length(fi_so_far)/2=72 and depth <= 41"
> uv run snark.py optimize -r results/snark.sqlite -o results/heart18.sqlite -l 100 -n 450 --partial-range=72-73
```

This pretty easily finds one!

But let's go back all the way to heart7 and finish the search there, then try the branch with a full match instead of a partial match -- finding the blinkers was hard and created a lot of debris to clean up. We might get better results just sending zero-degree gliders.

After that finished, there are 33 full matches for step 64 with 192 or 193 gliders.

```bash
> uv run snark.py setup-next-search -i results/heart7.sqlite -o results/finish1.sqlite -q "length(fi_so_far)/2=64 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish1.sqlite -l 100 -n 450 --partial-range=64-73
```

Stopping at 233, this already found one result for step 65. However, the expected length from here would be about 220 as well -- just as much as the other path. Instead, let's continue with heart11 which stopped at 282 gens before.

Stopping heart11 at 360 gens, we have 94 results at step 69 with a missing blinker, and 1 result at step 68. Let's try the full result.

```bash
> uv run snark.py setup-next-search -i results/heart11.sqlite -o results/finish2.sqlite -q "full_intermediate is not null"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish2.sqlite -l 100 -n 450 --partial-range=68-73
```

This finished with 7 results at step 69.

```bash
> uv run snark.py setup-next-search -i results/finish2.sqlite -o results/finish3.sqlite -q "length(fi_so_far)/2=69 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish3.sqlite -l 100 -n 450 --partial-range=69-73
```

This finished with no results at step 70, so let's use it to clean up a bit. Grouping by full_intermediate_overlapping_digest, we find the one with the smallest value also cleans up the partial traffic light in front of the snark pattern. There are 4 results there.

The beehive and ship behind the ship-boat constellation that will become one of the eaters prevents the reaction, so those will need to be cleaned up somehow.

```bash
> uv run snark.py setup-next-search -i results/finish3.sqlite -o results/finish4.sqlite -q "length(fi_so_far)/2=69 and full_intermediate_overlapping_digest=-2826165780866903392 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish4.sqlite -l 100 -n 450 --partial-range=69-73
```

This found 42 results at step 70.

```bash
> uv run snark.py setup-next-search -i results/finish4.sqlite -o results/finish5.sqlite -q "length(fi_so_far)/2=70 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish5.sqlite -l 100 -n 450 --partial-range=70-73
```

Stopping early at 369, there are 85 results at step 71.

```bash
> uv run snark.py setup-next-search -i results/finish5.sqlite -o results/finish6.sqlite -q "length(fi_so_far)/2=71 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish6.sqlite -l 100 -n 450 --partial-range=71-73
```

But they are immediate dead ends -- the 450 depth search ends in 30 seconds. Let's try continuing finish5 just in-case.

Letting finish5 finish at 450, there are now 300 unique results at step 71. Let's try those.

```bash
> uv run snark.py setup-next-search -i results/finish5.sqlite -o results/finish7.sqlite -q "length(fi_so_far)/2=71 and depth <= 40"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish7.sqlite -l 100 -n 450 --partial-range=71-73
```

This time we found 106 results which make it to step 72.
There's also some results which change the beehive and ship for other patterns:

-4452943268195082795
-1843599893608182778

Let's try these first, to see if that unblocks the final glider.

```bash
> uv run snark.py setup-next-search -i results/finish7.sqlite -o results/finish8.sqlite -q "length(fi_so_far)/2>=71 and depth <= 40 and full_intermediate_overlapping_digest in (-4452943268195082795, -1843599893608182778)"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish8.sqlite -l 100 -n 450 --partial-range=71-73
```

This finished without finding any way to clean up behind the boat and ship, and the lengths are 221 or 222. The previous branch was better, so let's finish the search at heart16.

Stopped heart16 at 366 after running overnight, with 100 million items still queued.

These are some of the full_intermediate_overlapping_digests which clear the area for the last two gliders:

- 1643698079398279217
- 5263946418873762400
- -6527835380348743352

I sorted the unique overlapping digests by full_intermediate_overlapping_population, and these are some of the first, so they should also help us with cleanup.

This gives us 113 starting points.

```bash
> uv run snark.py setup-next-search -i results/heart16.sqlite -o results/finish9.sqlite -q "length(fi_so_far)/2>=71 and depth <= 40 and full_intermediate_overlapping_digest in (1643698079398279217, 5263946418873762400, -6527835380348743352)"
> uv run snark.py optimize -r results/snark.sqlite -o results/finish9.sqlite -l 100 -n 450 --partial-range=71-73
```

Stopping early at 383, there is one result which makes it to 73, but has a depth of 49. There are 7 that make it to step 72, and thousands that are at step 71.

Let's take:

- The one that makes it to step 73, but remove the last two gliders to see if a related pattern will avoid the depth issue.
- The 7 that make it to step 72 with good depth.
- The 135 at step 71 with only 217 gliders so far.

```bash
> uv run snark.py setup-next-search -i results/finish9.sqlite -o /tmp/finish10.1.sqlite -q 'length(fi_so_far)/2 = 73'
>  sqlite3 /tmp/finish10.1.sqlite 'update starting_points set stream = cast(substr(stream, 1, length(stream)-2) as blob)'
> uv run snark.py setup-next-search -i results/finish9.sqlite -o /tmp/finish10.2.sqlite \
  -q 'length(fi_so_far)/2 = 72 and depth <= 40' \
  -q 'length(fi_so_far)/2 = 71 and depth <= 40 and length(full_stream)=217'
> uv run snark.py combine-starting-points -i /tmp/finish10.1.sqlite -i /tmp/finish10.2.sqlite -o results/finish10.sqlite
> uv run snark.py optimize -r results/snark.sqlite -o results/finish10.sqlite -l 100 -n 450 --partial-range=71-73
```

Stopping early at 414, we find 6 results with finished snarks and good depth. There's also two more with a depth of 42 we can include.

```bash
> uv run snark.py setup-next-search -i results/finish10.sqlite -o results/cleanup1.sqlite -q 'length(fi_so_far)/2=73 and depth <= 42'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup1.sqlite -l 100 -n 450 --partial-range=73
```

This ran to completion.

- There aren't any results that meaningfully increase the full_intermediate_depth_separation -- there's a reaction that turns the far blinker into a somewhat closer block, but those are equally easy to remove with a glider.
- There aren't any results that meaninfully decrease the lane_width either
- The full_intermediate_overlapping population of the initial candidates was 42, and we can get as low as 24. Let's set a threshold of 28, which gives a few more results.
- The overlapping digests 7330672971558783818 and -5813752341754367267 remove the blinker in the SW.

Let's also try removing the last glider from each starting point so that we can explore more variants that didn't stabilize but might be better.

```bash
> uv run snark.py setup-next-search -i results/cleanup1.sqlite -o results/cleanup2.sqlite \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_digest in (7330672971558783818, -5813752341754367267)' \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_population <= 28' \
  --truncate-n-gliders=1
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup2.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=40
```

Stopping early at 446, I manually checked the first ~800 unique overlapping digests (ordered by overlapping population) as well as the top few for other sorts, and found many interesting ones:

- Cleans up blinker with a LWSS for extra style points: -193538454103534806

- NW side only 3 objects: 7080715839506110744, -8922247175969426314

- Cleans up the whole SW side

  - 2711815672287932577
  - 5788682425296831354

- Cleans up half the SW side

  - 5893732646151755446
  - 4050500890404537443
  - -3408235280866999927
  - 1304690945056674708
  - 3359459027557450862
  - -8623849582041254641
  - -7643252376437056406
  - 2490448728136782260
  - 8637930417447167883
  - 1562405922136898573
  - 1844611965056140523
  - 8455680543190117296
  - 7223024944539302272
  - 6869679154518934195
  - 7969757290436604118
  - -9139039429075897654
  - -7361550325341088326
  - -2764620812118996950
  - 1818424822155382147
  - 5723234143359291499
  - -8766779118075164848
  - -6371525127987798017
  - -5880551631504239654
  - 124897356654445334
  - 5941407449638303984
  - 8495978029819361907
  - 8983533862950547820
  - -9172692098597985830

Taking the four best for cleaning up the overlap, we get 70 unique results.

```bash
> uv run snark.py setup-next-search -i results/cleanup2.sqlite -o results/cleanup3.sqlite \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_digest in (7080715839506110744, -8922247175969426314, 5788682425296831354, 2711815672287932577)' \
  --truncate-n-gliders=1
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup3.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=40
```

Stopping early at 335, here are interesting overlapping digests:

- One object SW, 3 objects NE (22 pop): 697238926407951390, 6389572532358325233
- 1.5 objects SW, 3 objects NE (21 pop): 5535626920864532644, 6137094073080243635
- The 14 and 15 overlapping population options have 3 objects SW, 1 object NE.

This is 25 unique results.

```bash
> uv run snark.py setup-next-search -i results/cleanup3.sqlite -o results/cleanup4.sqlite \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_digest in (697238926407951390, 6389572532358325233, 5535626920864532644, 6137094073080243635)' \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_population <= 15'\
  --truncate-n-gliders=1
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup4.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=40
```

Stopping early at 336, there's one result with an overlap of 6. It leaves the far SW blinker and the close NE blinker. The NE blinker is placed so that it can be removed with a single glider.

Let's try that candidate for a bit.

```bash
> uv run snark.py setup-next-search -i results/cleanup4.sqlite -o results/cleanup5.sqlite \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_population=6' \
  --truncate-n-gliders=1
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup5.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=40
```

Stopping at 411 we didn't find anything with a better overlapping population. Going back to cleanup4.

Stopping cleanup4 at 377 this time, we've found another result with overlapping_population of 6.

```bash
> uv run snark.py setup-next-search -i results/cleanup4.sqlite -o results/cleanup6.sqlite \
  -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_digest=4501616169387995746' \
  --truncate-n-gliders=1
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup6.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=40
```

Stopping early at 411, I didn't find any improvements on the overlapping population of 6. The far blinker is tough to clean up. I will go back to cleanup2 and try just the patterns that clean up the entire SW side. This is only 9 starting points, so we can search deeper more effectively.

```bash
> uv run snark.py setup-next-search -i results/cleanup2.sqlite -o results/cleanup7.sqlite -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_digest in (2711815672287932577, 5788682425296831354)' --truncate-n-gliders=1
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup7.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=40
```

This ran to completion overnight.

The unique overlapping digests up to population 26 all preserve the removal of the SW side, but that totals to 4284 candidates. Let's take a subset of those, as well as the 2 candidates which increased the full_intermediate_depth_separation.

I won't use the truncate gliders feature this time, since it requires deeper searches to find good results.

```bash
> uv run snark.py setup-next-search -i results/cleanup7.sqlite -o results/cleanup8.sqlite -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_population <= 26 order by full_intermediate_overlapping_population limit 30' \
-q 'full_intermediate is not null and depth <= 40 and full_intermediate_depth_separation > -42'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup8.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

This ran to completion, and find a result with an overlap of only 4! It also uses a snark reflected glider to help with the cleanup which is very cool. The final block is also coincidentally in just the right spot to be cleaned up by a follow-up glider.

```bash
> uv run snark.py setup-next-search -i results/cleanup8.sqlite -o results/cleanup9.sqlite -q 'full_intermediate is not null and depth <= 40 and full_intermediate_overlapping_population <= 4'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup9.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

Stopped early at 375. There are many results which clean up the block. It seems that every follow up from 156 to 255 works. After the two gliders pass through the snark, there's a glider which crosses the path of the incoming gliders which can be used to recover from the empty lane.

For 156, a follow-up of 209+ will collide with the crossing glider, but you can delay the 156 glider and shorten the 209 glider to get essentially the same pattern. This adds a lot of search space with little benefit. Let's just pick the 156 glider.

```bash
> uv run snark.py setup-next-search -i results/cleanup9.sqlite -o results/cleanup10.sqlite -q 'hex(stream)="9C"'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup10.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

It was a bit difficult to recover a usable elbow, but we found ~800 results which have zero overlap and depth <= 40. That's probably because the useful results probably only start with a glider of 209+, then there's only a limited set of things to consider to fit in 450 gens.

There are two results which improve the lane_width with a well-placed 90 degree glider. Let's take those and the top 10 with lowest final population.

```bash
> uv run snark.py setup-next-search -i results/cleanup10.sqlite -o results/cleanup11.sqlite -q 'depth <= 40 and full_intermediate_depth_separation > 0 and full_intermediate is not null and lane_width < 79' \
  -q 'depth <= 40 and full_intermediate_depth_separation > 0 and full_intermediate is not null order by population limit 10'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup11.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

Stopping early at 322, there's a result which reduces the lane width to 59. Let's try that for a bit. The cleanup reaction takes a while, so hopefully we can actually keep it going without interfering with our follow-up gliders.

```bash
> uv run snark.py setup-next-search -i results/cleanup11.sqlite -o results/cleanup12.sqlite -q 'depth <= 40 and full_intermediate_depth_separation > 0 and full_intermediate is not null and lane_width < 60'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup12.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

This ran to completion without finding an improvement in depth separation or lane width. Unfortunately there are 4 blocks right around the depth separation of 3, so increasing the depth separation requires cleaning all of those up at once. I will manually check the digests, ordered by population, to find patterns that clean those up.

These 3 clean up the 4th block (in the NE): 2733760994371880776, -4492787098070468790, 5697137463405988850

```bash
> uv run snark.py setup-next-search -i results/cleanup12.sqlite -o results/cleanup13.sqlite -q 'depth <= 40 and full_intermediate_depth_separation > 0 and full_intermediate is not null and lane_width < 60 and r.digest in (2733760994371880776, -4492787098070468790, 5697137463405988850)'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup13.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

This ran to completion. There was one result with a lane_width of 59 but it had an overlapping population of 14.

Let's just use a generic combination of all the parameters to optimize:

```bash
> uv run snark.py setup-next-search -i results/cleanup13.sqlite -o results/cleanup14.sqlite -q 'depth <= 40 and full_intermediate_depth_separation >= 3 and full_intermediate is not null order by (depth-full_intermediate_depth_separation)*lane_width*lane_width*population limit 100'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup14.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

Stopped early at 407. There are 4 candidates which increase the full_intermediate_depth_separation to 5, 7, and 10 and keep a lane_width within 60.

```bash
> uv run snark.py setup-next-search -i results/cleanup14.sqlite -o results/cleanup15.sqlite -q 'depth <= 40 and full_intermediate_depth_separation >= 5 and full_intermediate is not null and lane_width < 60'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup15.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

This ran to completion.

```bash
> uv run snark.py setup-next-search -i results/cleanup15.sqlite -o results/cleanup16.sqlite -q 'full_intermediate is not null and full_intermediate_depth_separation > 0 and depth <= 40 order by 1.0*population*lane_width*lane_width*population/full_intermediate_depth_separation limit 10' \
  -q 'full_intermediate is not null and full_intermediate_depth_separation > 0 and depth <= 40 and lane_width=48'
> uv run snark.py optimize -r results/snark.sqlite -o results/cleanup16.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=40
```

I've been making progress, but there's probably a better strategy. I will go back to cleanup11, and pick some in each of these categories:

- Lowest population
- Highest depth separation
- Lowest lane width
- Lowest depth - depth separation
- Each combination of each of these
- The top n of each of these as well as a sample of the top n digests

```bash
> shrink() {
  infile=$1
  outfile=$2
  n=$3

  cond="full_intermediate is not null and depth <= 50 and full_intermediate_depth_separation > 0"

  a="population"
  b="(1.0/full_intermediate_depth_separation)"
  c="(lane_width*sqrt(lane_width))"
  d="(depth - full_intermediate_depth_separation)"
  tiebreak="($a * $b * $c * $d)"

  uv run snark.py optimize -r results/snark.sqlite -o "$infile" -l 100 -n 400 --partial-range=73 --live-view-depth=50 || exit 1
  if [ ! -f "$outfile" ]; then
    uv run snark.py setup-next-search -i "$infile" -o "$outfile" \
        -q "$cond order by $a, $tiebreak limit $n" \
        -q "$cond order by $b, $tiebreak limit $n" \
        -q "$cond order by $c, $tiebreak limit $n" \
        -q "$cond order by $d, $tiebreak limit $n" \
        \
        -q "$cond order by $a * $b, $tiebreak limit $n" \
        -q "$cond order by $a * $c, $tiebreak limit $n" \
        -q "$cond order by $a * $d, $tiebreak limit $n" \
        \
        -q "$cond order by $b * $c, $tiebreak limit $n" \
        -q "$cond order by $b * $d, $tiebreak limit $n" \
        \
        -q "$cond order by $c * $d, $tiebreak limit $n" \
        \
        -q "$cond order by $a * $b * $c, $tiebreak limit $n" \
        -q "$cond order by $a * $b * $d, $tiebreak limit $n" \
        -q "$cond order by $a * $c * $d, $tiebreak limit $n" \
        -q "$cond order by $b * $c * $d, $tiebreak limit $n" \
        \
        -q "$cond order by $tiebreak limit $n" \
        \
        -q "$cond group by r.digest order by $a, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $b, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $c, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $d, $tiebreak limit $n" \
        \
        -q "$cond group by r.digest order by $a * $b, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $a * $c, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $a * $d, $tiebreak limit $n" \
        \
        -q "$cond group by r.digest order by $b * $c, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $b * $d, $tiebreak limit $n" \
        \
        -q "$cond group by r.digest order by $c * $d, $tiebreak limit $n" \
        \
        -q "$cond group by r.digest order by $a * $b * $c, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $a * $b * $d, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $a * $c * $d, $tiebreak limit $n" \
        -q "$cond group by r.digest order by $b * $c * $d, $tiebreak limit $n" \
        \
        -q "$cond group by r.digest order by $tiebreak limit $n"
  fi
}

> shrink results/cleanup11.sqlite results/autoshrink1.sqlite 32
> for i in 1 2 3 4 5 6 7 8 9 10; do
    shrink "results/autoshrink$i.sqlite" "results/autoshrink$(($i + 1)).sqlite" 32
  done
```

Autoshrink7 got us our first result!

00875D696B735B69667665605C8A9793816C5B749A958072CA8080786E71A2735A5B927F677687B07CB4606CDA5B5A6F6F6368CAAE876FD6745EB65B5DBE676A5F60755B7A6E93755B785C69956C77666A7E7C6A80968284865AC563845BA192646C91618A6465A75BB78C5A5E635D64696699695C795C5A636061745BC15E5B7564677A795A6DCD5A696E5DE86C645D91766A5A659786718D605B7B5B6F5A665F695D6B7AA25A72605C727F6D7E62875F8D72627C6694815B5C886BF9B55D8D6A6D62715F806CFA69626D6460AA5E5F6665CE6264AA6F98A9618DBA64655E605F6E5F866F62735B5B6066626265AF9CEE6463AC747AD492608A9865686062838A7F675E81607893628E86

0, 135, 93, 105, 107, 115, 91, 105, 102, 118, 101, 96, 92, 138, 151, 147, 129, 108, 91, 116, 154, 149, 128, 114, 202, 128, 128, 120, 110, 113, 162, 115, 90, 91, 146, 127, 103, 118, 135, 176, 124, 180, 96, 108, 218, 91, 90, 111, 111, 99, 104, 202, 174, 135, 111, 214, 116, 94, 182, 91, 93, 190, 103, 106, 95, 96, 117, 91, 122, 110, 147, 117, 91, 120, 92, 105, 149, 108, 119, 102, 106, 126, 124, 106, 128, 150, 130, 132, 134, 90, 197, 99, 132, 91, 161, 146, 100, 108, 145, 97, 138, 100, 101, 167, 91, 183, 140, 90, 94, 99, 93, 100, 105, 102, 153, 105, 92, 121, 92, 90, 99, 96, 97, 116, 91, 193, 94, 91, 117, 100, 103, 122, 121, 90, 109, 205, 90, 105, 110, 93, 232, 108, 100, 93, 145, 118, 106, 90, 101, 151, 134, 113, 141, 96, 91, 123, 91, 111, 90, 102, 95, 105, 93, 107, 122, 162, 90, 114, 96, 92, 114, 127, 109, 126, 98, 135, 95, 141, 114, 98, 124, 102, 148, 129, 91, 92, 136, 107, 249, 181, 93, 141, 106, 109, 98, 113, 95, 128, 108, 250, 105, 98, 109, 100, 96, 170, 94, 95, 102, 101, 206, 98, 100, 170, 111, 152, 169, 97, 141, 186, 100, 101, 94, 96, 95, 110, 95, 134, 111, 98, 115, 91, 91, 96, 102, 98, 98, 101, 175, 156, 238, 100, 99, 172, 116, 122, 212, 146, 96, 138, 152, 101, 104, 96, 98, 131, 138, 127, 103, 94, 129, 96, 120, 147, 98, 142, 128, (156)

We still need to find one which leaves an elbow before the snark, though. Let's see if any of these results work.

```bash
> uv run snark.py setup-next-search -i results/autoshrink7.sqlite -o results/last-elbow.sqlite -q 'full_intermediate is not null and population < 65'
> uv run snark.py optimize -r results/snark.sqlite -o results/last-elbow.sqlite -l 100 -n 512 --partial-range=73 --live-view-depth=50
```

After a short while (stopping at 277), we see that there are 2 digests that look like pi explosions in the results, but they are due to a different reaction, not an elbow being formed.

5572399308306247052 7033401698931445928

Let's let autoshrink7 run to completion then try checking again.

```bash
> uv run snark.py optimize -r results/snark.sqlite -o results/autoshrink7.sqlite -l 100 -n 400 --partial-range=73 --live-view-depth=50
```

Continued running autoshrink until autoshrink8 finished. It found a lot of blocks near the lane. Let's try them to see if any are the pi explosion block.

The snark + offset elbow has a population of 53, so we want to view results with at least 57 population. If the elbow is correct, then we'll see a population of 108 for the pi explosion remanent + snark + block.

```bash
> uv run snark.py setup-next-search -i results/autoshrink8.sqlite -o results/done1.sqlite -q 'full_intermediate is not null and population > 56 and population <= 60'
> uv run snark.py optimize -r results/snark.sqlite -o results/done1.sqlite -l 100 -n 255 --partial-range=73 --live-view-depth=40
```

Let's do the search with more candidates, since we may have the correct block + a still life that can be deleted with an extra glider.

```bash
> uv run snark.py setup-next-search -i results/autoshrink8.sqlite -o results/done2.sqlite -q 'full_intermediate is not null and population > 56 and population <= 64'
> uv run snark.py optimize -r results/snark.sqlite -o results/done2.sqlite -l 100 -n 300 --partial-range=73 --live-view-depth=40
```

Recovering a block: 271 gliders
00875D696B735B69667665605C8A9793816C5B749A958072CA8080786E71A2735A5B927F677687B07CB4606CDA5B5A6F6F6368CAAE876FD6745EB65B5DBE676A5F60755B7A6E93755B785C69956C77666A7E7C6A80968284865AC563845BA192646C91618A6465A75BB78C5A5E635D64696699695C795C5A636061745BC15E5B7564677A795A6DCD5A696E5DE86C645D91766A5A659786718D605B7B5B6F5A665F695D6B7AA25A72605C727F6D7E62875F8D72627C6694815B5C886BF9B55D8D6A6D62715F806CFA69626D6460AA5E5F6665CE6264AA6F98A9618DBA64655E605F6E5F866F62735B5B6066626265AF9CEE6463AC747AD492608A9865686062838A7F675E816078905B6E5A6064E8

0,135,93,105,107,115,91,105,102,118,101,96,92,138,151,147,129,108,91,116,154,149,128,114,202,128,128,120,110,113,162,115,90,91,146,127,103,118,135,176,124,180,96,108,218,91,90,111,111,99,104,202,174,135,111,214,116,94,182,91,93,190,103,106,95,96,117,91,122,110,147,117,91,120,92,105,149,108,119,102,106,126,124,106,128,150,130,132,134,90,197,99,132,91,161,146,100,108,145,97,138,100,101,167,91,183,140,90,94,99,93,100,105,102,153,105,92,121,92,90,99,96,97,116,91,193,94,91,117,100,103,122,121,90,109,205,90,105,110,93,232,108,100,93,145,118,106,90,101,151,134,113,141,96,91,123,91,111,90,102,95,105,93,107,122,162,90,114,96,92,114,127,109,126,98,135,95,141,114,98,124,102,148,129,91,92,136,107,249,181,93,141,106,109,98,113,95,128,108,250,105,98,109,100,96,170,94,95,102,101,206,98,100,170,111,152,169,97,141,186,100,101,94,96,95,110,95,134,111,98,115,91,91,96,102,98,98,101,175,156,238,100,99,172,116,122,212,146,96,138,152,101,104,96,98,131,138,127,103,94,129,96,120,144,91,110,90,96,100,232,(90)