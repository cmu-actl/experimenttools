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
