import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_rayjoin_m3_gap_analysis.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_rayjoin_m3_gap_analysis_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixSpatialRayJoinM3GapAnalysisTest(unittest.TestCase):
    def load(self):
        return json.loads(PACKET_JSON.read_text(encoding="utf-8"))

    def test_packet_is_not_release_or_m7(self):
        payload = self.load()
        self.assertEqual(payload["status"], "spatial_rayjoin_m3_gap_analysis_not_m7")
        self.assertEqual(payload["generic_capability"], "point_location_topology_stream")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["paper_reproduction_claim_authorized"])
        self.assertFalse(payload["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["v4_embedding_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_same_stream_keeps_author_gap_visible(self):
        same = self.load()["same_stream_pip_100k"]
        self.assertEqual(same["contract"], "scalar_exact_positive_membership_count")
        self.assertEqual(same["query_count"], 100000)
        self.assertGreater(same["optix_over_embree_wall_speedup"], 10.0)
        self.assertGreater(same["rayjoin_author_over_rtdl_optix_wall_speedup"], 10.0)
        self.assertTrue(same["exact_backend_counts_match"])
        self.assertIn("RayJoin author RT is still faster", same["reading"])

    def test_large_device_resident_delta_is_internal_engine_target(self):
        large = self.load()["large_pip_device_resident_delta"]
        self.assertEqual(large["query_points"], 5288684)
        self.assertEqual(large["count"], 3823783)
        self.assertTrue(large["counts_match"])
        self.assertGreater(large["device_resident_wall_speedup_vs_default"], 2.0)
        self.assertGreater(large["visible_residual_reduction_vs_default"], 100.0)
        self.assertGreater(large["default_host_points"]["visible_residual_after_native_transfer_sec"], 0.1)
        self.assertLess(large["device_resident_points"]["visible_residual_after_native_transfer_sec"], 0.005)
        self.assertEqual(large["device_resident_points"]["point_upload_median_sec"], 0.0)
        self.assertIn("not a true zero-copy product claim", large["reading"])

    def test_m3_gap_names_required_engine_work(self):
        gap = self.load()["m3_public_row_gap"]
        self.assertEqual(gap["current_state"], "partial_m3_gap_analysis_not_public_row")
        for phase in (
            "static_scene_prepare_sec",
            "query_stream_prepare_sec",
            "device_transfer_or_residency_sec",
            "rt_traversal_sec",
            "topology_continuation_sec",
            "host_return_or_scalar_materialization_sec",
        ):
            self.assertIn(phase, gap["required_phases"])
        self.assertIn("single fresh runner", " ".join(gap["missing_or_not_public_row_ready"]))
        self.assertIn("keeps query columns resident", gap["next_engine_target"])
        self.assertIn("without RayJoin-specific native logic", gap["next_engine_target"])

    def test_markdown_records_boundaries_and_decision_audit(self):
        text = PACKET_MD.read_text(encoding="utf-8")
        for phrase in (
            "optimization-target packet",
            "true_zero_copy_claim_authorized: false",
            "M7 rows added by this packet: 0",
            "Device-resident wall speedup vs default",
            "M3 Public-Row Gap",
            "Do not call the device-resident internal delta true zero-copy.",
            "Do not implement a RayJoin-only native shortcut",
            "Was I foolish?",
            "Treat resident topology-stream columns",
        ):
            self.assertIn(phrase, text)

    def test_script_rebuilds_packet(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--pretty",
                ],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.load())
            self.assertIn("Spatial RayJoin M3 Gap Analysis", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
