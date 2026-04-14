# Interesting recipes

This is a collection of interesting recipes for sc90b5p120 -- aka, a stream of gliders with minimum spacing 90 crashing head-on into the stream of a p120 glider gun with a 5 lane offset.

There are 8 unique collisions that happen depending on the timing of the recipe glider. I've chosen to label them with this numbering:

- 0: both gliders deleted
- 1: block created, on the side with the gun glider's lane
- 2: backwards kickback -- 0 degree glider towards the gun gliders
- 3: pond on gun side
- 4: delete
- 5: pond on recipe side
- 6: forwards kickback -- 180 degree glider towards the recipe gliders
- 7: block on recipe side

The recipes start with a number showing the mod 8 timing they start on.

The kickback gliders will delete the next glider on that lane. This gives the very useful `2, (90)` recipe, which deletes two gun gliders, allowing you to push forward large amounts with just one glider.

The raw data for most combinations of 4 gliders is available at https://drive.google.com/file/d/1eZvUXMR2_LEaEr9ZYgbiJfwE6yULxSHp/view?usp=sharing (40Mb download, 500Mb unzipped). I have excluded results which had gliders in multiple directions and results with a large cloud of ash (200+ characters on the line).

The `oncoming.py` file implements many useful tools for working with this toolkit:

```bash
# Print a demo of a recipe. Automatically adjusts the mod 8 timing when you have multiple recipes with minimum follow-ups.
# Use ; to show multiple streams side-by-side.
uv run oncoming.py --print-rle="3, 102, 90, (90) 48 + 7, 158, 144" --n-gun-gliders=10

# Search a different toolkit instead of sc90b5p120
uv run oncoming.py --toolkit=sc61b5p256 --depth=2 --max-delay=400 --simulate-gens=1024 --n-gun-gliders=10

# Use a specific gun instead of a simulated stream. Automatically discovers the gun's phase and lines it up to work the same as the simulated stream. Gun should be sending gliders SE.
uv run oncoming.py --use-gun-rle='x = 37, y = 26, rule = B3/S23
3$11bo$11b3o$14bo$13b2o5$2b2o5b2o$2b2o5b2o2$6b2o$6b2o4$29b2o$16bo12b2o
$14bobo$14b3o9b2o5b2o$14bo11b2o5b2o!' ...

# Check if a pattern safely absorbs incoming gliders from the gun (i.e., it shuts off the gun). Use ; to separate multiple recipes.
uv run oncoming.py --check-for-shutoff="3,174,138"

# Search a specific subset of the tree.
# E.g., search 1-4 glider recipes with the first gliders 1,3,5 and 7, then follow-up with a 90-120 glider, then two more gliders from 90-255.
uv run oncoming.py --subtree="1,3,5,7 ; 90-120" --depth=4 --max-delay=255

# Find the minimum distance for a follow-up glider that won't interact with
# the reaction. Use ; to separate multiple recipes.
uv run oncoming.py --find-minimum-follow="3, 102, 90"
```

## Best gliders NE

Key:

- ♝♗ - on the black/white squares of the chessboard. Equivalent to depth mod 2
- ⓪① - whether the phase of the glider is even or odd.
- ⬀⬃⬁⬂ - the direction of the glider. ⬃ is the recipe side 90 degree, ⬀ is the gun side 90 degree, ⬁ is 0 degree towards the gun, ⬂ is 180 degree towards the recipe.

### Black even

+ 3, 102, 90, (90) {total: 282} - glider(d-5)(ph2)(♝⬀⓪)
+ 7, 158, 144, (162) {total: 464} - glider(d11)(ph2)(♝⬀⓪)
+ 7, 188, 102, 150, (90) {total: 530} - glider(d13)(ph2)(♝⬀⓪)
+ 3, 93, 197, 188, (90) {total: 568} - glider(d9)(ph2)(♝⬀⓪)
+ 3, 104, 129, 250, (90) {total: 573} - glider(d19)(ph0)(♝⬀⓪)

### Black odd

+ 3, 212, 96, (104) {total: 412} - glider(d21)(ph1)(♝⬀①)
+ 3, 104, 129, 97, (90) {total: 420} - glider(d21)(ph3)(♝⬀①)
+ 3, 105, 233, (90) {total: 428} - glider(d-3)(ph3)(♝⬀①)
+ 7, 170, 94, 92, (90) {total: 446} - glider(d7)(ph3)(♝⬀①)
+ 7, 180, 96, 93, (90) {total: 459} - glider(d5)(ph1)(♝⬀①)
+ 5, 144, 148, 93, (90) {total: 475} - glider(d9)(ph1)(♝⬀①)

### White even

+ 7, 148, 106, (90) {total: 344} - glider(d6)(ph2)(♗⬀⓪)
+ 3, 201, (167) {total: 368} - glider(d-10)(ph2)(♗⬀⓪)
+ 7, 164, 101, 98, (90) {total: 453} - glider(d8)(ph2)(♗⬀⓪)
+ 7, 132, 126, 156, (90) {total: 504} - glider(d20)(ph0)(♗⬀⓪)
+ 5, 144, 157, 115, (90) {total: 506} - glider(d18)(ph0)(♗⬀⓪)
+ 3, 219, 113, 107, (90) {total: 529} - glider(d12)(ph0)(♗⬀⓪)

### White odd

+ 3, 159, 122, 95, (90) {total: 466} - glider(d12)(ph1)(♗⬀①)
+ 3, 217, 129, 93, (90) {total: 529} - glider(d8)(ph3)(♗⬀①)
+ 7, 164, 182, 133, (90) {total: 569} - glider(d40)(ph3)(♗⬀①)
+ 7, 212, 170, 100, (90) {total: 572} - glider(d26)(ph1)(♗⬀①)

## Best gliders SW

### Black even

+ 1, 100, 137, 115, (105) {total: 457} - glider(d-7)(ph0)(♝⬃⓪)
+ 5, 144, 132, 107, (90) {total: 474} - glider(d3)(ph2)(♝⬃⓪)
+ 3, 208, 186, (90) {total: 484} - glider(d-5)(ph0)(♝⬃⓪)
+ 7, 170, 96, 148, (90) {total: 504} - glider(d1)(ph0)(♝⬃⓪)
+ 3, 105, 164, 161, (90) {total: 520} - glider(d-3)(ph2)(♝⬃⓪)
+ 7, 162, 110, 195, (90) {total: 557} - glider(d27)(ph2)(♝⬃⓪)

### Black odd

+ 5, 138, 125, (90) {total: 353} - glider(d-1)(ph1)(♝⬃①)
+ 1, 92, 163, (150) {total: 405} - glider(d-5)(ph3)(♝⬃①)
+ 3, 96, 92, 147, (90) {total: 425} - glider(d-15)(ph3)(♝⬃①)
+ 7, 132, 114, 133, (90) {total: 496} - glider(d21)(ph3)(♝⬃①)
+ 3, 93, 169, 148, (90) {total: 500} - glider(d3)(ph3)(♝⬃①)
+ 3, 215, 90, 161, (90) {total: 556} - glider(d5)(ph3)(♝⬃①)

### White even

+ 3, 93, 197, 168 - glider(d14)(ph2)(♗⬃⓪)
+ 3, 96, 143, 130 - glider(d-16)(ph2)(♗⬃⓪)
+ 3, 185, 129 - glider(d-6)(ph0)(♗⬃⓪)
+ 3, 196, 128 - glider(d-10)(ph0)(♗⬃⓪)
+ 3, 198, 97, 90 - glider(d10)(ph0)(♗⬃⓪)
+ 7, 132, 96, 177 - glider(d8)(ph0)(♗⬃⓪)
+ 7, 156, 105, 157 - glider(d12)(ph0)(♗⬃⓪)
+ 7, 164, 105, 157 - glider(d14)(ph0)(♗⬃⓪)
+ 7, 164, 198, 105 - glider(d22)(ph0)(♗⬃⓪)

### White odd

+ 1, 92, 134 - glider(d-12)(ph1)(♗⬃①)
+ 3, 104, 129, 164 - glider(d20)(ph3)(♗⬃①)
+ 3, 165, 101, 120 - glider(d-16)(ph1)(♗⬃①)
+ 7, 132, 220, 90 - glider(d2)(ph1)(♗⬃①)
+ 7, 156, 198, 151 - glider(d16)(ph3)(♗⬃①)


## Offset blocks NE

+ 3, 211, 122, 174, (90) {total: 507} - block(l32,d10)
+ 5, 185, 180, 115, (90) {total: 570} - block(l33,d-15)
+ 5, 196, 169, 115, (90) {total: 570} - block(l33,d-15)
+ 3, 225, 137, 148, (90) {total: 600} - block(l37,d3)
+ 7, 166, 233, 134, (231) {total: 764} - block(l32,d34)

## Offset blocks SW

- (3, 104, 96, 115) ['block(l-32,d10)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 120, 122, 175) ['block(l-33,d-3)', 'g0', 'g1', 'g2', 'g3']
- (7, 252, 93, 173) ['block(l-37,d35)', 'g0', 'g1', 'g2', 'g3']

## Far offset beehive #1

- 1, 92, 90, 219, (179) - place an offset boat

- 3, 219, 229, 127, (298) - send a 0 degree glider towards the boat to make a delayed 90 degree glider

- 1, 104, 93, 129, (90) - send a lwss that will collide with the glider

To have the glider+lwss collide into a beehive, you need to add 1400+A delay to let the stream advance before sending the zero degree glider, then A delay again to let the stream advance before sending the LWSS to intercept it.

i.e.: The entire recipe should look like:
`1,92,90,219,(179){A+1400}+3,219,229,127,(298){A}+1,104,93,129`
where A >= 0, in increments of 8.

The distance to the offset beehive increases at c/4, so for each 8 gen increase in A, it will be 2 full diagonals further away. The limit depends on the length of the construction arm.

E.g.,
```bash
uv run oncoming.py --print-rle="1,92,90,219,(179)2000+3,219,229,127,(298)600+1,104,93,129" --n-gun-gliders=30
```

TODO: Find three other versions of this for the other directions/corners. Will need new 0/180 degree recipes and clean lwss's.

## Far offset beehive #2



## Cap/uncap stream

Blocks the gun stream with a boat-bit reaction, so you don't have to keep sending
gliders during a long wait. Minimum time is 3, 1073, (90) ~ 1166. Compare to sending 2, 240, 240, 240, 240,... (90) to keep the stream in the same place.

(cap) 3,174,138, (uncap) 657+240*n,104,(90)

## LWSS

### Clean

- 1, 104, 93, 129 (90) - lwss(-9,-499)(0,-2)
- 3, 219, 108, 132, 183, 93, (90) - lwss(275,-7)(2,0)

### Partials

- (7, 156, 97, 160) ['beehive(l-11,d22)', 'blinker(l-2,d-4)', 'blinker(l-4,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'lwss(388,-6)(2,0)']
- (7, 188, 96, 153) ['g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'loaf(l-3,d19)', 'lwss(391,-5)(2,0)']
- (3, 134, 134, 128) ['beehive(l-12,d-21)', 'blinker(l15,d-27)', 'blinker(l17,d-27)', 'block(l-23,d-29)', 'block(l17,d11)', 'g0', 'g1', 'g2', 'g3', 'g4', 'lwss(-403,2)(-2,0)']
- (3, 118, 159, 114) ['blinker(l-29,d-13)', 'blinker(l-31,d-13)', 'block(l-13,d1)', 'block(l21,d9)', 'g0', 'g1', 'g2', 'g3', 'lwss(-344,-4)(-2,0)']
- (3, 128, 136, 186) ['blinker(l13,d-27)', 'blinker(l15,d-27)', 'block(l-13,d19)', 'g0', 'g1', 'g2', 'lwss(-294,16)(-2,0)']
- (3, 128, 137, 185) ['blinker(l13,d-27)', 'blinker(l15,d-27)', 'block(l-13,d19)', 'g0', 'g1', 'g2', 'lwss(-294,16)(-2,0)']
- (1, 118, 136, 147) ['beehive(l13,d-28)', 'g0', 'g1', 'g2', 'g3', 'lwss(-13,358)(0,2)']

## MWSS

### Clean

- 3, 184, 131, 239, (201) - mwss(443,0)(2,0)
- 3, 225, 194, 140, 208, (284) - mwss(2,-236)(0,-2)

### Partials

+ (7, 188, 90, 175) ['beehive(l-21,d48)', 'blinker(l-18,d28)', 'blinker(l-20,d28)', 'block(l-24,d12)', 'g0', 'g1', 'g2', 'g3', 'g4', 'xq4_27dee6(9,441)(0,2)']
+ (5, 169, 214, 153) ['beehive(l24,d-25)', 'blinker(l22,d-20)', 'blinker(l24,d-20)', 'block(l-23,d1)', 'g0', 'g1', 'g2', 'loaf(l-23,d-15)', 'xq4_27dee6(-256,-15)(-2,0)']
+ (7, 140, 205, 96) ['beehive(l-3,d-6)', 'block(l-10,d-8)', 'block(l22,d-8)', 'block(l25,d-13)', 'g0', 'g1', 'g2', 'xq4_27dee6(-345,-26)(-2,0)']

## HWSS

### Partials

+ (3, 91, 220, 180) ['beehive(l-6,d-11)', 'blinker(l-37,d25)', 'blinker(l-39,d25)', 'g0', 'g1', 'g2', 'xq4_27deee6(354,8)(2,0)']

## Glider pairs

These recipes send a pair of gliders. If the separation matches, you might be able to save time by using them.

- 1, 92, 203, (617) glider(d-5)(ph0)(♝⬃①), glider(d-7)(ph2)(♝⬃⓪)
- 1, 96, 224, 96, (150) - glider(d-16)(ph0)(♗⬃①), glider(d-6)(ph0)(♗⬃①)
- 1, 96, 240, 96, (150) - glider(d-12)(ph0)(♗⬃①), glider(d-6)(ph0)(♗⬃①)
- 3, 102, 136, 123, (162) - glider(d-1)(ph0)(♝⬀①), glider(d-5)(ph2)(♝⬀⓪)
- 3, 105, 217, 182, (90) - glider(d-2)(ph0)(♗⬃⓪), glider(d12)(ph0)(♗⬃⓪)
- 3, 160, 100, 118, (650) - glider(d-17)(ph0)(♝⬃⓪), glider(d-20)(ph0)(♗⬃①)
- 3, 163, 250, 226, (413) - glider(d5)(ph0)(♝⬀①), glider(d7)(ph2)(♝⬀⓪)
- 3, 165, 101, 103, (526) - glider(d-16)(ph0)(♗⬃①), glider(d12)(ph0)(♗⬃⓪)
- 3, 196, 136, 211, (190) - glider(d-10)(ph0)(♗⬃⓪), glider(d-17)(ph0)(♝⬃⓪)
- 3, 196, 146, 130, (178) - glider(d-10)(ph0)(♗⬃⓪), glider(d3)(ph2)(♝⬃⓪)
- 3, 196, 147, 147, (171) - glider(d-10)(ph0)(♗⬃⓪), glider(d-8)(ph0)(♗⬃①)
- 3, 196, 152, 108, (90) - glider(d-10)(ph0)(♗⬃⓪), glider(d-3)(ph0)(♝⬃①)
- 3, 196, 171, 212, (90) - glider(d-10)(ph0)(♗⬃⓪), glider(d7)(ph2)(♝⬃⓪)
- 3, 201, 95, 201, (351) - glider(d-10)(ph2)(♗⬀⓪), glider(d-26)(ph2)(♗⬀⓪)
- 3, 201, 103, 201, (343) - glider(d-10)(ph2)(♗⬀⓪), glider(d-24)(ph2)(♗⬀⓪)
- 3, 201, 111, 201, (167) - glider(d-10)(ph2)(♗⬀⓪), glider(d-22)(ph2)(♗⬀⓪)
- 3, 201, 141, 111 - glider(d-10)(ph2)(♗⬀⓪), glider(d-9)(ph2)(♝⬀⓪)
- 3, 201, 167, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-38)(ph2)(♗⬀⓪)
- 3, 201, 175, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-36)(ph2)(♗⬀⓪)
- 3, 201, 183, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-34)(ph2)(♗⬀⓪)
- 3, 201, 191, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-32)(ph2)(♗⬀⓪)
- 3, 201, 199, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-30)(ph2)(♗⬀⓪)
- 3, 201, 207, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-28)(ph2)(♗⬀⓪)
- 3, 201, 215, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-26)(ph2)(♗⬀⓪)
- 3, 201, 239, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-20)(ph2)(♗⬀⓪)
- 3, 201, 247, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-18)(ph2)(♗⬀⓪)
- 3, 201, 255, 201 - glider(d-10)(ph2)(♗⬀⓪), glider(d-16)(ph2)(♗⬀⓪)
- 3, 219, 220, 221 - glider(d-4)(ph0)(♗⬀①), glider(d-5)(ph0)(♝⬀⓪)
- 3, 219, 220, 231 - glider(d-4)(ph0)(♗⬀①), glider(d-5)(ph0)(♝⬀⓪)
- 5, 138, 119, 163, (336) - glider(d-1)(ph0)(♝⬃①), glider(d-10)(ph0)(♗⬃①)
- 5, 138, 121, 219, (90)  - glider(d-1)(ph0)(♝⬃①), glider(d-3)(ph0)(♝⬃⓪)
- 5, 138, 121, 221, (90) - glider(d-1)(ph0)(♝⬃①), glider(d-2)(ph2)(♗⬃⓪)
- 5, 138, 129, 219, (90) - glider(d-1)(ph0)(♝⬃⓪), glider(d-1)(ph0)(♝⬃①)
- 5, 138, 129, 221, (90) - glider(d-1)(ph0)(♝⬃①), glider(d0)(ph2)(♗⬃⓪)
- 5, 138, 137, 219, (90) - glider(d-1)(ph0)(♝⬃①), glider(d1)(ph0)(♝⬃⓪)
- 5, 138, 137, 221 - glider(d-1)(ph0)(♝⬃①), glider(d2)(ph2)(♗⬃⓪)
- 5, 138, 145, 219 - glider(d-1)(ph0)(♝⬃①), glider(d3)(ph0)(♝⬃⓪)
- 5, 138, 145, 221 - glider(d-1)(ph0)(♝⬃①), glider(d4)(ph2)(♗⬃⓪)
- 5, 138, 153, 219 - glider(d-1)(ph0)(♝⬃①), glider(d5)(ph0)(♝⬃⓪)
- 5, 138, 153, 221 - glider(d-1)(ph0)(♝⬃①), glider(d6)(ph2)(♗⬃⓪)
- 5, 138, 161, 219 - glider(d-1)(ph0)(♝⬃①), glider(d7)(ph0)(♝⬃⓪)
- 5, 138, 161, 221 - glider(d-1)(ph0)(♝⬃①), glider(d8)(ph2)(♗⬃⓪)
- 5, 138, 169, 219 - glider(d-1)(ph0)(♝⬃①), glider(d9)(ph0)(♝⬃⓪)
- 5, 138, 169, 221 - glider(d-1)(ph0)(♝⬃①), glider(d10)(ph2)(♗⬃⓪)
- 5, 138, 177, 219 - glider(d-1)(ph0)(♝⬃①), glider(d11)(ph0)(♝⬃⓪)
- 5, 138, 177, 221 - glider(d-1)(ph0)(♝⬃①), glider(d12)(ph2)(♗⬃⓪)
- 5, 138, 185, 219 - glider(d-1)(ph0)(♝⬃①), glider(d13)(ph0)(♝⬃⓪)
- 5, 138, 185, 221 - glider(d-1)(ph0)(♝⬃①), glider(d14)(ph2)(♗⬃⓪)
- 5, 138, 193, 219 - glider(d-1)(ph0)(♝⬃①), glider(d15)(ph0)(♝⬃⓪)
- 5, 138, 193, 221 - glider(d-1)(ph0)(♝⬃①), glider(d16)(ph2)(♗⬃⓪)
- 5, 138, 201, 219 - glider(d-1)(ph0)(♝⬃①), glider(d17)(ph0)(♝⬃⓪)
- 5, 138, 201, 221 - glider(d-1)(ph0)(♝⬃①), glider(d18)(ph2)(♗⬃⓪)
- 5, 138, 209, 219 - glider(d-1)(ph0)(♝⬃①), glider(d19)(ph0)(♝⬃⓪)
- 5, 138, 209, 221 - glider(d-1)(ph0)(♝⬃①), glider(d20)(ph2)(♗⬃⓪)
- 5, 138, 217, 219 - glider(d-1)(ph0)(♝⬃①), glider(d21)(ph0)(♝⬃⓪)
- 5, 138, 217, 221 - glider(d-1)(ph0)(♝⬃①), glider(d22)(ph2)(♗⬃⓪)
- 5, 138, 225, 219 - glider(d-1)(ph0)(♝⬃①), glider(d23)(ph0)(♝⬃⓪)
- 5, 138, 225, 221 - glider(d-1)(ph0)(♝⬃①), glider(d24)(ph2)(♗⬃⓪)
- 5, 138, 233, 219 - glider(d-1)(ph0)(♝⬃①), glider(d25)(ph0)(♝⬃⓪)
- 5, 138, 233, 221 - glider(d-1)(ph0)(♝⬃①), glider(d26)(ph2)(♗⬃⓪)
- 5, 138, 241, 219 - glider(d-1)(ph0)(♝⬃①), glider(d27)(ph0)(♝⬃⓪)
- 5, 138, 241, 221 - glider(d-1)(ph0)(♝⬃①), glider(d28)(ph2)(♗⬃⓪)
- 5, 138, 249, 219 - glider(d-1)(ph0)(♝⬃①), glider(d29)(ph0)(♝⬃⓪)
- 5, 138, 249, 221 - glider(d-1)(ph0)(♝⬃①), glider(d30)(ph2)(♗⬃⓪)
- 5, 153, 196, 108 - glider(d32)(ph0)(♗⬀①), glider(d7)(ph2)(♝⬀⓪)
- 7, 140, 206, 126 - glider(d6)(ph0)(♗⬃①), glider(d7)(ph2)(♝⬃⓪)
- 7, 156, 222, 113 - glider(d-1)(ph0)(♝⬀①), glider(d16)(ph0)(♗⬀⓪)
- 7, 196, 196, 155 - glider(d10)(ph0)(♗⬃⓪), glider(d3)(ph2)(♝⬃⓪)
- 7, 196, 213, 103 - glider(d-2)(ph0)(♗⬃⓪), glider(d15)(ph2)(♝⬃⓪)
- 7, 228, 160, 100 - glider(d11)(ph0)(♝⬃⓪), glider(d8)(ph0)(♗⬃①)
- 7, 244, 160, 100 - glider(d12)(ph0)(♗⬃①), glider(d15)(ph0)(♝⬃⓪)

## Teardown gun

+ 58, 96, 96, 109, 133, 99 -- destroy construction arm, leaving nothing behind.

Note that 58 is just an arbitary label for the mod 120 phase of the glider gun. Here's what this looks like:

```
x = 185, y = 194, rule = LifeHistory
9.A$9.3A$12.A$11.2A5$2A5.2A$2A5.2A$18.3A$4.2A12.A4.A$4.2A13.A3.2A$
24.2A$21.A2.A$22.2A$27.2A$27.2A2$24.2A5.2A$24.2A5.2A11$28.A$29.A$
27.3A11$34.3D.3D5.3D.3D5.3D.3D6.D2.3D.3D6.D2.3D.3D5.3D.3D$34.D3.D.
D5.D.D.D7.D.D.D7.2D2.D.D.D.D5.2D4.D3.D5.D.D.D.D$34.3D.3D5.3D.3D5.
3D.3D6.D2.D.D.3D6.D2.3D.3D5.3D.3D$36.D.D.D7.D.D.D7.D.D.D6.D2.D.D3.
D6.D4.D3.D7.D3.D$34.2D2.3D5.3D.3D5.3D.3D5.3D.3D.3D5.3D.3D.3D5.3D.
3D10$49.2A$49.A.A$49.A22$73.2A$73.A.A$73.A22$97.2A$97.A.A$97.A25$
125.A$124.2A$124.A.A32$157.3A$157.A$158.A22$183.A$182.2A$182.A.A!
```

## Faraway items

Single items placed at least 20 hd from the lane.

- (1, 104, 99, 131) ['g0', 'g1', 'g2', 'g3', 'g4', 'loaf(l-20,d-14)']
- (3, 101, 198, 105) ['g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'pond(l-20,d16)']
- (3, 159, 135, 134) ['g0', 'g1', 'long boat(l-27,d7)']
- (3, 165, 102, 175) ['g0', 'g1', 'tub(l24,d2)']
- (3, 208, 146, 121) ['g0', 'g1', 'g2', 'g3', 'loaf(l20,d10)']
- (3, 216, 94, 152) ['g0', 'g1', 'g2', 'g3', 'ship(l26,d-6)']
- (3, 218, 240, 157) ['g0', 'g1', 'g2', 'loaf(l24,d-6)']
- (3, 219, 93, 115) ['g0', 'g1', 'g2', 'g3', 'pond(l27,d-5)']
- (3, 219, 113, 156) ['g0', 'g1', 'pond(l21,d17)']
- (3, 222, 160, 251) ['g0', 'loaf(l22,d0)']
- (3, 225, 148, 186) ['g0', 'g1', 'g2', 'g3', 'loaf(l-20,d48)']
- (3, 225, 158, 166) ['g0', 'g1', 'g2', 'g3', 'toad(l21,d11)']
- (3, 240, 101, 198) ['g0', 'pond(l-20,d-14)']
- (5, 142, 147, 235) ['g0', 'g1', 'g2', 'g3', 'g4', 'ship tie(l21,d-7)']
- (5, 142, 181, 171) ['g0', 'g1', 'g2', 'pond(l28,d8)']
- (5, 144, 163, 145) ['g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'tub(l22,d0)']
- (5, 144, 173, 106) ['g0', 'g1', 'g2', 'g3', 'g4', 'loaf(l-27,d-3)']
- (5, 185, 192, 93) ['g0', 'g1', 'g2', 'g3', 'g4', 'loaf(l23,d-25)']
- (7, 130, 230, 252) ['g0', 'g1', 'loaf(l-24,d-14)']
- (7, 140, 221, 251) ['g0', 'pond(l21,d19)']
- (7, 148, 105, 203) ['g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'loaf(l21,d3)']
- (7, 150, 144, 185) ['g0', 'g1', 'g2', 'toad(l23,d15)']
- (7, 164, 197, 92) ['g0', 'g1', 'g2', 'g3', 'pond(l-20,d10)']
- (7, 172, 182, 113) ['g0', 'g1', 'g2', 'loaf(l-25,d27)']
- (7, 180, 95, 206) ['g0', 'g1', 'g2', 'g3', 'loaf(l20,d-6)']
- (7, 180, 162, 98) ['g0', 'g1', 'g2', 'g3', 'g4', 'loaf(l22,d6)']
- (7, 204, 167, 223) ['g0', 'loaf(l-23,d-3)']
- (7, 212, 133, 178) ['g0', 'g1', 'pond(l28,d32)']
- (7, 230, 250, 247) ['g0', 'loaf(l37,d21)']
- (1, 90, 109, 132) ['block(l28,d-10)', 'g0', 'g1', 'g2', 'g3']
- (1, 90, 231, 231) ['block(l25,d-3)', 'g0', 'g1', 'g2', 'g3']
- (1, 96, 119) ['block(l24,d-20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (1, 96, 132, 90) ['block(l21,d-17)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (1, 92, 241, 103) ['block(l29,d-43)', 'g0', 'g1', 'g2']
- (1, 92, 241, 116) ['block(l29,d-43)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 92, 241, 118) ['block(l29,d-43)', 'g0', 'g1', 'g2', 'g3']
- (1, 94, 132, 174) ['block(l25,d-11)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 96, 121, 133) ['boat(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (1, 101, 117, 98) ['block(l22,d22)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 222, 148, 113) ['block(l27,d-17)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 101, 139, 163) ['block(l24,d18)', 'g0', 'g1', 'g2', 'g3']
- (1, 101, 188, 159) ['block(l22,d-30)', 'g0', 'g1', 'g2']
- (1, 104, 99, 202) ['block(l-20,d-16)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 104, 213, 167) ['beehive(l28,d17)', 'g0', 'g1', 'g2']
- (1, 109, 122, 226) ['block(l22,d-26)', 'g0', 'g1', 'g2', 'g3']
- (1, 110, 94, 184) ['block(l-24,d16)', 'g0', 'g1', 'g2', 'g3']
- (1, 112, 96, 119) ['block(l24,d-52)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 114, 91, 166) ['beehive(l-22,d-77)', 'g0', 'g1', 'g2']
- (1, 114, 162, 98) ['boat(l20,d-32)', 'g0', 'g1', 'g2']
- (1, 114, 216, 137) ['beehive(l22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (1, 116, 151, 95) ['block(l20,d-44)', 'g0', 'g1', 'g2', 'g3']
- (1, 116, 182, 109) ['beehive(l24,d-57)', 'g0', 'g1', 'g2']
- (1, 120, 96, 119) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 122, 91, 166) ['beehive(l-22,d-75)', 'g0', 'g1', 'g2']
- (1, 122, 162, 98) ['boat(l20,d-30)', 'g0', 'g1', 'g2']
- (1, 122, 216, 137) ['beehive(l22,d-43)', 'g0', 'g1', 'g2', 'g3']
- (1, 124, 151, 95) ['block(l20,d-42)', 'g0', 'g1', 'g2', 'g3']
- (1, 124, 182, 109) ['beehive(l24,d-55)', 'g0', 'g1', 'g2']
- (1, 128, 96, 119) ['block(l24,d-48)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 130, 91, 166) ['beehive(l-22,d-73)', 'g0', 'g1', 'g2']
- (1, 130, 162, 98) ['boat(l20,d-28)', 'g0', 'g1', 'g2']
- (1, 130, 216, 137) ['beehive(l22,d-41)', 'g0', 'g1', 'g2', 'g3']
- (1, 132, 151, 95) ['block(l20,d-40)', 'g0', 'g1', 'g2', 'g3']
- (1, 132, 182, 109) ['beehive(l24,d-53)', 'g0', 'g1', 'g2']
- (1, 136, 96, 119) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 138, 91, 166) ['beehive(l-22,d-71)', 'g0', 'g1', 'g2']
- (1, 138, 162, 98) ['boat(l20,d-26)', 'g0', 'g1', 'g2']
- (1, 138, 216, 137) ['beehive(l22,d-39)', 'g0', 'g1', 'g2', 'g3']
- (1, 140, 151, 95) ['block(l20,d-38)', 'g0', 'g1', 'g2', 'g3']
- (1, 140, 182, 109) ['beehive(l24,d-51)', 'g0', 'g1', 'g2']
- (1, 144, 96, 119) ['block(l24,d-44)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 146, 91, 166) ['beehive(l-22,d-69)', 'g0', 'g1', 'g2']
- (1, 146, 162, 98) ['boat(l20,d-24)', 'g0', 'g1', 'g2']
- (1, 146, 216, 137) ['beehive(l22,d-37)', 'g0', 'g1', 'g2', 'g3']
- (1, 148, 151, 95) ['block(l20,d-36)', 'g0', 'g1', 'g2', 'g3']
- (1, 148, 182, 109) ['beehive(l24,d-49)', 'g0', 'g1', 'g2']
- (1, 152, 96, 119) ['block(l24,d-42)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 154, 91, 166) ['beehive(l-22,d-67)', 'g0', 'g1', 'g2']
- (1, 154, 162, 98) ['boat(l20,d-22)', 'g0', 'g1', 'g2']
- (1, 154, 216, 137) ['beehive(l22,d-35)', 'g0', 'g1', 'g2', 'g3']
- (1, 156, 151, 95) ['block(l20,d-34)', 'g0', 'g1', 'g2', 'g3']
- (1, 156, 182, 109) ['beehive(l24,d-47)', 'g0', 'g1', 'g2']
- (1, 160, 96, 119) ['block(l24,d-40)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 162, 91, 166) ['beehive(l-22,d-65)', 'g0', 'g1', 'g2']
- (1, 162, 162, 98) ['boat(l20,d-20)', 'g0', 'g1', 'g2']
- (1, 164, 151, 95) ['block(l20,d-32)', 'g0', 'g1', 'g2', 'g3']
- (1, 164, 182, 109) ['beehive(l24,d-45)', 'g0', 'g1', 'g2']
- (1, 168, 96, 119) ['block(l24,d-38)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 170, 91, 166) ['beehive(l-22,d-63)', 'g0', 'g1', 'g2']
- (1, 170, 162, 98) ['boat(l20,d-18)', 'g0', 'g1', 'g2']
- (1, 170, 216, 137) ['beehive(l22,d-31)', 'g0', 'g1', 'g2', 'g3']
- (1, 172, 151, 95) ['block(l20,d-30)', 'g0', 'g1', 'g2', 'g3']
- (1, 172, 182, 109) ['beehive(l24,d-43)', 'g0', 'g1', 'g2']
- (1, 176, 96, 119) ['block(l24,d-36)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 178, 91, 166) ['beehive(l-22,d-61)', 'g0', 'g1', 'g2']
- (1, 178, 162, 98) ['boat(l20,d-16)', 'g0', 'g1', 'g2']
- (1, 178, 216, 137) ['beehive(l22,d-29)', 'g0', 'g1', 'g2', 'g3']
- (1, 180, 151, 95) ['block(l20,d-28)', 'g0', 'g1', 'g2', 'g3']
- (1, 180, 182, 109) ['beehive(l24,d-41)', 'g0', 'g1', 'g2']
- (1, 184, 96, 119) ['block(l24,d-34)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 151, 95) ['block(l20,d-12)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (1, 186, 91, 166) ['beehive(l-22,d-59)', 'g0', 'g1', 'g2']
- (1, 186, 162, 98) ['boat(l20,d-14)', 'g0', 'g1', 'g2']
- (1, 186, 216, 137) ['beehive(l22,d-27)', 'g0', 'g1', 'g2', 'g3']
- (1, 188, 151, 95) ['block(l20,d-26)', 'g0', 'g1', 'g2', 'g3']
- (1, 188, 182, 109) ['beehive(l24,d-39)', 'g0', 'g1', 'g2']
- (1, 192, 96, 97) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3']
- (1, 192, 96, 100) ['block(l24,d-32)', 'g0', 'g1', 'g2']
- (1, 192, 96, 118) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3']
- (1, 192, 96, 119) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 192, 96, 126) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 192, 96, 129) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 192, 96, 131) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 192, 96, 134) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 192, 96, 139) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3']
- (1, 192, 96, 141) ['block(l24,d-32)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 194, 91, 166) ['beehive(l-22,d-57)', 'g0', 'g1', 'g2']
- (1, 194, 162, 98) ['boat(l20,d-12)', 'g0', 'g1', 'g2']
- (1, 194, 216, 137) ['beehive(l22,d-25)', 'g0', 'g1', 'g2', 'g3']
- (1, 196, 151, 95) ['block(l20,d-24)', 'g0', 'g1', 'g2', 'g3']
- (1, 196, 182, 109) ['beehive(l24,d-37)', 'g0', 'g1', 'g2']
- (1, 200, 96, 97) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3']
- (1, 200, 96, 100) ['block(l24,d-30)', 'g0', 'g1', 'g2']
- (1, 200, 96, 118) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3']
- (1, 200, 96, 119) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 200, 96, 126) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 200, 96, 129) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 200, 96, 131) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 200, 96, 134) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 200, 96, 139) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3']
- (1, 200, 96, 141) ['block(l24,d-30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 202, 91, 166) ['beehive(l-22,d-55)', 'g0', 'g1', 'g2']
- (1, 202, 162, 98) ['boat(l20,d-10)', 'g0', 'g1', 'g2']
- (1, 202, 216, 137) ['beehive(l22,d-23)', 'g0', 'g1', 'g2', 'g3']
- (1, 204, 151, 95) ['block(l20,d-22)', 'g0', 'g1', 'g2', 'g3']
- (1, 204, 182, 109) ['beehive(l24,d-35)', 'g0', 'g1', 'g2']
- (1, 208, 96, 97) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3']
- (1, 208, 96, 100) ['block(l24,d-28)', 'g0', 'g1', 'g2']
- (1, 208, 96, 118) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3']
- (1, 208, 96, 119) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 208, 96, 126) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 208, 96, 129) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 208, 96, 131) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 208, 96, 134) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 208, 96, 139) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3']
- (1, 208, 96, 141) ['block(l24,d-28)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 210, 91, 166) ['beehive(l-22,d-53)', 'g0', 'g1', 'g2']
- (1, 210, 162, 98) ['boat(l20,d-8)', 'g0', 'g1', 'g2']
- (1, 210, 216, 137) ['beehive(l22,d-21)', 'g0', 'g1', 'g2', 'g3']
- (1, 212, 151, 95) ['block(l20,d-20)', 'g0', 'g1', 'g2', 'g3']
- (1, 212, 182, 109) ['beehive(l24,d-33)', 'g0', 'g1', 'g2']
- (1, 216, 96, 97) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3']
- (1, 216, 96, 100) ['block(l24,d-26)', 'g0', 'g1', 'g2']
- (1, 216, 96, 118) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3']
- (1, 216, 96, 119) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 216, 96, 126) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 216, 96, 129) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 216, 96, 131) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 216, 96, 134) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 216, 96, 139) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3']
- (1, 216, 96, 141) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 218, 91, 166) ['beehive(l-22,d-51)', 'g0', 'g1', 'g2']
- (1, 218, 162, 98) ['boat(l20,d-6)', 'g0', 'g1', 'g2']
- (1, 218, 216, 137) ['beehive(l22,d-19)', 'g0', 'g1', 'g2', 'g3']
- (1, 220, 151, 95) ['block(l20,d-18)', 'g0', 'g1', 'g2', 'g3']
- (1, 220, 182, 109) ['beehive(l24,d-31)', 'g0', 'g1', 'g2']
- (1, 224, 96, 97) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3']
- (1, 224, 96, 100) ['block(l24,d-24)', 'g0', 'g1', 'g2']
- (1, 224, 96, 118) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3']
- (1, 224, 96, 119) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 224, 96, 126) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 224, 96, 129) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 224, 96, 131) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 224, 96, 134) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 224, 96, 139) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3']
- (1, 224, 96, 141) ['block(l24,d-24)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 226, 91, 166) ['beehive(l-22,d-49)', 'g0', 'g1', 'g2']
- (1, 226, 162, 98) ['boat(l20,d-4)', 'g0', 'g1', 'g2']
- (1, 226, 216, 137) ['beehive(l22,d-17)', 'g0', 'g1', 'g2', 'g3']
- (1, 228, 151, 95) ['block(l20,d-16)', 'g0', 'g1', 'g2', 'g3']
- (1, 228, 182, 109) ['beehive(l24,d-29)', 'g0', 'g1', 'g2']
- (1, 232, 96, 97) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3']
- (1, 232, 96, 100) ['block(l24,d-22)', 'g0', 'g1', 'g2']
- (1, 232, 96, 118) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3']
- (1, 232, 96, 119) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 232, 96, 126) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 232, 96, 129) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 232, 96, 131) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 232, 96, 134) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 232, 96, 139) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3']
- (1, 232, 96, 141) ['block(l24,d-22)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 234, 91, 166) ['beehive(l-22,d-47)', 'g0', 'g1', 'g2']
- (1, 234, 162, 98) ['boat(l20,d-2)', 'g0', 'g1', 'g2']
- (1, 234, 216, 137) ['beehive(l22,d-15)', 'g0', 'g1', 'g2', 'g3']
- (1, 236, 151, 95) ['block(l20,d-14)', 'g0', 'g1', 'g2', 'g3']
- (1, 236, 182, 109) ['beehive(l24,d-27)', 'g0', 'g1', 'g2']
- (1, 242, 91, 166) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (1, 242, 162, 98) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (1, 242, 216, 137) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (1, 244, 182, 109) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (1, 248, 96, 97) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (1, 248, 96, 100) ['block(l24,d-18)', 'g0', 'g1', 'g2']
- (1, 248, 96, 118) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (1, 248, 96, 119) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 248, 96, 126) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 248, 96, 129) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 248, 96, 131) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 248, 96, 134) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 248, 96, 139) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (1, 248, 96, 141) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (1, 250, 91, 166) ['beehive(l-22,d-43)', 'g0', 'g1', 'g2']
- (1, 250, 162, 98) ['boat(l20,d2)', 'g0', 'g1', 'g2']
- (1, 250, 216, 137) ['beehive(l22,d-11)', 'g0', 'g1', 'g2', 'g3']
- (1, 252, 151, 95) ['block(l20,d-10)', 'g0', 'g1', 'g2', 'g3']
- (1, 252, 182, 109) ['beehive(l24,d-23)', 'g0', 'g1', 'g2']
- (3, 91, 166) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 109) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 110) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 111) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 112) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 140) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 141) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 142) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 91, 166, 144) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 148) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 149) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 150) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 152) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 156) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 157) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 158) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 160) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 164) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 165) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 166) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 168) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 172) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 173) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 174) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 176) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 180) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 181) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 182) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 184) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 188) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 189) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 190) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 192) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 196) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 197) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 198) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 200) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 204) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 205) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 206) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 208) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 212) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 213) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 214) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 216) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 220) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 221) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 222) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 224) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 228) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 229) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 230) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 232) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 236) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 237) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 238) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 240) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 244) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 245) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 246) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 248) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 252) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2', 'g3']
- (3, 91, 166, 253) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 166, 254) ['beehive(l-22,d-45)', 'g0', 'g1', 'g2']
- (3, 91, 178, 189) ['beehive(l24,d-9)', 'g0', 'g1', 'g2']
- (3, 93, 107, 92) ['block(l20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 93, 122) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 143) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 170) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 172) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 173) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 203) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 204) ['block(l22,d6)', 'g0', 'g1', 'g2']
- (3, 93, 122, 227) ['block(l22,d6)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 177, 93) ['block(l-20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 93, 177, 100) ['block(l-20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 93, 177, 101) ['block(l-20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 177, 108) ['block(l-20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 93, 177, 117) ['block(l-20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 93, 177, 118) ['block(l-20,d20)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 93, 195, 94) ['block(l29,d9)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 93, 197, 225) ['beehive(l-27,d14)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 211, 134) ['beehive(l22,d9)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 211, 142) ['beehive(l22,d9)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 211, 145) ['beehive(l22,d9)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 217, 96) ['block(l24,d-2)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 225, 96) ['block(l24,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 93, 245, 147) ['block(l21,d9)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 94, 137, 157) ['beehive(l26,d-7)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 94, 137, 200) ['boat(l20,d2)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 94, 138, 94) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 94, 138, 105) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 94, 138, 114) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 115) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 116) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 117) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 119) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 94, 138, 127) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 128) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 129) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 130) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 135) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 136) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 94, 138, 137) ['block(l21,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 97, 93, 98) ['boat(l33,d-17)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 97, 109, 135) ['block(l22,d-18)', 'g0', 'g1', 'g2']
- (3, 97, 109, 159) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 97, 110, 116) ['beehive(l23,d-10)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 115, 90) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 97, 115, 96) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 115, 100) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 115, 101) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 115, 108) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 115, 111) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 245, 97) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (3, 97, 245, 100) ['block(l24,d-18)', 'g0', 'g1', 'g2']
- (3, 97, 245, 118) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (3, 97, 245, 119) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 245, 126) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 245, 129) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 245, 131) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 245, 134) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 97, 245, 139) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (3, 97, 245, 141) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 101, 161, 220) ['beehive(l-26,d17)', 'g0', 'g1', 'g2', 'g3']
- (3, 101, 190, 107) ['beehive(l-31,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 101, 190, 112) ['beehive(l-31,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (3, 104, 96, 115) ['block(l-32,d10)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 104, 107, 110) ['block(l25,d-25)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 104, 129, 210) ['block(l24,d10)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 105, 177, 105) ['beehive(l21,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 105, 180, 105) ['beehive(l21,d-8)', 'g0', 'g1', 'g2']
- (3, 105, 194, 144) ['beehive(l21,d18)', 'g0', 'g1', 'g2']
- (3, 105, 198, 145) ['block(l23,d13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 105, 199, 122) ['beehive(l-28,d-41)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 105, 227, 181) ['block(l28,d2)', 'g0', 'g1', 'g2', 'g3']
- (3, 105, 238, 143) ['block(l22,d-28)', 'g0', 'g1', 'g2', 'g3']
- (3, 105, 239, 142) ['block(l22,d-28)', 'g0', 'g1', 'g2', 'g3']
- (3, 108, 196, 109) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (3, 120, 122, 175) ['block(l-33,d-3)', 'g0', 'g1', 'g2', 'g3']
- (3, 128, 144, 152) ['block(l23,d-7)', 'g0', 'g1', 'g2', 'g3']
- (3, 156, 117, 144) ['block(l20,d-2)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 158, 92, 199) ['beehive(l24,d-3)', 'g0', 'g1', 'g2', 'g3']
- (3, 158, 155, 99) ['boat(l22,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 98) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 101) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 106) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 108) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 109) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 119) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 122) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 129) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 131) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 133) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 134) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 136) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 137) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 138) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 139) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 141) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 162, 98, 142) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 145) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 146) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 147) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 149) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 153) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 154) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 155) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 157) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 161) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 162) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 163) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 165) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 169) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 170) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 171) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 173) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 177) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 178) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 179) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 181) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 185) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 186) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 187) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 189) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 193) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 194) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 195) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 197) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 201) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 202) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 203) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 205) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 209) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 213) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 217) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 220) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 221) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 162, 98, 225) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 226) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 227) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 229) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 233) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 234) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 235) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 237) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 241) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 242) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 243) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 245) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 249) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 162, 98, 250) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 251) ['boat(l20,d0)', 'g0', 'g1', 'g2']
- (3, 162, 98, 253) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (3, 165, 113, 96) ['beehive(l43,d4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 165, 113, 111) ['beehive(l43,d4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 165, 162, 97) ['boat(l30,d14)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 166, 110, 126) ['beehive(l-37,d2)', 'g0', 'g1', 'g2', 'g3']
- (3, 170, 91, 145) ['boat(l20,d16)', 'g0', 'g1', 'g2', 'g3']
- (3, 181, 103, 94) ['block(l21,d-23)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 194, 108, 109) ['beehive(l22,d-1)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 195, 127, 107) ['block(l24,d-22)', 'g0', 'g1', 'g2']
- (3, 202, 175, 148) ['block(l26,d-6)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 202, 176, 108) ['block(l21,d7)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 205, 248, 174) ['block(l32,d10)', 'g0', 'g1', 'g2', 'g3']
- (3, 205, 252, 208) ['beehive(l20,d17)', 'g0', 'g1', 'g2']
- (3, 207, 170, 252) ['block(l21,d-15)', 'g0', 'g1', 'g2', 'g3']
- (3, 208, 125, 174) ['block(l32,d10)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 129, 208) ['beehive(l20,d17)', 'g0', 'g1', 'g2', 'g3']
- (3, 208, 146, 160) ['block(l22,d14)', 'g0', 'g1', 'g2', 'g3']
- (3, 208, 163, 110) ['boat(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 177, 101) ['block(l24,d-8)', 'g0', 'g1', 'g2']
- (3, 208, 177, 119) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 208, 177, 120) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 177, 127) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 177, 130) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 177, 132) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 177, 135) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 208, 177, 140) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 208, 177, 142) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 123, 174) ['block(l32,d10)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 127, 208) ['beehive(l20,d17)', 'g0', 'g1', 'g2', 'g3']
- (3, 210, 144, 160) ['block(l22,d14)', 'g0', 'g1', 'g2', 'g3']
- (3, 210, 161, 110) ['boat(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 175, 101) ['block(l24,d-8)', 'g0', 'g1', 'g2']
- (3, 210, 175, 119) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 210, 175, 120) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 175, 127) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 175, 130) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 175, 132) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 175, 135) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 210, 175, 140) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 210, 175, 142) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 122, 174) ['block(l32,d10)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 126, 208) ['beehive(l20,d17)', 'g0', 'g1', 'g2', 'g3']
- (3, 211, 143, 160) ['block(l22,d14)', 'g0', 'g1', 'g2', 'g3']
- (3, 211, 160, 110) ['boat(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 174, 101) ['block(l24,d-8)', 'g0', 'g1', 'g2']
- (3, 211, 174, 119) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 211, 174, 120) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 174, 127) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 174, 130) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 174, 132) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 174, 135) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 211, 174, 140) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3']
- (3, 211, 174, 142) ['block(l24,d-8)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 215, 94, 191) ['beehive(l20,d23)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 215, 94, 205) ['block(l22,d18)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 215, 98, 114) ['block(l20,d32)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 215, 99, 245) ['beehive(l26,d3)', 'g0', 'g1', 'g2']
- (3, 215, 211, 114) ['block(l-20,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 90, 114) ['block(l-20,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 92) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 93) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 94) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 99) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 100) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 101) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 103) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 104) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 111) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 216, 137, 112) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 116) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 117) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 118) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 119) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 120) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 124) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 125) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 126) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 127) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 128) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 132) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 133) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 134) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 135) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 136) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 140) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 141) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 142) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 143) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 144) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 148) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 149) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 150) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 151) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 152) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 156) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 157) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 158) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 159) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 160) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 164) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 165) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 166) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 167) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 168) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 172) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 173) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 174) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 175) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 176) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 180) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 181) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 182) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 183) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 184) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 188) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 189) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 190) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 191) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 192) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 196) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 197) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 198) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 199) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 200) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 204) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 205) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 206) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 207) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 208) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 212) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 213) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 214) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 215) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 216) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 220) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 221) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 222) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 223) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 224) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 228) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 229) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 230) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 231) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 232) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 236) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 237) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 238) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 239) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 240) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 244) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 245) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 246) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 247) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 137, 248) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 252) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 216, 137, 253) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 254) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 216, 137, 255) ['beehive(l22,d-13)', 'g0', 'g1', 'g2']
- (3, 216, 145, 158) ['beehive(l-24,d1)', 'g0', 'g1', 'g2']
- (3, 216, 145, 169) ['beehive(l-24,d1)', 'g0', 'g1', 'g2', 'g3']
- (3, 217, 95, 159) ['block(l24,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 219, 111, 156) ['beehive(l23,d-10)', 'g0', 'g1', 'g2']
- (3, 219, 111, 164) ['beehive(l23,d-10)', 'g0', 'g1', 'g2', 'g3']
- (3, 219, 131, 102) ['block(l21,d-9)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 219, 222, 107) ['block(l22,d16)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 219, 222, 127) ['block(l22,d10)', 'g0', 'g1', 'g2', 'g3']
- (3, 219, 222, 131) ['block(l21,d5)', 'g0', 'g1', 'g2', 'g3']
- (3, 219, 222, 153) ['beehive(l20,d17)', 'g0', 'g1', 'g2', 'g3']
- (3, 222, 136, 118) ['block(l22,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 225, 91, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 93, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 95, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 97, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 99, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 101, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 103, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 105, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 107, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 109, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 111, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 113, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 115, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 117, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 119, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 121, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 123, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 125, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 127, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 129, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 131, 134) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (3, 225, 137, 148) ['block(l37,d3)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 225, 157, 107) ['block(l21,d13)', 'g0', 'g1', 'g2', 'g3']
- (3, 225, 169, 107) ['beehive(l28,d11)', 'g0', 'g1', 'g2', 'g3']
- (3, 225, 180, 151) ['block(l26,d12)', 'g0', 'g1', 'g2']
- (3, 225, 181, 106) ['beehive(l21,d12)', 'g0', 'g1', 'g2']
- (3, 225, 191, 163) ['block(l20,d40)', 'g0', 'g1', 'g2', 'g3']
- (3, 225, 198, 115) ['block(l23,d5)', 'g0', 'g1', 'g2', 'g3']
- (3, 225, 229, 98) ['block(l21,d21)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 130, 142) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 230, 130, 143) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 230, 130, 144) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 230, 130, 145) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 230, 130, 146) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (3, 230, 130, 147) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 130, 148) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 130, 149) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 130, 161) ['block(l-24,d-4)', 'g0', 'g1', 'g2']
- (3, 230, 130, 163) ['block(l-24,d-4)', 'g0', 'g1', 'g2']
- (3, 230, 130, 173) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 130, 181) ['block(l-24,d-4)', 'g0', 'g1', 'g2']
- (3, 230, 130, 187) ['block(l-24,d-4)', 'g0', 'g1', 'g2']
- (3, 230, 130, 188) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 130, 189) ['block(l-24,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 224, 96) ['block(l24,d-26)', 'g0', 'g1', 'g2', 'g3']
- (3, 230, 245, 230) ['block(l20,d6)', 'g0', 'g1', 'g2', 'g3']
- (3, 231, 96, 157) ['beehive(l26,d-13)', 'g0', 'g1', 'g2', 'g3']
- (3, 231, 96, 200) ['boat(l20,d-4)', 'g0', 'g1', 'g2', 'g3']
- (3, 231, 97, 94) ['block(l21,d-19)', 'g0', 'g1', 'g2']
- (3, 231, 97, 105) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3']
- (3, 231, 97, 114) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 115) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 116) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 117) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 119) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3']
- (3, 231, 97, 127) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 128) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 129) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 130) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 135) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 136) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 231, 97, 137) ['block(l21,d-19)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (3, 232, 90, 171) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 91, 170) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 92, 169) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 93, 168) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 94, 167) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 95, 166) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 96, 165) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 97, 164) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 98, 163) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 99, 162) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 100, 161) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 101, 160) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 102, 159) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 103, 158) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 104, 157) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 105, 156) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 106, 155) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 107, 154) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 108, 153) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 109, 152) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 110, 151) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 111, 150) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 112, 149) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 113, 148) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 114, 147) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 115, 146) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 116, 145) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 117, 144) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 118, 143) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 119, 142) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 120, 141) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 121, 140) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 122, 139) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 123, 138) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 124, 137) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 125, 136) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 126, 135) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 127, 134) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 128, 133) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 129, 132) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 130, 131) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 131, 130) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 132, 129) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 133, 128) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 134, 127) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 135, 126) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 136, 125) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 137, 124) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 138, 123) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 139, 122) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 140, 121) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 141, 120) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 142, 119) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 143, 118) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 144, 117) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 145, 116) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 146, 115) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 147, 114) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 148, 113) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 149, 112) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 150, 111) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 151, 110) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 152, 109) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 153, 108) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 154, 107) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 155, 106) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 156, 105) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 157, 104) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 158, 103) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 159, 102) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 160, 101) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 161, 100) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 162, 99) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 163, 98) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 164, 97) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 165, 96) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 166, 95) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 167, 94) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 168, 93) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 169, 92) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 170, 91) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 232, 171, 90) ['beehive(l23,d8)', 'g0', 'g1', 'g2', 'g3']
- (3, 233, 191, 109) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (3, 238, 96, 97) ['block(l24,d-50)', 'g0', 'g1', 'g2']
- (3, 238, 96, 118) ['block(l24,d-50)', 'g0', 'g1', 'g2']
- (3, 238, 96, 119) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3']
- (3, 238, 96, 126) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3']
- (3, 238, 96, 129) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3']
- (3, 238, 96, 131) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3']
- (3, 238, 96, 134) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3']
- (3, 238, 96, 139) ['block(l24,d-50)', 'g0', 'g1', 'g2']
- (3, 238, 96, 141) ['block(l24,d-50)', 'g0', 'g1', 'g2', 'g3']
- (3, 254, 96, 97) ['block(l24,d-46)', 'g0', 'g1', 'g2']
- (3, 254, 96, 118) ['block(l24,d-46)', 'g0', 'g1', 'g2']
- (3, 254, 96, 119) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3']
- (3, 254, 96, 126) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3']
- (3, 254, 96, 129) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3']
- (3, 254, 96, 131) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3']
- (3, 254, 96, 134) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3']
- (3, 254, 96, 139) ['block(l24,d-46)', 'g0', 'g1', 'g2']
- (3, 254, 96, 141) ['block(l24,d-46)', 'g0', 'g1', 'g2', 'g3']
- (5, 90, 107, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 90, 107, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 90, 107, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 90, 107, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 91, 106, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 91, 106, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 91, 106, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 91, 106, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 92, 105, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 92, 105, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 92, 105, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 92, 105, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 93, 104, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 93, 104, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 93, 104, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 93, 104, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 94, 103, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 94, 103, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 94, 103, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 94, 103, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 95, 102, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 95, 102, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 95, 102, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 95, 102, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 96, 101, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 96, 101, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 96, 101, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 96, 101, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 97, 100, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 97, 100, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 97, 100, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 97, 100, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 98, 99, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 98, 99, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 98, 99, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 98, 99, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 99, 98, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 99, 98, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 99, 98, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 99, 98, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 100, 97, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 100, 97, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 100, 97, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 100, 97, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 101, 96, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 101, 96, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 101, 96, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 101, 96, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 102, 95, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 102, 95, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 102, 95, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 102, 95, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 103, 94, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 103, 94, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 103, 94, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 103, 94, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 104, 93, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 104, 93, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 104, 93, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 104, 93, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 105, 92, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 105, 92, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 105, 92, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 105, 92, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 106, 91, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 106, 91, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 106, 91, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 106, 91, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 107, 90, 134) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 107, 90, 138) ['beehive(l22,d-33)', 'g0', 'g1', 'g2']
- (5, 107, 90, 178) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 107, 90, 218) ['beehive(l22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (5, 132, 148, 98) ['boat(l20,d0)', 'g0', 'g1', 'g2', 'g3']
- (5, 132, 202, 137) ['beehive(l22,d-13)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 134, 154, 183) ['block(l28,d36)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 143, 131, 224) ['block(l28,d0)', 'g0', 'g1', 'g2', 'g3']
- (5, 143, 137, 134) ['block(l22,d30)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 143, 147, 142) ['boat(l-27,d11)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (5, 144, 165, 125) ['boat(l22,d2)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 145, 222, 92) ['block(l-29,d29)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 146, 103, 251) ['block(l22,d-24)', 'g0', 'g1', 'g2', 'g3']
- (5, 146, 214, 221) ['beehive(l26,d-25)', 'g0', 'g1', 'g2']
- (5, 146, 233, 122) ['beehive(l24,d-27)', 'g0', 'g1', 'g2']
- (5, 146, 236, 122) ['beehive(l24,d-27)', 'g0', 'g1', 'g2']
- (5, 146, 252, 160) ['block(l22,d-36)', 'g0', 'g1', 'g2']
- (5, 147, 180, 254) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 184, 250) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 188, 246) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 192, 242) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 196, 238) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 200, 234) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 204, 230) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 208, 226) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 212, 222) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 216, 218) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 220, 214) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 224, 210) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 228, 206) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 232, 202) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 236, 198) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 240, 194) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 244, 190) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 247, 202) ['beehive(l23,d0)', 'g0', 'g1', 'g2']
- (5, 147, 248, 186) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 147, 252, 182) ['block(l25,d-19)', 'g0', 'g1', 'g2']
- (5, 148, 96, 223) ['block(l24,d-18)', 'g0', 'g1', 'g2', 'g3']
- (5, 166, 141, 90) ['boat(l20,d-14)', 'g0', 'g1', 'g2', 'g3']
- (5, 168, 182, 99) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 182, 109, 90) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 92) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 96) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 97) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 98) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 100) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 108) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 112) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 182, 109, 115) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 182, 109, 116) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 182, 109, 120) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 121) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 122) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 124) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 128) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 129) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 130) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 132) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 136) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 137) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 138) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 140) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 144) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 145) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 146) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 148) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 152) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 153) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 154) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 156) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 160) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 161) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 162) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 164) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 168) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 169) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 170) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 172) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 176) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 177) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 178) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 180) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 184) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 185) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 186) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 188) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 192) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 193) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 194) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 196) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 200) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 201) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 202) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 204) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 208) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 209) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 210) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 212) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 216) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 217) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 218) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 220) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 224) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 225) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 226) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 228) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 232) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 233) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 234) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 236) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 240) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 241) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 242) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 244) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 248) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 109, 249) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 250) ['beehive(l24,d-25)', 'g0', 'g1', 'g2']
- (5, 182, 109, 252) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 151, 202) ['beehive(l24,d-25)', 'g0', 'g1', 'g2', 'g3']
- (5, 182, 151, 221) ['boat(l20,d-14)', 'g0', 'g1', 'g2', 'g3']
- (5, 185, 180, 115) ['block(l33,d-15)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (5, 196, 169, 115) ['block(l33,d-15)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 130, 115, 168) ['block(l22,d-4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 130, 220, 146) ['beehive(l20,d9)', 'g0', 'g1', 'g2', 'g3']
- (7, 130, 244, 173) ['block(l21,d-3)', 'g0', 'g1', 'g2']
- (7, 132, 237, 162) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 164) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 166) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 168) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 170) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 172) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 174) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 176) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 178) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 180) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 182) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 184) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 186) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 188) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 190) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 192) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 194) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 196) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 198) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 200) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 202) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 204) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 206) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 208) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 210) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 212) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 214) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 216) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 218) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 220) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 222) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 224) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 232) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 250) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 132, 237, 252) ['block(l23,d21)', 'g0', 'g1', 'g2', 'g3']
- (7, 136, 156, 118) ['block(l29,d1)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 136, 187, 207) ['beehive(l20,d23)', 'g0', 'g1', 'g2']
- (7, 139, 111, 163) ['block(l24,d22)', 'g0', 'g1', 'g2', 'g3']
- (7, 140, 95, 90) ['block(l21,d7)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (7, 140, 95, 101) ['block(l21,d7)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 140, 95, 107) ['block(l21,d7)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5', 'g6']
- (7, 144, 231, 151) ['beehive(l-20,d-5)', 'g0', 'g1', 'g2']
- (7, 144, 239, 143) ['beehive(l-20,d-5)', 'g0', 'g1', 'g2']
- (7, 144, 247, 135) ['beehive(l-20,d-5)', 'g0', 'g1', 'g2']
- (7, 144, 255, 127) ['beehive(l-20,d-5)', 'g0', 'g1', 'g2']
- (7, 146, 106, 174) ['block(l25,d-3)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 148, 105, 254) ['beehive(l26,d-9)', 'g0', 'g1', 'g2']
- (7, 148, 204, 100) ['block(l-26,d20)', 'g0', 'g1', 'g2', 'g3']
- (7, 148, 210, 143) ['block(l-22,d28)', 'g0', 'g1', 'g2']
- (7, 148, 214, 100) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 148, 214, 101) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 148, 214, 102) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 148, 214, 103) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 148, 214, 104) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 148, 214, 105) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 148, 214, 106) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 148, 214, 108) ['beehive(l-21,d16)', 'g0', 'g1', 'g2']
- (7, 148, 214, 117) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3']
- (7, 148, 214, 164) ['beehive(l-21,d16)', 'g0', 'g1', 'g2', 'g3']
- (7, 152, 130, 96) ['block(l20,d4)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 152, 130, 98) ['block(l20,d4)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 152, 130, 105) ['block(l20,d4)', 'g0', 'g1', 'g2', 'g3']
- (7, 152, 140, 144) ['block(l-24,d14)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 156, 100, 146) ['boat(l-29,d13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 156, 216, 137) ['beehive(l22,d-3)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 158, 139, 113) ['block(l29,d5)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 158, 151, 95) ['block(l20,d-2)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 158, 182, 109) ['beehive(l24,d-15)', 'g0', 'g1', 'g2', 'g3']
- (7, 160, 136, 146) ['beehive(l22,d13)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 160, 148, 214) ['beehive(l-21,d26)', 'g0', 'g1', 'g2', 'g3']
- (7, 164, 91, 166) ['beehive(l-22,d-33)', 'g0', 'g1', 'g2', 'g3']
- (7, 164, 215, 188) ['beehive(l22,d15)', 'g0', 'g1', 'g2']
- (7, 166, 151, 95) ['block(l20,d0)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 166, 233, 134) ['block(l32,d34)', 'g0', 'g1', 'g2']
- (7, 172, 157, 116) ['block(l-22,d16)', 'g0', 'g1', 'g2', 'g3']
- (7, 174, 142, 148) ['beehive(l20,d11)', 'g0', 'g1', 'g2', 'g3']
- (7, 174, 150, 227) ['beehive(l-29,d2)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 174, 150, 242) ['beehive(l-29,d2)', 'g0', 'g1', 'g2', 'g3']
- (7, 176, 139, 129) ['block(l26,d-2)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 182, 90, 104) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 91, 103) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 92, 102) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 93, 101) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 94, 100) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 95, 99) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 96, 98) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 97, 97) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 98, 96) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 99, 95) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 100, 94) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 101, 93) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 102, 92) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 103, 91) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 182, 104, 90) ['beehive(l24,d19)', 'g0', 'g1', 'g2', 'g3']
- (7, 186, 101, 157) ['block(l26,d-2)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 188, 213, 201) ['beehive(l-22,d25)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 190, 142, 148) ['beehive(l20,d15)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 194, 96, 114) ['block(l24,d0)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 194, 104, 239) ['beehive(l20,d15)', 'g0', 'g1', 'g2']
- (7, 196, 96, 144) ['block(l21,d13)', 'g0', 'g1', 'g2']
- (7, 196, 147, 229) ['block(l20,d36)', 'g0', 'g1', 'g2', 'g3']
- (7, 196, 203, 107) ['block(l21,d31)', 'g0', 'g1', 'g2', 'g3']
- (7, 196, 203, 109) ['block(l21,d31)', 'g0', 'g1', 'g2', 'g3']
- (7, 196, 203, 111) ['block(l21,d31)', 'g0', 'g1', 'g2', 'g3']
- (7, 200, 140, 226) ['boat(l-22,d-2)', 'g0', 'g1', 'g2', 'g3']
- (7, 204, 230, 130) ['block(l-24,d18)', 'g0', 'g1', 'g2', 'g3']
- (7, 210, 96, 102) ['block(l24,d4)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 210, 108, 134) ['block(l21,d21)', 'g0', 'g1', 'g2', 'g3', 'g4', 'g5']
- (7, 218, 96, 102) ['block(l24,d6)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 218, 96, 132) ['block(l24,d6)', 'g0', 'g1', 'g2']
- (7, 234, 96, 102) ['block(l24,d10)', 'g0', 'g1', 'g2', 'g3', 'g4']
- (7, 252, 93, 173) ['block(l-37,d35)', 'g0', 'g1', 'g2', 'g3']
