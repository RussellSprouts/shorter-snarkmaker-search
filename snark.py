import signal

# ignore Ctrl+C until later, so that subprocesses ignore Ctrl+C.
# lifelib uses a subprocess.
signal.signal(signal.SIGINT, signal.SIG_IGN)

from collections import defaultdict
from dataclasses import dataclass
from typing import List, Dict, Optional, Set
import sys
import argparse
import math
import pathlib
import traceback

from speedometer import Speedometer
from font import write_text
from lifetree import lt
from optimized_stream_simulation import optimized_stream_simulation
from recipe_intermediates import RecipeGraph, recipe_intermediates
from db import (
    ProcessingDatabase,
    SavedResult,
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
    reconstruct,
    single_channel_stream,
)
from component_search import ComponentSearch
from probability import total_probability, NEGATIVE_INFINITY
from life_history import write_life_history
from arg_parser import range_str_to_list
from multiprocess_search import MultiprocessSearch
from components import pattern_components

def interrupt_handler(_a, _b):
    print("Gracefully exiting...")
    sys.exit(1)


signal.signal(signal.SIGINT, interrupt_handler)

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


def combine_starting_points(input_dbs, output_db, reset_costs):
    print(input_dbs)
    out_db = ProcessingDatabase(output_db)
    out_db.conn.execute("DELETE FROM queue;")
    out_db.conn.execute("DELETE FROM starting_points;")

    total_transferred = 0
    for i in input_dbs:
        [i] = i
        in_db = ProcessingDatabase(i)
        for s in in_db.starting_points.values():
            s.id = None
            out_db.add_starting_points([s])
            total_transferred += 1

    # reload so we know the new ids
    out_db.reload_starting_points()

    out_db.push_queue(
        [
            StreamJob(
                id=None,
                cost=0 if reset_costs else s.cost,
                starting_point=s.id,
                stream=b"",
                follow_up_gen_limit=255,
                max_depth=s.max_depth,
                follow_ups=None,
            )
            for s in out_db.starting_points.values()
        ]
    )

    out_db.commit()

    print(f"Tranferred {total_transferred} starting points.")


def setup_next_search(
    input_results_db: pathlib.Path,
    output_starting_points_db: pathlib.Path,
    queries: List[str],
    reset_costs: bool,
    truncate_n_gliders: int,
):
    in_db = ProcessingDatabase(input_results_db)
    out_db = ProcessingDatabase(output_starting_points_db)

    results: Set[SavedResult] = set()
    print(queries)
    if not queries:
        print("No queries given, transfering all results", file=sys.stdout)
        queries = ["1 = 1"]
    for query in queries:
        query = query[0]
        if not query.lower().startswith("select "):
            query = f"SELECT * FROM r LEFT OUTER JOIN recipe_intermediates fi ON full_intermediate = fi.id WHERE {query};"
        for result in in_db.conn.execute(query):
            results.add(SavedResult.from_row(result))

    results: List[SavedResult] = list(results)
    results.sort(
        key=lambda a: in_db.starting_points[a.starting_point].cost + len(a.stream)
    )

    # de-dup by before_hit_digest, which should indicate identical results.
    by_digest = defaultdict(list)
    for r in results:
        by_digest[r.before_hit_digest].append(r)

    for rs in by_digest.values():
        # sort each group by actual cost
        rs.sort(
            key=lambda a: sum(in_db.starting_points[a.starting_point].stream + a.stream)
        )

    original_length = len(results)

    # take the first result of each group
    results = list(map(lambda a: a[0], by_digest.values()))

    # truncate the end gliders, if requested
    if truncate_n_gliders > 0:
        by_stream = defaultdict(list)
        for r in results:
            new_stream = r.stream[0:-truncate_n_gliders]
            by_stream[new_stream].append(r)

        results = list(map(lambda a: a[0], by_stream.values()))

    if len(results) < original_length:
        print(
            f"Filtered {original_length - len(results)} duplicate results",
            file=sys.stderr,
        )

    next_id = -1
    things_to_add = [
        (
            StartingPoint(
                id=(next_id := next_id + 1),
                cost=0 if reset_costs else r.cost,
                stream=in_db.starting_points[r.starting_point].stream
                + (
                    r.stream[0:-truncate_n_gliders]
                    if truncate_n_gliders > 0
                    else r.stream
                ),
                follow_up_gen_limit=255,
                max_depth=r.max_depth,
            ),
            StreamJob(
                id=None,
                cost=0 if reset_costs else r.cost,
                starting_point=next_id,
                stream=b"",
                follow_up_gen_limit=255,
                max_depth=r.max_depth,
                follow_ups=None,
            ),
        )
        for r in results
    ]
    print(f"Transferred {len(results)} results as starting_points.")

    out_db.conn.execute("DELETE FROM starting_points;")
    out_db.conn.execute("DELETE FROM queue;")
    out_db.add_starting_points(list(map(lambda x: x[0], things_to_add)))
    out_db.push_queue(list(map(lambda x: x[1], things_to_add)))
    out_db.commit()


def row_to_string(row):
    return f'Row({', '.join([f"{k}={row[k]}" for k in row.keys()])})'


def view_results(input_results_db, show_completion):
    db = ProcessingDatabase(input_results_db)

    [sample_row] = db.conn.execute("select * from results limit 1").fetchall()
    expected_keys = set(sample_row.keys())

    import readline

    try:
        while True:
            query = input("> ")
            try:
                cursor = db.conn.execute(query)
                pattern = lt.pattern()
                red_pattern = lt.pattern()
                is_results = True
                for i, row in enumerate(cursor):
                    if i > 100:
                        break
                    keys = row.keys()
                    if not expected_keys.issubset(keys):
                        # this isn't a result row, just print it
                        print(row_to_string(row))
                        is_results = False
                        continue
                    result = SavedResult.from_row(row)
                    starting_point = db.starting_points[result.starting_point]
                    full_intermediate = (
                        db.recipe_intermediates[result.full_intermediate]
                        if result.full_intermediate is not None
                        else None
                    )
                    partial_intermediate = (
                        db.recipe_intermediates[result.partial_intermediate]
                        if result.partial_intermediate is not None
                        else None
                    )
                    stream = starting_point.stream + result.stream
                    block = (
                        PI_BLOCKS[1] if result.flipped_offset_block else PI_BLOCKS[0]
                    )

                    if full_intermediate:
                        evaluated_pattern = (single_channel_stream(stream) + block)[
                            sum(stream) + 1024
                        ](300 * i, 0)

                        full_intermediate_pattern = lt.pattern(
                            full_intermediate.rle_string
                        )(
                            i * 300
                            + full_intermediate.x
                            + (result.full_intermediate_shift or 0)
                            - result.flipped_offset_block,
                            full_intermediate.y
                            + (result.full_intermediate_shift or 0)
                            - result.flipped_offset_block,
                        )

                        remaining_gliders = lt.pattern()
                        for j, (lane, phase) in enumerate(
                            full_intermediate.remaining + ((0, 0),)
                        ):
                            remaining_gliders = remaining_gliders + mk_glider(
                                lane, 400 - phase
                            )(j * 100 + i * 300, j * 100)

                        if show_completion:
                            red_pattern = red_pattern + (
                                evaluated_pattern(150, 0)
                                - full_intermediate_pattern(150, 0)
                            )
                            pattern = (
                                pattern
                                + full_intermediate_pattern(150, 0)
                                + remaining_gliders(150, 0)
                            )

                        red_pattern = red_pattern + full_intermediate_pattern
                    elif partial_intermediate:
                        red_pattern = red_pattern + lt.pattern(
                            partial_intermediate.rle_string
                        )(
                            i * 300
                            + partial_intermediate.x
                            + (result.partial_intermediate_shift or 0)
                            - result.flipped_offset_block,
                            partial_intermediate.y
                            + (result.partial_intermediate_shift or 0)
                            - result.flipped_offset_block,
                        )
                    pattern = pattern + (single_channel_stream(stream) + block)(
                        i * 300, 0
                    )
                    print(result)

                    if result.label is not None:
                        red_pattern = red_pattern + write_text(str(result.label))(
                            i * 300, -200
                        )

                if is_results:
                    red_pattern = red_pattern + write_text(
                        input_results_db.name.replace("_", "-")
                    )(-300, 0)
                    print(
                        write_life_history(
                            green=pattern - red_pattern,
                            red=red_pattern - pattern,
                            white=pattern & red_pattern,
                        )
                    )
            except Exception as e:
                print(e)
                print(traceback.format_exc())
    finally:
        db.close()


@dataclass
class OptimizeArgs:
    starting_points: Dict[int, StartingPoint]
    recipe_intermediates: Dict[int, Recipe]
    component_search: ComponentSearch
    max_gens: int
    gen_options: List[int]
    min_offset_block_lane: int
    snark_offsets: Dict[int, Set[int]]
    partial_progress_factor: float
    partial_range: Set[int]


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
    comps = pattern_components(end_pattern)
    for c in comps:
        x, y, w, h = c.getrect()
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

    lanes.sort(key=lambda l: abs_lane(l[0]))

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
            job=job,
            follow_up=follow_up,
            before_hit_digest=before_hit_digest,
            end_pattern=flip_pattern_as_if_other_pi_block(end_pattern),
            shared_args=shared_args,
            recursed=True,
        )

    # max depth of all components including the offset block
    end_pattern_x, end_pattern_y, _, _ = end_pattern.getrect()

    original_components = set(
        shared_args.component_search.pattern_cache.id(c) for _, _, c in lanes
    )
    depth = max(map(lambda c: c.depth, original_components))
    max_depth = max(job.max_depth, depth)
    # components shifted to line up with the snark that would
    # hit the elbow
    components = set(
        shared_args.component_search.pattern_cache.id(c(-snark_offset, -snark_offset))
        for _, _, c in lanes
    )

    overlapping_recipes = shared_args.component_search.overlapping_recipes(components)
    best_full_intermediate_match: Optional[Recipe] = None
    best_partial_intermediate_match: Optional[Recipe] = None
    best_partial_prob = NEGATIVE_INFINITY
    best_partial_positive_prob = NEGATIVE_INFINITY
    full_elbow_intermediate_depth_separation = 0
    full_elbow_intermediate_overlapping_population = 0
    full_elbow_intermediate_overlapping_digest = 0
    full_intermediate_shift = 0
    partial_elbow_intermediate_depth_separation = 0
    partial_elbow_intermediate_overlapping_population = 0
    partial_intermediate_shift = 0

    for recipe in overlapping_recipes:
        recipe_components = shared_args.component_search.recipe_components(recipe)
        missing = recipe_components - components
        elbow = components - recipe_components
        partial_match = components - elbow
        if not missing:
            # full match!
            if (
                not best_full_intermediate_match
                or recipe.pattern.population
                > best_full_intermediate_match.pattern.population
            ):
                best_full_intermediate_match = recipe
                elbow_min_depth = min(
                    map(lambda x: x.depth, elbow), default=float("inf")
                )
                partial_match_max_depth = max(map(lambda x: x.depth, partial_match))
                full_elbow_intermediate_depth_separation = (
                    elbow_min_depth - partial_match_max_depth
                )
                full_elbow_intermediate_overlapping_population = sum(
                    [
                        c.pattern.population
                        for c in elbow
                        if c.depth <= partial_match_max_depth
                    ]
                )
                # get the digest of the full intermediate match
                # plus the pattern elements which overlap.
                overlapping_pattern = sum(
                    [c.pattern for c in elbow if c.depth <= partial_match_max_depth],
                    start=lt.pattern(),
                ) + sum([c.pattern for c in partial_match], start=lt.pattern())
                full_elbow_intermediate_overlapping_digest = (
                    overlapping_pattern.digest()
                )
                full_intermediate_shift = snark_offset
        else:
            # partial match!
            # find probability of finding rest of match
            p = total_probability(missing)
            if p == NEGATIVE_INFINITY:
                continue
            p -= len(recipe.remaining) * shared_args.partial_progress_factor
            if p > best_partial_prob:
                best_partial_prob = p
                best_partial_intermediate_match = recipe
                best_partial_positive_prob = total_probability(partial_match)

                elbow_min_depth = min(
                    map(lambda x: x.depth, elbow), default=float("inf")
                )
                partial_match_max_depth = max(map(lambda x: x.depth, partial_match))
                partial_elbow_intermediate_depth_separation = (
                    elbow_min_depth - partial_match_max_depth
                )
                partial_elbow_intermediate_overlapping_population = sum(
                    [
                        c.pattern.population
                        for c in elbow
                        if c.depth <= partial_match_max_depth
                    ]
                )
                partial_intermediate_shift = snark_offset

    return StreamResult(
        follow_up=follow_up,
        digest=end_pattern.digest(),
        before_hit_digest=before_hit_digest,
        x=end_pattern_x,
        y=end_pattern_y,
        offset_block_lane=furthest_lane,
        lane_width=abs_lane(lanes[-1][0]),  # next highest lane
        max_depth=max_depth,
        depth=depth,
        population=end_pattern.population,
        flipped_offset_block=1 if recursed else 0,
        full_intermediate=(
            best_full_intermediate_match.id if best_full_intermediate_match else None
        ),
        full_intermediate_depth_separation=full_elbow_intermediate_depth_separation,
        full_intermediate_overlapping_population=full_elbow_intermediate_overlapping_population,
        full_intermediate_overlapping_digest=full_elbow_intermediate_overlapping_digest,
        full_intermediate_shift=full_intermediate_shift,
        partial_intermediate=(
            best_partial_intermediate_match.id
            if best_partial_intermediate_match
            else None
        ),
        partial_intermediate_log_prob=best_partial_prob,
        partial_intermediate_positive_log_prob=best_partial_positive_prob,
        partial_intermediate_depth_separation=partial_elbow_intermediate_depth_separation,
        partial_intermediate_overlapping_population=partial_elbow_intermediate_overlapping_population,
        partial_intermediate_shift=partial_intermediate_shift,
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
        depth=a.depth,
        population=a.population,
        flipped_offset_block=a.flipped_offset_block,
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
        full_intermediate_overlapping_digest=(
            a.full_intermediate_overlapping_digest
            if a_better
            else b.full_intermediate_overlapping_digest
        ),
        full_intermediate_shift=(
            a.full_intermediate_shift if a_better else b.full_intermediate_shift
        ),
        partial_intermediate=(
            a.partial_intermediate if a_partial_better else b.partial_intermediate
        ),
        partial_intermediate_log_prob=(
            a.partial_intermediate_log_prob
            if a_partial_better
            else b.partial_intermediate_log_prob
        ),
        partial_intermediate_positive_log_prob=(
            a.partial_intermediate_positive_log_prob
            if a_partial_better
            else b.partial_intermediate_positive_log_prob
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
        partial_intermediate_shift=(
            a.partial_intermediate_shift
            if a_partial_better
            else b.partial_intermediate_shift
        ),
    )


def find_p2_output(job: StreamJob, queue, shared_args: OptimizeArgs):
    starting_points = shared_args.starting_points
    max_gens = shared_args.max_gens
    gen_options = shared_args.gen_options

    starting_point = starting_points[job.starting_point]
    result = StreamJobResult(
        starting_point=job.starting_point,
        stream=job.stream,
        valid_children=[],
        before_hit_digests={},
    )

    initial_added_gens = sum(job.stream)
    for next_possibility in job.follow_ups or gen_options:
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

        before_hit_x, before_hit_y, _, _ = before_hit.getrect() or (0, 0, 0, 0)
        result.before_hit_digests[next_possibility] = (
            before_hit_digest,
            before_hit_x,
            before_hit_y,
        )
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
                        follow_ups=None,
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
                        follow_ups=None,
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
                        follow_ups=None,
                    )
                )

    return result


def optimize(
    recipe_intermediates_db: pathlib.Path,
    output_db: pathlib.Path,
    max_gens: int,
    gen_options: str,
    min_offset_block_lane: int,
    partial_progress_factor: float,
    partial_range: str,
    n_processes: int,
    live_view_depth: float
):
    output_db: ProcessingDatabase = ProcessingDatabase(output_db)
    gen_options: List[int] = range_str_to_list(gen_options)
    partial_range: Set[int] = set(range_str_to_list(partial_range))
    if not output_db.recipe_intermediates:
        print(
            f"Transferring recipe_intermediates from {recipe_intermediates_db}",
            file=sys.stderr,
        )
        # Copy the recipe intermediates if the output doesn't have any
        recipe_intermediates_db: ProcessingDatabase = ProcessingDatabase(
            recipe_intermediates_db
        )
        new_intermediates = recipe_intermediates_db.recipe_intermediates
        output_db.add_recipe_intermediates(list(new_intermediates.values()))
        output_db.reload_recipe_intermediates()
        output_db.commit()
    else:
        print(
            f"Recipe intermediates already present in output DB, assuming already transferred.",
            file=sys.stderr,
        )

    snark_offsets = mk_snark_offset_target_options(output_db)

    shared_args = OptimizeArgs(
        starting_points=output_db.starting_points,
        recipe_intermediates=output_db.recipe_intermediates,
        component_search=None,
        max_gens=max_gens,
        gen_options=gen_options,
        min_offset_block_lane=min_offset_block_lane,
        snark_offsets=snark_offsets,
        partial_progress_factor=partial_progress_factor,
        partial_range=partial_range,
    )
    queue_stats = output_db.queue_stats
    print(f"Queue contains {sum(queue_stats.values())} job(s). Costs:", queue_stats)

    already_seen_results = set()
    speedo = Speedometer(interval_s=10)
    best_full_intermediate = 0
    n_best = 0
    best_log_prob = float("-inf")
    n_best_p = 0
    best_area = float("inf")
    best_area_str = "infxinf A"
    n_best_area = 0

    best_overlapping_population = float("inf")
    n_best_overlapping_population = 0

    with MultiprocessSearch(
        fn=find_p2_output,
        shared_args=shared_args,
        db=output_db,
        n_processes=n_processes,
    ) as search:
        for job, result, new_jobs in search:
            if isinstance(result, Exception):
                raise Exception("error in child process") from result
            for r in result.valid_children:
                if r.depth <= live_view_depth:
                    if r.partial_intermediate_log_prob is not None:
                        if r.partial_intermediate_log_prob > best_log_prob:
                            best_log_prob = r.partial_intermediate_log_prob
                            n_best_p = 1
                        elif r.partial_intermediate_log_prob == best_log_prob:
                            n_best_p += 1
                    if r.full_intermediate is not None and r.depth <= 40:
                        width = r.lane_width
                        depth = r.depth - r.full_intermediate_depth_separation

                        if width < best_area:
                            best_area = width
                            best_area_str = f"{width}x{depth} A"
                            n_best_area = 1
                        elif width == best_area:
                            n_best_area += 1

                        if (
                            r.full_intermediate_overlapping_population
                            < best_overlapping_population
                        ):
                            best_overlapping_population = (
                                r.full_intermediate_overlapping_population
                            )
                            n_best_overlapping_population = 1
                        elif (
                            r.full_intermediate_overlapping_population
                            == best_overlapping_population
                        ):
                            n_best_overlapping_population += 1

                        progress = len(
                            output_db.recipe_intermediates[r.full_intermediate].so_far
                        )
                        if progress == best_full_intermediate:
                            n_best += 1
                        elif progress > best_full_intermediate:
                            n_best = 1
                            best_full_intermediate = progress
            streams_in_job = job.follow_up_gen_limit - gen_options[0] + 1
            if speedo.tick(streams_in_job):
                current_per_s = speedo.get_current_speed_and_reset()
                avg_per_s = speedo.overall_speed()
                done = speedo.n_finished
                gens = (
                    search.pending_tracker.min_cost_pending() + gen_options[0],
                    min(
                        search.pending_tracker.min_cost_pending() + gen_options[-1],
                        max_gens,
                    ),
                )
                remaining = (gens[1] - gens[0] + 1) * search.db.queue_stats.get(
                    search.pending_tracker.min_cost_pending(), 0
                )
                total = search.n_streams_queued()
                print(
                    f"{current_per_s:.2f}/s, {avg_per_s:.2f} avg/s, {done:,} done, {gens[0]}-{gens[1]} gens, {remaining:,}/{total:,} pending, {best_full_intermediate}x{n_best}, {best_log_prob:.2f}x{n_best_p}, {best_area_str} ({n_best_area}), {best_overlapping_population} overlap ({n_best_overlapping_population})",
                    file=sys.stderr,
                )

            # the streams of new jobs that have a new before_hit_digest
            follow_ups_to_filter = set()
            # sort by follow up
            digests = sorted(result.before_hit_digests.items())
            for follow_up, key in digests:
                if key in already_seen_results:
                    # Skip exploring patterns we've already
                    # seen, based on the before_hit_digest
                    follow_ups_to_filter.add(follow_up)
                    continue
                already_seen_results.add(key)

            search.queue(
                [x for x in new_jobs if x.stream[-1] not in follow_ups_to_filter]
            )


def reprocess(input_db, output_db, queries):
    in_db = ProcessingDatabase(input_db)
    out_db = ProcessingDatabase(output_db)

    results: Set[SavedResult] = set()
    print(queries)
    if not queries:
        print("No queries given, transfering all results", file=sys.stdout)
        queries = ["1 = 1"]
    for query in queries:
        query = query[0]
        for result in in_db.conn.execute(
            f"SELECT * FROM results LEFT OUTER JOIN recipe_intermediates fi ON full_intermediate = fi.id WHERE {query};"
        ):
            results.add(SavedResult.from_row(result))

    print("Retrieved all results")

    results: List[SavedResult] = list(results)

    # group results by all but the last result
    groups = defaultdict(set)
    for r in results:
        stream = in_db.starting_points[r.starting_point].stream + r.stream
        max_depth = in_db.starting_points[r.starting_point].max_depth
        groups[(stream[0:-1], max_depth)].add(r)

    print(len(groups))

    things_to_add = []
    next_id = -1
    for (stream_start, max_depth), results in groups.items():
        things_to_add.append(
            (
                StartingPoint(
                    id=(next_id := next_id + 1),
                    cost=0,
                    stream=stream_start,
                    follow_up_gen_limit=255,
                    max_depth=max_depth,
                ),
                StreamJob(
                    id=None,
                    cost=0,
                    starting_point=next_id,
                    stream=b"",
                    follow_up_gen_limit=255,
                    follow_ups=bytes(map(lambda a: a.stream[-1], results)),
                    max_depth=max_depth,
                ),
            )
        )

    out_db.conn.execute("DELETE FROM starting_points;")
    out_db.conn.execute("DELETE FROM queue;")
    out_db.add_starting_points(list(map(lambda x: x[0], things_to_add)))
    out_db.push_queue(list(map(lambda x: x[1], things_to_add)))
    out_db.commit()

    print(f"Wrote queue to {output_db}. Run optimize with max-gens 0 to process.")


def recipe_tree(recipe_intermediates_db, start):
    recipes_db = ProcessingDatabase(recipe_intermediates_db)
    intermediates = recipes_db.recipe_intermediates
    start_int = intermediates[start]
    zero_int = next(i for i in intermediates.values() if len(i.so_far) == 0)
    starting_block = lt.pattern(zero_int.rle_string)(zero_int.x, zero_int.y)

    recipe = start_int.so_far + start_int.remaining
    end_target = reconstruct(recipe, starting_block, 100)[len(recipe) * 512]
    recipe_graph = RecipeGraph(end_target)

    def recurse(intermediate, depth=2):
        next_possibilities = recipe_graph.explore(intermediate, depth=1, width=73)
        if depth > 0:
            for n in next_possibilities:
                recurse(n, depth - 1)

    recurse(start_int, 4)
    print(recipe_graph.stamp_collection(include_glider=True).rle_string())


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
        required=True,
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
        "--n-processes",
        default=20,
        type=int,
        help="Number of processes to use for processing.",
    )
    parser_optimize.add_argument(
        "-l",
        "--min-offset-block-lane",
        type=int,
        default=80,
        help="Minimum offset for the offset block. (The block that will become the new elbow after the snark is created).",
    )
    parser_optimize.add_argument(
        "-p",
        "--partial-progress-factor",
        type=float,
        default=0.1,
        help="For partial intermediates, a factor affecting how much the distance of the partial from a complete snark affects its score.",
    )
    parser_optimize.add_argument(
        "--partial-range",
        type=str,
        default="0-255",
        help="The range of partial intermediates to consider, based on the number of gliders so far.",
    )
    parser_optimize.add_argument(
        "--live-view-depth",
        type=int,
        default=float('inf'),
        help="The max depth result to consider for results in the live view."
    )

    parser_view_results = subcommand.add_parser(
        "view-results", description="Explore and view results"
    )
    parser_view_results.add_argument(
        "-i",
        "--input-results-db",
        type=pathlib.Path,
        required=True,
        help="DB containing results to view",
    )
    parser_view_results.add_argument(
        "--show-completion",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If true, full_intermediate matches will show the slow zero degree gliders that would complete the pattern.",
    )

    parser_setup_next_search = subcommand.add_parser(
        "setup-next-search",
        description="Pick results to use as starting points for the next search",
    )
    parser_setup_next_search.add_argument(
        "-i",
        "--input-results-db",
        type=pathlib.Path,
        help="DB containing results to use as starting points",
    )
    parser_setup_next_search.add_argument(
        "-o",
        "--output-starting-points-db",
        type=pathlib.Path,
        help="Output file with starting points set up",
    )
    parser_setup_next_search.add_argument(
        "-q",
        "--query",
        type=str,
        help="SQL WHERE clause to select the relevant paths. Database query will be `SELECT * FROM results WHERE {query};`",
        action="append",
        nargs="*",
    )
    parser_setup_next_search.add_argument(
        "-r",
        "--reset-costs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If true, the starting options will all have cost 0, regardless of the result cost.",
    )
    parser_setup_next_search.add_argument(
        "-t",
        "--truncate-n-gliders",
        type=int,
        default=0,
        help="Remove the last n gliders from each starting point.",
    )

    parser_combine_starting_points = subcommand.add_parser(
        "combine-starting-points",
        description="Takes in multiple databases that haven't started processing, and combines their starting points and queues.",
    )
    parser_combine_starting_points.add_argument(
        "-i", "--input-db", type=pathlib.Path, nargs="+", action="append"
    )
    parser_combine_starting_points.add_argument("-o", "--output-db", type=pathlib.Path)
    parser_combine_starting_points.add_argument(
        "-r",
        "--reset-costs",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="If true, the starting options will all have cost 0, regardless of the initial cost.",
    )

    parser_reprocess = subcommand.add_parser(
        "reprocess",
        description="Reprocesses the results from a database. Useful if you have changed the scoring criteria in the code.",
    )
    parser_reprocess.add_argument(
        "-i", "--input-db", type=pathlib.Path, help="Input database with results"
    )
    parser_reprocess.add_argument(
        "-q",
        "--query",
        type=str,
        help="SQL WHERE clause to select the relevant paths. Database query will be `SELECT * FROM results WHERE {query};`",
        action="append",
        nargs="*",
    )
    parser_reprocess.add_argument(
        "-o",
        "--output-db",
        help="Output sqlite database file.",
        type=pathlib.Path,
        required=True,
    )

    parser_recipe_tree = subcommand.add_parser(
        "recipe-tree",
        description="Prints the tree of possible next steps after the given recipe intermediate",
    )
    parser_recipe_tree.add_argument(
        "-r",
        "--recipe-intermediates-db",
        type=pathlib.Path,
        help="DB containing recipe intermediates",
        required=True,
    )
    parser_recipe_tree.add_argument(
        "--start",
        help="The recipe intermediate ID to start with",
        type=int,
        required=True,
    )
    parser_recipe_tree.add_argument(
        "--end", help="The recipe intermediate ID to end with", type=int, default=None
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
                partial_progress_factor=args.partial_progress_factor,
                partial_range=args.partial_range,
                n_processes=args.n_processes,
                live_view_depth=args.live_view_depth,
            )
        case "view-results":
            print("Show completion", args.show_completion)
            view_results(
                input_results_db=args.input_results_db,
                show_completion=args.show_completion,
            )
        case "setup-next-search":
            setup_next_search(
                input_results_db=args.input_results_db,
                output_starting_points_db=args.output_starting_points_db,
                queries=args.query,
                reset_costs=args.reset_costs,
                truncate_n_gliders=args.truncate_n_gliders,
            )
        case "combine-starting-points":
            combine_starting_points(
                input_dbs=args.input_db,
                output_db=args.output_db,
                reset_costs=args.reset_costs,
            )
        case "reprocess":
            reprocess(
                input_db=args.input_db, output_db=args.output_db, queries=args.query
            )
        case "recipe-tree":
            recipe_tree(
                recipe_intermediates_db=args.recipe_intermediates_db, start=args.start
            )
