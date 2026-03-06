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
> uv run snark.py optimize -r results/snark.sqlite -o results/partial_search4.sqlite -l 100 -n 400 --partial-range=13 # (stopped early ~388)
```

There are 5 results with a full match and depth <= 0. If we were to remove
the extra blocks, each of these patterns is 60 zero-degree gliders away from
a complete snark.

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

Interestingly, for most of the intermediates, the searches ended early without
ever reaching 512 generations. This can happen because the search skips
processing patterns that are identical to earlier ones -- if the reactions
settle quickly, then you might only need to send a 90 and 91 gen follow-up.

```bash
> uv run snark.py setup-next-search -i results/zero_degree1.1.sqlite -o /tmp/1.1.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.2.sqlite -o /tmp/1.2.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.3.sqlite -o /tmp/1.3.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.4.sqlite -o /tmp/1.4.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py setup-next-search -i results/zero_degree1.5.sqlite -o /tmp/1.5.sqlite -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population limit 100'
> uv run snark.py combine-starting-points -i /tmp/1.1.sqlite -i /tmp/1.2.sqlite -i /tmp/1.3.sqlite -i /tmp/1.4.sqlite -i /tmp/1.5.sqlite -o results/zero_degree2.sqlite
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree2.sqlite -l 100 -n 400 # (stopped early ~371)
```

There are many ways to improve from here, so let's explore each of those dimensions:

```bash
> uv run snark.py setup-next-search -i results/zero_degree2.sqlite -o results/zero_degree3.sqlite \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width*full_intermediate_overlapping_population/length(fi.so_far) limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by full_intermediate_depth_separation desc limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by full_intermediate_overlapping_population limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by lane_width limit 30' \
  -q 'length(fi.so_far) >= 26 and depth <= 0 order by length(fi.so_far) desc, lane_width*full_intermediate_overlapping_population limit 30'
> uv run snark.py optimize -r results/snark.sqlite -o results/zero_degree3.sqlite -l 100 -n 512
```