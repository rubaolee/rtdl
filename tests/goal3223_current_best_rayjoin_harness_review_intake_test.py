from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3223_claude_review_intake_current_best_rayjoin_harness_2026-06-03.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3223_spatial_rayjoin_current_best_count_harness_2026-06-03.json"
STDOUT = ROOT / "docs" / "reports" / "goal3223_spatial_rayjoin_current_best_count_harness_2026-06-03.stdout"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal3221_claude_review_goal3220_current_best_rayjoin_count_harness_2026-06-03.md"


class Goal3223CurrentBestRayJoinHarnessReviewIntakeTest(unittest.TestCase):
    def test_report_intakes_claude_findings_and_records_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        review = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", review)
        self.assertIn("L1: Hardware metadata reduced from the Goal3218 standard", review)
        self.assertIn("L2: `overlay_seed` expected count of 0 is a trivially weak parity test", review)
        self.assertIn("Goal3223 addresses both", report)
        self.assertIn("active_seed_count", report)
        self.assertIn("does not authorize release", report)
        self.assertIn("Row overlay continuation is still deferred", report)

    def test_pod_artifact_records_v2_schema_and_stronger_metadata(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["source_commit"], "824dc01950e629f307f03ef83233a58f7e87d4ce")
        self.assertEqual(data["harness_version"], "rtdl.goal3220.spatial_rayjoin_current_best_count_harness.v2")
        self.assertEqual(data["dataset_policy"], "per_workload_defaults_unless_overridden")
        self.assertEqual(data["gpu"], "NVIDIA A40, 570.211.01")
        self.assertIn("CUDA Version", data["cuda_driver_query"])
        self.assertIn("release 12.8", data["nvcc_version"])
        self.assertEqual(data["rtdl_optix_library"], "/root/rtdl_goal3151/build/librtdl_optix.so")

        boundary = data["claim_boundary"]
        self.assertTrue(boundary["canonical_harness_candidate"])
        self.assertTrue(boundary["tier_a_count_or_parity_only"])
        self.assertTrue(boundary["row_overlay_continuation_deferred_tier_b"])
        self.assertFalse(boundary["public_speedup_claim_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["true_zero_copy_claim_authorized"])
        self.assertFalse(boundary["paper_reproduction_claim_authorized"])
        self.assertFalse(boundary["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(boundary["native_engine_customization"])

    def test_pod_artifact_uses_nonzero_overlay_active_seed_contract(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        rows = {row["workload"]: row for row in data["rows"]}

        self.assertEqual(rows["pip"]["expected_count"], 6)
        self.assertEqual(rows["pip"]["observed_count"], 6)
        self.assertEqual(rows["lsi"]["expected_count"], 1)
        self.assertEqual(rows["lsi"]["observed_count"], 1)

        overlay = rows["overlay_seed"]
        self.assertEqual(overlay["dataset"], "derived/authored_overlay_squares_tiled_x64")
        self.assertEqual(overlay["expected_count"], 64)
        self.assertEqual(overlay["observed_count"], 64)
        self.assertEqual(overlay["prepared_output_contract"], "overlay_active_pair_dependency_count")
        self.assertTrue(overlay["matches_cpu_reference"])
        self.assertEqual(set(overlay["observed_counts"]), {64})

    def test_stdout_matches_json_payload(self) -> None:
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        stdout = json.loads(STDOUT.read_text(encoding="utf-8"))

        self.assertEqual(stdout, artifact)


if __name__ == "__main__":
    unittest.main()
