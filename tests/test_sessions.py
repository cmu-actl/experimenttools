import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

import experimenttools as et


class TestSessions(unittest.TestCase):
    def test_session(self):
        m0 = et.metrics.NumericMetric("m0")
        m1 = et.metrics.TimedNumericMetric("m1")

        with tempfile.TemporaryDirectory(prefix="experimenttools_tests_") as tmpdir:
            session = et.Session(tmpdir, metrics=[m0, m1])

            m0_expected = []
            m1_expected = []
            for i in range(5):
                m0(i)
                m0_expected.append(i)
                m1(i * i)
                m1_expected.append(i * i)

            session.update()

            tmpdir = Path(tmpdir)
            self.assertTrue((tmpdir / "index.html").is_file())
            with open(tmpdir / "serialized" / "m0.txt") as f:
                m0_actual = [int(l) for l in f.read().split()[1:]]
            self.assertListEqual(m0_expected, m0_actual)
            with open(tmpdir / "serialized" / "m1.txt") as f:
                m1_actual = [int(l.split(",")[-1]) for l in f.read().split()[1:]]
            self.assertListEqual(m1_expected, m1_actual)

    def test_session_callbacks(self):
        m0 = et.metrics.NumericMetric("m0")
        m1 = et.metrics.TimedNumericMetric("m1")

        mock = Mock()

        callback = et.callbacks.LambdaSessionCallback(
            on_session_start=mock.method,
            on_metric_add=mock.method,
            on_update=mock.method,
        )
        with tempfile.TemporaryDirectory(prefix="experimenttools_tests_") as tmpdir:
            session = et.Session(tmpdir, metrics=[m0], callbacks=[callback])

            self.assertEqual(mock.method.call_count, 2)
            session.add_metric(m1)
            self.assertEqual(mock.method.call_count, 3)
            session.update()
            self.assertEqual(mock.method.call_count, 4)

    def test_session_manager(self):
        m0 = et.metrics.NumericMetric("m0")

        with tempfile.TemporaryDirectory(prefix="experimenttools_tests_") as tmpdir:
            session = et.Session(tmpdir, metrics=[m0])
            et.SessionManager(session, update_type="updates", update_freq=2).manage()
            m0_expected = []
            for i in range(5):
                m0(i)
                m0_expected.append(i)

            # Last metric update should not have triggered a session update
            m0_expected = m0_expected[:-1]
            tmpdir = Path(tmpdir)
            self.assertTrue((tmpdir / "index.html").is_file())
            with open(tmpdir / "serialized" / "m0.txt") as f:
                m0_actual = [int(l) for l in f.read().split()[1:]]
            self.assertListEqual(m0_expected, m0_actual)

    def test_session_manager_close(self):
        m0 = et.metrics.NumericMetric("m0")

        with tempfile.TemporaryDirectory(prefix="experimenttools_tests_") as tmpdir:
            session = et.Session(tmpdir, metrics=[m0])
            manager = et.SessionManager(
                session, update_type="updates", update_freq=2
            ).manage()
            m0_expected = []
            for i in range(6):
                m0(i)
                m0_expected.append(i)

            manager.close()
            # Should not triggered a session updates
            for i in range(6):
                m0(i * i)

            tmpdir = Path(tmpdir)
            self.assertTrue((tmpdir / "index.html").is_file())
            with open(tmpdir / "serialized" / "m0.txt") as f:
                m0_actual = [int(l) for l in f.read().split()[1:]]
            self.assertListEqual(m0_expected, m0_actual)

    def test_session_manager_context(self):
        m0 = et.metrics.NumericMetric("m0")

        with tempfile.TemporaryDirectory(prefix="experimenttools_tests_") as tmpdir:
            session = et.Session(tmpdir, metrics=[m0])
            with et.SessionManager(
                session, update_type="updates", update_freq=2
            ).manage():
                m0_expected = []
                for i in range(6):
                    m0(i)
                    m0_expected.append(i)

            # Should not triggered a session updates
            for i in range(6):
                m0(i * i)

            tmpdir = Path(tmpdir)
            self.assertTrue((tmpdir / "index.html").is_file())
            with open(tmpdir / "serialized" / "m0.txt") as f:
                m0_actual = [int(l) for l in f.read().split()[1:]]
            self.assertListEqual(m0_expected, m0_actual)

    def test_session_server(self):

        m0 = et.metrics.NumericMetric("m0")
        m1 = et.metrics.NumericMetric("m1")

        with tempfile.TemporaryDirectory(prefix="experimenttools_tests_") as tmpdir:
            tmpdir = Path(tmpdir)
            session_0 = et.Session(tmpdir / "session_0", name="session_0", metrics=[m0])
            session_1 = et.Session(tmpdir / "session_1", name="session_1", metrics=[m1])
            server = et.SessionServer([session_0, session_1], tmpdir / "server")

            for i in range(5):
                m0(i)
                m1(i * i)

            session_0.update()
            session_1.update()

            for session in [session_0, session_1]:
                with open(session.output_dir / "index.html") as f:
                    session_html = f.read()
                with open(server.output_dir / f"{session.name}.html") as f:
                    server_html = f.read()
                self.assertEqual(session_html, server_html)
