import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3548_v2_9_a5000_same_contract_repeat_evidence_2026-06-06.md"
FULL_SUMMARY = (
    ROOT
    / "docs"
    / "reports"
    / "goal3548_v2_9_repeat_hook_10s_rerun_a5000_compact_calibrated3"
    / "summary.json"
)
RTNN_SUPPLEMENT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3548_v2_9_repeat_hook_10s_rerun_a5000_rtnn_supplement"
    / "summary.json"
)
ROBOT_APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "robot_collision"
    / "rtdl_robot_collision_benchmark_app.py"
)
V23_PATCH = (
    ROOT
    / "docs"
    / "patches"
    / "goal3547_v23_measurement_overlay_repeat_hooks_2026-06-06.patch"
)


class Goal3548A5000SameContractRepeatEvidenceTest(unittest.TestCase):
    def test_full_packet_is_present_and_claim_bounded(self) -> None:
        data = json.loads(FULL_SUMMARY.read_text(encoding="utf-8"))
        self.assertEqual(data["gpu"], "NVIDIA RTX A5000, 580.126.09, 24564 MiB")
        self.assertEqual(data["summary"]["row_count"], 11)
        self.assertEqual(data["summary"]["target_met_by_plan_pair_count"], 11)
        self.assertFalse(data["claim_boundary"]["release_authorized"])
        self.assertFalse(data["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(data["claim_boundary"]["true_zero_copy_claim_authorized"])
        for comparison in data["comparisons"]:
            self.assertFalse(comparison["claim_boundary"]["release_authorized"])
            self.assertFalse(comparison["claim_boundary"]["public_speedup_claim_authorized"])

    def test_full_packet_only_observed_gap_is_rtnn_v23_and_supplement_closes_it(self) -> None:
        data = json.loads(FULL_SUMMARY.read_text(encoding="utf-8"))
        misses = [
            (row["lane"], row["case_id"], row["execution"]["observed_measured_sec"])
            for row in data["rows"]
            if not row["execution"]["target_met_by_observed_sum"]
        ]
        self.assertEqual(
            misses,
            [("v23", "rtnn_optix_prepared_3d_ranked_summary", misses[0][2])],
        )
        self.assertGreater(misses[0][2], 6.0)

        supplement = json.loads(RTNN_SUPPLEMENT.read_text(encoding="utf-8"))
        self.assertEqual(supplement["schema"], "rtdl.goal3548.rtnn_supplement.v1")
        self.assertEqual(supplement["repeat"], 12000)
        self.assertGreater(supplement["speedup_v28_vs_v23"], 1.09)
        for run in supplement["runs"]:
            self.assertTrue(run["ok"])
            self.assertGreater(run["observed_sec"], 10.0)
            self.assertEqual(run["returncode"], 0)

    def test_robot_repeat_ledger_is_scalar_only_in_current_and_v23_overlay_patch(self) -> None:
        current_source = ROBOT_APP.read_text(encoding="utf-8")
        patch_text = V23_PATCH.read_text(encoding="utf-8")

        self.assertIn('"prepared_scene_used": bool(result["prepared_scene_used"])', current_source)
        self.assertIn('"prepared_query_run_index": int(result.get("prepared_query_run_index", 0))', current_source)
        self.assertNotIn('"backend_result": result', current_source)
        self.assertNotIn('"flags": flags', current_source)

        self.assertIn('-                    "backend_result": result,', patch_text)
        self.assertIn('+                    "prepared_scene_used": bool(result["prepared_scene_used"]),', patch_text)
        self.assertIn('-                    "flags": flags,', patch_text)

    def test_report_documents_provenance_and_no_release_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        required = [
            "internal evidence, accept-with-boundary",
            "Provenance Boundary",
            "does not authorize",
            "v2.9 release",
            "public speedup claims",
            "RTNN supplement",
            "rt_dbscan",
            "robot_collision",
        ]
        for phrase in required:
            self.assertIn(phrase, report)


if __name__ == "__main__":
    unittest.main()

