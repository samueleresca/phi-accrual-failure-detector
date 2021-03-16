from __future__ import annotations

import math


class _HeartbeatHistory:
    """
    Represent the sample window defined in the φ Accrual failure detector paper.
    It stores a limited list of heartbeats in a list of max_sample_size.
    """

    def __init__(self, max_sample_size: int, intervals=None, interval_sum: float = 0,
                 squared_interval_sum: float = 0):
        """
        Constructor of the _HeartbeatHistory class.
        :param max_sample_size: the size of the samples to use.
        :param intervals: the list of intervals stored by the class instance
        :param interval_sum: represents the sum of the intervals
        :param squared_interval_sum:  represent the squared interval sum of the intervals
        """
        if intervals is None:
            intervals = list()

        if max_sample_size < 1:
            raise Exception(f"max_sample_size must be >= 1, got {max_sample_size}")

        if interval_sum < 0:
            raise Exception(f"interval_sum must be >= 0, got {interval_sum}")

        if squared_interval_sum < 0:
            raise Exception(f"squared_interval_sum must be >= 0, got {squared_interval_sum}")

        self.max_sample_size = max_sample_size
        self.intervals = intervals
        self.interval_sum = interval_sum
        self.squared_interval_sum = squared_interval_sum

    def mean(self) -> float:
        """
        :return: Returns the mean of the intervals
        """
        return self.interval_sum / self.max_sample_size

    def variance(self) -> float:
        """
        :return: Returns the variance of the intervals
        """
        return (self.squared_interval_sum / len(self.intervals)) - (self.mean() * self.mean())

    def std_dev(self) -> float:
        """
        :return: Returns the standard deviation of the collection of intervals
        """
        return math.sqrt(self.variance())

    def drop_oldest(self) -> _HeartbeatHistory:
        """
        Drop the oldest interval in the intervals list.
        :return: Returns a new instance of class without the oldest interval
        """
        return _HeartbeatHistory(
            max_sample_size=self.max_sample_size,
            intervals=self.intervals[1:],
            interval_sum=self.interval_sum - self.intervals[0],
            squared_interval_sum=self.squared_interval_sum - (self.intervals[0] * self.intervals[0])
        )

    def __add__(self, interval: int) -> _HeartbeatHistory:
        """
        Add a new interval in the list of intervals
        :param interval: the interval to add
        :return: Returns a new instance of the class with the new interval
        """
        if len(self.intervals) < self.max_sample_size:
            return _HeartbeatHistory(
                max_sample_size=self.max_sample_size,
                intervals=self.intervals + [interval],
                interval_sum=self.interval_sum + interval,
                squared_interval_sum=self.squared_interval_sum + (interval * interval))
        else:
            return self.drop_oldest() + interval
