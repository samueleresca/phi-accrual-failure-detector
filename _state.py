from _heartbeat_history import _HeartbeatHistory
from typing import Optional


class _State:
    """
    Represents the accrual failure detector's state. It is wraps the _HeartbeatHistory and the latest (most recent) timestamp.
    Attributes:
        history: The heartbeat history wrapped into the state
        timestamp: Optional; The latest timestamp to wrap in the state.
    """
    def __init__(self, history: _HeartbeatHistory, timestamp: Optional[float] = None):
        """
        Constructor of _State class.
        """
        self.history = history
        self.timestamp = timestamp
