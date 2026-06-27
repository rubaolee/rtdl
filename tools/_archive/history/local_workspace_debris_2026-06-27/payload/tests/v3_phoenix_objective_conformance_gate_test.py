import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_objective_conformance_gate.py"
JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_objective_conformance_gate_2026-06-22.json"


class V3PhoenixObjectiveConformanceGateTest(unittest.TestCase):
    def _run_gate(self, *extra_args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *extra_args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_gate_maps_v3_objectives_to_current_capability_evidence(self):
        payload = self._run_gate()

        self.assertEqual(payload["tool"], "v3_phoenix_objective_conformance_gate")
        self.assertEqual(payload["gate"], "phoenix_v3_goal_conformance_contract")
        self.assertEqual(payload["status"], "objective_conformance_passed_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))
        self.assertTrue(payload["checks"]["objective_raydb_grouped_reduction_covered"])
        self.assertTrue(payload["checks"]["objective_rtdbscan_component_union_covered"])
        self.assertTrue(payload["checks"]["objective_spatial_rayjoin_topology_stream_covered"])
        self.assertTrue(payload["checks"]["objective_triangle_prepared_graph_covered"])
        self.assertTrue(payload["checks"]["objective_rtnn_ranked_summary_covered"])

        evidence = payload["evidence"]
        self.assertEqual(evidence["current_surface_total_m7_row_count"], 13)
        self.assertEqual(evidence["current_surface_capability_family_count"], 9)
        self.assertEqual(evidence["objective_required_capability_coverage_count"], 5)
        self.assertEqual(evidence["objective_required_capability_count"], 5)

        requirements = evidence["objective_capability_requirements"]
        self.assertEqual(requirements["raydb_grouped_reduction"]["capability"], "grouped_reduction")
        self.assertEqual(requirements["raydb_grouped_reduction"]["row_count"], 3)
        self.assertEqual(requirements["rtdbscan_component_union"]["capability"], "component_union")
        self.assertEqual(requirements["rtdbscan_component_union"]["row_count"], 1)
        self.assertEqual(requirements["spatial_rayjoin_topology_stream"]["capability"], "point_location_topology_stream")
        self.assertEqual(requirements["spatial_rayjoin_topology_stream"]["row_count"], 1)
        self.assertEqual(requirements["triangle_prepared_graph"]["capability"], "prepared_graph_chunk")
        self.assertEqual(requirements["triangle_prepared_graph"]["row_count"], 1)
        self.assertEqual(requirements["rtnn_ranked_summary"]["capability"], "ranked_summary")
        self.assertEqual(requirements["rtnn_ranked_summary"]["row_count"], 1)

    def test_gate_keeps_v4_and_broad_claims_out_of_v3(self):
        payload = self._run_gate()
        evidence = payload["evidence"]

        self.assertTrue(payload["checks"]["surface_rows_all_generic"])
        self.assertTrue(payload["checks"]["surface_rows_block_unsupported_claims"])
        self.assertTrue(payload["checks"]["app_boundary_rows_are_attributed"])
        self.assertTrue(payload["checks"]["v4_cabi_embedding_out_of_v3_public_surface"])
        self.assertTrue(payload["checks"]["broad_v2_speedup_claim_out"])
        self.assertEqual(evidence["wording_gate_status"], "pass")
        self.assertEqual(evidence["wording_gate_violation_count"], 0)
        self.assertFalse(evidence["claim_flags_required_false"]["release_authorized"])
        self.assertEqual(
            set(evidence["future_research_work_ids"]),
            {"barnes_hut_vector_accumulation_frontier_shape"},
        )
        self.assertEqual(
            set(evidence["additional_current_capabilities"]),
            {"aabb_candidate_stream", "aggregate_frontier", "collision_flag_stream", "threshold_summary"},
        )
        self.assertIn("v4_c_abi_embedding", evidence["exclusions"])
        self.assertIn("broad_v3_over_v2_speedup_claim", evidence["exclusions"])
        for value in evidence["claim_flags_required_false"].values():
            self.assertFalse(value)

    def test_gate_can_write_current_json_and_records_decision_audit(self):
        payload = self._run_gate("--pretty", "--json-out", str(JSON_OUT))
        self.assertTrue(JSON_OUT.exists())
        saved = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "objective_conformance_passed_not_release")
        self.assertEqual(saved["evidence"]["objective_required_capability_coverage_count"], 5)

        audit = payload["decision_audit"]
        self.assertEqual(
            set(audit),
            {"decision", "was_i_foolish", "foolish_actions", "other_path", "different_path_now"},
        )
        self.assertIn("No.", audit["was_i_foolish"])
        self.assertIn("objective conformance", audit["decision"])
        self.assertIn("machine-checkable", audit["different_path_now"])
        self.assertIn("serious all-app", audit["different_path_now"])


if __name__ == "__main__":
    unittest.main()
