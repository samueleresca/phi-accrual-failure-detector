from atomiclong import AtomicLong


class _HeartbeatHistory:

    def __init__(self, max_sample_size: int):
        self.max_sample_size = max_sample_size
        self.intervals = list()
        self.interval_sum = AtomicLong(0)
        self.squared_interval_sum = AtomicLong(0)

