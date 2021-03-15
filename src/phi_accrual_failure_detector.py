import math
import time

from atomos.atomic import AtomicReference

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
                 min_std_deviation_millis: int,
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
        self.state = AtomicReference(_State(history=self._first_heartbeat(), timestamp=None))

    def _ensure_valid_std_deviation(self, std_deviation: float) -> float:
        return max(std_deviation, self.min_std_deviation_millis)

    def _is_available(self, timestamp: float) -> bool:
        return self._phi(timestamp) < self.threshold

    def is_available(self) -> bool:
        return self._is_available(self._get_time())

    def phi(self) -> float:
        return self._phi(self._get_time())

    def heartbeat(self) -> None:
        timestamp = self._get_time()
        old_state = self.state.get()
        new_history = None

        if old_state.timestamp is None:
            new_history = self._first_heartbeat()
        else:
            latest_timestamp = old_state.timestamp
            interval = timestamp - latest_timestamp

            if self._is_available(timestamp):
                new_history = old_state.history + interval

        new_state = _State(history=new_history, timestamp=timestamp)

        if not self.state.compare_and_set(old_state, new_state):
            self.heartbeat()

    def _phi(self, timestamp: float) -> float:
        last_state = self.state
        last_timestamp = last_state.get().timestamp

        if last_timestamp is None:
            return 0.0

        time_diff = timestamp - last_timestamp
        last_history = last_state.get().history
        mean = last_history.mean()
        std_dev = self._ensure_valid_std_deviation(last_history.std_dev())

        return _phi(time_diff, mean + self.acceptable_heartbeat_pause_millis, std_dev)

    def _first_heartbeat(self) -> _HeartbeatHistory:
        mean = self.first_heartbeat_estimate_millis
        std_dev = mean / 4
        heartbeat = _HeartbeatHistory(self.max_sample_size) + int((mean - std_dev))
        heartbeat = heartbeat + int(mean + std_dev)
        return heartbeat

    @classmethod
    def _get_time(cls) -> float:
        return round(time.time() * 1000)
