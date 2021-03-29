from __future__ import annotations

import math


class _HeartbeatHistory:
    """
    Represent the sample window defined in the φ Accrual failure detector paper.
    It stores a limited list of heartbeats in a list of length max_sample_size.

    See:
       https://github.com/akka/akka/blob/master/akka-remote/src/main/scala/akka/remote/PhiAccrualFailureDetector.scala#L237

    Attributes:
        _max_sample_size: the length of the list of samples to use
        intervals: the list of intervals used by the class
        _interval_sum: represents the total sum of the intervals list
        _squared_interval_sum: represents the squared interval total sum of the intervals list
    """

    def __init__(self, max_sample_size: int, intervals=None, interval_sum: float = 0,
                 squared_interval_sum: float = 0):
        """
        Constructor of the _HeartbeatHistory class.
        """
        if intervals is None:
            intervals = list()

        if max_sample_size < 1:
            raise Exception(f"max_sample_size must be >= 1, got {max_sample_size}")

        if interval_sum < 0:
            raise Exception(f"interval_sum must be >= 0, got {interval_sum}")

        if squared_interval_sum < 0:
            raise Exception(f"squared_interval_sum must be >= 0, got {squared_interval_sum}")

        self.intervals = intervals
        self._max_sample_size = max_sample_size
        self._interval_sum = interval_sum
        self._squared_interval_sum = squared_interval_sum

    def mean(self) -> float:
        """ Calculate the mean of the intervals distribution.
        Returns:
            the mean of the intervals
        """
        return self._interval_sum / len(self.intervals)

    def variance(self) -> float:
        """ Calculate the variance of the intervals distribution.
        Returns:
             the variance of the intervals
        """
        return (self._squared_interval_sum / len(self.intervals)) - (self.mean() * self.mean())

    def std_dev(self) -> float:
        """ Calculate the standard deviation of the intervals distribution.
        Returns:
             the standard deviation of the collection of intervals
        """
        return math.sqrt(self.variance())

    def drop_oldest(self) -> _HeartbeatHistory:
        """  Drop the oldest interval in the intervals list.
        Returns:
             a new instance of class without the oldest interval
        """
        return _HeartbeatHistory(
            max_sample_size=self._max_sample_size,
            intervals=self.intervals[1:],
            interval_sum=self._interval_sum - self.intervals[0],
            squared_interval_sum=self._squared_interval_sum - (self.intervals[0] * self.intervals[0])
        )

    def __add__(self, interval: int) -> _HeartbeatHistory:
        """ Add a new interval in the list of intervals
        Args:
            interval: the interval to add
        Returns:
             a new instance of the class with the new interval
        """
        if len(self.intervals) < self._max_sample_size:
            return _HeartbeatHistory(
                max_sample_size=self._max_sample_size,
                intervals=self.intervals + [interval],
                interval_sum=self._interval_sum + interval,
                squared_interval_sum=self._squared_interval_sum + (interval * interval))
        else:
            return self.drop_oldest() + interval
