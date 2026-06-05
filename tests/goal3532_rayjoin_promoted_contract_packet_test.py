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


if __name__ == "__main__":
    unittest.main()
