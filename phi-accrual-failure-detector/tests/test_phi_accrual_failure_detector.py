import time
from typing import Iterable

import pytest

from phi_accrual_failure_detector import PhiAccrualFailureDetector


class TestPhiAccrualFailureDetector:

    @classmethod
    def get_time_mocked(cls, times: Iterable[float]):
        def mocked_func():
            current_time = next(times)
            print(f"Current time: {current_time}")
            return current_time
        return mocked_func

    def test_constructor_requirements(self):
        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=-1,
                max_sample_size=200,
                min_std_deviation_millis=500,
                acceptable_heartbeat_pause_millis=0,
                first_heartbeat_estimate_millis=500
            )

        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=0,
                min_std_deviation_millis=500,
                acceptable_heartbeat_pause_millis=0,
                first_heartbeat_estimate_millis=500
            )

        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=200,
                min_std_deviation_millis=-1,
                acceptable_heartbeat_pause_millis=0,
                first_heartbeat_estimate_millis=500
            )
        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=200,
                min_std_deviation_millis=1,
                acceptable_heartbeat_pause_millis=-1,
                first_heartbeat_estimate_millis=500
            )

        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=200,
                min_std_deviation_millis=1,
                acceptable_heartbeat_pause_millis=1,
                first_heartbeat_estimate_millis=0
            )

    def test_failure_detector_initialization(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        assert failure_detector._state is not None
        assert failure_detector._state.get().history is not None
        assert failure_detector._state.get().timestamp is None

    def test_failure_detector_phi(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        assert failure_detector.phi() is not None

    def test_failure_detector_heartbeat(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.phi() is not None

    def test_failure_detector_with_series_of_successful_heartbeats(self):
        def mock_time():
            yield 0
            yield 1000
            yield 1100
            yield 1200

        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=1000,
            min_std_deviation_millis=10,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=1000
        )

        failure_detector._get_time = self.get_time_mocked(mock_time())

        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True

    def test_failure_detector_with_death_node_if_heartbeat_missed(self):
        def mock_time() -> iter:
            yield 0
            yield 1000
            yield 1100
            yield 1200
            yield 4200
            yield 9200

        failure_detector = PhiAccrualFailureDetector(
            threshold=3,
            max_sample_size=1000,
            min_std_deviation_millis=10,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=1000
        )

        failure_detector._get_time = self.get_time_mocked(mock_time())

        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True
        failure_detector._get_time()
        assert failure_detector.is_available() is False

    def test_failure_after_configured_accetable_missing_heartbeat(self):
        def mock_time() -> iter:
            yield 0
            yield 1000
            yield 2000
            yield 3000
            yield 4000
            yield 5000
            yield 5500
            yield 6000
            yield 11000

        failure_detector = PhiAccrualFailureDetector(
            threshold=3,
            max_sample_size=1000,
            min_std_deviation_millis=10,
            acceptable_heartbeat_pause_millis=3000,
            first_heartbeat_estimate_millis=1000
        )

        failure_detector._get_time = self.get_time_mocked(mock_time())

        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True
        failure_detector.heartbeat()
        assert failure_detector.is_available() is False
