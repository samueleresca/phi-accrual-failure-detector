import math

from atomiclong import AtomicLong


class _HeartbeatHistory:
    def __init__(self, max_sample_size: int):
        self.max_sample_size = max_sample_size
        self.intervals = list()
        self.interval_sum = AtomicLong(0)
        self.squared_interval_sum = AtomicLong(0)

    def mean(self) -> float:
        return self.interval_sum.value / self.max_sample_size

    def variance(self) -> float:
        return (self.squared_interval_sum.value / len(self.intervals)) - (self.mean() * self.mean())

    def std_dev(self) -> float:
        return math.sqrt(self.variance())
