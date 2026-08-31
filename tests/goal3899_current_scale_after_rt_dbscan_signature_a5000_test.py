from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3899_current_scale_after_rt_dbscan_signature_a5000"
SUMMARY = ARTIFACT_DIR / "summary.json"
EXIT_CODE = ARTIFACT_DIR / "exit_code"
OLD_SUMMARY = ROOT / "docs" / "reports" / "goal3894_current_scale_with_runtime_provenance_a5000" / "summary.json"
REPORT = ROOT / "docs" / "reports" / "goal3899_current_scale_after_rt_dbscan_signature_2026-06-08.md"


class Goal3899CurrentScaleAfterRtDbscanSignatureA5000Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
        cls.old_summary = json.loads(OLD_SUMMARY.read_text(encoding="utf-8"))

    def test_full_scale_packet_passes_with_clean_runtime_provenance(self) -> None:
        self.assertEqual(EXIT_CODE.read_text(encoding="utf-8").strip(), "0")
        self.assertTrue(self.summary["all_pass"])
        self.assertEqual(self.summary["json_pass_count"], 10)
        self.assertEqual(len(self.summary["rows"]), 10)
        env = self.summary["runtime_environment"]
        self.assertEqual(env["source_commit_short"], "84c860a3")
        self.assertTrue(env["working_tree_clean"])
        self.assertEqual(env["git_status_short"], [])
        self.assertIn("NVIDIA RTX A5000", env["nvidia_smi"])

        for row in self.summary["rows"]:
            with self.subTest(row=row["row_id"]):
                self.assertEqual(row["status"], "pass")
                self.assertEqual(row["semantic_stdout_check"]["claim_flag_violations"], [])

    def test_rt_dbscan_payload_uses_segmented_count_signature_and_improves_hot_time(self) -> None:
        new_row = next(row for row in self.summary["rows"] if row["app"] == "rt_dbscan")
        old_row = next(row for row in self.old_summary["rows"] if row["app"] == "rt_dbscan")
        new_payload = json.loads((ROOT / new_row["stdout_path"]).read_text(encoding="utf-8"))
        old_payload = json.loads((ROOT / old_row["stdout_path"]).read_text(encoding="utf-8"))

        self.assertEqual(new_payload["signature"], old_payload["signature"])
        metadata = new_payload["metadata"]
        self.assertEqual(metadata["column_signature_strategy"], "numba_segmented_count_all_core_labels")
        self.assertTrue(metadata["column_signature_uses_numba_segmented_count"])
        self.assertFalse(metadata["column_signature_materializes_point_ids"])
        self.assertFalse(metadata["column_signature_materializes_core_flags"])

        old_breakdown = old_payload["metadata"]["benchmark_timing_breakdown"]
        new_breakdown = new_payload["metadata"]["benchmark_timing_breakdown"]
        self.assertLess(new_payload["elapsed_sec"], old_payload["elapsed_sec"] * 0.8)
        self.assertLess(
            new_breakdown["host_observed_sec"]["column_signature_sec"],
            old_breakdown["host_observed_sec"]["column_signature_sec"] / 4.0,
        )

    def test_report_preserves_internal_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3899",
            "not a public performance comparison",
            "does not authorize release action",
            "scale-runner process elapsed is pod-budget evidence",
            "numba_segmented_count_all_core_labels",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
