# Search scripts to optimize the Snarkmaker recipe

The [Snarkmaker](https://conwaylife.com/wiki/Snarkmaker) is a recipe
which uses ~2400 gliders on a single lange track to construct a
snark on the lane to reflect the gliders.

The original Snarkmaker recipe is compiled from a library of composable
recipes which start with an elbow block in a known location, have some
effect, like creating an offset block, or emitting a glider on a certain
lane, then return to a block. This library makes it easy to assemble any
recipe, but is not necessarily the most efficient for a specific recipe.

This search program searches for an optimized recipe which builds up the
snark step by step, not returning to any particular configuration
inbetween. For this we need to have a score for how close we are to
guide the search.

## Finding an offset elbow

![Diagram showing offset block schematic](images/diagram1.svg)

The first step of the search is to find an offset elbow. This is
a block or equivalent still life that is far away on the lane axis.
This will become the starting elbow after the snark is complete.

- Gliders come from the SE on lane 0, hitting the starting elbow.
- Offset/separation: The offset block should be far away from the rest of the
pattern to avoid interfering with the rest of construction, and to give us
more options for follow-up recipes once the snark is complete.
- Elbow depth/max depth: increasing the elbow depth and decreasing the max
  depth helps when chaining the snarkmaker recipe multiple times. If the
  recipe extends far back along the depth axis during construction, it will
  interfere with the previous snark.
- Elbow ash cloud: all things equal, a smaller ash cloud is more manageable
  and increases our chances that we can clean up at the end.

## Constructing the snark

![Diagram showing snark building schematic](images/diagram2.svg)

The original Snarkmaker recipe worked using a zero degree elbow.
Using the library of composable recipes, an average of 25 gliders on lane 0
with specific spacings was able to emit one slow glider on a specific parallel
lane and return to a zero degree elbow. Combining these implemented the known
90 glider single-sided slow salvo for a snark.

Today, we know a 73 glider recipe for a snark, and we can search for recipes that
go directly from one arbitrary ash cloud to another.

The diagram shows the criteria we will use to guide the search.

- Offset elbow: The offset elbow fixes one or two locations for the snark --
  the output gliders need to hit the elbow in the right location.
- Max depth: as before, decreasing the max depth makes it easier to chain
  our new snarkmaker recipe.
- Zero-degree elbow ash cloud: as before, a smaller ash cloud is more manageable
and increases our changes that we can clean up at the end.
- Separation: The zero-degree elbow ash cloud might overlap the in-progress
  recipe, but that runs the risk of some ash hiding behind the recipe in a way
  that's hard to clean up. Some separation between the zones helps.
  However, a smaller separation increases the chances we find a lucky reaction
  which does the work of multiple slow gliders. So, the separation should be
  not too big either.
- In-progress recipe: We have a 73 glider slow-salvo recipe which starts with a
  block, so if the in-progress recipe is a match for one of the intermediate
  stages, we know how many slow gliders are needed to finish construction. We can
  also consider partial matches weighted by the rarity of the missing components.
  
  For example, here are the first few steps of the recipe:
  ![Diagram showing the first 5 gliders of the slow salvo snark recipe](images/snark-first-few-steps.png)

  However, the 73 glider recipe is actually a whole family of recipes -- at many
  points, we have options for which glider to send next.
  Here's a sample of the options found by trying the same set of gliders
  in different orders. The first six gliders are fixed, after that it quickly
  grows into many possibilities. There are often separate areas of the constellation
  which we can make progress on independently. This gives our search more freedom
  to make progress at any given step.
  ![Diagram showing a stamp collection of intermediate stages of possible snark recipe orderings](images/snark-recipe-options.png)

  There are some precursors that are quite simple, such as this
  constellation of 2 traffic lights and a block. It normally takes 11 slow
  gliders to turn a block into this pattern, but it's conceivable that we
  could find this directly in our ash and skip ahead several stages.

  ![alt text](images/snark-simple-precursor.png)

  When we consider the "in-progress recipe" and "zero degree elbow ash cloud",
  it is relative to one of these intermediate precursors. Ash components which match
  the intermediate stages are considered "in-progress recipe", and others are
  considered part of the "zero degree elbow ash cloud".

  We combine the scores for each intermediate recipe weighted by the distance
  from the final step to get the final score.
