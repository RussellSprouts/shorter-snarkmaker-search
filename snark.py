from dataclasses import dataclass
from typing import List
import sys
import argparse
import math
import pathlib

from speedometer import Speedometer
from font import write_text
from lifetree import lt
from optimized_stream_simulation import optimized_stream_simulation
from recipe_intermediates import recipe_intermediates

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog = "snark.py",
        description="Searches for an optimized snarkmaker recipe."
    )
    subcommand = parser.add_subparsers(dest='command', required=True)

    parser_recipe_intermediates = subcommand.add_parser('recipe-intermediates', description='Processes the input recipe to find intermediate stages')
    parser_recipe_intermediates.add_argument(
        '-i',
        '--input-recipe',
        help='Input rle/mc file for the recipe. The slow salvo gliders should travel NW and hit a block. There should be one extra glider at the end that defines lane 0.',
        type=pathlib.Path,
        required=True
    )
    parser_recipe_intermediates.add_argument(
        '-o',
        '--output-db',
        help='Output sqlite database file.',
        type=pathlib.Path,
        required=True,
    )
    parser_recipe_intermediates.add_argument(
        '-d',
        '--search-depth',
        help='How many gliders deep to search from the initial block. -1 for the entire recipe.',
        default=-1,
        type=int
    )
    parser_recipe_intermediates.add_argument(
        '-w',
        '--search-width',
        help='The search tries to move a slice of future gliders to the present. Check slices of length 1 to search_width.',
        default=3,
        type=int
    )
    parser_recipe_intermediates.add_argument(
        '-n',
        '--max-pool',
        type=int,
        default=2048,
        help='Maximum number of recipes to keep in the pool at each depth.'
    )

    parser_optimize = subcommand.add_parser('optimize', description='Optimizes the recipe.')
    parser_optimize.add_argument(
        '-r',
        '--recipe-intermediates',
        help='Database file of recipe-intermediates',
        type=pathlib.Path,
        required=True
    )
    parser_optimize.add_argument(
        '-o',
        '--output-db',
        help='Output sqlite database file.',
        type=int,
        required=True
    )
    parser_optimize.add_argument(
        '-n',
        '--max-gens',
        type=int,
        help='Max number of generations to search',
    )
    parser_optimize.add_argument(
        '-g',
        '--gen-options',
        type=str,
        default='90-255',
        help='Options for spacing of gliders in a stream. E.g. "74,75,78-255". Defaults to "90-255". Maximum 255.'
    )
    parser_optimize.add_argument(
        '-l',
        '--min-offset-block-lane',
        type=int,
        default=80,
        help='Minimum offset for the offset block. (The block that will become the new elbow after the snark is created).'
    )
    args = parser.parse_args()

    match args.command:
        case 'recipe-intermediates':
            recipe_intermediates(
                input_recipe=args.input_recipe,
                output_db=args.output_db,
                search_depth=args.search_depth,
                search_width=args.search_width,
                max_pool=args.max_pool
            )
        case 'optimize':
            pass

sys.exit(0)

gen_options = bytes(range(90, 256))
max_gens = 1200

before_hit_digests_seen = set()

# Patterns that work as offset elbow to be used after
# the snark.
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

elbow_offsets_even = {
    lt.pattern(rle).digest(): v
    for rle, v in {
        "oo$oo": -20,  # block
        "boo$obbo$boo": -17,  # beehive horizontal
        "bo$obo$obo$bo": -21,  # beehive vertical
        "2o$obo$b2o!": -21,  # ship nw<->se
        "2o$obo$bo!": -21,  # boat nw
        "b2o$o2bo$o2bo$b2o!": -17,  # pond
    }.items()
}
elbow_offsets_odd = {
    lt.pattern(rle).digest(): v
    for rle, v in {
        "oo$oo": -16,
        "boo$obbo$boo": None,  # beehive horizontal
        "bo$obo$obo$bo": None,  # beehive vertical
        "2o$obo$b2o!": None,  # ship nw<->se
        "2o$obo$bo!": None,  # boat nw
        "bo$obo$b2o!": -16,  # boat se
        "b2o$o2bo$o2bo$b2o!": -21,  # pond
    }.items()
}


def offset_snark_for_elbow(elbow_digest, depth):
    if depth % 2 == 0:
        r = elbow_offsets_even[elbow_digest]
        if r is None:
            return None
        return r + depth // 2
    else:
        r = elbow_offsets_odd[elbow_digest]
        if r is None:
            return None
        return r + depth // 2


@dataclass
class PatternComponent:
    digest: int
    x: int
    y: int
    w: int
    h: int

    def lane(self):
        return max(
            self.x - self.y,
            (self.x + self.w) - (self.y + self.h),
            key=abs,
        )

    def depth(self):
        return self.x + self.y + self.w + self.h

    def offset_elbow(self):
        if self.digest not in offset_elbows:
            return None
        return offset_snark_for_elbow(self.digest, self.depth())


def extract_offset_elbow(components: List[PatternComponent]):
    extreme_lane = 0
    extreme_component = None
    for c in components:
        lane = c.lane()
        if abs(lane) >= abs(extreme_lane):
            extreme_lane = lane
            extreme_component = c
    if extreme_component is None:
        return None
    offset = extreme_component.offset_elbow()
    if offset is None:
        return None
    return extreme_component, extreme_lane, offset


def score_offset_elbow(pattern):
    components = [
        PatternComponent(c.digest(), *c.getrect()) for c in pattern.components()
    ]
    offset_elbow = extract_offset_elbow(components)
    if offset_elbow is None:
        return 0
    extreme_component, extreme_lane, offset = offset_elbow


def find_p2_output(job, queue):
    initial_gens = sum(job.stream)
    result = StreamJobResult(job.stream, [])
    for next_possibility in job.next_possibilities:
        stream = job.stream + bytes((next_possibility,))
        gens = initial_gens + next_possibility

        before_hit = optimized_stream_simulation(stream)
        before_hit_digest = before_hit.digest()
        if before_hit_digest in before_hit_digests_seen:
            # we've reached a state we've seen before with
            # a shorter glider sequence. No need to explore further.
            break

        before_hit_digests_seen.add(before_hit_digest)

        # snapshots
        just_after_hit = before_hit[20]
        just_after_hit1 = just_after_hit[1]
        just_after_hit2 = just_after_hit1[1]
        end_pattern = just_after_hit2[512 - 22]
        end_pattern2 = end_pattern[2]

        if end_pattern == end_pattern2:
            # the pattern settles into a p1 or p2. It could be a valid
            # result! We need to get statistics about it for scoring.
            lanes = []
            depths = {}
            for c in end_pattern.components():
                (x, y, w, h) = c.getrect()
                is_pi_equivalent = c.digest() in offset_elbows
                lanes.append(
                    (
                        max(
                            x - y,
                            (x + w) - (y + h),
                            key=abs,
                        ),
                        is_pi_equivalent,
                        c,
                    )
                )
                depths[c] = x + w + y + h

            if len(lanes) > 1:
                lanes.sort(key=lambda x: abs(x[0]))
                (max_lane, is_pi_equivalent) = lanes[-1]
                if is_pi_equivalent:
                    # the most extreme edge is a possible
                    # offset block
                    (x, y, _, _) = end_pattern.getrect()
                    result.valid_children.append(
                        StreamResult(
                            next_possibility=next_possibility,
                            digest=end_pattern.digest(),
                            before_hit_digest=before_hit_digest,
                            x=x,
                            y=y,
                            max_lane=max_lane,
                            next_highest_lane=lanes[-2][0],
                            population=end_pattern.population,
                        )
                    )

        if gens <= max_gens - gen_options[0]:
            if just_after_hit == just_after_hit1:
                # the pattern very quickly stabilized to p1,
                # only queue the fastest possible next glider
                queue(
                    gens,
                    StreamJob(
                        stream=stream,
                        starting_block=job.starting_block,
                        next_possibilities=gen_options[0:1],
                    ),
                )
            elif just_after_hit == just_after_hit2:
                queue(
                    gens,
                    StreamJob(
                        stream=stream,
                        starting_block=job.starting_block,
                        next_possibilities=bytes(
                            [x for x in gen_options[0:2] if x + gens <= max_gens]
                        ),
                    ),
                )
            else:
                queue(
                    gens,
                    StreamJob(
                        stream=stream,
                        starting_block=job.starting_block,
                        next_possibilities=bytes(
                            [x for x in gen_options if x + gens <= max_gens]
                        ),
                    ),
                )

    return result


starting_candidates = [(0,)]

sys.exit(0)

if __name__ == "__main__":
    pass


def search():
    speedo = Speedometer(interval_s=10)
    starting_jobs = [
        (
            sum(c),
            StreamJob(
                stream=bytes(c), starting_block=0, next_possibilities=gen_options
            ),
        )
        for c in starting_candidates
    ]

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
