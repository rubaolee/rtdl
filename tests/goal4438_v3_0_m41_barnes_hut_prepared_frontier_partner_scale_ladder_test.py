from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.md"
EVIDENCE = ROOT / "docs/reports/goal4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder_2026-06-16.json"
PARTNER_MATRIX = ROOT / "docs/learn/benchmark_partner_reference_matrix.md"
EVIDENCE_INDEX = ROOT / "docs/learn/benchmark_evidence_index.md"
RT_CORE_MATRIX = ROOT / "docs/learn/rt_core_evidence_matrix.md"

sys.path.insert(0, str(ROOT / "src"))


class Goal4438V30M41BarnesHutPreparedFrontierPartnerScaleLadderTest(unittest.TestCase):
    def test_scale_ladder_json_records_same_contract_numba_win_without_public_claims(self) -> None:
        payload = json.loads(EVIDENCE.read_text(encoding="utf-8"))

        self.assertEqual(
            payload["goal"],
            "4438_v3_0_m41_barnes_hut_prepared_frontier_partner_scale_ladder",
        )
        self.assertEqual(payload["repeat_count"], 5)
        self.assertEqual([row["point_count"] for row in payload["rows"]], [8192, 16384, 32768])
        self.assertTrue(payload["claims"]["same_frontier_contract"])
        self.assertTrue(payload["claims"]["compares_cupy_and_numba_partners"])
        self.assertTrue(payload["claims"]["prepared_lookup_columns_resident"])
        self.assertFalse(payload["claims"]["frontier_rows_materialized_on_host"])
        self.assertFalse(payload["claims"]["contribution_rows_materialized_on_host"])
        self.assertFalse(payload["claims"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claims"]["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["claims"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claims"]["true_zero_copy_claim_authorized"])

        for row in payload["rows"]:
            comparison = row["comparison"]
            self.assertNotIn("row_count", comparison)
            self.assertIsInstance(comparison["frontier_row_count"], int)
            self.assertGreater(comparison["numba_partner_speedup_vs_cupy"], 6.0)
            self.assertGreater(comparison["numba_hot_speedup_vs_cupy"], 1.3)
            self.assertLess(
                comparison["numba_partner_seconds_median"],
                comparison["cupy_partner_seconds_median"],
            )
            self.assertLess(
                comparison["numba_hot_seconds_median"],
                comparison["cupy_hot_seconds_median"],
            )
            self.assertTrue(row["correctness"]["passed"])
            self.assertLess(row["correctness"]["max_abs_diff_x"], row["correctness"]["tolerance"])
            self.assertLess(row["correctness"]["max_abs_diff_y"], row["correctness"]["tolerance"])

    def test_report_and_docs_record_m41_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        partner_matrix = PARTNER_MATRIX.read_text(encoding="utf-8")
        evidence_index = EVIDENCE_INDEX.read_text(encoding="utf-8")
        rt_core_matrix = RT_CORE_MATRIX.read_text(encoding="utf-8")

        for phrase in (
            "current fastest measured partner",
            "same-contract comparison partner",
            "M41 does not authorize public RT-core or whole-application speedup wording",
            "It is not an OptiX-vs-Embree or GPU-vs-CPU claim",
        ):
            self.assertIn(phrase, report)
        self.assertIn("Goal4438/4439", partner_matrix)
        self.assertIn("Numba wins the prepared RTDL/OptiX device-column partner route", evidence_index)
        self.assertIn("Goal4438/4439 show RTDL/OptiX can emit aggregate-frontier device columns", rt_core_matrix)
        self.assertIn("Goal4442 adds a fused CPU/Numba route", rt_core_matrix)

    def test_route_registry_uses_numba_fastest_policy_for_this_contract(self) -> None:
        import rtdsl as rt

        route = rt.explain_current_benchmark_route("barnes_hut")
        validation = rt.validate_current_benchmark_route_decisions()

        self.assertEqual("accept", validation["status"])
        self.assertEqual(
            "rtdl.v3_0.current_benchmark_route_decisions.goal4479.v1",
            route["version"],
        )
        self.assertEqual("mixed_explicit", route["decision_kind"])
        self.assertEqual("explicit_route_choice_cpu_numba_or_optix_numba_cupy_comparison", route["partner_policy"])
        self.assertIn("Goal4436", route["evidence_refs"])
        self.assertIn("Goal4438", route["evidence_refs"])
        self.assertIn("Goal4439", route["evidence_refs"])
        self.assertIn("Goal4440", route["evidence_refs"])
        self.assertIn("Goal4441", route["evidence_refs"])
        self.assertIn("Goal4442", route["evidence_refs"])
        self.assertIn("Numba remains the fastest measured GPU partner", route["current_reader_decision"])
        self.assertIn("fused_frontier_force_sum_bucketized_cpu_numba", route["current_reader_decision"])
        self.assertIn("universal Numba fastest claim", route["rejected_or_unpromoted_candidates"])
        self.assertIn("universal CuPy fastest claim", route["rejected_or_unpromoted_candidates"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["public_speedup_claim_authorized"])
        self.assertFalse(route["whole_app_speedup_claim_authorized"])
        self.assertFalse(route["broad_rt_core_claim_authorized"])


if __name__ == "__main__":
    unittest.main()


