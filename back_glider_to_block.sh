
for i in {1..6}; do
  echo "sc90b${i}p120"
  uv run oncoming.py --toolkit="sc90b${i}p120" --max-delay=128 --subtree="0-7" --depth=4 --max-population=4 --n-gun-gliders=1 --simulate-gens=1024 | grep -P 'block\(l(-3|4)'
done