from __future__ import annotations

import json
import statistics
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3252_closed_shape_device_filtered_count_pod_evidence_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3252_closed_shape_device_filtered_count_probe_pod_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3252_closed_shape_device_filtered_count_probe_pod_2026-06-03.stdout"
SCRIPT = ROOT / "scripts" / "goal3252_closed_shape_device_filtered_count_probe.py"


class Goal3252ClosedShapeDeviceFilteredCountPodEvidenceTest(unittest.TestCase):
    def test_report_records_result_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Closed-Shape Device-Filtered Count Pod Evidence",
            "0.895219 ms",
            "0.785675 ms",
            "1.14x",
            "device_filtered_count",
            "still about `4.05x` slower",
            "does not authorize release",
            "paper-reproduction claims",
        ):
            self.assertIn(phrase, text)

    def test_artifact_is_clean_and_claim_bounded(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["goal"], 3252)
        self.assertEqual(data["repo_state"]["commit"], "1b12cb1660f2bcb42c8416d585c95a35291145c1")
        self.assertEqual(data["repo_state"]["source_dirty"], [])
        self.assertTrue(all(value is False for value in data["claim_boundary"].values()))

    def test_device_filtered_count_matches_exact_and_removes_materialization_phases(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertTrue(data["comparison"]["all_counts_match"])
        self.assertFalse(data["comparison"]["device_filtered_is_exact_authority"])
        self.assertTrue(data["comparison"]["requires_exact_oracle_validation_per_workload"])
        self.assertEqual(data["exact_count"]["counts"], [1430] * 9)
        self.assertEqual(data["device_filtered_count"]["counts"], [1430] * 9)
        self.assertGreater(data["comparison"]["speedup_over_exact_count"], 1.1)
        self.assertLess(data["comparison"]["speedup_over_exact_count"], 1.3)

        device_phases = data["device_filtered_count"]["phase_samples"]
        self.assertTrue(all(sample["mode"] == "device_filtered_count" for sample in device_phases))
        self.assertTrue(all(sample["candidate_write_pass"] == 0.0 for sample in device_phases))
        self.assertTrue(all(sample["candidate_download"] == 0.0 for sample in device_phases))
        self.assertTrue(all(sample["exact_refine"] == 0.0 for sample in device_phases))
        self.assertEqual([sample["raw_candidate_count"] for sample in device_phases], [1430] * 9)

        traversal_median = statistics.median(sample["candidate_count_pass"] for sample in device_phases)
        self.assertGreater(traversal_median, 0.0007)

    def test_stdout_and_script_explain_validation_boundary(self) -> None:
        stdout = STDOUT.read_text(encoding="utf-8")
        self.assertIn("[goal3252] warmup 1/2: exact=1430 device_filtered=1430", stdout)
        self.assertIn("[goal3252] repeat 9/9", stdout)

        script = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("count_device_filtered", script)
        self.assertIn("device_filtered_is_exact_authority", script)
        self.assertIn("requires_exact_oracle_validation_per_workload", script)


if __name__ == "__main__":
    unittest.main()
