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
                min_std_deviation_ms=500,
                acceptable_heartbeat_pause_ms=0,
                first_heartbeat_estimate_ms=500
            )

        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=0,
                min_std_deviation_ms=500,
                acceptable_heartbeat_pause_ms=0,
                first_heartbeat_estimate_ms=500
            )

        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=200,
                min_std_deviation_ms=-1,
                acceptable_heartbeat_pause_ms=0,
                first_heartbeat_estimate_ms=500
            )
        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=200,
                min_std_deviation_ms=1,
                acceptable_heartbeat_pause_ms=-1,
                first_heartbeat_estimate_ms=500
            )

        with pytest.raises(Exception):
            PhiAccrualFailureDetector(
                threshold=16,
                max_sample_size=200,
                min_std_deviation_ms=1,
                acceptable_heartbeat_pause_ms=1,
                first_heartbeat_estimate_ms=0
            )

    def test_initialization(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=200,
            min_std_deviation_ms=500,
            acceptable_heartbeat_pause_ms=0,
            first_heartbeat_estimate_ms=500
        )

        assert failure_detector._state is not None
        assert failure_detector._state.get().history is not None
        assert failure_detector._state.get().timestamp is None

    def test_phi(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=200,
            min_std_deviation_ms=500,
            acceptable_heartbeat_pause_ms=0,
            first_heartbeat_estimate_ms=500
        )

        assert failure_detector.phi() is not None

    def test_heartbeat(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=200,
            min_std_deviation_ms=500,
            acceptable_heartbeat_pause_ms=0,
            first_heartbeat_estimate_ms=500
        )

        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.phi() is not None

    def test_with_series_of_successful_heartbeats(self):
        def mock_time():
            yield 0
            yield 1000
            yield 1100
            yield 1200

        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=1000,
            min_std_deviation_ms=10,
            acceptable_heartbeat_pause_ms=0,
            first_heartbeat_estimate_ms=1000
        )

        failure_detector._get_time = self.get_time_mocked(mock_time())

        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True

    def test_success_with_a_missing_heartbeat_and_right_acceptable_timeout(self):
        def mock_time():
            yield 0
            yield 1000
            yield 2000
            yield 3000
            yield 7000
            yield 8000
            yield 9000

        failure_detector = PhiAccrualFailureDetector(
            threshold=8,
            max_sample_size=1000,
            min_std_deviation_ms=10,
            acceptable_heartbeat_pause_ms=3000,
            first_heartbeat_estimate_ms=1000
        )

        failure_detector._get_time = self.get_time_mocked(mock_time())

        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True
        failure_detector.heartbeat()
        assert failure_detector.is_available() is True

    def test_failure_if_heartbeat_missed(self):
        def mock_time() -> iter:
            yield 0
            yield 1000
            yield 1100
            yield 1200
            yield 5200
            yield 8200

        failure_detector = PhiAccrualFailureDetector(
            threshold=3,
            max_sample_size=1000,
            min_std_deviation_ms=10,
            acceptable_heartbeat_pause_ms=0,
            first_heartbeat_estimate_ms=1000
        )

        failure_detector._get_time = self.get_time_mocked(mock_time())

        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True
        failure_detector._get_time()
        assert failure_detector.is_available() is False

    def test_failure_after_configured_acceptable_missing_heartbeat(self):
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
            min_std_deviation_ms=10,
            acceptable_heartbeat_pause_ms=3000,
            first_heartbeat_estimate_ms=1000
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
