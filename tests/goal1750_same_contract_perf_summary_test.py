import json
import unittest

from scripts.goal1750_same_contract_perf_summary import (
    REPORT_JSON,
    REPORT_MD,
    build_report,
    write_report,
)


class Goal1750SameContractPerfSummaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        write_report(build_report())

    def test_summary_keeps_claims_blocked(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(
            payload["verdict"],
            "same_contract_perf_summary_ready_without_public_claim",
        )
        self.assertFalse(payload["public_claim_authorized"])
        self.assertFalse(payload["release_authorized"])
        self.assertIn("No public speedup", payload["boundary"])

    def test_optix_has_broad_same_contract_primary_ratios(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["optix"]["artifact_pair_rows"], 17)
        self.assertEqual(
            payload["optix"]["class_counts"],
            {"same_contract_primary_ratio": 17},
        )
        rows = {row["app"]: row for row in payload["optix"]["rows"]}
        for app in (
            "service_coverage_gaps",
            "event_hotspot_screening",
            "facility_knn_assignment",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "ann_candidate_search",
            "barnes_hut_force_app",
            "graph_visibility_edges",
            "graph_bfs",
            "graph_triangle_count",
        ):
            self.assertEqual(rows[app]["classification"], "same_contract_primary_ratio")
            self.assertIsInstance(rows[app]["baseline_over_current_ratio"], float)
            self.assertGreater(rows[app]["baseline_over_current_ratio"], 0.0)

    def test_embree_separates_database_from_recovered_diagnostic_rows(self) -> None:
        payload = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(payload["embree"]["same_contract_artifact_pair_rows"], 1)
        self.assertEqual(payload["embree"]["same_contract_rows"][0]["app"], "database_analytics")
        self.assertEqual(
            payload["embree"]["same_contract_rows"][0]["classification"],
            "same_contract_primary_ratio",
        )
        self.assertEqual(payload["embree"]["recovered_goal1746_rows"], 14)
        self.assertEqual(payload["embree"]["goal1748_class_counts"]["phase_mapped_diagnostic"], 4)
        self.assertEqual(payload["embree"]["goal1748_class_counts"]["timing_schema_mismatch"], 7)
        self.assertEqual(payload["embree"]["goal1748_class_counts"]["missing_current_artifact"], 3)

    def test_report_states_diagnostic_boundary(self) -> None:
        text = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("OptiX", text)
        self.assertIn("Embree", text)
        self.assertIn("diagnostic and not public same-contract claims", text)
        self.assertIn("does not authorize public speedup language", text)


if __name__ == "__main__":
    unittest.main()
