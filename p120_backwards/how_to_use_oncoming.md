# How to use the scripts for the Oncoming Glider Gun Construction Arm (OGGCA)

First, [install `uv`](https://docs.astral.sh/uv/getting-started/installation/) for managing Python dependencies and running the code. I recommend a Linux-like environment, like WSL or a Linux distribution.

## `oncoming.py`

General toolkit for searching and viewing single channel recipes.

By default, oncoming.py will search for recipes and output results, but there are various commands to do other tasks.

### General options

Options that are applicable to multiple commands.

- `--toolkit` - defaults to sc90b5p120, i.e., minimum spacing 90 generations, 5 lane offset between the glider gun and recipe gliders, and a p120 stream of gun gliders. This the standard toolkit with the p120 Simkin gun.

  Related:

  - `--tandem-delay`, `--tandem-offset` - adds an additional glider stream to the gun gliders, so that there are two gliders in tandem. The numbers indicate the number of generations behind and number of cells offset the other glider is. For example, `--toolkit=sc90b6p120 --tandem-delay=19 --tandem-offset=0` gives a p120 stream of two gliders separated by 19 ticks. This particular pair of gliders can send 90 degree gliders of both colors with a single glider recipe.

  - `--actually-not-oncoming` - rotates the gun stream by 90 degrees so that the glider streams meet at a 90 degree angle. This style of construction arm is not as efficient as the OGGCA, because there is a fixed intersection point, but it may be more efficient than traditional single channel recipes. In this mode the lane offset of the toolkit is ignored.

- `--n-gun-gliders` - how many gun gliders to include in the simulation. This also sets the default amount of time to simulate, so that we don't find recipes that rely on the gun gliders stopping.

  Related:
  - `--simulate-gens` - override the default number of generations to simulate, which is the period * n_gun_gliders.

  - `--use-gun-rle` - use an rle pattern as the gun for simulation or printing. Automatically detects the output stream and places the gun accordingly. With this, `--n-gun-gliders` controls how far away the gun is placed.
  You can also just use `--use-gun-rle=120` or `--use-gun-rle=46` to get a corresponding gun.

- `--with-debris-rle` - Adds additional items near the glider streams. This is useful for finding recipes that react to nearby objects, for logical operations or cleaning up. The rle must include an example glider in the position of delay `0`, to show the debris position relative to the recipes. (It must look like `ooo$o$bo`).

  Related:
  - `--and-without-debris` - Also simulates/prints the same recipe without the debris added. When recipe searching, the results will show the diff.
  - `--evolve-debris-gens` - Simulate the debris forward some generations before adding it, e.g., if it's a glider or oscillator.
  - `--without-debris-max-population` - filter out simulations that result in a population greater than this if the debris is not included (see also `--max-population` for the equivalent with the debris).
  - `--without-debris-same-gliders-consumed` - filter out simulations where a different set of gun gliders escapes the reaction depending on whether the debris is included.
  - `--without-debris-must-differ` - filter out simulations where the reaction with and without the debris has the same ash.

### Search options

- `--subtree` - a semi-colon separated list of recipe patterns to try. Each component can take ranges or comma separated delays: For example, `--subtree="1,3,5-9;90-255;90-255"` will search for recipes that start with 1, 3, 5, 6, 7, 8, or 9, followed by two gliders with delays of 90-255. You can specify multiple subtrees and all will be searched.

  Related:
  - `--subtree-file` - load subtrees from a file, one per line.
  - `--max-delay` - for components not specified in subtree, search from the minimum defined in `--toolkit`, to the maximum in `--max-delay`. Default 255.

- `--depth` - the maximum number of gliders to include in the recipes searched.

- `--max-population` - filter out results that have a population larger than this (not including escaping gun gliders). These will report 'too big' instead of showing a breakdown of the recipe components. This highly speeds up processing of results -- try to set this at e.g., 24 or 32 -- the results which make a huge mess are also slowest to process.

- `--concurrent` - use multiple threads to process the search. This speeds up the search, and some search options are only supported in this mode. The results won't necessarily be in order, though. Defaults to true.

- `--only-gliders`, `--only-90-degree-gliders` - filter out results that aren't pure gliders. Highly speeds up the search.

### `--print-rle` Command

Takes in a text description of a single channel recipe, and outputs an rle. It can accept basic recipes of comma separated delays, but it also supports a small programming language for more complex recipes. See the full documentation at [print-rle.md](../print-rle.md).

```bash
$ uv run oncoming.py --print-rle="3, 201, swim 4, (167)"

$ uv run oncoming.py --print-rle"$(cat path/to/recipe/file.txt)"
```

Related:

- `--(no-)recipe-label` - whether to include a LifeHistory red state text for the delays in the printed pattern.

### `--find-minimum-follow` Command

Finds the minimum follow distance for the recipes (semi-colon separated), where the next glider will not interact with the reaction.

### `--evaluate` Command

Given an rle pattern, prints the results as if it were evaluated as a result from a search. The rle must include a glider at delay 0 (must look like `ooo$o$bo`) to show the position of the items.

### `--view-orientations` Command

Given a name (beehive, ship, etc.) or apgcode, shows the labels given to the orientations in search results (each object has `o0`-`o7` indicating its orientation). The orientation labels are arbitrary but consistent for each object.

### `--extract-recipes` Command

Given a results file, finds the recipes that result in a clean object.

## `compile_p120_fast.py`

```bash
$ uv run compile_p120_fast.py path/to/salvo.rle --toolkit-file=recipes/sc90b5p120-gliders.txt --color=1 --parity=0 --direction=SW --optimize=time --beam-width=100
```

compile_p120_fast.py converts a slow salvo pattern into an OGGCA recipe. The slow salvo should include gliders heading NW, and be a simple B3/S23 rle pattern.

First, it agnosticizes the recipe. For each glider in the recipe, it finds alternatives that have the same effect. If step 5 of the recipe deletes an extra block, then it will find alternative glider lanes and phases that delete the block without affecting the rest of the pattern. For this to work, each phase of the recipe must have a stable result (p2).

Next, it does a beam search to find the most efficient way to send gliders to make the recipe. At each step of the recipe, it considers every possible starting state from the current beam, every possible next glider from the agnosticization, and every recipe in the toolkit file that can send that glider. It builds a new beam of the best results, then continues.

Some recipes in the toolkit files include `{requires state: n}` or `{to state: n}`. These are for multi-part recipes that send multiple gliders with adjustable positions. In sc90b5p120, the recipe `5, 138, (121)` sends a 90 degree glider and a 180 degree glider. So, when we use this recipe we move to `state 1`, where we have the normal gun gliders, but there's an extra 180 degree glider in front of them. It so happens that from there, we can send gliders of two color/parity options with the recipes `0, 221, (90)` and `0, 219, (90)`. When we can use these recipes, they are more efficient than the standard single ones.

The toolkit files also include a section of "Swim" recipes. These recipes have no output, but consume gun gliders faster than they are produced, so they can be used to swim upstream against the glider gun.

The output of compile_p120_fast.py will look like this:

```
Calculating recipe dag, this may take a few seconds...
Step 0
  color=0 phase=0 gli_lane=0
Step 1
  color=1 phase=0 gli_lane=3
gliders = 6
duration = 857
[21, 92, 163, 265, 92, 134]
1, 92, 163, swim 4, (150), wait 112, 1, 92, 134, swim 3, (90)
#######################################################
let g2a(d-11) = 1, 92, 134, swim 3, (90) in
let g4d(d-4) = 1, 92, 163, swim 4, (150) in
g4d(d0), g2a(d3), 
```

The step progress will show all of the alternate gliders considered for each step.

At the end, it will show the number of total gliders and total duration for the best single channel OGGCA recipe.

Then, it will show three versions of the recipe:

1. The raw delays from processing. The first number (`21` in this case) is not as meaningful and should be replaced with `1`.

2. A more symbolic representation for `--print-rle` showing all of the details, with each individual single channel glider shown. First, we use `1, 92, 163` to send a SW white odd glider, which consumes 4 gun gliders in the process. We wait 150 + 112 generations, and then send `1, 92, 134` to send a SW black odd glider, which consumes 3 gun gliders, and we could continue with another glider after 90 generations.

3. A fully symbolic representation for `--print-rle`, showing only the 90 degree gliders sent. First, we define all of the recipes we will use. g2a, for example, refers to the first recipe in the SW black odd category, and g4d refers to the fourth recipe in the SW white odd category. We use those definitions to say which gliders to send. We don't specify any delay or swimming recipes -- `--print-rle` automatically handles the delays and swimming operations we need to ensure the glider recipes output on the correct lanes.

## oncoming-pp.py

Postprocessor to convert `oncoming.py` results created with `--only-gliders` into toolkit files for `compile_p120_fast.py`.