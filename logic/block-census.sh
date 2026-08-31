

mkdir -p results/logic/block-census
for i in {6..20}; do
  debris="3o\$o\$bo$(($i + 4))\$6b2o\$6b2o!"
  echo uv run oncoming.py --with-debris-rle="'"$debris"'" --depth=1 --subtree="0-256"
  echo "# block(l-$i)"
  uv run oncoming.py --with-debris-rle="$debris" --depth=3 --subtree="0-256" --max-population=24 --without-debris-max-population=24 --and-without-debris --without-debris-same-gliders-consumed --concurrent | grep -v 'too big' > results/logic/block-census/block-l-$i.txt
done