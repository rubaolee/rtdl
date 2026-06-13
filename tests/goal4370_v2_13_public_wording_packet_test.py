from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_13_public_wording_packet import (
    markdown_v2_13_public_wording_packet,
    v2_13_public_wording_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_13_public_wording_packet.py"
REPORT = ROOT / "docs" / "reports" / "goal4370_v2_13_public_wording_packet_2026-06-13.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal4370_v2_13_public_wording_packet_2026-06-13.json"


class Goal4370V213PublicWordingPacketTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = v2_13_public_wording_packet()

    def test_public_wording_packet_accepts_row_scoped_only(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        self.assertEqual("accept_public_wording_packet", self.payload["status"])
        self.assertEqual(11, self.payload["summary"]["row_count"])
        self.assertEqual(10, self.payload["summary"]["row_scoped_public_wording_authorized_count"])
        self.assertEqual(1, self.payload["summary"]["blocked_row_count"])
        self.assertTrue(self.payload["summary"]["zero_unexplained_rows"])
        self.assertFalse(self.payload["broad_rt_core_claim_authorized"])
        self.assertFalse(self.payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(self.payload["rayjoin_whole_system_claim_authorized"])

    def test_blocked_wording_names_the_dangerous_claims(self) -> None:
        blocked = "\n".join(self.payload["blocked_wording"])
        for phrase in (
            "every benchmark app",
            "whole-application",
            "RayJoin paper",
            "RTDL beats RayJoin as a whole system",
            "RTNN is an RT-core neighbor-search",
            "automatic",
            "Intel GPU or AMD GPU",
        ):
            self.assertIn(phrase, blocked)

    def test_each_row_has_ratio_explanation_and_allowed_wording(self) -> None:
        for row in self.payload["rows"]:
            self.assertIn("divided by", row["speedup_explanation"], row["app"])
            self.assertTrue(row["allowed_wording"], row["app"])
            self.assertFalse(row["whole_app_speedup_claim_authorized"], row["app"])
        rows = {row["app"]: row for row in self.payload["rows"]}
        self.assertEqual(
            "blocked_not_rt_core_neighbor_search_claim",
            rows["rtnn"]["public_wording_status"],
        )
        self.assertFalse(rows["rtnn"]["row_scoped_public_wording_authorized"])
        self.assertIn("Do not publish RTNN", rows["rtnn"]["allowed_wording"])
        self.assertTrue(rows["spatial_rayjoin_pip"]["row_scoped_public_wording_authorized"])
        self.assertIn("output-surface caveat", rows["spatial_rayjoin_pip"]["allowed_wording"])

    def test_amd_decision_is_after_v2_13_close_not_now(self) -> None:
        amd = self.payload["amd_gpu_decision"]
        self.assertFalse(amd["prepare_amd_gpu_now"])
        self.assertTrue(self.payload["summary"]["prepare_amd_gpu_after_v2_13_close"])
        self.assertIn("after v2.13 is closed", amd["recommended_timing"])

    def test_markdown_contains_public_table_and_boundaries(self) -> None:
        markdown = markdown_v2_13_public_wording_packet(self.payload)
        self.assertIn("Goal4370 v2.13 Public Wording Packet", markdown)
        self.assertIn("Allowed Portfolio Wording", markdown)
        self.assertIn("Blocked Wording", markdown)
        self.assertIn("Prepare AMD GPU now: `False`", markdown)
        self.assertIn("broad speedup wording remains blocked", markdown)

    def test_script_writes_report_and_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "packet.json"
            out_md = Path(tmp) / "packet.md"
            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(out_json),
                    "--output-markdown",
                    str(out_md),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(out_json.read_text(encoding="utf-8"))
            report = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Goal4370 v2.13 Public Wording Packet", report)

    def test_committed_report_artifacts_are_current(self) -> None:
        committed = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["version"], committed["version"])
        self.assertEqual("accept", committed["validation"]["status"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal4370 v2.13 Public Wording Packet", report)
        self.assertIn("RTNN", report)


if __name__ == "__main__":
    unittest.main()
