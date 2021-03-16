import time
from multiprocessing import Process
from typing import Iterable

from pytest import mark

from src.phi_accrual_failure_detector import PhiAccrualFailureDetector


class TestPhiAccrualFailureDetector:

    @classmethod
    def get_time_mocked(cls, times: Iterable[float]):
        def mocked_func():
            current_time = next(times)
            print(current_time)
            return current_time

        return mocked_func

    def test_failure_detector_initialization(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=16,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        assert failure_detector.state is not None
        assert failure_detector.state.get().history is not None
        assert failure_detector.state.get().timestamp is None

    def test_failure_detector_phi(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=16,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        assert failure_detector.phi() is not None

    def test_failure_detector_heartbeat(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=16,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.phi() is not None

    def test_failure_detector_heartbeats(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=16,
            max_sample_size=10,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        prev_value = 1
        for counter in range(0, 5):
            failure_detector.heartbeat()
            current_phi = failure_detector.phi()

            assert prev_value > current_phi
            print(prev_value)
            prev_value = current_phi
            time.sleep(1.0)

    def test_failure_detector_with_series_of_successful_heartbeats(self):
        def mock_time():
            yield 0
            yield 1000
            yield 100
            yield 100

        failure_detector = PhiAccrualFailureDetector(
            threshold=3,
            max_sample_size=1000,
            min_std_deviation_millis=10000,
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
            yield 100
            yield 100
            yield 3000
            yield 5000

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

    def test_failure_after_configured_missing_accetable_heartbeat(self):
        def mock_time():
            yield 0
            yield 1000
            yield 1000
            yield 1000
            yield 1000
            yield 1000
            yield 500
            yield 500
            yield 5000

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
        failure_detector.heartbeat()
        failure_detector.heartbeat()
        failure_detector.heartbeat()

        assert failure_detector.is_available() is True
        failure_detector._get_time()
        assert failure_detector.is_available() is False

    @mark.skip
    def test_failure_detector_heartbeat_multi_thread(self):
        failure_detector = PhiAccrualFailureDetector(
            threshold=16,
            max_sample_size=200,
            min_std_deviation_millis=500,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=500
        )

        p1 = Process(target=failure_detector.heartbeat)
        p2 = Process(target=failure_detector.heartbeat)

        p1.start()
        p2.start()
        p1.join()
        p2.join()

        assert failure_detector.phi() is not None
