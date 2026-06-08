from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4055_barnes_hut_route_metadata_after_numba_session_2026-06-08.md"


def _by_app(rows: tuple[dict[str, object], ...], app: str) -> dict[str, object]:
    for row in rows:
        if row["app"] == app:
            return row
    raise AssertionError(f"missing app row: {app}")


class Goal4055BarnesHutRouteMetadataAfterNumbaSessionTest(unittest.TestCase):
    def test_route_decision_mentions_prepared_numba_session_without_promoting_whole_app(self) -> None:
        row = _by_app(rt.current_benchmark_route_decisions(), "barnes_hut")

        self.assertIn("Goal4053", row["current_reader_decision"])
        self.assertIn("prepared grouped-vector session", row["user_choice_guidance"])
        self.assertIn("deeper hierarchical vector primitive design", row["next_runtime_action"])
        self.assertIn("Goal4052", row["evidence_refs"])
        self.assertIn("Goal4053", row["evidence_refs"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["whole_app_speedup_claim_authorized"])
        self.assertFalse(row["app_specific_native_engine_logic_allowed"])

    def test_adequacy_row_records_kernel_session_win_as_subcontract_only(self) -> None:
        row = _by_app(rt.current_benchmark_adequacy(), "barnes_hut")

        self.assertIn("Goal4052", row["current_performance_reading"])
        self.assertIn("Goal4053", row["current_performance_reading"])
        self.assertIn("3.77x-3.89x", row["current_performance_reading"])
        self.assertIn("presegmented grouped-vector continuation", row["next_generic_runtime_action"])
        self.assertIn("deeper hierarchical vector primitive design", row["next_generic_runtime_action"])
        self.assertIn("Goal4052", row["evidence_refs"])
        self.assertIn("Goal4053", row["evidence_refs"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["whole_app_speedup_claim_authorized"])
        self.assertFalse(row["true_zero_copy_claim_authorized"])

    def test_scale_profile_keeps_exact_force_row_boundary(self) -> None:
        rows = rt.current_benchmark_scale_profiles()
        row = next(item for item in rows if item["row_id"] == "barnes_hut_numba_scale_default_8192")

        self.assertIn("Goal4053 separately covers prepared grouped-vector stream reductions", row["purpose"])
        self.assertIn("Goal4052", row["evidence_refs"])
        self.assertIn("Goal4053", row["evidence_refs"])
        self.assertEqual(row["expected_runtime_class"], "safe_summary_output")
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["app_specific_native_engine_logic_allowed"])

    def test_report_records_scope(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4055", text)
        self.assertIn("Barnes-Hut route and adequacy metadata", text)
        self.assertIn("prepared Numba", text)
        self.assertIn("grouped-vector continuation session", text)
        self.assertIn("does not promote", text)


if __name__ == "__main__":
    unittest.main()
