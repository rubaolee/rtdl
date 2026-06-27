from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4_maintainer as v4


SCRIPT = ROOT / "scripts" / "v4_goal4709_formal_hp_app_target_selection.py"


class V4Goal4709FormalHpAppTargetSelectionTest(unittest.TestCase):
    def test_selects_new_generic_app_target_without_pod_authorization(self) -> None:
        validation = v4.validate_v4_goal4709_formal_hp_app_target_selection()
        selection = validation["selection"]
        self.assertEqual("passed", validation["status"])
        self.assertEqual("ray_triangle_custom_scored_accumulation", selection["selected_app"])
        self.assertFalse(selection["pod_authorized"])
        self.assertFalse(selection["app_level_speed_claim_authorized"])
        self.assertTrue(selection["selected_target_contract"]["not_app_specific_kernel"])
        self.assertGreaterEqual(len(selection["rejected_existing_targets"]), 5)

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "target.json"
            md_out = tmp_path / "target.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")

        self.assertEqual("passed", payload["validation_status"])
        self.assertEqual("passed", stdout_payload["validation_status"])
        self.assertIn("Formal High-Performance App Target Selection", markdown)


if __name__ == "__main__":
    unittest.main()
