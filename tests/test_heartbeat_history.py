import pytest

from src._heartbeat_history import _HeartbeatHistory


class TestHeartbeatHistory:
    def test_mean(self):
        history = _HeartbeatHistory(3)
        history += 1
        history += 2
        history += 3

        assert history.mean() == 2.0

    def test_std_dev(self):
        history = _HeartbeatHistory(3)
        history += 1
        history += 2
        history += 3

        assert history.std_dev() == 0.8164965809277263

    def test_variance(self):
        history = _HeartbeatHistory(3)
        history += 1
        history += 2
        history += 3

        assert history.variance() == 0.666666666666667

    def test_dropping_works(self):
        history = _HeartbeatHistory(3)
        history += 1
        history += 2
        history += 3
        history += 4

        assert len(history.intervals) == 3
