# phi-accrual-failure-detector

[![Pipeline](https://github.com/samueleresca/phi-accrual-failure-detector/actions/workflows/tests.yml/badge.svg)](https://github.com/samueleresca/phi-accrual-failure-detector/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/samueleresca/phi-accrual-failure-detector/branch/main/graph/badge.svg?token=0PXF0584P3)](https://codecov.io/gh/samueleresca/phi-accrual-failure-detector)


A python port of the [Akka's (φ) Accrual failure detector implementation](https://github.com/akka/akka/blob/master/akka-remote/src/main/scala/akka/remote/PhiAccrualFailureDetector.scala).


## Getting started

You can import the library into the project using:
```shell
pip install py-accrual-failure-detector
```
You can use the package as follows:

```python
from phi_accrual_failure_detector import PhiAccrualFailureDetector

failure_detector = PhiAccrualFailureDetector(
            threshold=3,
            max_sample_size=1000,
            min_std_deviation_millis=10,
            acceptable_heartbeat_pause_millis=0,
            first_heartbeat_estimate_millis=1000
        )

failure_detector.heartbeat() # sends an heartbeat
failure_detector.heartbeat() # sends an heartbeat
failure_detector.heartbeat() # sends an heartbeat

node_is_available = failure_detector.is_available()
```

## References 

- [The ϕ Accrual Failure Detector - Naohiro Hayashibara, Xavier Défago, Rami Yared1 and Takuya Katayama](https://dspace.jaist.ac.jp/dspace/bitstream/10119/4784/1/IS-RR-2004-010.pdf)

- [Cassandra - A Decentralized Structured Storage System](https://www.cs.cornell.edu/projects/ladis2009/papers/lakshman-ladis2009.pdf)

- [Phi Accrual Failure Detector - Akka documentation](https://doc.akka.io/docs/akka/current/typed/failure-detector.html)

- [akka/akka source code](https://github.com/akka/akka/blob/master/akka-remote/src/main/scala/akka/remote/PhiAccrualFailureDetector.scala)

- [A logistic approximation to the cumulative normal distribution](https://core.ac.uk/download/pdf/41787448.pdf)
