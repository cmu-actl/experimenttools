"""Keep track of an experiment session.

`Sesssion` objects can hold a set of metrics so they can be plotted and
serialized together.

`SessionManager` objects can manage the automatic periodic updating of
`Session` outputs.

"""
import time
from datetime import datetime
from pathlib import Path

import holoviews as hv

from experimenttools.callbacks import LambdaSessionCallback
from experimenttools.metrics import PlottableMetric, SerializableMetric

hv.extension("bokeh")


class Session:
    """Stores, plots, and serializes a collection of `Metric` objects.

    Examples
    --------
    >>> import experimenttools as et
    >>> import tempfile
    >>> m0 = et.metrics.NumericMetric("m0")
    >>> m1 = et.metrics.NumericMetric("m1")
    >>> session_dir = tempfile.mkdtemp()
    >>> session = et.Session(session_dir, metrics=[m0, m1])
    >>> for i in range(5):
    ...     m0(i)
    ...     m1(2*i)
    >>> session.plot() # Writes plots to 'experiment/index.html'
    >>> session.serialize() # Writes to 'experiments/serialized'

    """

    def __init__(
        self,
        output_dir,
        name=None,
        metrics=None,
        callbacks=None,
        plot_metrics=True,
        serialize_metrics=True,
    ):
        """Create a new experiment session.

        Parameters
        ----------
        output_dir: path-like object
                Directory to store session data in.
        name: str
                Name of the session, used if serving multiple sessions.
        metrics: list of Metric
                The metrics to mointor.
        callbacks: list of Sessioncallback
                callbacks to add to the session.
        plot_metrics: bool
                Whether or not to plots metrics.
        serialize_metrics: bool
                Whether or not to save metrics to files.

        """
        self.output_dir = Path(output_dir)
        self.name = name

        self.callbacks = []
        if callbacks:
            for callback in callbacks:
                self.add_callback(callback)
        self.call_callbacks(lambda h: h.on_session_start())

        self._metrics = []
        if metrics:
            for metric in metrics:
                self.add_metric(metric)

        self._update_actions = []
        if plot_metrics:
            self._update_actions.append(self.plot)
        if serialize_metrics:
            self._update_actions.append(self.serialize)

    @property
    def metrics(self):
        """Get the metrics tracked by this session."""
        return self._metrics

    def add_metric(self, metric):
        """Add a metric to the session."""
        if metric.name in [m.name for m in self._metrics]:
            raise ValueError(f"Session already has metric with name: {metric.name}")
        self._metrics.append(metric)
        self.call_callbacks(lambda h: h.on_metric_add(metric))

    def add_callback(self, callback):
        """Add a `SessionCallback` to the session."""
        callback.set_session(self)
        self.callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove a `SessionCallback` from the session."""
        self.callbacks.remove(callback)

    def call_callbacks(self, fn):
        """Call a function with each callback as an argument."""
        for callback in self.callbacks:
            fn(callback)

    def update(self):
        """Update the session outputs."""
        for action in self._update_actions:
            action()
        self.call_callbacks(lambda h: h.on_update())

    def plot(self):
        """Plot all plottable metrics."""
        self.output_dir.mkdir(exist_ok=True, parents=True)
        plots = []
        for metric in self._metrics:
            if isinstance(metric, PlottableMetric):
                plots.append(metric.plot())
        layout = hv.Layout(plots)
        hv.save(layout, self.output_dir / "index.html")

    def serialize(self):
        """Serialize all serializable metrics."""
        self.output_dir.mkdir(exist_ok=True, parents=True)
        serialize_dir = self.output_dir / "serialized"
        serialize_dir.mkdir(exist_ok=True)
        for metric in self._metrics:
            if isinstance(metric, SerializableMetric):
                metric.serialize(serialize_dir / metric.name)


class SessionManager:
    """Manages the updating of a `Session`.

    A `SessionManager` does not begin managing until `manage` is called.
    At that point, it will continue managing until `close` is called.
    Alternatively, the `SesssionManager` can be used as a context manager.

    Examples
    --------
    >>> import experimenttools as et
    >>> import tempfile
    >>> m0 = et.metrics.NumericMetric("m0")
    >>> session_dir = tempfile.mkdtemp()
    >>> session = et.Session(session_dir, metrics=[m0])
    >>> manager = et.SessionManager(session, update_type="updates")
    >>> _ = manager.manage()
    >>> for i in range(120):
    ...     m0(i) # m0 will be plotted and serialized every 60th update
    >>> manager.close() # Stop tracking metric updates
    >>> for i in range(120):
    ...     m0(i) # Session will not be updated automatically because manager is closed

    As a context manager
    >>> with SessionManager(session, update_type="updates").manage():
    ...     for i in range(120):
    ...         m0(i)
    >>> m0(1) # Manager no longer managing the session

    >>> manager = SessionManager(session, update_type="updates")
    >>> with manager.manage():
    ...     for i in range(120):
    ...         m0(i)

    """

    def __init__(self, session, update_type="seconds", update_freq=60, verbose=0):
        """Create a new session manager.

        Parameters
        ----------
        session: Session
                The session to manage.
        update_type: str
                Either 'seconds' or 'updates'. If 'seconds', session will be
                updated every `update_freq` seconds. If 'updates' session
                will be updated every `update_freq` total updates to
                metrics.
        update_freq: int
                The frequency for updating the session.
        verbose: int
                0, 1, or 2. 0 = silent, 1 = warnings, 2 = info.

        """
        self._verbose = verbose
        self._session = session
        self._managing = False
        self._session_callback = LambdaSessionCallback(
            on_metric_add=lambda m: m.add_callback(self.process_metric_update)
        )
        if update_type == "seconds":
            self._last_update_seconds = time.time()
        elif update_type == "updates":
            self._num_updates = 0
        else:
            raise ValueError(
                f"Uknown value for parameter 'update_type': '{update_type}'"
            )
        self._update_freq = update_freq
        self._log(2, f"Session outputting to {self._session.output_dir}")

    def _log(self, level, msg):
        if self._verbose >= level:
            print(f"{datetime.now()}: expeexperimenttools.SessionManager] {msg}")

    def manage(self):
        """Beginning managing the sesssion.

        Allows the manager to update the session when metrics are updated.

        Raises
        ------
        RuntimeError
                If the manager has already begun to manage the session.

        """
        self._log(2, "Beginning management")
        self._managing = True
        self._session.add_callback(self._session_callback)
        for m in self._session.metrics:
            m.add_callback(self.process_metric_update)
        return self

    def close(self):
        """Stop managing the session.

        The manager will no longer update the session when metrics have
        been updated.

        Raises
        ------
        RuntimeError
                If the manager is not currently managing the session.

        """
        self._log(2, "Ending management")
        self._session.remove_callback(self._session_callback)
        for m in self._session.metrics:
            m.remove_callback(self.process_metric_update)

    @property
    def session(self):
        """Get the sesssion being managed."""
        return self._session

    def __enter__(self):
        """Use the session manager as a context manager."""
        if not self._managing:
            raise RuntimeError("Use 'with manager.manage()' for context management")

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Close the session manager upon exiting the context."""
        self.close()

    def process_metric_update(self, _):
        """Update the session if the update frequency has been reached."""
        try:
            if time.time() - self._last_update_seconds >= self._update_freq:
                self._log(2, "Updating session")
                self._session.update()
                self._last_update_seconds = time.time()
        except AttributeError:
            if self._num_updates + 1 >= self._update_freq:
                self._log(2, "Updating session")
                self._session.update()
                self._num_updates = 0
            else:
                self._num_updates += 1
