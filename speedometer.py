import time

class Speedometer:
    """Timer for how fast we are processing."""
    def __init__(self, interval_s):
        self.n_finished = 0
        self.last_time = time.monotonic()
        self.begin_time = self.last_time
        self.n_finished_since = 0
        self.interval = interval_s

    def tick(self, n=1):
        now = time.monotonic()
        self.n_finished += n
        self.n_finished_since += n
        return now - self.last_time > 10

    def get_current_speed_and_reset(self):
        now = time.monotonic()
        result = self.n_finished_since / (now - self.last_time)
        self.n_finished_since = 0
        self.last_time = now
        return result

    def overall_speed(self):
        now = time.monotonic()
        return self.n_finished / (now - self.begin_time)