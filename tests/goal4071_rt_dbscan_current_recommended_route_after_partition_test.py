from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4071_rt_dbscan_current_recommended_route_after_partition.py"
REPORT = ROOT / "docs" / "reports" / "goal4071_rt_dbscan_current_recommended_route_after_partition_2026-06-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4071_rt_dbscan_current_recommended_route_after_partition_pod.json"


class Goal4071RtDbscanCurrentRecommendedRouteSourceTest(unittest.TestCase):
    def test_script_and_report_define_route_positioning_packet(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8") + "\n" + REPORT.read_text(encoding="utf-8")
        for fragment in (
            "Goal4071",
            "recommended_rt_core_grouped_stream_numba_signature",
            "partition_count_then_emit_cupy_signature_candidate",
            "partner_numba_prepared_grid_components",
            "partner_cupy_prepared_grid_components",
            "same_signature_as_recommended",
            "same_component_size_signature_as_recommended",
            "speedup_of_recommended_over_row",
            "does not authorize release",
            "true-zero-copy",
        ):
            self.assertIn(fragment, text)


class Goal4071RtDbscanCurrentRecommendedRoutePodArtifactTest(unittest.TestCase):
    def test_pod_artifact_keeps_rt_core_route_recommended_without_claim_leakage(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal4071 pod artifact has not been produced yet")
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["goal"], "Goal4071")
        self.assertEqual(payload["profile"], "clustered3d_65536")
        self.assertEqual(payload["recommended_route"], "recommended_rt_core_grouped_stream_numba_signature")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["paper_speedup_claim_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["rt_core_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["native_abi_added"])
        self.assertEqual(len(payload["rows"]), 4)
        recommended = payload["rows"][0]
        self.assertTrue(recommended["rt_core_accelerated"])
        self.assertEqual(recommended["name"], "recommended_rt_core_grouped_stream_numba_signature")
        self.assertEqual(recommended["column_signature_strategy"], "numba_direct_component_signature_counts")
        for row in payload["rows"]:
            self.assertTrue(row["same_component_size_signature_as_recommended"])
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["rt_core_speedup_claim_authorized"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"])
            self.assertFalse(row["true_zero_copy_claim_authorized"])
        opponents = payload["rows"][1:]
        self.assertTrue(all(row["speedup_of_recommended_over_row"] > 1.0 for row in opponents))


if __name__ == "__main__":
    unittest.main()
