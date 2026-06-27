from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_JSON = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.json"
PACKET_MD = ROOT / "docs/rebuild/v3/phoenix_v3_spatial_rayjoin_relation_status_exact_f64_intake_2026-06-21.md"
SCRIPT = ROOT / "scripts/v3_phoenix_spatial_rayjoin_relation_status_exact_f64_intake.py"


class V3PhoenixSpatialRelationStatusExactF64IntakeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_exact_f64_repair_without_m7_promotion(self) -> None:
        packet = self.packet
        self.assertEqual(
            packet["status"],
            "spatial_rayjoin_relation_status_exact_f64_device_scalar_count_intake_not_m7",
        )
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertEqual(packet["old_no_go_candidate_minus_exact"], -3)
        self.assertEqual(packet["current_exact_count"], 47262)
        self.assertTrue(packet["current_row_count_consistent"])
        self.assertEqual(packet["failed_checks"], [])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)
        for key in (
            "m7_promotion_authorized",
            "release_authorized",
            "public_speedup_claim_authorized",
            "row_scoped_public_speedup_claim_authorized",
            "broad_v3_faster_than_v2_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "v4_embedding_claim_authorized",
            "whole_app_speedup_claim_authorized",
        ):
            self.assertFalse(packet[key], key)

    def test_comparison_is_material_but_scoped(self) -> None:
        comparison = self.packet["comparison_vs_exact_executor"]
        self.assertGreater(comparison["prepared_query_speedup_vs_exact_executor"], 3.6)
        self.assertGreater(comparison["prepared_query_total_speedup_vs_exact_executor"], 3.6)
        self.assertGreater(comparison["runner_wall_speedup_vs_exact_executor"], 1.4)
        self.assertEqual(comparison["new_topology_continuation_sec"], 0.0)
        self.assertGreater(comparison["old_topology_continuation_sec"], 0.02)

    def test_native_counters_show_full_candidate_exact_filtering(self) -> None:
        native = self.packet["native_phase_timings_first_sample"]
        self.assertEqual(native["raw_candidate_count"], 155555)
        self.assertEqual(native["boundary_candidate_count"], 47550)
        self.assertEqual(native["dropped_candidate_count"], 108293)
        self.assertEqual(native["emitted_count"], 47262)
        self.assertFalse(native["row_stream_materialized"])
        self.assertTrue(native["native_exact_device_scalar_count_produced"])

    def test_checks_capture_source_build_pod_and_old_no_go(self) -> None:
        checks = self.packet["checks"]
        self.assertTrue(all(checks.values()))
        for name in (
            "native_source_uses_exact_f64_full_predicate",
            "native_source_no_longer_keeps_status_one_without_exact_check",
            "build_succeeded",
            "repeat_exact_count_matches",
            "old_no_go_retained",
        ):
            self.assertTrue(checks[name], name)

    def test_markdown_keeps_claim_boundary_and_self_audit_visible(self) -> None:
        markdown = self.markdown
        self.assertIn("3.680x", markdown)
        self.assertIn("3.703x", markdown)
        self.assertIn("1.465x", markdown)
        self.assertIn("This is an intake packet, not release authorization and not an M7 promotion.", markdown)
        self.assertIn("Previous no-go packet retained", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)
        self.assertIn("RTDL-beats-RayJoin claim authorized: `false`", markdown)

    def test_script_rebuilds_checked_in_packet(self) -> None:
        before_json = PACKET_JSON.read_text(encoding="utf-8")
        before_md = PACKET_MD.read_text(encoding="utf-8")
        subprocess.run([sys.executable, str(SCRIPT)], cwd=ROOT, check=True, capture_output=True, text=True)
        self.assertEqual(PACKET_JSON.read_text(encoding="utf-8"), before_json)
        self.assertEqual(PACKET_MD.read_text(encoding="utf-8"), before_md)


if __name__ == "__main__":
    unittest.main()
