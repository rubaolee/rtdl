from __future__ import annotations

import unittest
from unittest import mock


class Goal1036OutlierDensityCountOracleTest(unittest.TestCase):
    def test_density_count_uses_closed_form_oracle_not_bruteforce(self) -> None:
        app = __import__("examples.rtdl_outlier_detection_app", fromlist=["run_app"])
        with mock.patch.object(app, "brute_force_outlier_rows", side_effect=AssertionError("bruteforce oracle called")):
            payload = app.run_app("cpu", copies=2000, output_mode="density_count")
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual(payload["outlier_count"], 4000)
        self.assertEqual(payload["oracle_outlier_count"], 4000)
        self.assertEqual(payload["summary_mode"], "scalar_threshold_count_oracle")

    def test_full_mode_still_uses_bruteforce_oracle(self) -> None:
        app = __import__("examples.rtdl_outlier_detection_app", fromlist=["run_app"])
        with mock.patch.object(app, "brute_force_outlier_rows", return_value=app.expected_tiled_density_rows(copies=1)) as mocked:
            payload = app.run_app("cpu", copies=1, output_mode="full")
        mocked.assert_called_once()
        self.assertTrue(payload["matches_oracle"])


if __name__ == "__main__":
    unittest.main()
