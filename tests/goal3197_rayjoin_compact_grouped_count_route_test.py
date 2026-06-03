from __future__ import annotations

import json
from pathlib import Path
import unittest

from examples.v2_0.research_benchmarks.spatial_rayjoin import rtdl_rayjoin_v2_spatial_join_app as app


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "spatial_rayjoin" / "README.md"
REPORT = ROOT / "docs" / "reports" / "goal3197_rayjoin_compact_grouped_count_route_2026-06-03.md"
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3197_rayjoin_compact_grouped_count_route_pod_2026-06-03.json"


class Goal3197RayJoinCompactGroupedCountRouteTest(unittest.TestCase):
    def test_route_is_wired_to_compact_device_columns(self) -> None:
        source = APP.read_text(encoding="utf-8")

        self.assertIn("run_rayjoin_prepared_optix_compact_grouped_count_workload", source)
        self.assertIn("prepared_optix_compact_grouped_count", source)
        self.assertIn("grouped_count_by_left_id_compact_device_columns", source)
        self.assertIn("segment_segment_intersection_count_by_left_id_compact_device_columns", source)
        self.assertIn("left_id_remap", source)
        self.assertIn("generic grouped-count primitive uses direct-address key capacity", source)
        self.assertIn("RayJoin workload interpretation and left-ID remapping stay in Python", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn('"true_zero_copy_claim_authorized": False', source)

    def test_readme_documents_compact_grouped_count_route(self) -> None:
        readme = README.read_text(encoding="utf-8")

        self.assertIn("--execution-route prepared_optix_compact_grouped_count", readme)
        self.assertIn("counts per left segment", readme)
        self.assertIn("Left-ID remapping stays in Python", readme)
        self.assertIn("generic compact grouped-count device columns", readme)
        self.assertIn("not a full RayJoin reproduction or public speedup claim", readme)

    def test_route_rejects_non_lsi_workloads_before_optix_import(self) -> None:
        with self.assertRaisesRegex(ValueError, "supports only the lsi workload"):
            app.run_rayjoin_prepared_optix_compact_grouped_count_workload("pip")

    def test_report_records_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "prepared_optix_compact_grouped_count",
            "app-facing reference route",
            "left-ID remapping stays in Python",
            "compact group_key/count columns remain CUDA-resident",
            "not a public speedup claim",
            "true_zero_copy_claim_authorized: False",
            "release_authorized: False",
        ):
            self.assertIn(phrase, report)

    def test_pod_artifact_records_app_route_evidence(self) -> None:
        data = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        payload = data["payload"]

        self.assertEqual(data["goal"], 3197)
        self.assertEqual(data["commit"], "71812e99")
        self.assertEqual(payload["execution_route"], "prepared_optix_compact_grouped_count")
        self.assertEqual(payload["workload"], "lsi")
        self.assertEqual(payload["summary"]["output_contract"], "segment_segment_intersection_count_by_left_id_compact_device_columns")
        self.assertTrue(payload["left_id_remap"]["enabled"])
        self.assertTrue(payload["compact_grouped_count_columns"]["device_resident"])
        self.assertEqual(payload["compact_grouped_count_columns"]["output_residency"], "device_resident_compact_grouped_count_columns")
        self.assertTrue(data["checks"]["count_sum_matches_row_count"])
        self.assertTrue(data["checks"]["returned_rows_match_compact_row_count"])
        self.assertFalse(payload["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["full_rayjoin_reproduction"])


if __name__ == "__main__":
    unittest.main()
