from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1192_public_wording_evidence_batch_packet as goal1192


ROOT = Path(__file__).resolve().parents[1]


class Goal1192PublicWordingEvidenceBatchPacketTest(unittest.TestCase):
    def test_packet_is_valid_and_has_expected_rows(self) -> None:
        payload = goal1192.build_packet()
        self.assertTrue(payload["valid"], payload)
        self.assertEqual(payload["expected_app_count"], 6)
        self.assertEqual(payload["expected_output_count"], 12)
        self.assertEqual(payload["blockers"], [])

    def test_runner_contains_boundaries_and_commands(self) -> None:
        text = (ROOT / payload_runner()).read_text(encoding="utf-8")
        self.assertIn("does not authorize public", text)
        self.assertIn("make build-optix", text)
        self.assertIn("database_compact_summary_optix.json", text)
        self.assertIn("polygon_jaccard_safe_chunk_embree.json", text)
        self.assertIn("hausdorff_threshold_prepared_optix.json", text)
        self.assertIn("tar -czf", text)

    def test_cli_writes_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_json = Path(tmp) / "packet.json"
            output_md = Path(tmp) / "packet.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1192_public_wording_evidence_batch_packet.py",
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"])
            self.assertIn("expected outputs: `12`", markdown)
            self.assertIn("does not authorize public RTX speedup wording", markdown)


def payload_runner() -> str:
    return goal1192.build_packet()["runner"]


if __name__ == "__main__":
    unittest.main()
