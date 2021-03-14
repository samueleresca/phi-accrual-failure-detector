from __future__ import annotations

import math

from atomos.atomic import AtomicLong


class _HeartbeatHistory:

    def __init__(self, max_sample_size: int, intervals=None, interval_sum: AtomicLong = AtomicLong(0),
                 squared_interval_sum: AtomicLong = AtomicLong(0)):

        if intervals is None:
            intervals = list()
        self.max_sample_size = max_sample_size
        self.intervals = intervals
        self.interval_sum = interval_sum
        self.squared_interval_sum = squared_interval_sum

    def mean(self) -> float:
        return self.interval_sum.get() / self.max_sample_size

    def variance(self) -> float:
        return (self.squared_interval_sum.get() / len(self.intervals)) - (self.mean() * self.mean())

    def std_dev(self) -> float:
        return math.sqrt(self.variance())

    def drop_oldest(self) -> _HeartbeatHistory:
        return _HeartbeatHistory(
            max_sample_size=self.max_sample_size,
            intervals=self.intervals[1:],
            interval_sum=AtomicLong(self.interval_sum.get() - self.intervals[0]),
            squared_interval_sum=AtomicLong(self.squared_interval_sum.get() - (self.intervals[0] * self.intervals[0]))
        )

    def __add__(self, interval: int) -> _HeartbeatHistory:
        if len(self.intervals) < self.max_sample_size:
            return _HeartbeatHistory(
                max_sample_size=self.max_sample_size,
                intervals=self.intervals + [interval],
                interval_sum=AtomicLong(self.interval_sum.get() + interval),
                squared_interval_sum=AtomicLong(self.squared_interval_sum.get() + (interval * interval)))
        else:
            return self.drop_oldest() + interval
