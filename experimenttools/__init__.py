"""ExperimentTools.

Tools for tracking, visualizing, and saving metrics from experiments.

`experimenttools` uses `Metric` objects to track experiment metrics, which can
then be added to a `Session` which can plot and save the metrics.
`SessionManager` objects can be used to automatically plot and save the
metrics of a `Session` periodically. Multiple experiments can be visualized
together using `SessionServer` objects.

Examples
--------
>>> import experimenttools as et
>>> import tempfile
>>> import time
>>> m0 = et.metrics.NumericMetric("m0")
>>> m1 = et.metrics.TimedNumericMetric("m1")
>>> session_dir = tempfile.mkdtemp()
>>> server_dir = tempfile.mkdtemp()
>>> session = et.Session(session_dir, name="sess", metrics=[m0, m1])
>>> manager = et.SessionManager(session, update_type="updates", update_freq=2).manage()
>>> for i in range(5):
...     m0(i)
...     m1(i**2)
...     time.sleep(0.25)

run `python -m experimenttools.sessionserver SESSION_DIR` to serve the sesssion.

"""

from experimenttools.sessions import Session, SessionManager
from experimenttools.sessionserver import SessionServer
