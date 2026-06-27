from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_relation_status_squared_boundary_candidate.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_relation_status_squared_boundary_candidate_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")
BASELINE_EVIDENCE = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "evidence"
    / "phoenix_v3_spatial_guarded_squared_boundary_20260621"
    / "baseline_prefilter_zero_repeat50_sample7.json"
)
SQUARED_EVIDENCE = BASELINE_EVIDENCE.with_name("guarded_squared_prefilter_zero_repeat50_sample7.json")
EQUIVALENCE_PACKET = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.json"
)


class V3PhoenixSpatialRelationStatusSquaredBoundaryCandidateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_is_pending_review_candidate_not_release(self) -> None:
        packet = self.packet
        self.assertEqual(
            packet["status"],
            "spatial_relation_status_squared_boundary_default_path_m7_row_accepted_with_boundary",
        )
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertTrue(packet["m7_candidate"])
        self.assertTrue(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 1)
        self.assertEqual(packet["external_review_status"], "claude_accept_with_boundary_default_path")
        self.assertEqual(packet["previous_external_review_status"], "claude_accept_with_boundary")
        self.assertEqual(
            packet["codex_consensus_status"],
            "claude_codex_consensus_accept_default_path_m7_row",
        )
        self.assertEqual(
            packet["previous_codex_consensus_status"],
            "claude_codex_consensus_accept_with_boundary_not_release",
        )
        self.assertFalse(packet["p1_default_path_resolution_required"])
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["row_scoped_public_speedup_claim_authorized"])
        self.assertFalse(packet["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(packet["true_zero_copy_claim_authorized"])
        self.assertFalse(packet["v4_embedding_claim_authorized"])
        self.assertEqual(packet["failed_checks"], [])
        self.assertTrue(all(packet["checks"].values()))

    def test_candidate_has_material_speedup_and_exact_count(self) -> None:
        summary = self.packet["summary"]
        candidate = self.packet["squared_boundary_candidate"]
        baseline = self.packet["baseline_prefilter_zero"]
        self.assertAlmostEqual(summary["baseline_prefilter_zero_median_ms"], 1.8956884741783142)
        self.assertAlmostEqual(summary["squared_boundary_median_ms"], 1.0804496705532074)
        self.assertAlmostEqual(summary["default_path_median_ms"], 1.0805986821651459)
        self.assertGreater(summary["speedup_vs_current_prefilter_zero"], 1.75)
        self.assertGreater(summary["speedup_vs_author_query_timer"], 1.72)
        self.assertGreater(summary["default_path_speedup_vs_author_query_timer"], 1.72)
        self.assertGreater(summary["default_path_speedup_vs_disable_control"], 5.3)
        self.assertGreater(summary["author_bar_margin_ms"], 0.78)
        self.assertGreater(summary["default_path_author_bar_margin_ms"], 0.78)
        self.assertEqual(candidate["row_count"], 47262)
        self.assertEqual(self.packet["default_path_candidate"]["row_count"], 47262)
        self.assertTrue(candidate["row_count_consistent"])
        self.assertTrue(self.packet["default_path_candidate"]["row_count_consistent"])
        self.assertEqual(candidate["raw_counts"], baseline["raw_counts"])
        self.assertEqual(candidate["emitted_counts"], baseline["emitted_counts"])
        self.assertEqual(candidate["boundary_counts"], baseline["boundary_counts"])
        self.assertEqual(candidate["dropped_counts"], baseline["dropped_counts"])
        self.assertEqual(self.packet["default_path_candidate"]["raw_counts"], [47570])
        self.assertEqual(self.packet["default_path_candidate"]["dropped_counts"], [308])
        self.assertEqual(self.packet["disable_control"]["raw_counts"], [155555])
        self.assertEqual(self.packet["disable_control"]["dropped_counts"], [108293])
        self.assertLess(candidate["max_ms"], self.packet["author_bar"]["author_query_ms"])
        self.assertLess(self.packet["default_path_candidate"]["max_ms"], self.packet["author_bar"]["author_query_ms"])

    def test_squared_only_probe_records_default_surface_value(self) -> None:
        squared_only = self.packet["squared_boundary_only"]
        summary = self.packet["summary"]
        self.assertAlmostEqual(
            squared_only["baseline_default_no_prefilter"]["median_ms"],
            5.404520779848099,
        )
        self.assertAlmostEqual(
            squared_only["squared_only_no_prefilter"]["median_ms"],
            2.8457939624786377,
        )
        self.assertGreater(squared_only["speedup_vs_default_no_prefilter"], 1.89)
        self.assertFalse(squared_only["clears_author_query_bar"])
        self.assertAlmostEqual(summary["squared_only_no_prefilter_median_ms"], 2.8457939624786377)
        self.assertAlmostEqual(summary["squared_only_speedup_vs_default_no_prefilter"], 1.8991258155389625)
        self.assertFalse(summary["squared_only_clears_author_query_bar"])

    def test_evidence_files_and_source_flags_are_recorded(self) -> None:
        self.assertTrue(BASELINE_EVIDENCE.exists())
        self.assertTrue(SQUARED_EVIDENCE.exists())
        self.assertTrue(EQUIVALENCE_PACKET.exists())
        self.assertEqual(
            self.packet["source"]["baseline_evidence"],
            "docs/rebuild/v3/evidence/phoenix_v3_spatial_guarded_squared_boundary_20260621/baseline_prefilter_zero_repeat50_sample7.json",
        )
        self.assertEqual(
            self.packet["source"]["squared_evidence"],
            "docs/rebuild/v3/evidence/phoenix_v3_spatial_guarded_squared_boundary_20260621/guarded_squared_prefilter_zero_repeat50_sample7.json",
        )
        self.assertEqual(
            self.packet["source"]["default_path_evidence"],
            "docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/default_path_guarded_squared_repeat50_sample7.json",
        )
        self.assertEqual(
            self.packet["source"]["disable_control_evidence"],
            "docs/rebuild/v3/evidence/phoenix_v3_spatial_default_path_20260622/disable_control_both_zero_repeat10_sample1.json",
        )
        self.assertEqual(
            self.packet["source"]["pod_built_optix_library_sha256"],
            "36500bba1bdd1bd7b517376b28ca23aeb51af82b97f908786bdb900ec1b40877",
        )
        self.assertEqual(self.packet["predicate_equivalence"]["guarded_mismatch_count"], 0)
        self.assertEqual(self.packet["predicate_equivalence"]["pure_squared_mismatch_count"], 10)
        self.assertIn(
            "RTDL_OPTIX_RELATION_STATUS_CORRECTED_EXACT_F64_SQUARED_BOUNDARY",
            self.packet["optimization"]["native_flags"],
        )
        self.assertTrue(self.packet["optimization"]["default_enabled"])
        self.assertIn("0", self.packet["optimization"]["default_disable_values"])
        self.assertTrue(self.packet["checks"]["native_source_has_default_on_relation_status_helper"])
        self.assertTrue(self.packet["checks"]["native_source_default_enables_prefilter_zero"])
        self.assertTrue(self.packet["checks"]["native_source_default_enables_squared_boundary"])
        self.assertTrue(self.packet["checks"]["native_source_does_not_keep_default_off_squared_boundary_gate"])
        self.assertIn("falling back", self.packet["optimization"]["implementation_summary"])
        self.assertTrue(self.packet["checks"]["native_source_does_not_define_dead_exact_boundary_contact"])
        self.assertTrue(self.packet["checks"]["previous_claude_review_exists"])
        self.assertTrue(self.packet["checks"]["previous_codex_consensus_exists"])
        self.assertTrue(self.packet["checks"]["claude_default_path_review_exists"])
        self.assertTrue(self.packet["checks"]["codex_default_path_consensus_exists"])
        self.assertEqual(
            self.packet["source"]["external_review"],
            "docs/reviews/claude_phoenix_v3_spatial_default_path_promotion_review_2026-06-22.md",
        )
        self.assertEqual(
            self.packet["source"]["codex_consensus"],
            "docs/reviews/codex_phoenix_v3_spatial_default_path_promotion_2ai_consensus_2026-06-22.md",
        )
        self.assertEqual(
            self.packet["source"]["previous_external_review"],
            "docs/reviews/claude_phoenix_v3_spatial_squared_boundary_candidate_review_2026-06-21.md",
        )
        self.assertEqual(
            self.packet["source"]["previous_codex_consensus"],
            "docs/reviews/codex_phoenix_v3_spatial_squared_boundary_candidate_2ai_consensus_2026-06-22.md",
        )
        self.assertIn("RayJoin author query_exec does not print result count", " ".join(self.packet["source"]["provenance_limitations"]))

    def test_markdown_keeps_boundary_wording(self) -> None:
        for phrase in (
            "Status: `spatial_relation_status_squared_boundary_default_path_m7_row_accepted_with_boundary`.",
            "default-path POD evidence",
            "P1 default-path resolution required: `false`",
            "Guarded squared-boundary median: `1.080450 ms`",
            "Default-path guarded squared-boundary median: `1.080599 ms`",
            "Speedup vs current prefilter-zero route: `1.755x`",
            "Default path vs disable control: `5.372x`",
            "Guarded-squared-only no-prefilter median: `2.845794 ms`",
            "Guarded-squared-only speedup vs default no-prefilter: `1.899x`",
            "Guarded-Squared-Only Default-Surface Probe",
            "Default Path Evidence",
            "Predicate Equivalence",
            "Pure squared mismatch count recorded: `10`",
            "Default path vs author Query timer: `1.727x`",
            "does not by itself authorize public release",
            "M7 rows added now: 1",
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
            self.assertIn("Spatial Guarded Squared-Boundary Candidate", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
