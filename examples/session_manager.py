import tempfile
import time

import experimenttools as et


def main():
    m0 = et.metrics.NumericMetric("m0")
    m1 = et.metrics.TimedNumericMetric("m1")

    session_dir = tempfile.mkdtemp(prefix="experimenttools_example_session_manager_")
    session = et.Session(session_dir, metrics=[m0, m1])
    with et.SessionManager(
        session, update_type="updates", update_freq=2, verbose=2
    ).manage():
        for i in range(5):
            m0(i)
            m1(i ** 2)
            time.sleep(0.25)


if __name__ == "__main__":
    main()
