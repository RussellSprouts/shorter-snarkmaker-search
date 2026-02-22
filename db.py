from functools import cached_property
import sqlite3
from dataclasses import dataclass, field
from typing import List, Any
import itertools

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

    def from_row(row: sqlite3.Row):
        return StreamJob(
            id=row["id"],
            cost=row["cost"],
            starting_point=row["starting_point"],
            stream=row["stream"],
            follow_up_gen_limit=row["follow_up_gen_limit"],
            max_depth=row["max_depth"],
        )

    def __repr__(self):
        return f"StreamJob(id={self.id}, cost={self.cost}, starting_point={self.starting_point}, stream=bytes({tuple(self.stream)}), follow_up_gen_limit={self.follow_up_gen_limit}, max_depth={self.max_depth})"


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
    population: int

    full_intermediate: int
    full_intermediate_depth_separation: int
    full_intermediate_overlapping_population: int

    partial_intermediate: int
    partial_intermediate_log_prob: float
    partial_intermediate_depth_separation: int
    partial_intermediate_overlapping_population: int


@dataclass
class StreamJobResult:
    starting_point: int
    stream: bytes
    valid_children: List[StreamResult]


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
                max_depth INTEGER
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
                population INTEGER,
                full_intermediate INTEGER REFERENCES recipe_intermediates(id),
                full_intermediate_depth_separation INTEGER,
                full_intermediate_overlapping_population INTEGER,
                partial_intermediate INTEGER REFERENCES recipe_intermediates(id),
                partial_intermediate_log_prob REAL,
                partial_intermediate_depth_separation INTEGER,
                partial_intermediate_overlapping_population INTEGER
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

        self.reset_in_progress_queue()

        self.starting_points = {
            row["id"]: StartingPoint.from_row(row)
            for row in self.conn.execute("""SELECT * FROM starting_points""")
        }

        self.reload_recipe_intermediates()

        self.n_queued = sum(self.queue_stats().values())

    def reload_recipe_intermediates(self):
        self.recipe_intermediates = {
            row["id"]: Recipe.from_row(row)
            for row in self.conn.execute("""SELECT * from recipe_intermediates""")
        }
    def pop_queue(self, max_cost, max_num_results=1000) -> List[StreamJob]:
        result = [
            StreamJob.from_row(row)
            for row in self.conn.execute(
                """UPDATE queue
                   SET in_progress = 1
                   WHERE id in (
                     SELECT id FROM queue WHERE in_progress = 0 AND cost < ?
                     ORDER BY cost ASC
                     LIMIT ?
                   )
                   RETURNING id, cost, starting_point, stream, follow_up_gen_limit, max_depth""",
                (max_cost, max_num_results),
            )
        ]
        if not result:
            print([row['in_progress'] for row in self.conn.execute("""SELECT in_progress FROM queue""")])
        return result

    def reset_in_progress_queue(self):
        self.conn.execute("""UPDATE queue SET in_progress = 0 WHERE in_progress = 1""")


    def queue_stats(self):
        return {
            k: v
            for k, v in self.conn.execute(
                """SELECT cost, COUNT(cost) FROM queue GROUP BY cost"""
            )
        }

    def push_queue(self, jobs):
        self.n_queued += len(jobs)
        self.conn.executemany(
            """INSERT INTO queue (in_progress, cost, starting_point, stream, follow_up_gen_limit, max_depth) VALUES (?, ?, ?, ?, ?, ?)""",
            [
                (
                    0,
                    job.cost,
                    job.starting_point,
                    job.stream,
                    job.follow_up_gen_limit,
                    job.max_depth,
                )
                for job in jobs
            ],
        )


    def save_results(self, results: List[tuple[StreamJob, StreamJobResult]]):
        print("Saving results", results)
        self.n_queued -= len(results)
        self.conn.executemany(
            """
            INSERT INTO results
            (stream, starting_point, digest, before_hit_digest, x, y, offset_block_lane, lane_width, max_depth, population, full_intermediate, full_intermediate_depth_separation, full_intermediate_overlapping_population, partial_intermediate, partial_intermediate_log_prob, partial_intermediate_depth_separation, partial_intermediate_overlapping_population)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
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
                    child.population,
                    child.full_intermediate,
                    child.full_intermediate_depth_separation,
                    child.full_intermediate_overlapping_population,
                    child.partial_intermediate,
                    child.partial_intermediate_log_prob,
                    child.partial_intermediate_depth_separation,
                    child.partial_intermediate_overlapping_population,
                )
                for _, result in results
                for child in result.valid_children
            ],
        )

        self.conn.executemany(
            """DELETE FROM queue WHERE id = ? RETURNING id""",
            [(job.id,) for job, _ in results],
        )
        
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
    queue_stats = db.queue_stats()
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
