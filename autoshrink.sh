set -e

shrink() {
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

uv run snark.py optimize -r results/snark.sqlite -o results/cleanup11.sqlite -l 100 -n 450 --partial-range=73 --live-view-depth=50 || exit 1
shrink results/cleanup11.sqlite results/autoshrink1.sqlite 32

for i in 1 2 3 4 5 6 7 8 9 10; do
    shrink "results/autoshrink${i}.sqlite" "results/autoshrink$(($i + 1)).sqlite" 32
done