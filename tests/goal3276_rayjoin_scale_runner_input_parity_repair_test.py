from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3276_rayjoin_scale_runner_input_parity_repair_2026-06-03.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3276_scale_pod"


class Goal3276RayJoinScaleRunnerInputParityRepairTest(unittest.TestCase):
    def test_report_records_invalid_first_attempt_and_repaired_scale_run(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "RayJoin inputs were still hard-coded",
            "must not be used as performance evidence",
            "Corrected Pod Scale Diagnostic",
            "true same-input RayJoin/RTDL comparisons",
            "not a simple monotonic function of slice size",
        ):
            self.assertIn(phrase, report)

    def test_scale_artifacts_are_source_clean_and_input_matched(self) -> None:
        expected_counts = {
            "128": {"lsi": 0, "pip": 360},
            "256": {"lsi": 73, "pip": 717},
            "384": {"lsi": 246, "pip": 1083},
            "512": {"lsi": 294, "pip": 1430},
        }
        for slice_id, counts in expected_counts.items():
            path = ARTIFACT_DIR / f"slice_{slice_id}.json"
            self.assertTrue(path.exists(), str(path))
            artifact = json.loads(path.read_text(encoding="utf-8"))

            self.assertEqual(artifact["source_dirty"], [])
            self.assertEqual(artifact["status"], "pass_with_optimization_gap")
            self.assertIn("dd30defe", artifact["rtdl_commit"])
            self.assertIn(f"count{slice_id}.cdb", artifact["rayjoin"]["lsi"]["input_poly1"])
            self.assertIn(f"count{slice_id}.cdb", artifact["rayjoin"]["lsi"]["input_poly2"])
            self.assertIn(f"count{slice_id}.cdb", artifact["rayjoin"]["pip"]["input_poly1"])
            self.assertIn(f"count{slice_id}.cdb", artifact["rayjoin"]["pip"]["input_poly2"])

            lsi = next(row for row in artifact["comparisons"] if row["workload"] == "lsi")
            pip = next(row for row in artifact["comparisons"] if row["workload"] == "pip")
            self.assertEqual(lsi["count_contract_status"], "matching_visible_lsi_count")
            self.assertEqual(lsi["rayjoin_visible_count"], counts["lsi"])
            self.assertEqual(lsi["rtdl_count"], counts["lsi"])
            self.assertEqual(pip["count_contract_status"], "rayjoin_pip_count_not_visible")
            self.assertEqual(pip["rtdl_count"], counts["pip"])
            self.assertGreater(pip["rtdl_over_rayjoin_query_ratio"], 1.0)

            boundary = artifact["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])


if __name__ == "__main__":
    unittest.main()

