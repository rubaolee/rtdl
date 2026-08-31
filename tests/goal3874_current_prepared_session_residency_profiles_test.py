from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3874_current_prepared_session_residency_profiles_2026-06-08.md"


class Goal3874CurrentPreparedSessionResidencyProfilesTest(unittest.TestCase):
    def test_registry_covers_goal3872_scene_heavy_rows(self) -> None:
        rows = rt.current_prepared_session_residency_profiles()
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            {row["app"] for row in rows},
            {"hausdorff_xhd", "librts_spatial_index", "rtnn", "triangle_counting"},
        )
        self.assertEqual(len({row["row_id"] for row in rows}), 4)
        self.assertEqual(
            {row["prepared_session_contract_version"] for row in rows},
            {rt.PREPARED_SESSION_RESIDENCY_VERSION},
        )

    def test_profiles_validate_without_authorizing_claims(self) -> None:
        validation = rt.validate_current_prepared_session_residency_profiles()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())

        for row in rt.current_prepared_session_residency_profiles():
            self.assertTrue(row["prepared_session_reuse_recommended"], row["row_id"])
            self.assertGreaterEqual(row["timing"]["prepare_to_hot_query_ratio"], 10.0)
            self.assertFalse(row["release_authorized"], row["row_id"])
            self.assertFalse(row["public_speedup_claim_authorized"], row["row_id"])
            self.assertFalse(row["broad_rt_core_claim_authorized"], row["row_id"])
            self.assertFalse(row["true_zero_copy_claim_authorized"], row["row_id"])
            self.assertFalse(row["automatic_partner_selection_authorized"], row["row_id"])
            self.assertFalse(row["app_specific_native_engine_logic_allowed"], row["row_id"])
            self.assertFalse(row["policy"]["automatic_partner_selection_authorized"], row["row_id"])
            self.assertFalse(row["policy"]["true_zero_copy_claim_authorized"], row["row_id"])

    def test_primitives_remain_generic_even_when_app_rows_are_named(self) -> None:
        forbidden = tuple(rt.PREPARED_SESSION_APP_SPECIFIC_FORBIDDEN_TERMS)
        for row in rt.current_prepared_session_residency_profiles():
            primitive = row["primitive"].lower()
            for term in forbidden:
                self.assertNotIn(term, primitive, row["row_id"])
            self.assertTrue(row["cache_key"]["explicit_key_required"], row["row_id"])

    def test_summary_preserves_goal3872_ratio_scale(self) -> None:
        summary = rt.summarize_current_prepared_session_residency_profiles()
        self.assertEqual(summary["version"], rt.CURRENT_PREPARED_SESSION_RESIDENCY_PROFILE_VERSION)
        self.assertEqual(summary["row_count"], 4)
        self.assertEqual(summary["app_count"], 4)
        self.assertGreater(summary["geomean_prepare_to_hot_query_ratio"], 400.0)
        self.assertGreater(summary["max_prepare_to_hot_query_ratio"], 12_000.0)
        self.assertEqual(len(summary["reuse_recommended_rows"]), 4)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["true_zero_copy_claim_authorized"])
        self.assertFalse(summary["automatic_partner_selection_authorized"])

    def test_report_documents_registry_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3874",
            "current benchmark matrix",
            "cold prepare vs hot query",
            "prepared-session cache key",
            "explicit lifetime and invalidation",
            "no hidden automatic partner/backend selection",
            "not a true-zero-copy or public speedup claim",
            "app-specific native-engine logic remains forbidden",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
