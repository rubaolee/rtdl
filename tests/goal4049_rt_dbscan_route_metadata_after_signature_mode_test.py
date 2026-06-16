from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4049_rt_dbscan_route_metadata_after_signature_mode_2026-06-08.md"


class Goal4049RtDbscanRouteMetadataAfterSignatureModeTest(unittest.TestCase):
    def test_route_records_signature_output_without_default_promotion(self) -> None:
        route = rt.explain_current_benchmark_route("rt_dbscan")

        self.assertIn("prepared direct-status", route["current_reader_decision"])
        self.assertIn("all-items direct-status", route["current_reader_decision"])
        self.assertIn("hidden factor selection", route["next_runtime_action"])
        self.assertIn("Goal4108", route["evidence_refs"])
        self.assertIn("Goal4177", route["evidence_refs"])
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(route["release_authorized"])

    def test_adequacy_row_records_narrower_contract_boundary(self) -> None:
        rows = {row["app"]: row for row in rt.current_benchmark_adequacy()}
        row = rows["rt_dbscan"]

        self.assertEqual(row["adequacy"], "strong")
        self.assertIn("Goal4046/4047", row["current_performance_reading"])
        self.assertIn("narrower component-size-signature contract", row["current_performance_reading"])
        self.assertIn("not for full DBSCAN", row["current_performance_reading"])
        self.assertIn("component-size signature mode", row["next_generic_runtime_action"])
        self.assertIn("narrower graph-component", row["next_generic_runtime_action"])
        self.assertIn("Goal4046", row["evidence_refs"])
        self.assertIn("Goal4047", row["evidence_refs"])
        self.assertFalse(row["automatic_partner_selection_authorized"])
        self.assertFalse(row["public_speedup_claim_authorized"])
        self.assertFalse(row["broad_rt_core_claim_authorized"])

    def test_report_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for fragment in (
            "grouped-stream plus Numba column signature remains",
            "explicit and unpromoted",
            "fixed_radius_graph_component_size_signature_3d",
            "full DBSCAN core/border/noise semantics",
            "public speedup wording",
            "automatic partner selection",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


if __name__ == "__main__":
    unittest.main()
