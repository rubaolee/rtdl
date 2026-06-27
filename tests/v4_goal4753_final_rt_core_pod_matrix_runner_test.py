from __future__ import annotations

import unittest
from pathlib import Path
import tempfile

from scripts.v4_goal4753_final_rt_core_pod_matrix import run_matrix


class V4Goal4753FinalRtCorePodMatrixRunnerTest(unittest.TestCase):
    def test_dry_run_exposes_thirty_command_bound_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = run_matrix(
                out_dir=Path(tmp),
                apps=None,
                versions=None,
                profile="serious",
                timeout_sec=1,
                dry_run=True,
            )

        self.assertEqual("dry_run_only_not_executed", payload["status"])
        self.assertEqual(30, payload["row_count"])
        for row in payload["rows"]:
            with self.subTest(app=row["app"], version=row["version"]):
                self.assertTrue(row["command"])
                self.assertEqual("optix_rt_core", row["backend"])
                self.assertFalse(row["embree_primary_denominator_authorized"])

    def test_dry_run_filters_without_relabeling_missing_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            payload = run_matrix(
                out_dir=Path(tmp),
                apps={"robot_collision"},
                versions={"v4_0"},
                profile="smoke",
                timeout_sec=1,
                dry_run=True,
            )

        self.assertEqual(1, payload["row_count"])
        row = payload["rows"][0]
        self.assertEqual("robot_collision", row["app"])
        self.assertEqual("v4_0", row["version"])
        self.assertEqual("runnable_protocol_template", row["route_status"])
        self.assertIn("--pose-count", row["command"])
        self.assertIn("128", row["command"])


if __name__ == "__main__":
    unittest.main()
