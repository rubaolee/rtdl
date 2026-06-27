from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_relation_status_prefilter_zero_experiment.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_prefilter_zero_experiment_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixSpatialRelationStatusPrefilterZeroExperimentTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_material_optimization_but_not_m7(self) -> None:
        packet = self.packet
        self.assertEqual(packet["status"], "spatial_relation_status_prefilter_zero_near_miss_not_m7")
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertEqual(packet["optimization"]["native_flag"], "RTDL_OPTIX_RELATION_STATUS_CORRECTED_PREFILTER_ZERO")
        self.assertTrue(packet["optimization"]["default_enabled"])
        self.assertTrue(packet["checks"]["native_source_default_enables_prefilter_zero"])
        self.assertTrue(packet["checks"]["native_source_does_not_keep_default_off_prefilter_gate"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)
        self.assertEqual(packet["failed_checks"], [])
        self.assertTrue(all(packet["checks"].values()))

    def test_stable_candidate_is_correct_but_still_slower_than_author(self) -> None:
        summary = self.packet["summary"]
        stable = self.packet["stable_candidate"]
        self.assertEqual(stable["row_count"], 47262)
        self.assertTrue(stable["row_count_consistent"])
        self.assertAlmostEqual(stable["prepared_query_ms_median"], 1.903492957353592)
        self.assertAlmostEqual(summary["old_best_prepared_query_ms"], 5.406518)
        self.assertGreater(summary["stable_prefilter_speedup_vs_old_best"], 2.8)
        self.assertAlmostEqual(summary["author_query_ms"], 1.86566)
        self.assertGreater(summary["author_speedup_vs_stable_prefilter"], 1.0)
        self.assertGreater(summary["still_missing_author_bar_by_ms"], 0.0)

    def test_ordering_sweep_and_restored_smoke_are_recorded(self) -> None:
        rows = {row["name"]: row for row in self.packet["prefilter_zero_results"]}
        self.assertEqual(
            set(rows),
            {
                "natural",
                "x_then_y",
                "morton_xy",
                "y_then_x_sample5",
                "y_then_x_sample7",
                "restored_y_then_x_sample3",
            },
        )
        self.assertLess(rows["y_then_x_sample7"]["prepared_query_ms_median"], rows["morton_xy"]["prepared_query_ms_median"])
        self.assertLess(rows["morton_xy"]["prepared_query_ms_median"], rows["natural"]["prepared_query_ms_median"])
        for row in rows.values():
            self.assertEqual(row["row_count"], 47262)
            self.assertTrue(row["row_count_consistent"])
            self.assertFalse(row["m7_promotion_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
        restored = self.packet["restored_library_smoke"]
        self.assertEqual(restored["row_count"], 47262)
        self.assertGreater(restored["speedup_vs_old_best_legal_route"], 2.8)

    def test_failed_boundary_helper_is_rejected(self) -> None:
        failed = self.packet["failed_followup_experiment"]
        self.assertEqual(failed["name"], "boundary_helper_exact_contact_fast_path")
        self.assertEqual(failed["status"], "rejected_exact_count_mismatch_not_kept")
        self.assertIn("47259 != 47262", failed["observed_error"])
        self.assertIn("was reverted", failed["decision"])

    def test_markdown_keeps_no_release_wording(self) -> None:
        for phrase in (
            "Status: `spatial_relation_status_prefilter_zero_near_miss_not_m7`.",
            "M7 rows added: 0",
            "Improvement vs old legal route: `2.840x`",
            "Author remains faster by: `1.020x`",
            "not a Phoenix V3 release row",
            "rejected_exact_count_mismatch_not_kept",
            "Was I foolish?",
        ):
            self.assertIn(phrase, self.markdown)

    def test_script_rebuilds_packet(self) -> None:
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
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.packet)
            self.assertIn("Spatial Relation-Status Prefilter-Zero", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
