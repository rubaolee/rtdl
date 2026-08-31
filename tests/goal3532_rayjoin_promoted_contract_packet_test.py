from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal3532_rayjoin_promoted_contract_packet.py"
PREFLIGHT = ROOT / "docs" / "reports" / "goal3530_rayjoin_promoted_contract_preflight_2026-06-05.md"
REPORT = ROOT / "docs" / "reports" / "goal3532_rayjoin_promoted_contract_packet_2026-06-05.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3532_rayjoin_promoted_contract_packet_a5000_cdb_pair" / "summary.json"


class Goal3532RayJoinPromotedContractPacketTest(unittest.TestCase):
    def test_dry_run_outputs_all_promoted_contract_rows(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            output = pathlib.Path(tmpdir) / "dry_run.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--dry-run",
                    "--output",
                    str(output),
                    "--artifact-dir",
                    str(pathlib.Path(tmpdir) / "artifacts"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                timeout=60,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr[-1000:])
            payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3532.rayjoin_promoted_contract_packet.v1")
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["row_count"], 10)
        row_ids = {row["row_id"] for row in payload["rows"]}
        self.assertIn("rayjoin_count_parity_pip_prepared_optix", row_ids)
        self.assertIn("rayjoin_count_parity_lsi_left_id_dense_count", row_ids)
        self.assertIn("rayjoin_count_parity_overlay_seed_active_count", row_ids)
        self.assertIn("rayjoin_relation_columns_cdb_pair", row_ids)
        self.assertIn("rayjoin_relation_grouped_count_cdb_pair", row_ids)
        self.assertIn("rayjoin_shape_pair_payload_bounds_cdb_pair", row_ids)
        self.assertIn("rayjoin_shape_pair_payload_witness_cdb_pair", row_ids)
        self.assertIn("rayjoin_overlay_area_relation_stream_cdb_pair", row_ids)
        self.assertIn("rayjoin_overlay_area_device_tile_planner_cdb_pair", row_ids)
        self.assertIn("rayjoin_overlay_area_tile_executor_cdb_pair", row_ids)
        for row in payload["rows"]:
            boundary = row["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["app_specific_native_engine_shortcut_authorized"])

    def test_script_uses_existing_validated_surfaces(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        required = (
            "goal3465_rayjoin_relation_continuation_packet.py",
            "goal3492_overlay_area_public_cdb_tile_task_executor.py",
            "prepared_optix_left_id_dense_count",
            "prepared_optix_shape_pair_active_count",
            "left_id_count_device_columns_sec",
            "relation-stream-steady-state-evidence",
            "device-tile-task-planner",
            "component-bounds-filter",
        )
        for phrase in required:
            self.assertIn(phrase, text)

    def test_preflight_and_packet_share_contract_boundaries(self) -> None:
        report = PREFLIGHT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")
        for phrase in (
            "count/parity",
            "relation columns",
            "shape-pair payload",
            "overlay-area continuation",
        ):
            self.assertIn(phrase, report)
        for phrase in (
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "full_overlay_area_claim_authorized",
            "app_specific_native_engine_shortcut_authorized",
        ):
            self.assertIn(phrase, script)

    def test_no_release_or_speedup_is_authorized(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn('"release_authorized": False', text)
        self.assertIn('"public_speedup_claim_authorized": False', text)
        self.assertIn('"rtdl_beats_rayjoin_claim_authorized": False', text)
        self.assertIn("does not authorize public performance wording", text)

    def test_a5000_artifact_has_ten_real_promoted_rows_and_clean_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "rtdl.goal3532.rayjoin_promoted_contract_packet.v1")
        self.assertEqual(payload["rtdl_commit"], "98879336e041bff6363f0a18e3996953a021d53a")
        self.assertIn("NVIDIA RTX A5000", payload["gpu"])
        self.assertFalse(payload["dry_run"])
        self.assertEqual(payload["row_count"], 10)
        for row in payload["rows"]:
            self.assertEqual(row["status"], "ok")
            self.assertIsInstance(row["primary_metric_sec"], float)
            self.assertGreaterEqual(row["primary_metric_sec"], 0.0)
            boundary = row["claim_boundary"]
            self.assertFalse(boundary["release_authorized"])
            self.assertFalse(boundary["public_speedup_claim_authorized"])
            self.assertFalse(boundary["rt_core_speedup_claim_authorized"])
            self.assertFalse(boundary["app_specific_native_engine_shortcut_authorized"])

    def test_report_records_dataset_boundary_and_non_release_status(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "checked-in non-empty CDB fixture pair",
            "not a RayJoin paper reproduction",
            "not a public speedup claim",
            "rayjoin_overlay_area_tile_executor_cdb_pair",
            "0.001268",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
