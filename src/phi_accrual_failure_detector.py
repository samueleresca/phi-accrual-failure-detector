

class PhiAccrualFailureDetector:
    def __init__(self, threshold: float,
                 max_sample_size: int,
                 min_std_deviation_millis: float,
                 acceptable_heartbeat_pause_millis: int,
                 first_heartbeat_estimate_millis: int):

        """

        :param threshold:
        :param max_sample_size:
        :param min_std_deviation_millis:
        :param acceptable_heartbeat_pause_millis:
        :param first_heartbeat_estimate_millis:
        """
        self.threshold = threshold
        self.max_sample_size = max_sample_size
        self.min_std_deviation_millis = min_std_deviation_millis
        self.acceptable_heartbeat_pause_millis = acceptable_heartbeat_pause_millis
        self.first_heartbeat_estimate_millis = first_heartbeat_estimate_millis



