"""Track the values of metrics.

Metrics can be created and then their current value can be updated by calling
them. Additionally, they can register callbacks to call every time the current
value is updated. Certain types of metrics can also be plotted and serialized.
Metric management can be automated using `Session` and `SessionManager`
objects.

Examples
--------
>>> import experimenttools as et
>>> m = et.metrics.NumericMetric("m")
>>> m(2)
>>> m.value
2
>>> m(3)
>>> m.value
3
>>> m.values
[2, 3]
>>> import holoviews as hv
>>> import tempfile
>>> f = tempfile.NamedTemporaryFile(suffix=".html")
>>> hv.save(m.plot(), f.name)

"""
from time import time as curr_time

import holoviews as hv


class Metric:
    """Base class for metrics. Does not actually track a value.

    Implements the basic callback functionality. `Metric` objects can be
    added to `Session` objects so that the session can perform some
    action every time the metric is updated.

    """

    def __init__(self, name, initial_value=None, callbacks=None):
        """Create a new metric.

        Parameters
        ----------
        name: str
                The name of the metric.
        initial_value
                The initial value of the metric.
                >>> m = Metric("example_metric", 2)

                is equivalent to running
                >>> m = Metric("example_metric")
                >>> m(2)

        callbacks: list of callable
                Callbacks to run at the end of `__call__`.

        """
        self.name = name
        self._callbacks = []
        if callbacks:
            for callback in callbacks:
                self.add_callback(callback)
        if initial_value is not None:
            self(initial_value)

    def __call__(self, *args, **kwargs):
        """Run all callbacks after updating metric."""
        for callback in self._callbacks:
            callback(self)

    def add_callback(self, callback):
        """Add a new callback."""
        self._callbacks.append(callback)

    def remove_callback(self, callback):
        """Remove a callback."""
        self._callbacks.remove(callback)


class SerializableMetric(Metric):
    """Base class for metrics that can be serialized to a file.

    `SerializableMetric` subclasses must implement `serialize(self,
    file)` which stores the current progess of a metric to a file. When
    used in a `Session`, the `file` argument will be the same every time
    the method is called, so the subclass can choose to append to the
    file instead of rewriting every time. Additionally, the subclass is
    responsible for appending the correct suffix to `file`.

    """

    def serialize(self, file):
        """Write metric history to a file."""
        raise NotImplementedError


class PlottableMetric(Metric):
    """Base class for metrics that can be plotted.

    `PlottableMetric` subclasses must implement `plot(self)` which
    returns a `holoviews.Element` plot of the current data.

    """

    def plot(self):
        """Plot metric history."""
        raise NotImplementedError


class TimedMetric(Metric):
    """Base class for capturing the time at which a metric is updated.

    Each time the metric is called with a new value, the current time
    offset by the time when the metric was first called is added to a
    list.

    """

    def __init__(self, *args, **kwargs):
        self._times = []
        self._start_time = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        """Record the time at which the metric is updated."""
        self._times.append(self.elapsed_time)
        super().__call__(*args, **kwargs)

    @property
    def start_time(self):
        """Get the seconds since epoch at which metric was first updated."""
        if not self._start_time:
            self._start_time = curr_time()
        return self._start_time

    @property
    def elapsed_time(self):
        """Get the seconds since the start time."""
        return curr_time() - self.start_time

    @property
    def times(self):
        """Get the list of times at which the metric was updated."""
        return self._times


class NumericMetric(SerializableMetric, PlottableMetric):
    """Track the change of a numeric metric."""

    def __init__(self, *args, **kwargs):
        self._values = []
        self._serialization_idx = 0
        super().__init__(*args, **kwargs)

    def __call__(self, value, *args, **kwargs):
        """Update the current metric value with `value`."""
        self._values.append(value)
        super().__call__(value, *args, **kwargs)

    def __iadd__(self, val):
        """Add to the most recent value of a numeric metric."""
        self(self.value + val)
        return self

    def __isub__(self, val):
        """Subtract from the most recent value of a numeric metric."""
        self(self.value - val)
        return self

    def __imul__(self, val):
        """Multiply the most recent value of a numeric metric."""
        self(self.value * val)
        return self

    def __ifloordiv__(self, val):
        """Floor divide the most recent value of a numeric metric."""
        self(self.value // val)
        return self

    def __idiv__(self, val):
        """Divide the most recent value of a numeric metric."""
        self(self.value / val)
        return self

    def __itruediv__(self, val):
        """Divide the most recent value of a numeric metric."""
        self(self.value / val)
        return self

    def __imod__(self, val):
        """Mod the most recent value of a numeric metric."""
        self(self.value % val)
        return self

    def __ipow__(self, val):
        """Pow the most recent value of a numeric metric."""
        self(self.value ** val)
        return self

    def __ilshift__(self, val):
        """Lshift the most recent value of a numeric metric."""
        self(self.value << val)
        return self

    def __irshift__(self, val):
        """Rshift the most recent value of a numeric metric."""
        self(self.value >> val)
        return self

    def __iand__(self, val):
        """And the most recent value of a numeric metric."""
        self(self.value & val)
        return self

    def __ior__(self, val):
        """Or the most recent value of a numeric metric."""
        self(self.value | val)
        return self

    def __ixor__(self, val):
        """Xor the most recent value of a numeric metric."""
        self(self.value ^ val)
        return self

    @property
    def value(self):
        """Get the current metric value."""
        try:
            return self._values[-1]
        except IndexError as e:
            raise ValueError("Metric has not been assigned a value yet.") from e

    @property
    def values(self):
        """Get the list of recorded metric values."""
        return self._values

    def serialize(self, file):
        """Write metric history to a file, one line per value."""
        with open(f"{file}.txt", "a") as f:
            if self._serialization_idx == 0:
                f.write("value\n")
            for value in self._values[self._serialization_idx :]:
                f.write(f"{value}\n")
                self._serialization_idx += 1

    def plot(self):
        """Plot metric history as a line plot."""
        return hv.Curve(
            (range(len(self._values)), self._values), "Iteration", self.name
        )


class TimedNumericMetric(NumericMetric, TimedMetric):
    """Track the change of a numeric metric over time."""

    def serialize(self, file):
        """Write metric history to a file as a csv (time,value)."""
        with open(f"{file}.txt", "a") as f:
            if self._serialization_idx == 0:
                f.write("time,value\n")
            for time, value in zip(
                self._times[self._serialization_idx :],
                self._values[self._serialization_idx :],
            ):
                f.write(f"{time},{value}\n")
                self._serialization_idx += 1

    def plot(self):
        """Plot metric history as a line plot with seconds as the x-axis."""
        return hv.Curve((self._times, self._values), "Seconds", self.name)
