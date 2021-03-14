import math
from time import clock
from atomos.atomic import AtomicReference, AtomicLong

from src._heartbeat_history import _HeartbeatHistory
from src._state import _State


def _phi(time_diff: float, mean: float, std_dev: float) -> float:
    y = (time_diff - mean) / std_dev
    e = math.exp(-y * (1.5976 + 0.070566 * y * y))
    if time_diff > mean:
        return -math.log10(e / (1.0 + e))
    else:
        return -math.log10(1.0 - 1.0 / (1.0 + e))


class PhiAccrualFailureDetector:
    def __init__(self, threshold: float,
                 max_sample_size: int,
                 min_std_deviation_millis: float,
                 acceptable_heartbeat_pause_millis: int,
                 first_heartbeat_estimate_millis: int):
        """
        :param threshold:
        :param max_sample_size:
        :param min_std_deviation_millis:
        :param acceptable_heartbeat_pause_millis:
        :param first_heartbeat_estimate_millis:
        """
        self.threshold = threshold
        self.max_sample_size = max_sample_size
        self.min_std_deviation_millis = min_std_deviation_millis
        self.acceptable_heartbeat_pause_millis = acceptable_heartbeat_pause_millis
        self.first_heartbeat_estimate_millis = first_heartbeat_estimate_millis
        self.state = AtomicReference(_State(history = self._first_heartbeat(), timestamp = None))

    def _ensure_valid_std_deviation(self, std_deviation: float) -> float:
        return max(std_deviation, self.min_std_deviation_millis)

    def _acceptable_heartbeat_pause_millis(self) -> float:
        return self.acceptable_heartbeat_pause_millis.real

    def phi(self) -> float:
        return self._phi(clock())

    def _phi(self, timestamp: float) -> float:
        old_state = self.state
        old_timestamp = old_state.get().timestamp

        if old_timestamp is None:
            return 0.0

        time_diff = timestamp - old_timestamp
        history = old_state.get().history
        mean = history.mean()
        std_dev = self._ensure_valid_std_deviation(history.std_dev())

        return _phi(time_diff, mean + self._acceptable_heartbeat_pause_millis(), std_dev)

    def _first_heartbeat(self) -> _HeartbeatHistory:
        mean = self.first_heartbeat_estimate_millis.real
        std_dev = mean / 4
        return _HeartbeatHistory(self.max_sample_size) + AtomicLong(mean - std_dev) + AtomicLong(mean + std_dev)
