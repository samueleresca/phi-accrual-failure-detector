from src._heartbeat_history import _HeartbeatHistory
from typing import Optional


class _State:
    """
    Represents the state of the failure detector. It is wraps the _HeartbeatHistory and the timestamp.
    """
    def __init__(self, history: _HeartbeatHistory, timestamp: Optional[float] = None):
        """
        Constructor of _State class.
        :param history: The history to wrap in the state
        :param timestamp: The timestamp to wrap in the state
        """
        self.history = history
        self.timestamp = timestamp
