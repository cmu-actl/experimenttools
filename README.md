[![Python package](https://github.com/cmu-actl/experimenttools/actions/workflows/python-package.yml/badge.svg)](https://github.com/cmu-actl/experimenttools/actions/workflows/python-package.yml)

# ExperimentTools

Tools for tracking, visualizing, and saving metrics from experiments.

## Installing

```shell
git clone https://github.com/cmu-actl/experimenttools.git
cd experimenttools
pip install -e .
```

## Getting started

`experimenttools` uses `Metric` objects to track experiment metrics, which can then be added to a `Session` which can plot and save the metrics. `SessionManagers` can be used to automatically plot and save the metrics of a `Session` periodically.

### Example
```python
import tempfile
import time

import experimenttools as et


def main():
    # Create two metrics
    m0 = et.metrics.NumericMetric("m0")
    m1 = et.metrics.TimedNumericMetric("m1")

    # Store the metrics in a session
    session_dir = tempfile.mkdtemp(prefix="experimenttools_example_session_manager_")
    session = et.Session(session_dir, metrics=[m0, m1])

    # Automatically plot the metrics every 2 updates
    with et.SessionManager(
        session, update_type="updates", update_freq=2, verbose=2
    ).manage():
        for i in range(5):
            m0(i)
            m1(i**2)
            time.sleep(0.25)


if __name__ == "__main__":
    main()
```

## Documentation

Documentation is avaialbe at https://cmu-actl.github.io/experimenttools/

## Developing

Tests use unittest and doctest.

```shell
make test
```

Use [pre-commit](https://pre-commit.com) to format and lint code before committing.

```shell
pip install pre-commit
cd experimenttools
pre-commit install
```

Docs are built using `pdoc3`.

```shell
pip install pdoc3
make docs
```
