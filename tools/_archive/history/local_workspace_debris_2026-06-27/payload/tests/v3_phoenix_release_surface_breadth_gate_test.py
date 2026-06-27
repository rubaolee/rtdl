import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_release_surface_breadth_gate.py"


class V3PhoenixReleaseSurfaceBreadthGateTest(unittest.TestCase):
    def test_gate_records_exact_surface_gap_without_authorizing_release(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["tool"], "v3_phoenix_release_surface_breadth_gate")
        self.assertEqual(payload["gate"], "phoenix_v3_major_release_surface_breadth")
        self.assertEqual(payload["status"], "surface_breadth_passed_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["checks"]["surface_row_integrity_manifest_has_thirteen_rows"])
        self.assertTrue(payload["checks"]["surface_row_integrity_manifest_rows_are_unique"])
        self.assertTrue(payload["checks"]["surface_row_integrity_manifest_matches_current_surface_rows"])
        self.assertTrue(payload["checks"]["surface_row_integrity_paths_exist"])
        self.assertTrue(payload["checks"]["surface_row_integrity_flags_block_unsupported_claims"])
        self.assertTrue(payload["checks"]["surface_row_integrity_rows_are_generic_capability_rows"])

        evidence = payload["evidence"]
        self.assertEqual(evidence["total_m7_row_count"], 13)
        self.assertEqual(evidence["surface_row_integrity_row_count"], 13)
        self.assertTrue(evidence["surface_row_integrity_all_paths_exist"])
        self.assertTrue(evidence["surface_row_integrity_all_flags_block_unsupported_claims"])
        self.assertTrue(evidence["surface_row_integrity_all_rows_are_generic_capability_rows"])
        self.assertEqual(
            {row["row_id"] for row in evidence["surface_row_integrity"]},
            {row_id for rows in evidence["m7_rows_by_capability"].values() for row_id in rows},
        )
        self.assertEqual(
            {row["source_kind"] for row in evidence["surface_row_integrity"]},
            {
                "base_m7_packet_row",
                "post_classification_final_review_packet",
                "closed_generic_engine_work_supplemental_row",
            },
        )
        for row in evidence["surface_row_integrity"]:
            self.assertFalse(row["release_authorized"])
            self.assertFalse(row["public_speedup_claim_authorized"])
            self.assertFalse(row["broad_v3_faster_than_v2_claim_authorized"])
            self.assertTrue(row["unsupported_claims_blocked"])
            self.assertTrue(row["evidence_paths_exist"])
            self.assertTrue(row["review_paths_exist"])
            self.assertTrue(row["consensus_paths_exist"])
            self.assertIn(row["generic_capability"], evidence["planned_capability_families"])
        self.assertEqual(evidence["base_m7_packet_row_count"], 12)
        self.assertEqual(evidence["supplemental_m7_row_count_from_current_queue"], 1)
        self.assertEqual(evidence["minimum_m7_capability_families_for_major_release"], 9)
        self.assertEqual(evidence["m7_capability_family_count"], 9)
        self.assertEqual(
            evidence["missing_m7_capability_families"],
            [],
        )
        self.assertEqual(evidence["missing_capability_future_work_map"], {})
        self.assertEqual(
            evidence["supplemental_m7_rows_from_current_queue"][0]["row_id"],
            "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
        )
        self.assertEqual(evidence["route_map_m7_qualified_release_rows"], 5)
        self.assertEqual(evidence["supplemental_m7_qualified_release_rows"], 7)
        self.assertEqual(evidence["app_boundary_m7_rows"], 8)
        self.assertEqual(evidence["apps_with_m7_row_count"], 8)
        self.assertEqual(evidence["unattributed_app_boundary_m7_row_count"], 0)
        self.assertEqual(evidence["unattributed_app_boundary_m7_rows"], [])
        self.assertEqual(
            set(evidence["apps_with_m7_rows"]),
            {
                "hausdorff_xhd",
                "librts_spatial_index",
                "raydb_style",
                "robot_collision",
                "rt_dbscan",
                "triangle_counting",
            },
        )
        self.assertFalse(evidence["existing_evidence_promotable_now"])
        self.assertEqual(evidence["active_generic_engine_queue_ids"], [])
        self.assertEqual(evidence["pending_external_review_candidate_count"], 0)
        self.assertEqual(evidence["pending_external_review_candidate_ids"], [])
        self.assertEqual(evidence["accepted_with_boundary_candidate_count"], 0)
        self.assertEqual(evidence["accepted_with_boundary_candidate_ids"], [])
        self.assertEqual(
            set(evidence["future_research_work_ids"]),
            {"barnes_hut_vector_accumulation_frontier_shape"},
        )
        self.assertEqual(
            set(evidence["future_research_capabilities"]),
            {"vector_accumulation"},
        )

        self.assertIn("release_authorization_false", payload["blocking_reasons"])
        self.assertIn("updated_thirteen_row_release_readiness_consensus_required", payload["blocking_reasons"])
        self.assertNotIn("existing_evidence_promotable_now_false", payload["blocking_reasons"])
        self.assertNotIn("missing_aggregate_frontier_m7_capability_family", payload["blocking_reasons"])
        self.assertNotIn("missing_point_location_topology_stream_m7_capability_family", payload["blocking_reasons"])
        self.assertNotIn("twelve_row_release_readiness_consensus_blocks_release", payload["blocking_reasons"])
        self.assertIn("Do not publish Phoenix V3 as a major release", payload["required_next_actions"][0])

    def test_gate_records_user_required_decision_audit(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        audit = json.loads(completed.stdout)["decision_audit"]

        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("No.", audit["was_i_foolish"])
        self.assertIn("thirteen row-scoped/supplemental wins", audit["foolish_actions"])
        self.assertIn("12 base packet rows plus 1 reviewed Spatial supplemental row", audit["decision"])
        self.assertIn("Use this gate", audit["different_path_now"])

    def test_gate_can_write_json_and_markdown_reports(self):
        out_dir = ROOT / "docs" / "rebuild" / "v3"
        json_out = out_dir / "phoenix_v3_release_surface_breadth_gate_2026-06-21.json"
        md_out = out_dir / "phoenix_v3_release_surface_breadth_gate_2026-06-21.md"
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--pretty",
                "--json-out",
                str(json_out),
                "--md-out",
                str(md_out),
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertTrue(json_out.exists())
        self.assertTrue(md_out.exists())

        saved_payload = json.loads(json_out.read_text(encoding="utf-8"))
        self.assertEqual(saved_payload["status"], "surface_breadth_passed_not_release")

        md_text = md_out.read_text(encoding="utf-8")
        self.assertIn("# Phoenix V3 Release Surface Breadth Gate", md_text)
        self.assertIn("`point_location_topology_stream`", md_text)
        self.assertIn("Missing M7 capability families: ``", md_text)
        self.assertIn("App-boundary attributed rows: `8` / `8`", md_text)
        self.assertIn("Pending external-review candidates: `0`", md_text)
        self.assertIn("Accepted-with-boundary candidates: `0`", md_text)
        self.assertIn("Surface row integrity rows: `13`", md_text)
        self.assertIn("Surface row paths all exist: `true`", md_text)
        self.assertIn("Surface row unsupported-claim flags blocked: `true`", md_text)
        self.assertIn("## Goal-Level Decision Self-Audit", md_text)


if __name__ == "__main__":
    unittest.main()
