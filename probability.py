import math

from lifetree import lt

# https://conwaylife.com/wiki/Most_common_objects_on_Catagolue
# Very simple heuristic to see how unlikely a constellation
# of objects is. Use log probabilities so they can be summed.
probabilities = {
    lt.pattern("2o$2o").octodigest(): math.log(1 / 3.24),  # block
    lt.pattern("3o").octodigest(): math.log(1 / 3.49),  # blinker
    lt.pattern("boo$obbo$boo").octodigest(): math.log(1 / 6.11),  # beehive
    lt.pattern("b2o$o2bo$bobo$2bo!").octodigest(): math.log(1 / 20.7),  # loaf
    lt.pattern("bo$obo$2o!").octodigest(): math.log(1 / 22.4),  # boat
    lt.pattern("b2o$obo$2o!").octodigest(): math.log(1 / 32.5),  # ship
    lt.pattern("bo$obo$bo!").octodigest(): math.log(1 / 103),  # tub
    lt.pattern("b2o$o2bo$o2bo$b2o!").octodigest(): math.log(1 / 106),  # pond
    lt.pattern("2o$obo$2bo$2b2o!").octodigest(): math.log(1 / 6407),  # eater 1
}


def get_pattern_frequency(pattern: PatternRef):
    return probabilities.get(pattern.octodigest, float("-inf"))

def relative_probability(pattern):
    """
    Calculate a score for how unlikely a constellation
    of objects is. A log probability.
    """
    prob = 1
    for c in pattern.components():
        digest = c.octodigest()
        c_prob = probabilities.get(digest, -10000000)
        prob += c_prob
    return prob