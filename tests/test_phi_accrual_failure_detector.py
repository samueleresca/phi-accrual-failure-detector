from multiprocessing import Process

from pytest import mark

from src.phi_accrual_failure_detector import PhiAccrualFailureDetector


class TestPhiAccrualFailureDetector:

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

    @mark.skip
    def test_failure_detector_heartbeat_multithread(self):
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
