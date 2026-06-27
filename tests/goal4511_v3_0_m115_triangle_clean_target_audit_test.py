from __future__ import annotations

import importlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "docs/reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.json"
REPORT = ROOT / "docs/reports/goal4511_v3_0_m115_triangle_clean_target_audit_2026-06-17.md"
README = ROOT / "examples/benchmark_apps/triangle_counting/README.md"
INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
SCRIPT = ROOT / "scripts/goal4511_m115_triangle_clean_target_audit.py"


class Goal4511V30M115TriangleCleanTargetAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.module = importlib.import_module("scripts.goal4511_m115_triangle_clean_target_audit")
        cls.packet = cls.module.build_packet(ROOT)
        cls.checked_in = json.loads(PACKET.read_text(encoding="utf-8"))

    def test_formal_external_comparison_keeps_public_claims_blocked(self) -> None:
        external = self.packet["formal_external_comparison"]
        rows = {row["dataset"]: row for row in external["rows"]}

        self.assertEqual("rtdl.v3_0.triangle_clean_target_audit.goal4511.v1", self.packet["version"])
        self.assertTrue(external["cugraph_wins_all_rows"])
        self.assertFalse(external["public_speedup_claim_authorized"])
        self.assertEqual({"com_lj", "soc_livejournal1", "com_orkut"}, set(rows))
        self.assertGreater(rows["com_lj"]["cugraph_faster_than_m78_total"], 3.0)
        self.assertGreater(rows["soc_livejournal1"]["cugraph_faster_than_m78_total"], 4.8)
        self.assertGreater(rows["com_orkut"]["cugraph_faster_than_m78_total"], 4.8)
        self.assertGreater(rows["com_lj"]["m78_total_faster_than_author_rt_pipeline"], 7.9)
        self.assertGreater(rows["soc_livejournal1"]["m78_total_faster_than_author_rt_pipeline"], 5.9)
        self.assertGreater(rows["com_lj"]["m78_query_slower_than_author_rt_count"], 2.4)
        self.assertEqual("failed_sigkill_after_149151_ms", rows["com_orkut"]["author_rt_pipeline_status"])

    def test_current_internal_route_is_m83_sort_rle_not_local_hash(self) -> None:
        current = self.packet["current_internal_route"]
        rows = {row["dataset"]: row for row in current["rows"]}

        self.assertIn("numba_direct_sort_rle", current["route"])
        self.assertTrue(current["same_counts_all_rows"])
        self.assertTrue(current["speedup_all_rows"])
        self.assertTrue(current["route_promoted_internal_only"])
        for row in rows.values():
            self.assertTrue(row["same_count_rays_weights"], row)
            self.assertGreater(row["total_speedup"], 1.05, row)
            self.assertGreater(row["segment_build_speedup"], 1.10, row)
        self.assertGreater(rows["com_orkut"]["sort_rle_telemetry_s"], 5.0)

    def test_local_hash_is_rejected_after_integrated_rerank(self) -> None:
        decision = self.packet["local_hash_decision"]
        rows = {row["dataset"]: row for row in decision["rows"]}

        self.assertTrue(decision["summary"]["single_small_kernel_rejected"])
        self.assertTrue(decision["summary"]["prototype_branch_validated"])
        self.assertTrue(decision["summary"]["integrated_candidate_rejected"])
        self.assertTrue(decision["summary"]["all_integrated_backend_regressed"])
        self.assertTrue(decision["summary"]["all_integrated_segment_build_regressed"])
        self.assertLess(rows["com_orkut"]["coverage_2048_pct"], 25.0)
        self.assertLess(rows["com_orkut"]["coverage_16384_pct"], 72.0)
        self.assertGreater(rows["com_orkut"]["prototype_2048_speedup_vs_reference"], 1.4)
        self.assertGreater(rows["com_orkut"]["baseline_over_hybrid_total"], 1.0)
        self.assertLess(rows["com_orkut"]["baseline_over_hybrid_backend"], 1.0)
        self.assertLess(rows["com_orkut"]["baseline_over_hybrid_segment_ray_build"], 1.0)

    def test_m113_boundary_and_readiness_are_explicit(self) -> None:
        applicability = self.packet["m113_applicability"]
        readiness = self.packet["readiness"]

        self.assertFalse(applicability["current_route_should_use_m113"])
        self.assertIn("prepared ray-batch", applicability["reason"])
        self.assertIn("future coarser-batched", applicability["future_use"])
        self.assertTrue(readiness["internal_v3_clean_target_closed"])
        self.assertTrue(readiness["all_three_large_paper_rows_exact"])
        self.assertFalse(readiness["public_rt_core_speedup_claim_authorized"])
        self.assertFalse(readiness["rtdl_beats_cugraph_claim_authorized"])
        self.assertFalse(readiness["rtdl_beats_authors_pure_kernel_claim_authorized"])
        self.assertFalse(readiness["automatic_partner_selection_authorized"])

    def test_report_readme_index_and_script_capture_closeout(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        index = INDEX.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertEqual(self.packet["version"], self.checked_in["version"])
        self.assertIn("Goal4511 / V3 M115", report)
        self.assertIn("Current route should use M113: `False`", report)
        self.assertIn("Goal4511", readme)
        self.assertIn("numba_direct_sort_rle", readme)
        self.assertIn("RTDL-beats-cuGraph", readme)
        self.assertIn("Goal4511 Triangle Counting clean-target audit", index)
        self.assertIn("PACKET_VERSION", script)


if __name__ == "__main__":
    unittest.main()
