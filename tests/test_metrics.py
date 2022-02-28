import tempfile
import unittest

import experimenttools as et


class TestMetrics(unittest.TestCase):
    def test_numeric_metric_ops(self):
        m0 = et.metrics.NumericMetric("m0")
        with self.assertRaises(ValueError):
            m0.value

        m0 = et.metrics.NumericMetric("m0", 0)
        m0 += 1
        self.assertEqual(m0.value, 1)
        m0 *= 3
        self.assertEqual(m0.value, 3)
        m0 /= 3
        self.assertEqual(m0.value, 1)

    def test_parameter_set_metric(self):
        data = {"a": 1, "b": "c"}
        m = et.metrics.ParameterSetMetric("test", data)
        with tempfile.NamedTemporaryFile(
            prefix="experimenttools_tests_", mode="r", suffix=".csv"
        ) as f:
            m.serialize(f.name.split(".")[0])
            read_data = {
                l.split(",")[0]: l.split(",")[1] for l in f.read().split("\n")[1:] if l
            }

        # Will be string when read back in
        data["a"] = "1"
        self.assertDictEqual(data, read_data)
