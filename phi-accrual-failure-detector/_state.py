from typing import Optional

from _heartbeat_history import _HeartbeatHistory


class _State:
    """
    Represents the accrual failure detector's state. It is wraps the _HeartbeatHistory and the latest (most recent) timestamp.

    See: https://github.com/akka/akka/blob/0326e113879f08f39ca80667512cc960f267c81b/akka-remote/src/main/scala/akka/remote/PhiAccrualFailureDetector.scala#L120

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
