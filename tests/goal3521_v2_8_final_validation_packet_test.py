import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3521_v2_8_final_validation_packet_2026-06-05.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3521_pod_artifacts"
COMMIT = "9ad59f1e7abbe0b2a97e785b28f7358aaa14d6c8"


def _json(relative: str) -> dict:
    return json.loads((ARTIFACT_DIR / relative).read_text(encoding="utf-8"))


class Goal3521V28FinalValidationPacketTest(unittest.TestCase):
    def test_report_records_internal_scope_and_commands(self):
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn(COMMIT, text)
        self.assertIn("internal validation packet; not release authorization", text)
        self.assertIn("Ran 112 tests", text)
        self.assertIn("NVIDIA RTX A5000", text)
        self.assertIn("Goal3522", text)

    def test_robot_collision_optix_row_is_current_head_and_bounded(self):
        data = _json("robot_collision/summary.json")
        rows = {row["mode"]: row for row in data["matrix"]["rows"]}

        self.assertEqual(data["source_commit"], COMMIT)
        self.assertIn("NVIDIA RTX A5000", data["gpu"])
        self.assertEqual(rows["cpu_reference"]["status"], "ok")
        self.assertEqual(rows["optix_prepared"]["status"], "ok")
        self.assertTrue(rows["optix_prepared"]["reuse_metadata"]["prepared_scene_reused"])
        self.assertGreater(rows["cpu_reference"]["tail_median_total_run_seconds"], 0.0)
        self.assertGreater(rows["optix_prepared"]["tail_median_total_run_seconds"], 0.0)

        boundary = data["claim_boundary"]
        self.assertTrue(boundary["internal_evidence_only"])
        for key, value in boundary.items():
            if key == "internal_evidence_only":
                continue
            self.assertFalse(value, key)

    def test_contact_manifold_phase_split_and_generic_boundary(self):
        data = _json("contact_manifold_grid4096_optix.json")
        phases = data["v2_4_phase_timing"]["phases_sec"]

        self.assertEqual(data["candidate_discovery_backend"], "optix")
        self.assertTrue(data["matches_cpu_reference"])
        self.assertEqual(data["valid_count"], 4096)
        self.assertFalse(data["engine_boundary"]["native_collision_logic_allowed"])
        for phase in ("scene_build", "rt_traversal", "partner_continuation", "materialization"):
            self.assertGreater(phases[phase], 0.0, phase)

    def test_rt_dbscan_grouped_stream_current_head(self):
        data = _json("rt_dbscan_grouped_stream.json")

        self.assertEqual(data["source_commit"], COMMIT)
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["point_counts"], [32768, 65536, 131072])
        self.assertTrue(data["signatures_match"])
        self.assertTrue(data["grouped_stream_rt_core_accelerated"])
        self.assertTrue(data["grouped_stream_avoids_neighbor_rows_and_full_adjacency_stream"])
        self.assertGreater(data["min_grouped_stream_speedup_vs_prepared_cupy_grid"], 4.0)
        for row in data["rows"]:
            self.assertTrue(row["prepared_cupy_signature_match"])
            self.assertTrue(row["grouped_stream_signature_match"])
            self.assertFalse(row["grouped_stream_materializes_neighbor_rows"])
            self.assertFalse(row["grouped_stream_materializes_directed_adjacency_stream"])

        boundary = data["claim_boundary"]
        self.assertTrue(boundary["canonical_live_harness"])
        for key, value in boundary.items():
            if key == "canonical_live_harness":
                continue
            self.assertFalse(value, key)

    def test_overlay_steady_state_read_current_head_and_exact(self):
        data = _json("overlay_steady_state_read.json")
        timing = data["timing_sec"]

        self.assertEqual(data["rtdl_commit"], COMMIT)
        self.assertEqual(data["schema"], "rtdl.goal3511.overlay_area_steady_state_relation_stream.v1")
        self.assertEqual(data["relation_row_count"], 4543)
        self.assertEqual(data["exact_positive_row_count"], data["observed_positive_row_count"])
        self.assertLess(data["total_area_abs_error"], 1.0e-8)
        self.assertLess(data["max_relation_abs_error"], 2.0e-9)
        self.assertLess(timing["active_relation_device_columns"], 0.01)
        self.assertGreater(timing["payload_cache_load"], 0.0)
        self.assertGreater(timing["device_tile_task_planning"], 0.0)
        self.assertGreater(timing["cupy_tile_task_executor"], 0.0)

        for key, value in data["claim_boundary"].items():
            self.assertFalse(value, key)


if __name__ == "__main__":
    unittest.main()
