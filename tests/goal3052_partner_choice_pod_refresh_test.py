from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3052_partner_choice_pod_refresh_2026-06-02"
REPORT = ROOT / "docs" / "reports" / "goal3052_partner_choice_pod_refresh_2026-06-02.md"
EXPECTED_COMMIT = "4cb8ce65255c6be8438e0a97ef69b2ea0c77a074"


def _load(name: str) -> dict:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal3052PartnerChoicePodRefreshTest(unittest.TestCase):
    def test_report_records_scope_environment_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "NVIDIA RTX A4000",
            EXPECTED_COMMIT,
            "initially lacked `numba`",
            "RayDB-style Numba count/sum/min/max/avg",
            "RayJoin compact-mask continuation",
            "median speedup vs CuPy",
            "do not authorize",
            "automatic partner selection",
        ):
            self.assertIn(phrase, text)

    def test_raydb_numba_minmax_artifact_passes_without_claims(self) -> None:
        data = _load("raydb_numba_minmax_1m.json")
        self.assertEqual(data["goal"], "Goal2995")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["rows"], 1_000_000)
        self.assertEqual(data["groups"], 4096)
        self.assertEqual(data["source_commit"], EXPECTED_COMMIT)
        self.assertEqual(
            set(data["mode_results"]),
            {"count", "sum", "min", "max", "avg_as_sum_count"},
        )
        for result in data["mode_results"].values():
            self.assertTrue(result["match_cpu"])
            self.assertEqual(result["neutral_handoff_status"], "accept")
            self.assertFalse(result["uses_legacy_torch_carrier"])
            self.assertFalse(result["uses_torch_conversion"])
        self._assert_claims_false(data["claim_boundary"])

    def test_triangle_and_rayjoin_compact_mask_artifacts_pass(self) -> None:
        triangle = _load("triangle_numba_compact_mask_1m.json")
        self.assertEqual(triangle["goal"], "Goal3000")
        self.assertEqual(triangle["status"], "pass")
        self.assertEqual(triangle["rows"], 1_000_000)
        self.assertEqual(triangle["source_commit"], EXPECTED_COMMIT)
        self.assertTrue(triangle["candidates_match_cpu"])
        self.assertTrue(triangle["indices_match_cpu"])
        self.assertTrue(triangle["partner_indices_match_cpu"])
        self.assertEqual(triangle["neutral_handoff_status"], "accept")
        self._assert_claims_false(triangle["claim_boundary"])

        rayjoin = _load("rayjoin_numba_compact_mask_1m.json")
        self.assertEqual(rayjoin["goal"], "Goal3003")
        self.assertEqual(rayjoin["status"], "pass")
        self.assertEqual(rayjoin["rows"], 1_000_000)
        self.assertEqual(rayjoin["source_commit"], EXPECTED_COMMIT)
        self.assertTrue(rayjoin["all_workloads_match_cpu"])
        self.assertEqual(set(rayjoin["workloads"]), {"pip", "lsi", "overlay_seed"})
        for workload in rayjoin["workloads"].values():
            self.assertEqual(workload["status"], "pass")
            self.assertTrue(workload["candidates_match_cpu"])
            self.assertTrue(workload["indices_match_cpu"])
            self.assertTrue(workload["partner_indices_match_cpu"])
            self.assertEqual(workload["neutral_handoff_status"], "accept")
        self._assert_claims_false(rayjoin["claim_boundary"])

    def test_grouped_arg_reducer_and_hausdorff_refresh_pass(self) -> None:
        grouped = _load("grouped_arg_reducer_1m.json")
        self.assertEqual(grouped["goal"], "Goal3007")
        self.assertEqual(grouped["status"], "pass")
        self.assertEqual(grouped["source_commit"], EXPECTED_COMMIT)
        self.assertTrue(grouped["all_cases_match_cpu_reference"])
        self.assertTrue(grouped["uses_v2_6_neutral_partner_handoff"])
        self.assertFalse(grouped["uses_legacy_torch_carrier"])
        self.assertFalse(grouped["uses_torch_conversion"])
        large = next(row for row in grouped["case_results"] if row["case"] == "large_stream")
        self.assertEqual(large["row_count"], 1_000_000)
        self.assertEqual(large["group_count"], 4096)
        self.assertTrue(large["argmin_all_match"])
        self.assertTrue(large["argmax_all_match"])
        self.assertFalse(grouped["automatic_partner_selection_allowed"])
        self.assertFalse(grouped["numba_speedup_claim_authorized"])

        hausdorff = _load("hausdorff_active_frontier_small_refresh.json")
        self.assertEqual(hausdorff["goal"], "Goal3046")
        self.assertEqual(hausdorff["datasets"], ["demo_offset", "clustered_shift"])
        self.assertEqual(hausdorff["sizes"], [32768, 65536])
        self.assertTrue(hausdorff["all_rows_match_distance"])
        self.assertGreater(hausdorff["min_median_speedup_vs_cupy"], 2.0)
        self.assertGreater(hausdorff["median_of_median_speedups_vs_cupy"], 3.0)
        self.assertFalse(hausdorff["public_speedup_claim_authorized"])
        self.assertFalse(hausdorff["rt_core_speedup_claim_authorized"])
        self.assertFalse(hausdorff["true_zero_copy_claim_authorized"])

    def _assert_claims_false(self, claims: dict) -> None:
        for field, value in claims.items():
            self.assertIs(value, False, msg=f"{field} must remain false")


if __name__ == "__main__":
    unittest.main()
