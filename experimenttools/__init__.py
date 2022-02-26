"""
ExperimentTools.

Tools for tracking, visualizing, and saving metrics from experiments.

`experimenttools` uses `Metric` objects to track experiment metrics, which can
then be added to a `Session` which can plot and save the metrics.
`SessionManagers` can be used to automatically plot and save the metrics of a
`Session` periodically.

Examples
--------
>>> import experimenttools as et
>>> import tempfile
>>> import time
>>> m0 = et.metrics.NumericMetric("m0")
>>> m1 = et.metrics.TimedNumericMetric("m1")
>>> session_dir = tempfile.mkdtemp()
>>> session = et.Session(session_dir, metrics=[m0, m1])
>>> with et.SessionManager(session, update_type="updates", update_freq=2).manage():
...     for i in range(5):
...         m0(i)
...         m1(i**2)
...         time.sleep(0.25)

"""

from experimenttools.sessions import Session, SessionManager
