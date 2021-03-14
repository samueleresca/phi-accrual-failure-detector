from src._heartbeat_history import _HeartbeatHistory
from typing import Optional


class _State:
    def __init__(self, history: _HeartbeatHistory, timestamp: Optional[int] = None):
        self.history = history
        self.timestamp = timestamp
