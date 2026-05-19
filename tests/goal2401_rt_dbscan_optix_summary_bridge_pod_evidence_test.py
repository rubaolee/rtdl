from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2401_rt_dbscan_optix_summary_bridge_pod"
REPORT = ROOT / "docs" / "reports" / "goal2401_rt_dbscan_optix_summary_bridge_pod_evidence_2026-05-19.md"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal2401RtDbscanOptixSummaryBridgePodEvidenceTest(unittest.TestCase):
    def test_clean_pod_environment_records_bridge_commit(self) -> None:
        environment = (ARTIFACT_DIR / "environment.txt").read_text(encoding="utf-8")

        self.assertIn("commit=00a349c7f60fe814432e1758caf3f531d77bb27b", environment)
        self.assertIn("NVIDIA RTX A5000, 570.211.01", environment)
        self.assertIn("RTDL_OPTIX_LIBRARY=/root/rtdl_goal2392_pod/build/librtdl_optix.so", environment)

    def test_hybrid_bridge_matches_existing_component_signatures(self) -> None:
        for dataset in ("clustered3d", "road3d"):
            with self.subTest(dataset=dataset):
                host = _load(f"{dataset}_partner_spatial_bucket_4096.json")
                grid = _load(f"{dataset}_partner_cupy_grid_4096.json")
                bridge = _load(f"{dataset}_optix_core_flags_cupy_grid_4096.json")

                self.assertEqual(bridge["signature"], host["signature"])
                self.assertEqual(bridge["signature"], grid["signature"])
                self.assertTrue(bridge["claim_boundary"]["rt_core_accelerated"])
                self.assertTrue(bridge["metadata"]["caller_supplied_core_flags"])
                self.assertFalse(bridge["metadata"]["materializes_neighbor_rows"])
                self.assertEqual(bridge["metadata"]["optix_core_flag_summary_rows"], 4096)
                self.assertIsNone(bridge["metadata"]["candidate_edge_count"])
                self.assertEqual(
                    bridge["metadata"]["candidate_edge_count_policy"],
                    "not_reported_for_caller_supplied_threshold_capped_counts",
                )

    def test_report_states_mixed_performance_and_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("accept-with-boundary", report)
        self.assertIn("pure CuPy device-grid baseline", report)
        self.assertIn("remains faster", report)
        self.assertIn("avoids O(edges) neighbor-row", report)
        self.assertIn("materialization", report)
        self.assertIn("not a paper-speedup claim", report)


if __name__ == "__main__":
    unittest.main()
