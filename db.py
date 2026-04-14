from functools import cached_property
import sqlite3
from dataclasses import dataclass, field
from typing import List, Any, Dict, Optional
import itertools
import time
import sys

from lifetree import lt

MAX_SQLITE_INT = 2**63 - 1


def digest_to_signed(digest):
    if digest <= MAX_SQLITE_INT:
        return digest
    return int.from_bytes(int.to_bytes(digest, 8), signed=True)


def digest_from_signed(digest):
    if digest >= 0:
        return digest
    return int.from_bytes(int.to_bytes(digest, 8, signed=True))


@dataclass
class StartingPoint:
    id: int
    cost: int
    stream: bytes
    follow_up_gen_limit: int
    max_depth: int

    def from_row(row: sqlite3.Row):
        return StartingPoint(
            row["id"],
            row["cost"],
            row["stream"],
            row["follow_up_gen_limit"],
            row["max_depth"],
        )

    def __repr__(self):
        return f"StartingPoint(id={self.id}, cost={self.cost}, stream=bytes({tuple(self.stream)}), follow_up_gen_limit={self.follow_up_gen_limit}, max_depth={self.max_depth})"


@dataclass(order=True)
class StreamJob:
    id: int
    cost: int
    starting_point: int
    stream: bytes
    follow_up_gen_limit: bytes
    max_depth: int
    follow_ups: Optional[bytes]

    def from_row(row: sqlite3.Row):
        keys = row.keys()
        return StreamJob(
            id=row["id"],
            cost=row["cost"],
            starting_point=row["starting_point"],
            stream=row["stream"],
            follow_up_gen_limit=row["follow_up_gen_limit"],
            max_depth=row["max_depth"],
            follow_ups=row["follow_ups"] if "follow_ups" in keys else None,
        )

    def __repr__(self):
        return f"StreamJob(id={self.id}, cost={self.cost}, starting_point={self.starting_point}, stream=bytes({tuple(self.stream)}), follow_up_gen_limit={self.follow_up_gen_limit}, max_depth={self.max_depth}, follow_ups={self.follow_ups})"


@dataclass(frozen=True)
class SavedResult:
    stream: bytes
    starting_point: int
    digest: int
    before_hit_digest: int
    x: int
    y: int
    offset_block_lane: int
    lane_width: int
    max_depth: int
    depth: int
    population: int
    flipped_offset_block: int

    full_intermediate: int
    full_intermediate_depth_separation: int
    full_intermediate_overlapping_population: int
    full_intermediate_overlapping_digest: int
    full_intermediate_shift: int
    partial_intermediate: int
    partial_intermediate_log_prob: float
    partial_intermediate_positive_log_prob: float
    partial_intermediate_depth_separation: int
    partial_intermediate_overlapping_population: int
    partial_intermediate_shift: int
    partial_intermediate_digest: int
    partial_intermediate_overlapping_digest: int

    # add `something as label` to the select
    # in view-results to print the label next to it.
    label: str

    def from_row(row: sqlite3.Row):
        keys = row.keys()

        return SavedResult(
            stream=row["stream"],
            starting_point=row["starting_point"],
            digest=row["digest"],
            before_hit_digest=row["before_hit_digest"],
            x=row["x"],
            y=row["y"],
            offset_block_lane=row["offset_block_lane"],
            lane_width=row["lane_width"],
            max_depth=row["max_depth"],
            depth=row["depth"] if "depth" in keys else row["max_depth"],
            population=row["population"],
            flipped_offset_block=row["flipped_offset_block"],
            full_intermediate=row["full_intermediate"],
            full_intermediate_depth_separation=row[
                "full_intermediate_depth_separation"
            ],
            full_intermediate_overlapping_population=row[
                "full_intermediate_overlapping_population"
            ],
            full_intermediate_overlapping_digest=(
                row["full_intermediate_overlapping_digest"]
                if "full_intermediate_overlapping_digest" in keys
                else 0
            ),
            full_intermediate_shift=row["full_intermediate_shift"],
            partial_intermediate=row["partial_intermediate"],
            partial_intermediate_log_prob=row["partial_intermediate_log_prob"],
            partial_intermediate_positive_log_prob=row[
                "partial_intermediate_positive_log_prob"
            ],
            partial_intermediate_depth_separation=row[
                "partial_intermediate_depth_separation"
            ],
            partial_intermediate_overlapping_population=row[
                "partial_intermediate_overlapping_population"
            ],
            partial_intermediate_shift=row["partial_intermediate_shift"],
            partial_intermediate_digest=row["partial_intermediate_digest"] if "partial_intermediate_digest" in keys else 0,
            partial_intermediate_overlapping_digest=(
                row["partial_intermediate_overlapping_digest"]
                if "partial_intermediate_overlapping_digest" in keys
                else 0
            ),
            label=row["label"] if "label" in keys else None
        )

    def __repr__(self):
        return (
            "SavedResult("
            f"stream=bytes({tuple(self.stream)}), "
            f"starting_point={self.starting_point}, "
            f"digest={self.digest}, "
            f"before_hit_digest={self.before_hit_digest}, "
            f"x={self.x}, "
            f"y={self.y}, "
            f"offset_block_lane={self.offset_block_lane}, "
            f"lane_width={self.lane_width}, "
            f"max_depth={self.max_depth}, "
            f"depth={self.depth}, "
            f"population={self.population}, "
            f"flipped_offset_block={self.flipped_offset_block}, "
            f"full_intermediate={self.full_intermediate}, "
            f"full_intermediate_depth_separation={self.full_intermediate_depth_separation}, "
            f"full_intermediate_overlapping_population={self.full_intermediate_overlapping_population}, "
            f"full_intermediate_overlapping_digest={self.full_intermediate_overlapping_digest}, "
            f"full_intermediate_shift={self.full_intermediate_shift}, "
            f"partial_intermediate={self.partial_intermediate}, "
            f"partial_intermediate_log_prob={self.partial_intermediate_log_prob}, "
            f"partial_intermediate_positive_log_prob={self.partial_intermediate_positive_log_prob}, "
            f"partial_intermediate_depth_separation={self.partial_intermediate_depth_separation}, "
            f"partial_intermediate_overlapping_population={self.partial_intermediate_overlapping_population}, "
            f"partial_intermediate_shift={self.partial_intermediate_shift}, "
            f"partial_intermediate_digest={self.partial_intermediate_digest}, "
            f"partial_intermediate_overlapping_digest={self.partial_intermediate_overlapping_digest}"
            ")"
        )


@dataclass
class StreamResult:
    follow_up: int
    digest: int
    before_hit_digest: int
    x: int
    y: int
    offset_block_lane: int
    lane_width: int
    max_depth: int
    depth: int
    population: int
    flipped_offset_block: int

    full_intermediate: int
    full_intermediate_depth_separation: int
    full_intermediate_overlapping_population: int
    full_intermediate_overlapping_digest: int
    full_intermediate_shift: int

    partial_intermediate: int
    partial_intermediate_log_prob: float
    partial_intermediate_positive_log_prob: float
    partial_intermediate_depth_separation: int
    partial_intermediate_overlapping_population: int
    partial_intermediate_shift: int
    partial_intermediate_digest: int
    partial_intermediate_overlapping_digest: int


@dataclass
class StreamJobResult:
    starting_point: int
    stream: bytes
    valid_children: List[StreamResult]
    # map of follow_up to (before_hit_digest, x, y)
    before_hit_digests: Dict[int, tuple[int, int, int]]


int.to_bytes(-1, 1, "little", signed=True)


@dataclass(eq=True, unsafe_hash=True)
class Recipe:
    id: int
    # The slow gliders we've sent so far
    so_far: tuple
    # The slow gliders still remaining to send
    remaining: tuple
    digest: int
    x: int
    y: int
    rle_string: str

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("pattern", None)
        return state

    @cached_property
    def pattern(self):
        return lt.pattern(self.rle_string)(self.x, self.y)

    def glider_stream_from_bytes(bs):
        return tuple(
            (int.from_bytes(int.to_bytes(lane), signed=True), phase)
            for lane, phase in itertools.batched(bs, 2)
        )

    def glider_stream_to_bytes(gs):
        return bytes(
            b
            for lane, phase in gs
            for b in (int.from_bytes(int.to_bytes(lane, signed=True)), phase)
        )

    def from_row(row):
        return Recipe(
            id=row["id"],
            so_far=Recipe.glider_stream_from_bytes(row["so_far"]),
            remaining=Recipe.glider_stream_from_bytes(row["remaining"]),
            digest=digest_from_signed(row["digest"]),
            x=row["x"],
            y=row["y"],
            rle_string=row["rle_string"],
        )


class ProcessingDatabase:
    def __init__(self, filename):
        self.conn = sqlite3.connect(filename)
        self.conn.autocommit = False
        self.conn.row_factory = sqlite3.Row

        # Table of starting points for the search.
        # Initialized with the first 0 delay glider, or the
        # best results from the previous step.
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS starting_points (
                id INTEGER PRIMARY KEY,
                cost INTEGER,
                stream BLOB,
                follow_up_gen_limit INTEGER,
                max_depth INTEGER
            )
            """
        )

        # Table of results that are queued for processing
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS queue (
                id INTEGER PRIMARY KEY,
                in_progress INTEGER,
                cost INTEGER,
                starting_point INTEGER REFERENCES starting_points(id),
                stream BLOB,
                follow_up_gen_limit INTEGER,
                max_depth INTEGER,
                follow_ups BLOB
            )
            """
        )
        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS queue_idx ON queue (cost ASC)
            """
        )
        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS queue_in_progress_idx ON queue (in_progress ASC)
            """
        )
        self.conn.execute(
            """
            CREATE INDEX IF NOT EXISTS queue_id_idx ON queue (id ASC)
            """
        )

        # Table of processing results
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS results (
                stream BLOB,
                starting_point INTEGER REFERENCES starting_points(id),
                digest INTEGER,
                before_hit_digest INTEGER,
                x INTEGER,
                y INTEGER,
                offset_block_lane INTEGER,
                lane_width INTEGER,
                max_depth INTEGER,
                depth INTEGER,
                population INTEGER,
                flipped_offset_block INTEGER,
                full_intermediate INTEGER REFERENCES recipe_intermediates(id),
                full_intermediate_depth_separation INTEGER,
                full_intermediate_overlapping_population INTEGER,
                full_intermediate_overlapping_digest INTEGER,
                full_intermediate_shift INTEGER,
                partial_intermediate INTEGER REFERENCES recipe_intermediates(id),
                partial_intermediate_log_prob REAL,
                partial_intermediate_positive_log_prob REAL,
                partial_intermediate_depth_separation INTEGER,
                partial_intermediate_overlapping_population INTEGER,
                partial_intermediate_shift INTEGER,
                partial_intermediate_digest INTEGER,
                partial_intermediate_overlapping_digest INTEGER
            )
            """
        )

        # If this is a new DB, seed it with the initial values
        self.conn.execute(
            """
            INSERT OR IGNORE INTO starting_points
                (id, cost, stream, follow_up_gen_limit, max_depth)
                VALUES (0, 0, x'00', ?, 0)
            """,
            (255,),
        )
        self.conn.execute(
            """
            INSERT OR IGNORE INTO queue (
                id, in_progress, cost, starting_point, stream, follow_up_gen_limit, max_depth
            ) SELECT 0, 0, 0, 0, x'', ?, 0
            WHERE NOT EXISTS (SELECT 1 FROM queue) AND NOT EXISTS (SELECT 1 from results)
            """,
            (255,),
        )

        # Table of intermediate stages of the slow salvo recipe
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS recipe_intermediates (
                id INTEGER PRIMARY KEY,
                so_far BLOB,
                remaining BLOB,
                digest INTEGER,
                rle_string TEXT,
                x INTEGER,
                y INTEGER
            )
            """
        )

        # Create a view with all the relevant joins for ease of
        # querying.
        self.conn.execute(
            """
            CREATE VIEW IF NOT EXISTS r AS
            SELECT
                r.stream as stream,
                r.starting_point as starting_point,
                r.digest as digest,
                r.before_hit_digest as before_hit_digest,
                r.x as x,
                r.y as y,
                r.offset_block_lane as offset_block_lane,
                r.lane_width as lane_width,
                r.max_depth as max_depth,
                r.depth as depth,
                r.population as population,
                r.flipped_offset_block as flipped_offset_block,
                r.full_intermediate as full_intermediate,
                r.full_intermediate_depth_separation as full_intermediate_depth_separation,
                r.full_intermediate_overlapping_population as full_intermediate_overlapping_population,
                r.full_intermediate_overlapping_digest as full_intermediate_overlapping_digest,
                r.full_intermediate_shift as full_intermediate_shift,
                r.partial_intermediate as partial_intermediate,
                r.partial_intermediate_log_prob as partial_intermediate_log_prob,
                r.partial_intermediate_positive_log_prob as partial_intermediate_positive_log_prob,
                r.partial_intermediate_depth_separation as partial_intermediate_depth_separation,
                r.partial_intermediate_overlapping_population as partial_intermediate_overlapping_population,
                r.partial_intermediate_shift as partial_intermediate_shift,
                r.partial_intermediate_digest as partial_intermediate_digest,
                r.partial_intermediate_overlapping_digest as partial_intermediate_overlapping_digest,

                fi.so_far as fi_so_far,
                fi.remaining as fi_remaining,
                fi.digest as fi_digest,
                fi.rle_string as fi_rle_string,
                fi.x as fi_x,
                fi.y as fi_y,

                pi.so_far as pi_so_far,
                pi.remaining as pi_remaining,
                pi.digest as pi_digest,
                pi.rle_string as pi_rle_string,
                pi.x as pi_x,
                pi.y as pi_y,

                sp.cost as sp_cost,
                sp.stream as sp_stream,
                sp.follow_up_gen_limit as sp_follow_up_gen_limit,
                sp.max_depth as sp_max_depth,

                CAST(sp.stream || r.stream AS BLOB) as full_stream
            FROM results r
            LEFT OUTER JOIN recipe_intermediates fi ON fi.id = full_intermediate
            LEFT OUTER JOIN recipe_intermediates pi on pi.id = partial_intermediate
            JOIN starting_points sp on sp.id = starting_point
            """
        )

        self.reset_in_progress_queue()

        self.reload_starting_points()

        self.reload_recipe_intermediates()

        self.queue_stats = self.fetch_queue_stats()
        self.n_queued = sum(self.queue_stats.values())

    def reload_recipe_intermediates(self):
        self.recipe_intermediates = {
            row["id"]: Recipe.from_row(row)
            for row in self.conn.execute("""SELECT * from recipe_intermediates""")
        }

    def reload_starting_points(self):
        self.starting_points = {
            row["id"]: StartingPoint.from_row(row)
            for row in self.conn.execute("""SELECT * FROM starting_points""")
        }

    def pop_queue(self, max_cost, max_num_results=1000) -> List[StreamJob]:
        result = sorted(
            [
                StreamJob.from_row(row)
                for row in self.conn.execute(
                    """UPDATE queue
                   SET in_progress = 1
                   WHERE id in (
                     SELECT id FROM queue WHERE in_progress = 0 AND cost < ?
                     ORDER BY cost ASC
                     LIMIT ?
                   )
                   RETURNING *""",
                    (max_cost, max_num_results),
                )
            ],
            key=lambda a: a.cost,
        )
        return result

    def push_queue(self, jobs):
        self.n_queued += len(jobs)
        for job in jobs:
            self.queue_stats[job.cost] = self.queue_stats.get(job.cost, 0) + 1
        self.conn.executemany(
            """INSERT INTO queue (in_progress, cost, starting_point, stream, follow_up_gen_limit, max_depth, follow_ups) VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    0,
                    job.cost,
                    job.starting_point,
                    job.stream,
                    job.follow_up_gen_limit,
                    job.max_depth,
                    job.follow_ups,
                )
                for job in jobs
            ],
        )

    def add_starting_points(self, starting_points: List[StartingPoint]):
        self.conn.executemany(
            """INSERT INTO starting_points
            (id, cost, stream, follow_up_gen_limit, max_depth)
            VALUES (?, ?, ?, ?, ?)""",
            (
                (s.id, s.cost, s.stream, s.follow_up_gen_limit, s.max_depth)
                for s in starting_points
            ),
        )

    def save_results(self, results: List[tuple[StreamJob, StreamJobResult]]):
        self.n_queued -= len(results)
        for job, _ in results:
            self.queue_stats[job.cost] = self.queue_stats.get(job.cost, 0) - 1

        self.conn.executemany(
            """INSERT INTO results
            (stream, starting_point, digest, before_hit_digest, x, y, offset_block_lane, lane_width, max_depth, depth, population, flipped_offset_block, full_intermediate, full_intermediate_depth_separation, full_intermediate_overlapping_population, full_intermediate_overlapping_digest, full_intermediate_shift, partial_intermediate, partial_intermediate_log_prob, partial_intermediate_positive_log_prob, partial_intermediate_depth_separation, partial_intermediate_overlapping_population, partial_intermediate_shift, partial_intermediate_digest, partial_intermediate_overlapping_digest)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    result.stream + bytes((child.follow_up,)),
                    result.starting_point,
                    digest_to_signed(child.digest),
                    digest_to_signed(child.before_hit_digest),
                    child.x,
                    child.y,
                    child.offset_block_lane,
                    child.lane_width,
                    child.max_depth,
                    child.depth,
                    child.population,
                    child.flipped_offset_block,
                    child.full_intermediate,
                    child.full_intermediate_depth_separation,
                    child.full_intermediate_overlapping_population,
                    digest_to_signed(child.full_intermediate_overlapping_digest),
                    child.full_intermediate_shift,
                    child.partial_intermediate,
                    child.partial_intermediate_log_prob,
                    child.partial_intermediate_positive_log_prob,
                    child.partial_intermediate_depth_separation,
                    child.partial_intermediate_overlapping_population,
                    child.partial_intermediate_shift,
                    digest_to_signed(child.partial_intermediate_digest),
                    digest_to_signed(child.partial_intermediate_overlapping_digest),
                )
                for _, result in results
                for child in result.valid_children
            ],
        )

        self.conn.executemany(
            """DELETE FROM queue WHERE id = ? RETURNING id""",
            [(job.id,) for job, _ in results],
        )

    def reset_in_progress_queue(self):
        self.conn.execute("""UPDATE queue SET in_progress = 0 WHERE in_progress = 1""")

    def fetch_queue_stats(self):
        return {
            k: v
            for k, v in self.conn.execute(
                """SELECT cost, COUNT(cost) FROM queue GROUP BY cost"""
            )
        }

    def add_recipe_intermediates(self, recipes: List[Recipe]):
        self.conn.executemany(
            """
            INSERT INTO recipe_intermediates (so_far, remaining, digest, rle_string, x, y)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    Recipe.glider_stream_to_bytes(recipe.so_far),
                    Recipe.glider_stream_to_bytes(recipe.remaining),
                    digest_to_signed(recipe.digest),
                    recipe.rle_string,
                    recipe.x,
                    recipe.y,
                )
                for recipe in recipes
            ],
        )

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.commit()
        self.conn.close()


if __name__ == "__main__":
    filename = "new-db.sqlite"
    db = ProcessingDatabase(filename)
    print(f"Opened database {filename}")
    queue_stats = db.fetch_queue_stats()
    print(f"Queue contains {sum(queue_stats.values())} job(s). Costs:", queue_stats)

    print(f"Database contains {len(db.recipe_intermediates)} recipe intermediates")

    for job in db.pop_queue(1):
        print(job)
        db.save_results(
            [
                (
                    job,
                    StreamJobResult(
                        starting_point=0,
                        stream=b"",
                        valid_children=[
                            StreamResult(
                                follow_up=90,
                                digest=123,
                                before_hit_digest=456,
                                x=0,
                                y=0,
                                offset_block_lane=100,
                                lane_width=20,
                                population=16,
                                best_full_intermediate_match=None,
                                best_partial_intermediate_match=None,
                                intermediate_match_fraction=0,
                                elbow_intermediate_depth_separation=0,
                                elbow_intermediate_overlapping_population=0,
                                max_depth=1,
                            )
                        ],
                    ),
                )
            ]
        )
    db.commit()

    for results in db.conn.execute("""SELECT * FROM results"""):
        print(results)
