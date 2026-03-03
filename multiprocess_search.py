import multiprocessing
import heapq
from typing import Callable, Generator, List
from multiprocessing import connection
import sys
import signal
from queue import Empty

from component_search import ComponentSearch, PatternCache
from db import ProcessingDatabase, StreamJob, StreamJobResult, StreamResult


def recursive_priority_process_wrapper(shared_args, queue, pipe, f):
    """Wrapper to handle pulling tasks from the queue and applying
    the provided function."""

    signal.signal(signal.SIGINT, signal.SIG_IGN)

    pattern_cache = PatternCache()
    shared_args.component_search = ComponentSearch(pattern_cache)
    for recipe in shared_args.recipe_intermediates.values():
        shared_args.component_search.add_recipe(recipe)

    while True:
        id = None
        try:
            s = queue.get()
            if not s:
                continue
            id = s[0]
            args = s[1]
            if id == "stop":
                return
            new_jobs = []

            def add_to_queue(data):
                new_jobs.append(data)

            res = f(args, queue=add_to_queue, shared_args=shared_args)
            pipe.send((id, multiprocessing.current_process().name, res, new_jobs))
        except Exception as e:
            print(f"Process error! {multiprocessing.current_process().name}")
            pipe.send((id, "err", e, []))
            raise
        finally:
            queue.task_done()



class PendingTracker:
    """
    Keeps track of the number of tasks of a specific
    generation cost that are pending in the pool.
    """

    def __init__(self):
        # a heap of [cost, n_pending]
        # only one entry for each cost
        self.pending_heap = []
        # a dict of cost -> heap entry
        self.pending_items = {}
        # the total number of pending tasks
        self.n_pending = 0

    def mark_pending(self, cost):
        self.n_pending += 1
        if cost in self.pending_items:
            pend = self.pending_items[cost]
            pend[1] = pend[1] + 1
        else:
            pend = [cost, 1]
            self.pending_items[cost] = pend
            heapq.heappush(self.pending_heap, pend)

    def mark_done(self, cost):
        if cost not in self.pending_items:
            raise KeyError(f"{cost} marked done but not pending")
        self.n_pending -= 1
        pend = self.pending_items[cost]
        pend[1] = pend[1] - 1
        if pend[1] == 0:
            # clear out the zero entries.
            while len(self.pending_heap) and self.pending_heap[0][1] == 0:
                p = heapq.heappop(self.pending_heap)
                to_delete = p[0]
                del self.pending_items[to_delete]

    def min_cost_pending(self):
        if len(self.pending_heap):
            return self.pending_heap[0][0]
        return float("inf")

class MultiprocessSearch:
    def __init__(self, fn, shared_args, db: ProcessingDatabase, n_processes = 20):
        self.fn = fn
        self.shared_args = shared_args
        self.db = db
        self.n_processes = n_processes

        self.next_id = 0
        self.id_to_args = {}
        self.pending_queue = multiprocessing.JoinableQueue()
        self.pending_tracker = PendingTracker()
        self.readers = []
        self.processes = []
        for i in range(0, self.n_processes):
            r, w = multiprocessing.Pipe()
            self.readers.append(r)
            p = multiprocessing.Process(
                target=recursive_priority_process_wrapper,
                args=(self.shared_args, self.pending_queue, w, self.fn),
            )
            self.processes.append(p)
            p.start()

    def __iter__(self) -> Generator[tuple[StreamJob, StreamJobResult, List[StreamJob]]]:
        def send_tasks(max_val):
            if self.pending_queue.empty():
                if max_val == float('inf'):
                    max_val = 2**63-1
                for task in self.db.pop_queue(max_val, 10000):
                    self.pending_tracker.mark_pending(task.cost)
                    self.id_to_args[self.next_id] = (task.cost, task)
                    self.pending_queue.put((self.next_id, task))
                    self.next_id += 1
                self.db.commit()

        stats = self.db.queue_stats()
        queued_costs = list(stats.keys())
        if len(queued_costs) == 0:
            print("Warning: queue is empty, not processing.", file=sys.stderr)
            return

        # start the first tasks.
        send_tasks(min(stats.keys()) + 1)

        while self.pending_tracker.n_pending or self.db.n_queued:
            for r in connection.wait(self.readers):
                id, status, result, new_jobs = r.recv()
                priority, args = self.id_to_args[id]
                del self.id_to_args[id]
                self.pending_tracker.mark_done(priority)
                self.db.save_results([
                    (args, result)
                ])
                yield (args, result, new_jobs)
                send_tasks(self.pending_tracker.min_cost_pending())


    def queue(self, new_jobs):
        self.db.push_queue(new_jobs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        print("Draining queue (if any)")
        try:
            while True:
                self.pending_queue.get_nowait()
                self.pending_queue.task_done()
        except Empty:
            pass
        print("Done.")
        print("Done.")
        print("Joining subprocesses...")
        for i in range(0, self.n_processes):
            self.pending_queue.put(("stop", None))
        self.pending_queue.join()
        for p in self.processes:
            p.join()
        print("Committing database")
        self.db.commit()
