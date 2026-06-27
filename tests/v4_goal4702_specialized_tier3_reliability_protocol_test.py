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


SCRIPT = ROOT / "scripts" / "v4_goal4702_specialized_tier3_reliability_protocol.py"


class V4Goal4702SpecializedTier3ReliabilityProtocolTest(unittest.TestCase):
    def test_protocol_freezes_20_attempts_4_variants_and_datasets(self) -> None:
        validation = v4.validate_v4_goal4702_specialized_tier3_reliability_protocol()
        protocol = validation["protocol"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual(4, len(protocol["callback_variants"]))
        self.assertEqual(5, protocol["attempts_per_variant"])
        self.assertEqual(20, protocol["total_attempts"])
        self.assertIn("dense_hits", protocol["datasets"])
        self.assertIn("sparse_hits", protocol["datasets"])
        self.assertIn("no_hit_empty_reduction", protocol["datasets"])
        self.assertGreaterEqual(protocol["compile_link_launch_success_floor"], 0.95)
        self.assertFalse(protocol["public_support_authorized"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "protocol.json"
            md_out = tmp_path / "protocol.md"
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
        self.assertIn("frozen protocol", markdown)


if __name__ == "__main__":
    unittest.main()
