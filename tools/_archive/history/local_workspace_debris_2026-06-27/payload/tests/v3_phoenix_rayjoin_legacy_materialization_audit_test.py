from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.v3_phoenix_rayjoin_legacy_materialization_audit import build_payload


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rayjoin_legacy_materialization_audit.py"
JSON_OUT = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rayjoin_legacy_materialization_audit_2026-06-22.json"
)
MD_OUT = JSON_OUT.with_suffix(".md")


class V3PhoenixRayJoinLegacyMaterializationAuditTest(unittest.TestCase):
    def test_payload_selects_topology_stream_without_authorizing_pod_spend(self) -> None:
        payload = build_payload()

        self.assertEqual(payload["status"], "rayjoin_materialization_audit_complete_not_release")
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])
        self.assertFalse(payload["all_app_pod_spend_authorized"])
        self.assertFalse(payload["focused_pod_spend_authorized"])
        self.assertFalse(payload["rayjoin_as_whole_app_target"])
        self.assertTrue(payload["rayjoin_topology_stream_family_target"])
        self.assertTrue(payload["host_materialization_source_exists"])
        self.assertTrue(payload["current_hot_routes_already_eliminate_many_host_boundaries"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["source_checks"].values()))
        self.assertEqual(
            payload["recommended_next_probe"],
            "pip_relation_status_corrected_executor_through_prepared_execution_runner",
        )

    def test_route_assessments_prevent_rtdbscan_style_parity_trap(self) -> None:
        payload = build_payload()
        routes = {row["route"]: row for row in payload["route_assessments"]}

        self.assertTrue(routes["pip_exact_prepared_points"]["v3_runtime_source_exists"])
        self.assertFalse(routes["pip_exact_prepared_points"]["immediate_material_probe"])
        self.assertTrue(routes["pip_relation_status_corrected_executor"]["immediate_material_probe"])
        self.assertFalse(routes["lsi_dense_left_id_count"]["v3_runtime_source_exists"])
        self.assertFalse(routes["overlay_active_count_device_continuation"]["immediate_material_probe"])
        self.assertIn("runner-vs-legacy", payload["pod_decision"])
        self.assertIn("goal_level_decision_audit", payload)

    def test_cli_writes_auditable_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "audit.json"
            md_out = Path(tmp) / "audit.md"
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
            saved = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(saved["status"], "rayjoin_materialization_audit_complete_not_release")
            markdown = md_out.read_text(encoding="utf-8")
            self.assertIn("Phoenix V3 RayJoin Legacy Materialization Audit", markdown)
            self.assertIn("focused_pod_spend_authorized: false", markdown)
            self.assertIn("point_location_topology_stream", markdown)

    def test_checked_in_outputs_match_builder(self) -> None:
        payload = build_payload()
        saved = json.loads(JSON_OUT.read_text(encoding="utf-8"))
        self.assertEqual(saved, payload)
        markdown = MD_OUT.read_text(encoding="utf-8")
        self.assertIn("Recommended next probe", markdown)
        self.assertIn("Release remains `redo_required`", markdown)


if __name__ == "__main__":
    unittest.main()
