
uv run oncoming.py --use-gun-rle='x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!' \
  --n-gun-gliders=1 --subtree="58;96;96;90-131" \
  --depth=6 --max-delay=255 --simulate-gens=1200 \
  | tee results/58_96_96_1.txt | awk 'NR % 100 == 0' &

uv run oncoming.py --use-gun-rle='x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!' \
  --n-gun-gliders=1 --subtree="58;96;96;132-173" \
  --depth=6 --max-delay=255 --simulate-gens=1200 \
  | tee results/58_96_96_2.txt | awk 'NR % 100 == 0' &

uv run oncoming.py --use-gun-rle='x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!' \
  --n-gun-gliders=1 --subtree="58;96;96;174-215" \
  --depth=6 --max-delay=255 --simulate-gens=1200 \
  | tee results/58_96_96_3.txt | awk 'NR % 100 == 0' &

uv run oncoming.py --use-gun-rle='x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!' \
  --n-gun-gliders=1 --subtree="58;96;96;216-255" \
  --depth=6 --max-delay=255 --simulate-gens=1200 \
  | tee results/58_96_96_4.txt | awk 'NR % 100 == 0'