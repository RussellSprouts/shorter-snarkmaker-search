from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
import sys
import argparse
import math
import pathlib

from speedometer import Speedometer
from font import write_text
from lifetree import lt
from optimized_stream_simulation import optimized_stream_simulation
from recipe_intermediates import recipe_intermediates
from db import (
    ProcessingDatabase,
    StreamJob,
    StreamJobResult,
    StartingPoint,
    Recipe,
    StreamResult,
)
from gliders import (
    flip_pattern_as_if_other_pi_block,
    mk_glider,
    PI_BLOCKS,
    offset_based_on_glider,
)
from component_search import ComponentSearch
from probability import total_probability, NEGATIVE_INFINITY
from life_history import write_life_history
from arg_parser import range_str_to_list
from multiprocess_search import MultiprocessSearch

halo = lt.pattern("3o$3o$3o!")

before_hit_digests_seen = set()

# Possible offset elbows, ignoring glider color.
offset_elbows = set(
    lt.pattern(rle).digest()
    for rle in [
        "oo$oo",  # block
        "boo$obbo$boo",  # beehive horizontal
        "bo$obo$obo$bo",  # beehive vertical
        "2o$obo$b2o!",  # ship nw<->se
        "2o$obo$bo!",  # boat nw
        "bo$obo$b2o!",  # boat se
        "b2o$o2bo$o2bo$b2o!",  # pond
    ]
)


def mk_snark_offset_target_options(db):
    """When there's an offset target, we need to shift the
    depth of the snark to line up with the target. This depends
    on the glider color -- depending on the depth, we might not
    be able to line up the offset target correctly. Creates a
    lookup table for how to shift the snark intermediates to
    line up with a particular block at a particular depth."""
    ne_glider = lt.pattern("3o$bbo$bo!")
    offset_elbow_patterns = [
        offset_based_on_glider(lt.pattern(rle), ne_glider)
        for rle in [
            # Patterns showing pi-producing interactions with a NE glider and offset still life
            # See offset_elbows.rle
            "5b2o$3o2b2o$2bo$bo!",  # block (option 1)
            "b2o$b2o3$3o$2bo$bo!",  # block (option 2)
            "b2o$o2bo$o2bo$b2o3$3o$2bo$bo!",  # pond (option 1)
            "6b2o$5bo2bo$3o2bo2bo$2bo3b2o$bo!",  # pond (option 2)
            "bo$obo$b2o3$3o$2bo$bo!",  # boat (facing SE)
            "5b2o$3o2bobo$2bo3bo$bo!",  # boat (facing NW)
            "5b2o$3o2bobo$2bo3b2o$bo!",  # ship (option 1)
            "b2o$bobo$2b2o3$b3o$3bo$2bo!",  # ship (option 2)
            "6bo$5bobo$3o2bobo$2bo3bo$bo!",  # beehive (vertical)
            "b2o$o2bo$b2o3$3o$2bo$bo!",  # beehive (horizontal)
        ]
    ]

    glider_depth = sum(ne_glider.getrect())

    for recipe in db.recipe_intermediates.values():
        if len(recipe.remaining) == 0:
            snark_final = recipe
            break

    # find the depth of the glider through the snark
    glider_through_snark = snark_final.pattern + mk_glider(0, 128)
    glider_through_snark = glider_through_snark[1024]
    for i in range(0, 4):
        m = glider_through_snark.match(ne_glider, halo=halo)
        if m.population:
            break
        glider_through_snark = glider_through_snark[1]
    else:
        raise Exception("NE glider not found -- is the snark recipe correct?")

    reflected_glider = m.convolve(ne_glider)
    reflected_glider_depth = sum(reflected_glider.getrect())

    offsets = defaultdict(set)
    for offset_target in offset_elbow_patterns:
        offset_depth = sum(offset_target.getrect())
        d = reflected_glider_depth - glider_depth + offset_depth
        offsets[offset_target.digest()].add(d)

    return offsets


def snark_offset_for_elbow_block(offsets, input_pattern):
    """Returns the offset to use for x and y to line up a snark with
    the input_pattern to have a pi explosion. Returns None if the input
    pattern is
    """

    digest = input_pattern.digest()
    if digest not in offsets:
        return None

    input_pattern_depth = sum(input_pattern.getrect())
    options = offsets[digest]
    valid_options = [o for o in options if (input_pattern_depth - o) % 2 == 0]
    if not valid_options:
        # Object is on the wrong color -- can't hit it with
        # a glider reflected off of lane 0.
        return None

    offset = valid_options[0]
    return (input_pattern_depth - offset) // 2


@dataclass
class OptimizeArgs:
    starting_points: Dict[int, StartingPoint]
    recipe_intermediates: Dict[int, Recipe]
    component_search: ComponentSearch
    max_gens: int
    gen_options: List[int]
    min_offset_block_lane: int
    snark_offsets: Dict[int, Set[int]]


def abs_lane(x):
    """The absolute value of the lane"""
    if x < 0:
        return -x + 1
    return x


def score_pattern(
    job: StreamJob,
    follow_up: int,
    before_hit_digest: int,
    end_pattern,
    shared_args: OptimizeArgs,
    recursed=False,
):
    lanes = []
    for c in end_pattern.components():
        (x, y, w, h) = c.getrect()
        is_pi_equivalent = c.digest() in offset_elbows
        lanes.append(
            (
                max(
                    x - y,
                    (x + w) - (y + h),
                    key=abs_lane,
                ),
                is_pi_equivalent,
                c,
            )
        )

    if len(lanes) < 2:
        # empty pattern or lonely block
        return None

    furthest_lane, is_pi_equivalent, elbow_component = lanes.pop()
    snark_offset = snark_offset_for_elbow_block(
        shared_args.snark_offsets, elbow_component
    )
    if (
        not is_pi_equivalent
        or abs_lane(furthest_lane) < shared_args.min_offset_block_lane
        or snark_offset is None
    ):
        # the object is not correct or too close to lane 0.
        return None

    if furthest_lane < 0 and not recursed:
        # flip the pattern to put the object on the NE side instead of SW.
        return score_pattern(
            flip_pattern_as_if_other_pi_block(end_pattern), shared_args, True
        )

    # max depth of all components including the offset block
    max_depth = max(job.max_depth, max(depths.value()))
    (end_pattern_x, end_pattern_y, _, _) = end_pattern.getrect()

    components = set(
        shared_args.component_search.pattern_cache.id(c) for _, _, c in lanes
    )
    max_depth = max(job.max_depth, max(map(lambda c: c.depth, components)))

    overlapping_recipes = shared_args.component_search.overlapping_recipes(components)
    best_full_intermediate_match: Optional[Recipe] = None
    best_partial_intermediate_match: Optional[Recipe] = None
    best_partial_prob = NEGATIVE_INFINITY
    full_elbow_intermediate_depth_separation = 0
    full_elbow_intermediate_overlapping_population = 0
    partial_elbow_intermediate_depth_separation = 0
    partial_elbow_intermediate_overlapping_population = 0
    for recipe in overlapping_recipes:
        recipe_components = shared_args.component_search.recipe_components(recipe)
        missing = recipe_components - components
        elbow = components - recipe_components
        partial_match = components - elbow
        if not missing:
            # full match!
            if not best_full_intermediate_match or len(recipe.remaining) < len(
                best_full_intermediate_match.remaining
            ):
                best_full_intermediate_match = recipe
                elbow_min_depth = min(elbow, key=lambda x: x.depth)
                partial_match_max_depth = max(partial_match, key=lambda x: x.depth)
                full_elbow_intermediate_depth_separation = (
                    elbow_min_depth - partial_match_max_depth
                )
                full_elbow_intermediate_overlapping_population = sum(
                    [
                        c.pattern.population
                        for c in elbow
                        if elbow.depth <= partial_match_max_depth
                    ]
                )
        else:
            # partial match!
            # find probability of finding rest of match
            p = total_probability(missing)
            if p == NEGATIVE_INFINITY:
                continue
            p -= len(
                recipe.remaining
            )  # a recipe further along should count for more TODO tune the factor
            if p > best_partial_prob:
                best_partial_prob = p
                best_partial_intermediate_match = recipe

                elbow_min_depth = min(elbow, key=lambda x: x.depth)
                partial_match_max_depth = max(partial_match, key=lambda x: x.depth)
                partial_elbow_intermediate_depth_separation = (
                    elbow_min_depth - partial_match_max_depth
                )
                partial_elbow_intermediate_overlapping_population = sum(
                    [
                        c.pattern.population
                        for c in elbow
                        if elbow.depth <= partial_match_max_depth
                    ]
                )

    return StreamResult(
        follow_up=follow_up,
        digest=end_pattern.digest(),
        before_hit_digest=before_hit_digest,
        x=end_pattern_x,
        y=end_pattern_y,
        offset_block_lane=furthest_lane,
        lane_width=abs_lane(lanes[-1]),  # next highest lane
        max_depth=max_depth,
        population=end_pattern.population,
        full_intermediate=(
            best_full_intermediate_match.id if best_full_intermediate_match else None
        ),
        full_intermediate_depth_separation=full_elbow_intermediate_depth_separation,
        full_intermediate_overlapping_population=full_elbow_intermediate_overlapping_population,
        partial_intermediate=(
            best_partial_intermediate_match.id
            if best_partial_intermediate_match
            else None
        ),
        partial_intermediate_log_prob=best_partial_prob,
        partial_intermediate_depth_separation=partial_elbow_intermediate_depth_separation,
        partial_intermediate_overlapping_population=partial_elbow_intermediate_overlapping_population,
    )


def combine_score(
    a: Optional[StreamResult], b: Optional[StreamResult], shared_args: OptimizeArgs
) -> StreamResult:
    if not b:
        return a
    if not a:
        return b

    full_a = (
        shared_args.recipe_intermediates[a.full_intermediate]
        if a.full_intermediate in shared_args.recipe_intermediates
        else None
    )
    full_b = (
        shared_args.recipe_intermediates[b.full_intermediate]
        if b.full_intermediate in shared_args.recipe_intermediates
        else None
    )

    full_a_remaining = len(full_a.remaining) if full_a else 10000
    full_b_remaining = len(full_b.remaining) if full_b else 10000

    a_better = full_a_remaining < full_b_remaining

    a_partial_better = a.partial_intermediate_log_prob > b.partial_intermediate_log_prob

    return StreamResult(
        follow_up=a.follow_up,
        digest=a.digest,
        before_hit_digest=a.before_hit_digest,
        x=a.x,
        y=a.y,
        offset_block_lane=a.offset_block_lane,
        lane_width=a.lane_width,
        max_depth=a.max_depth,
        population=a.population,
        full_intermediate=a.full_intermediate if a_better else b.full_intermediate,
        full_intermediate_depth_separation=(
            a.full_intermediate_depth_separation
            if a_better
            else b.full_intermediate_depth_separation
        ),
        full_intermediate_overlapping_population=(
            a.full_intermediate_overlapping_population
            if a_better
            else b.full_intermediate_overlapping_population
        ),
        partial_intermediate=(
            a.partial_intermediate if a_partial_better else b.partial_intermediate
        ),
        partial_intermediate_log_prob=(
            a.partial_intermediate_log_prob
            if a_partial_better
            else b.partial_intermediate_log_prob
        ),
        partial_intermediate_depth_separation=(
            a.partial_intermediate_depth_separation
            if a_partial_better
            else b.partial_intermediate_depth_separation
        ),
        partial_intermediate_overlapping_population=(
            a.partial_intermediate_overlapping_population
            if a_partial_better
            else b.partial_intermediate_overlapping_population
        ),
    )


def find_p2_output(job: StreamJob, queue, shared_args: OptimizeArgs):
    print("Finding p2 output")
    starting_points = shared_args.starting_points
    max_gens = shared_args.max_gens
    gen_options = shared_args.gen_options

    starting_point = starting_points[job.starting_point]
    result = StreamJobResult(
        starting_point=job.starting_point, stream=job.stream, valid_children=[]
    )

    initial_added_gens = sum(job.stream)
    for next_possibility in gen_options:
        if next_possibility > job.follow_up_gen_limit:
            break
        stream = starting_point.stream + job.stream + bytes([next_possibility])
        added_gens = initial_added_gens + next_possibility

        before_hit = optimized_stream_simulation(stream)
        before_hit_digest = before_hit.digest()
        if before_hit_digest in before_hit_digests_seen:
            # we've reached a state we've seen before with
            # a shorter glider sequence. No need to explore further.
            break

        before_hit_digests_seen.add(before_hit_digest)

        just_after_hit = before_hit[20]
        just_after_hit1 = just_after_hit[1]
        just_after_hit2 = just_after_hit1[1]
        end_pattern = just_after_hit2[512 - 22]
        end_pattern1 = end_pattern[1]
        end_pattern2 = end_pattern1[1]

        if end_pattern == end_pattern1:
            score = score_pattern(
                job=job,
                follow_up=next_possibility,
                before_hit_digest=before_hit_digest,
                end_pattern=end_pattern,
                shared_args=shared_args,
                recursed=False,
            )
            if score:
                result.valid_children.append(score)
        elif end_pattern == end_pattern2:
            score1 = score_pattern(
                job=job,
                follow_up=next_possibility,
                before_hit_digest=before_hit_digest,
                end_pattern=end_pattern,
                shared_args=shared_args,
                recursed=False,
            )
            score2 = score_pattern(
                job=job,
                follow_up=next_possibility,
                before_hit_digest=before_hit_digest,
                end_pattern=end_pattern,
                shared_args=shared_args,
                recursed=False,
            )
            score = combine_score(score1, score2, shared_args)
            if score:
                result.valid_children.append(score)

        if added_gens <= max_gens - gen_options[0]:
            if just_after_hit == just_after_hit1:
                # the pattern very quickly stabilized to p1,
                # only queue the fastest possible next glider
                queue(
                    StreamJob(
                        id=None,
                        cost=added_gens,
                        starting_point=job.starting_point,
                        stream=job.stream + bytes([next_possibility]),
                        follow_up_gen_limit=gen_options[0],
                        max_depth=job.max_depth,
                    )
                )
            elif just_after_hit == just_after_hit2:
                queue(
                    StreamJob(
                        id=None,
                        cost=added_gens,
                        starting_point=job.starting_point,
                        stream=job.stream + bytes([next_possibility]),
                        # todo this assumes that the first two gen_options
                        # are a mix of odd/even
                        follow_up_gen_limit=gen_options[1],
                        max_depth=job.max_depth,
                    )
                )
            else:
                queue(
                    StreamJob(
                        id=None,
                        cost=added_gens,
                        starting_point=job.starting_point,
                        stream=job.stream + bytes([next_possibility]),
                        follow_up_gen_limit=min(255, max_gens - added_gens),
                        max_depth=job.max_depth,
                    )
                )

    return result


def optimize(
    recipe_intermediates_db: pathlib.Path,
    output_db: pathlib.Path,
    max_gens: int,
    gen_options: str,
    min_offset_block_lane: int,
):
    output_db: ProcessingDatabase = ProcessingDatabase(output_db)
    if not output_db.recipe_intermediates:
        print(f"Transferring recipe_intermediates from {recipe_intermediates_db}", file=sys.stderr)
        # Copy the recipe intermediates if the output doesn't have any
        recipe_intermediates_db: ProcessingDatabase = ProcessingDatabase(recipe_intermediates_db)
        new_intermediates = recipe_intermediates_db.recipe_intermediates
        output_db.add_recipe_intermediates(list(new_intermediates.values()))
        output_db.reload_recipe_intermediates()
        output_db.commit()
    else:
        print(f"Recipe intermediates already present in output DB, assuming already transferred.", file=sys.stderr)

    snark_offsets = mk_snark_offset_target_options(output_db)

    shared_args = OptimizeArgs(
        starting_points=output_db.starting_points,
        recipe_intermediates=output_db.recipe_intermediates,
        component_search=None,
        max_gens=max_gens,
        gen_options=range_str_to_list(gen_options),
        min_offset_block_lane=min_offset_block_lane,
        snark_offsets=snark_offsets
    )
    queue_stats = output_db.queue_stats()
    print(f"Queue contains {sum(queue_stats.values())} job(s). Costs:", queue_stats)

    already_seen_results = set()
    speedo = Speedometer(interval_s=10)
    with MultiprocessSearch(fn=find_p2_output, shared_args=shared_args, db=output_db, n_processes=1) as search:
        for (job, result, new_jobs) in search:
            print(job, result, new_jobs)
            if isinstance(result, Exception):
                raise Exception("error in child process") from result
            if speedo.tick(1):
                print(
                    f"{speedo.get_current_speed_and_reset():.2f}/s, {speedo.overall_speed():.2f} avg/s, {speedo.n_finished} done, {search.pending_tracker.n_pending} queued, {search.pending_tracker.min_cost_pending()} gens ({search.pending_tracker.pending_items.get(search.pending_tracker.min_cost_pending(), [float('inf'),0])[1]} remaining)",
                    file=sys.stderr,
                )
            for c in result.valid_children:
                key = (c.before_hit_digest, c.x, c.y)
                if key in already_seen_results:
                    # Skip exploring patterns we've already
                    # seen, based on the before_hit_digest
                    continue
                already_seen_results.add(key)
                print(result)

            search.queue(new_jobs)

def search():
    speedo = Speedometer(interval_s=10)

    already_seen_results = set()

    for (
        stream_job,
        stream_result,
        new_jobs,
        queue,
        pending_tracker,
        local_queue,
    ) in recursive_priority_imap_unordered(
        find_p2_output, starting_jobs, n_processes=20
    ):
        if isinstance(stream_result, Exception):
            raise ChildProcessError("error in child process") from stream_result
        if speedo.tick(len(stream_job.next_possibilities)):
            print(
                f"{speedo.get_current_speed_and_reset():.2f}/s, {speedo.overall_speed():.2f} avg/s, {speedo.n_finished} done, {pending_tracker.n_pending}Q/{len(local_queue)}L queued, {pending_tracker.min_cost_pending()} gens ({pending_tracker.pending_items.get(pending_tracker.min_cost_pending(), [float('inf'),0])[1]} remaining)",
                file=sys.stderr,
            )

        valid_new_streams = set()
        for c in stream_result.valid_children:
            key = (c.before_hit_digest, c.x, c.y)
            if key in already_seen_results:
                # Skip exploring patterns we've already
                # seen, based on the before_hit_digest
                continue
            already_seen_results.add(key)
            new_stream = stream_job.stream + bytes((c.next_possibility,))
            valid_new_streams.add(new_stream)
            score = (
                c.max_lane
                * (abs(c.max_lane) - abs(c.next_highest_lane)) ** 2
                / math.sqrt(c.population)
            )
            print(
                score,
                c.digest,
                c.max_lane,
                c.next_highest_lane,
                c.population,
                stream_job.starting_block,
                tuple(new_stream),
                flush=True,
            )

        valid_new_jobs = [
            (cost, job) for cost, job in new_jobs if job.stream in valid_new_streams
        ]
        queue(valid_new_jobs)

    print(
        f"Finished with {speedo.overall_speed():.2f} jobs/s, {speedo.n_finished} total",
        file=sys.stderr,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="snark.py", description="Searches for an optimized snarkmaker recipe."
    )
    subcommand = parser.add_subparsers(dest="command", required=True)

    parser_recipe_intermediates = subcommand.add_parser(
        "recipe-intermediates",
        description="Processes the input recipe to find intermediate stages",
    )
    parser_recipe_intermediates.add_argument(
        "-i",
        "--input-recipe",
        help="Input rle/mc file for the recipe. The slow salvo gliders should travel NW and hit a block. There should be one extra glider at the end that defines lane 0.",
        type=pathlib.Path,
        required=True,
    )
    parser_recipe_intermediates.add_argument(
        "-o",
        "--output-db",
        help="Output sqlite database file.",
        type=pathlib.Path,
        required=True,
    )
    parser_recipe_intermediates.add_argument(
        "-d",
        "--search-depth",
        help="How many gliders deep to search from the initial block. -1 for the entire recipe.",
        default=-1,
        type=int,
    )
    parser_recipe_intermediates.add_argument(
        "-w",
        "--search-width",
        help="The search tries to move a slice of future gliders to the present. Check slices of length 1 to search_width.",
        default=3,
        type=int,
    )
    parser_recipe_intermediates.add_argument(
        "-n",
        "--max-pool",
        type=int,
        default=2048,
        help="Maximum number of recipes to keep in the pool at each depth.",
    )

    parser_optimize = subcommand.add_parser(
        "optimize", description="Optimizes the recipe."
    )
    parser_optimize.add_argument(
        "-r",
        "--recipe-intermediates-db",
        help="Database file containing output from recipe-intermediates",
        type=pathlib.Path,
        required=True,
    )
    parser_optimize.add_argument(
        "-o",
        "--output-db",
        help="Output sqlite database file.",
        type=pathlib.Path,
        required=True,
    )
    parser_optimize.add_argument(
        "-n",
        "--max-gens",
        type=int,
        default=255,
        help="Max number of generations to search",
    )
    parser_optimize.add_argument(
        "-g",
        "--gen-options",
        type=str,
        default="90-255",
        help='Options for spacing of gliders in a stream. E.g. "74,75,78-255". Defaults to "90-255". Maximum 255.',
    )
    parser_optimize.add_argument(
        "-l",
        "--min-offset-block-lane",
        type=int,
        default=80,
        help="Minimum offset for the offset block. (The block that will become the new elbow after the snark is created).",
    )
    args = parser.parse_args()

    match args.command:
        case "recipe-intermediates":
            recipe_intermediates(
                input_recipe=args.input_recipe,
                output_db=args.output_db,
                search_depth=args.search_depth,
                search_width=args.search_width,
                max_pool=args.max_pool,
            )
        case "optimize":
            optimize(
                recipe_intermediates_db=args.recipe_intermediates_db,
                output_db=args.output_db,
                max_gens=args.max_gens,
                gen_options=args.gen_options,
                min_offset_block_lane=args.min_offset_block_lane,
            )
