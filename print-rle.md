# `--print-rle` format

`uv run oncoming.py --print-rle="..."` converts a description of a single-channel stream
into an rle.

## Basic syntax

A basic recipe to send a 90 degree glider then wait for 16 ticks:
```
3, 201, swim 4, (167)
wait 2*8
# comment -- lines starting with # are ignored
```

- **3**: In the default mode, the first glider and each one after a minimum-follow indicator is the (mod 8) parity of the glider compared to the oncoming gun gliders. This determines how the glider will collide with the gun gliders to start the recipe.

- **201**: Another glider, 201 generations behind the previous.

- **swim 4**: Indicates that we've consumed 4 gun gliders with this recipe. This is optional, but accurately tracking the number of gun gliders consumed lets us determine the location of the construction arm.

- **(167)**: An integer in parens indicates the minimum time before we can send another recipe -- 167 generations after the 201 glider.

- **wait 2*8**: Wait an additional 16 ticks after the minimum wait time. This effectively pulls the arm back by two full diagonals.

## The modulo system

Because the glider gun is always running, the system needs to keep track of its state. The system keeps a counter `$currentTime`.

The recipe above is implicitly equivalent to:
```
set 0 (mod 240)
3 (mod 8), 201, swim 4, (167)
wait 16
```

- **set 0 (mod 240)**: Sets `$currentTime` to 0, and sets the tracking modulus to 240. This indicates the current state of the periodic components at that position are known to be 0 (mod 240).

- **3 (mod 8)**: Sends a glider, automatically adding generations of delay until the glider is lined up with `3 (mod 8)`, based on the `$currentTime`. It's an error to request a modulus that is greater than the last `set` modulus.

The recipe to build a Simkin gun-based p120 OGGCA looks like:
```
mode sc, 0, ..., 125, mode oggca, set 28 (mod 240), set d0, (90)
```

Once the simkin gun is constructed, the recipe uses `set 28 (mod 240)` to indicate the state that the gun will be in.

After each minimum follow directive, gliders have implicit modulus, if none is specified:

- **mode oggca**: Each glider after a minimum follow is (mod 8).
- **mode sc**: Each glider after a minimum follow us (mod 2).

## Commas?

Commas are optional between segments. These are equivalent:

```
3 201 swim 4 (167)
```

## Expressions

You can use mathematical operators with the normal operator precedence:

```
1 + 2, 100*2 + 1, swim 5-1, (167)
```

The operators are `+`, `-`, `*`, `/`, and `mod`. You can also use parens.

**Note**: There are no negative integer literals. Remember that commas are optional, so `1, -10*80 + 1000` would be equivalent to `1 -10*80 + 1000`, which would be ambiguous -- is it `1 minus 10 times 80 plus 1000`, or `1 then negative 10 times 80 plus 1000`? To indicate a negative number, use `(0 - 10)`.

## `Let` expressions

You can define a local name for an expression value:

```
let $a = 1 in
$a + $a
```

The general form is `let ${foo} = {expr} in {...}`.
The expression will be evaluated immediately and the current value stored in `$a`.

## `Let` recipes

You can also define recipes using let and names without `$`:

```
let glider = 3, 201, swim 4, (167) in
glider, glider, glider
```

Optionally, you can use a lane literal to further qualify the name:

A lane literal looks like `l1`, `l-7`, or `l(expr)`.
```
let block(l-7) = 1, 90, 91, 91, swim 3, (90) in
let block(l-21) = 1, 104, 94, 116, 95, 91, swim 5, (90) in

block(l-7)
block(l-21)
```

The lane is just a convenience to disambiguate multiple recipes which may create the same object at different distances from the construction arm. If the recipe definition contains a lane specificiation, then the lane is a required part of the name.

## Autoswimming and depths

Though a recipe for a block(l-7) could never create a block at l-8, a recipe for a block(l-7, d0) could create a block at d1 just by delaying for 8 ticks. The system is able to automatically do this for you:

```
let block(l-7,d-11) = 1, 90, 91, 91, swim 3, (90) in

block(l-7, d1)
block(l-7, d11)
block(l-7, d21)
```

The definition states that the recipe will place a block at a depth of -11. So, the system knows that to place a block at d1, we need to wait 12*8. It then knows that we've consumed 3 gun gliders, so it knows how long to wait for gun glider 4 to be in position to place the next block at d11.

Sometimes, the stream of glider has advanced too far, and we need to swim upstream to get into position. The system will check any recipes named like `swim_.*` to fix this. (For a p120b5 OGGCA these are built-in)

1. If any of the swim_ recipes immediately swim upstream far enough, it will pick the fastest one.

2. If none of the swim_ recipe immediately solve the issue, it will greedily pick the one that swims furthest and try again.
