import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_release_gap_ledger.py"
JSON_OUT = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_release_gap_ledger_2026-06-22.json"


class V3PhoenixReleaseGapLedgerTest(unittest.TestCase):
    def _run_ledger(self, *extra_args: str) -> dict:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), *extra_args],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        return json.loads(completed.stdout)

    def test_ledger_records_major_runtime_performance_p0_gap(self):
        payload = self._run_ledger()

        self.assertEqual(payload["tool"], "v3_phoenix_release_gap_ledger")
        self.assertEqual(payload["status"], "redo_required_major_performance_p0_open")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

        self.assertEqual({item["id"] for item in payload["done"]}, {
            "current_surface_width",
            "objective_capability_mapping",
            "unsupported_claim_boundaries",
            "source_tree_pod_gated_scope",
            "single_rtx_hardware_scope",
            "local_validation",
            "external_scoped_packet_verdict",
            "current_core_gap_external_redirect",
        })
        self.assertEqual(len(payload["remaining"]), 1)
        self.assertEqual(payload["remaining"][0]["id"], "major_runtime_performance_mandate")

    def test_ledger_carries_authoritative_gate_evidence(self):
        payload = self._run_ledger()
        evidence = payload["evidence"]

        self.assertEqual(evidence["readiness_status"], "redo_required")
        self.assertEqual(evidence["objective_conformance_status"], "objective_conformance_passed_not_release")
        self.assertEqual(evidence["external_verdict_intake_status"], "external_verdict_obtained")
        self.assertTrue(evidence["valid_external_verdict_obtained"])
        self.assertEqual(evidence["accepted_external_verdict"], "release_ready")
        self.assertTrue(evidence["scoped_packet_authorized"])
        self.assertEqual(evidence["current_core_gap_external_verdict"], "approve_blocked_not_release")
        self.assertEqual(
            evidence["current_core_gap_external_status_line"],
            "external_verdict_obtained_claude_approve_blocked_not_release",
        )
        self.assertFalse(evidence["current_core_gap_external_release_authorized"])
        self.assertEqual(
            evidence["current_core_gap_external_review_path"],
            "docs\\reviews\\claude_phoenix_v3_external_review_2026-06-22.md",
        )
        self.assertEqual(
            evidence["current_core_gap_external_status_path"],
            "docs\\rebuild\\v3\\phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md",
        )
        self.assertEqual(evidence["set_a_set_b_release_bar_proposal_status"], "proposal_only_not_authorization")
        self.assertEqual(
            evidence["set_a_set_b_release_bar_proposal_path"],
            "docs\\reviews\\phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md",
        )
        self.assertIn("runtime_executed True", evidence["set_a_set_b_release_bar_proposal_precondition"])
        self.assertEqual(evidence["major_performance_mandate_status"], "redo_required")
        self.assertEqual(evidence["reference_file_count"], 24)
        self.assertEqual(
            set(evidence["objective_capabilities_covered"]),
            {
                "raydb_grouped_reduction",
                "rtdbscan_component_union",
                "spatial_rayjoin_topology_stream",
                "triangle_prepared_graph",
                "rtnn_ranked_summary",
            },
        )
        self.assertIn("V4 C ABI", "\n".join(payload["claim_boundaries"]))
        self.assertIn("P0 gap", payload["decision_audit"]["different_path_now"])

    def test_ledger_can_write_json(self):
        payload = self._run_ledger("--pretty", "--json-out", str(JSON_OUT))
        self.assertTrue(JSON_OUT.exists())
        saved = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        self.assertEqual(saved["status"], "redo_required_major_performance_p0_open")
        self.assertEqual(saved["remaining"], payload["remaining"])


if __name__ == "__main__":
    unittest.main()
