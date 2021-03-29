import copy
import math
import time

from atomos.atomic import AtomicReference

from _heartbeat_history import _HeartbeatHistory
from _state import _State


class PhiAccrualFailureDetector:
    """
    The φ Accrual Failure Detector implementation.

    See:
        https://github.com/akka/akka/blob/master/akka-remote/src/main/scala/akka/remote/PhiAccrualFailureDetector.scala

    Attributes:
        threshold: The threshold used by the instance to trigger the suspicious level.
        max_sample_size: Max number of heartbeat samples to store.
        min_std_deviation_ms: Minimum standard deviation used in the calc of the φ
        acceptable_heartbeat_pause_ms: Number of lost / delayed heartbeat before considering an anomaly.
        first_heartbeat_estimate_ms: The first heartbeat duration, since the initial collection is empty.
        _state: encapsulates the _State of the current instance of the failure detector.
    """

    def __init__(self, threshold: float,
                 max_sample_size: int,
                 min_std_deviation_ms: int,
                 acceptable_heartbeat_pause_ms: int,
                 first_heartbeat_estimate_ms: int):
        """
        Constructor of the PhiAccrualFailureDetector class.
        """

        if threshold <= 0.0:
            raise Exception("threshold must be > 0")

        if max_sample_size <= 0:
            raise Exception("max-sample-size must be > 0")

        if min_std_deviation_ms <= 0:
            raise Exception("min_std_deviation_ms must be > 0")

        if acceptable_heartbeat_pause_ms < 0:
            raise Exception("acceptable_heartbeat_pause_ms must be >= 0")

        if first_heartbeat_estimate_ms <= 0:
            raise Exception("first_heartbeat_estimate_ms must be > 0")

        self.threshold = threshold
        self.max_sample_size = max_sample_size
        self.min_std_deviation_ms = min_std_deviation_ms
        self.acceptable_heartbeat_pause_ms = acceptable_heartbeat_pause_ms
        self.first_heartbeat_estimate_ms = first_heartbeat_estimate_ms
        self._state = AtomicReference(_State(history=self._first_heartbeat(), timestamp=None))

    def is_available(self) -> bool:
        """
        Returns the availability of the current resource based on the threshold and the calculated φ
        Returns:
            True if the resource is available otherwise False
        """
        return self._is_available(self._get_time())

    def phi(self) -> float:
        """
        Returns the φ calculated using the current state of the accrual failure detector.
        Returns:
            The value of the φ
        """
        return self._phi(self._get_time())

    def heartbeat(self) -> None:
        """
        Add an heartbeat to the state of the instance.
        """
        timestamp = self._get_time()
        old_state = self._state.get()

        if old_state.timestamp is None:
            new_history = self._first_heartbeat()
        else:
            latest_timestamp = old_state.timestamp
            interval = timestamp - latest_timestamp
            new_history = old_state.history

            if self._is_available(timestamp):
                new_history += interval

        new_state = _State(history=new_history, timestamp=timestamp)

        # Look for eventual concurrency issues, eventually it retry the heartbeat operation
        if not self._state.compare_and_set(old_state, new_state):
            self.heartbeat()

    def _phi(self, timestamp: float) -> float:
        """
        Calculate the φ based on the current state and the Tlast.
        Args:
            timestamp: the current timestamp to calculate the φ
        Returns:
            The value of the φ
        """
        last_state = self._state
        last_timestamp = last_state.get().timestamp

        if last_timestamp is None:
            return 0.0

        time_diff = timestamp - last_timestamp
        last_history = last_state.get().history
        mean = last_history.mean()
        std_dev = self._ensure_valid_std_deviation(last_history.std_dev())

        return self._calc_phi(time_diff, mean + self.acceptable_heartbeat_pause_ms, std_dev)

    def _first_heartbeat(self) -> _HeartbeatHistory:
        """
        Initialize a new _HeartbeatHistory instance using the first_heartbeat_estimate_ms
        Returns:
            A new instance of the _HeartbeatHistory
        """
        mean = self.first_heartbeat_estimate_ms
        std_dev = mean / 4
        heartbeat = _HeartbeatHistory(self.max_sample_size) + int(mean - std_dev)
        heartbeat = heartbeat + int(mean + std_dev)
        return heartbeat

    def _ensure_valid_std_deviation(self, std_deviation: float) -> float:
        """
        Returns the maximum between a std_deviation and the minimum standard deviation value configured in the constructor.
        Args:
            std_deviation: The std_dev value to check
        Returns:
            the maximum between a std_deviation and the minimum value configured in the constructor.
        """
        return max(std_deviation, self.min_std_deviation_ms)

    def _is_available(self, timestamp: float) -> bool:
        """
        Returns the availability of the current resource based on the threshold and the calculated φ
        Args:
            The timestamp of the current time.
        Returns:
            True if the resource is available otherwise False
        """
        phi_value = self._phi(timestamp)
        return phi_value < self.threshold

    @classmethod
    def _get_time(cls) -> float:
        """
        Get the time in ms. Useful for mocking during testing.
        Returns:
            The current time in ms.
        """
        return round(time.time() * 1000)

    @classmethod
    def _calc_phi(cls, time_diff: float, mean: float, std_dev: float) -> float:
        """
        Core method for calculating the phi φ coefficient. It uses a logistic approximation to the cumulative normal
        distribution.
        See: https://github.com/akka/akka/issues/1821
        Args:
            time_diff: the difference of the times (Tnow- Tlast)
            mean: the mean of the history distribution
            std_dev: the standard deviation of the history distribution
        Returns:
             The value of the φ
        """
        y = (time_diff - mean) / std_dev

        try:
            e = math.exp(-y * (1.5976 + 0.070566 * y * y))
        except OverflowError:
            e = float('inf')

        if time_diff > mean:
            return -math.log10(e / (1.0 + e))
        else:
            return -math.log10(1.0 - 1.0 / (1.0 + e))
