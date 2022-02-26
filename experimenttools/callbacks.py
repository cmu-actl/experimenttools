"""
Callbacks for Session objects.

Callbacks can be used to run custom code when certain events happen in a
session.

"""


class SessionCallback:
    """Base class for a session callback."""

    def __init__(self):
        """Create a new sessoin callback."""
        self.session = None

    def set_session(self, session):
        """
        Set the session.

        This will automatically be called by the session a callback is
        being added to, so there is no need to call it manually.

        """
        self.session = session

    def on_session_start(self):
        """Take action at the end of the intialization of a session."""

    def on_metric_add(self, metric):
        """Take action when a new metric is added to the session."""

    def on_update(self):
        """Take action when the session outputs are being updated."""


class LambdaSessionCallback(SessionCallback):
    """
    Create a session callback with lambda functions.

    Examples
    --------
    >>> callback = LambdaSessionCallback(on_sesson_start=lambda _: print("Hello World"))
    >>> session = Session('output_dir', callbacks=[callback])
    'Hello World'

    """

    def __init__(self, on_session_start=None, on_metric_add=None, on_update=None):
        """Use lambda functions for the session callbacks."""
        if on_session_start:
            self.on_session_start = on_session_start
        if on_metric_add:
            self.on_metric_add = on_metric_add
        if on_update:
            self.on_update = on_update
        super().__init__()
