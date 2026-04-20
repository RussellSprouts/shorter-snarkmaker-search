
uv run oncoming.py \
  --use-gun-rle='x = 96, y = 123, rule = B3/S23
14bo$14bo$14bo16$2o$obo64bo$bo65bo$67bo$17bo6b2o$16bobo5b2o37b3o3b3o$
16bobo$17bo49bo$34bo32bo$9b2o23b3o30bo$8bobo26bo$9bo26b2o5$25b2o5b2o$
25b2o5b2o46b2o$79bo2bo$29b2o49b2o$24bo4b2o$5b2o16bobo$5b2o16bobo$24bo$
52b2o$39bo12b2o$37bobo$37b3o9b2o5b2o$37bo11b2o5b2o$12bo$6b2o3bobo$5bo
2bo2b2o80b2o$6b2o85bobo$94bo11$44b2o$44b2o$36bo$36bo$36bo4$47b2ob2o$
47b2ob2o25$39b2o$39b2o2$48bo$48bo11b2o$48bo10bobo$60bo10$46b3o10$46b3o!' \
  --n-gun-gliders=1 \
  --simulate-gens=2000 \
  --subtree="3;122;122" --depth=5 | tee results/p120/cleanup-gun-3-122-122.txt \
  | awk 'NR % 100 == 0' &

uv run oncoming.py \
  --use-gun-rle='x = 96, y = 123, rule = B3/S23
14bo$14bo$14bo16$2o$obo64bo$bo65bo$67bo$17bo6b2o$16bobo5b2o37b3o3b3o$
16bobo$17bo49bo$34bo32bo$9b2o23b3o30bo$8bobo26bo$9bo26b2o5$25b2o5b2o$
25b2o5b2o46b2o$79bo2bo$29b2o49b2o$24bo4b2o$5b2o16bobo$5b2o16bobo$24bo$
52b2o$39bo12b2o$37bobo$37b3o9b2o5b2o$37bo11b2o5b2o$12bo$6b2o3bobo$5bo
2bo2b2o80b2o$6b2o85bobo$94bo11$44b2o$44b2o$36bo$36bo$36bo4$47b2ob2o$
47b2ob2o25$39b2o$39b2o2$48bo$48bo11b2o$48bo10bobo$60bo10$46b3o10$46b3o!' \
  --n-gun-gliders=1 \
  --simulate-gens=2000 \
  --subtree="11;128;134" --depth=5 | tee results/p120/cleanup-gun-11-128-134.txt \
  | awk 'NR % 100 == 0' &

uv run oncoming.py \
  --use-gun-rle='x = 96, y = 123, rule = B3/S23
14bo$14bo$14bo16$2o$obo64bo$bo65bo$67bo$17bo6b2o$16bobo5b2o37b3o3b3o$
16bobo$17bo49bo$34bo32bo$9b2o23b3o30bo$8bobo26bo$9bo26b2o5$25b2o5b2o$
25b2o5b2o46b2o$79bo2bo$29b2o49b2o$24bo4b2o$5b2o16bobo$5b2o16bobo$24bo$
52b2o$39bo12b2o$37bobo$37b3o9b2o5b2o$37bo11b2o5b2o$12bo$6b2o3bobo$5bo
2bo2b2o80b2o$6b2o85bobo$94bo11$44b2o$44b2o$36bo$36bo$36bo4$47b2ob2o$
47b2ob2o25$39b2o$39b2o2$48bo$48bo11b2o$48bo10bobo$60bo10$46b3o10$46b3o!' \
  --n-gun-gliders=1 \
  --simulate-gens=2000 \
  --subtree="43;144;94" --depth=5 | tee results/p120/cleanup-gun-43-144-94.txt \
  | awk 'NR % 100 == 0' &

uv run oncoming.py \
  --use-gun-rle='x = 96, y = 123, rule = B3/S23
14bo$14bo$14bo16$2o$obo64bo$bo65bo$67bo$17bo6b2o$16bobo5b2o37b3o3b3o$
16bobo$17bo49bo$34bo32bo$9b2o23b3o30bo$8bobo26bo$9bo26b2o5$25b2o5b2o$
25b2o5b2o46b2o$79bo2bo$29b2o49b2o$24bo4b2o$5b2o16bobo$5b2o16bobo$24bo$
52b2o$39bo12b2o$37bobo$37b3o9b2o5b2o$37bo11b2o5b2o$12bo$6b2o3bobo$5bo
2bo2b2o80b2o$6b2o85bobo$94bo11$44b2o$44b2o$36bo$36bo$36bo4$47b2ob2o$
47b2ob2o25$39b2o$39b2o2$48bo$48bo11b2o$48bo10bobo$60bo10$46b3o10$46b3o!' \
  --n-gun-gliders=1 \
  --simulate-gens=2000 \
  --subtree="27;155" --depth=4 | tee results/p120/cleanup-gun-27-155.txt \
  | awk 'NR % 100 == 0' &