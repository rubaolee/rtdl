from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4026_partition_convergence_root_work_estimator.py"
ARTIFACT = ROOT / "docs" / "reports" / "goal4026_partition_convergence_root_work_estimate.json"
REPORT = ROOT / "docs" / "reports" / "goal4026_partition_convergence_root_work_estimate_2026-06-08.md"


class Goal4026PartitionConvergenceRootWorkEstimatorTest(unittest.TestCase):
    def test_committed_artifact_has_conservative_reduction_rows(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal4026")
        self.assertTrue(data["estimator_boundary"]["diagnostic_only"])
        self.assertFalse(data["estimator_boundary"]["timing_claim_authorized"])
        by_profile = {row["profile"]: row for row in data["rows"]}
        self.assertEqual(set(by_profile), {"clustered3d", "road3d", "ngsim_dense"})
        self.assertGreater(by_profile["clustered3d"]["estimated_root_read_reduction_ratio"], 0.5)
        self.assertGreater(by_profile["road3d"]["estimated_root_read_reduction_ratio"], 0.5)
        self.assertGreater(by_profile["ngsim_dense"]["estimated_root_read_reduction_ratio"], 0.0)
        for row in data["rows"]:
            self.assertGreater(row["estimated_partition_route_root_read_upper"], 0)
            self.assertLess(row["estimated_partition_route_root_read_upper"], row["current_root_find_invocations"])

    def test_script_reproduces_artifact_shape(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = pathlib.Path(tmp) / "estimate.json"
            subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(out)],
                cwd=ROOT,
                check=True,
            )
            data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal4026")
        self.assertEqual(len(data["rows"]), 3)
        self.assertIn("estimated_safe_full_partition_union_root_read_upper", data["rows"][0])

    def test_report_documents_diagnostic_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for fragment in (
            "diagnostic only",
            "not a timing claim",
            "safe-full partition pair",
            "ambiguous root reads",
            "does not add a native ABI",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
