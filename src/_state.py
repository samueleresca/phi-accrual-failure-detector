from src._heartbeat_history import _HeartbeatHistory
from typing import Optional


class _State:
    """
    Represents the state of the failure detector. It is wraps the _HeartbeatHistory and the timestamp.
    Attributes:
        history: The history to wrap in the state.
        timestamp: Optional; The timestamp to wrap in the state.
    """
    def __init__(self, history: _HeartbeatHistory, timestamp: Optional[float] = None):
        """
        Constructor of _State class.
        """
        self.history = history
        self.timestamp = timestamp
