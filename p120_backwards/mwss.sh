# Search for completions of MWSS partials

uv run oncoming.py --n-gun-gliders=20 --subtree="7;188;90;175" \
  --depth=6 --max-delay=255 \
  | tee results/mwss-completion-2.txt | awk 'NR % 100 == 0' &

uv run oncoming.py --n-gun-gliders=20 --subtree="5;169;214;153" \
  --depth=6 --max-delay=255 \
  | tee results/mwss-completion-3.txt | awk 'NR % 100 == 0' &

uv run oncoming.py --n-gun-gliders=20 --subtree="7;140;205;96" \
  --depth=6 --max-delay=255 \
  | tee results/mwss-completion-4.txt | awk 'NR % 100 == 0'