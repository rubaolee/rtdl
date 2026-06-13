from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from rtdsl.v2_13_rayjoin_authors_code_packet import (
    markdown_v2_13_rayjoin_authors_code_packet,
    v2_13_rayjoin_authors_code_packet,
)


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_13_rayjoin_authors_code_packet.py"
REPORT_MD = ROOT / "docs" / "reports" / "goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.md"
REPORT_JSON = ROOT / "docs" / "reports" / "goal4367_rayjoin_authors_code_comparison_packet_2026-06-13.json"


class Goal4367RayJoinAuthorsCodeComparisonPacketTest(unittest.TestCase):
    def setUp(self) -> None:
        self.payload = v2_13_rayjoin_authors_code_packet()

    def test_packet_accepts_same_stream_authors_code_comparison(self) -> None:
        self.assertEqual("accept", self.payload["validation"]["status"], self.payload["validation"]["errors"])
        self.assertEqual(
            "rtdl.v2_13.rayjoin_authors_code_packet.goal4367.v1",
            self.payload["version"],
        )
        self.assertEqual("accepted_internal_authors_code_comparison_packet", self.payload["status"])
        self.assertTrue(self.payload["claim_boundary"]["same_query_stream_with_rayjoin_query_exec"])
        self.assertFalse(self.payload["claim_boundary"]["rtdl_beats_rayjoin_claim_authorized"])
        self.assertFalse(self.payload["claim_boundary"]["full_rayjoin_paper_reproduction"])

    def test_artifact_manifest_records_stream_hashes(self) -> None:
        manifest = {row["name"]: row for row in self.payload["artifact_manifest"]}
        self.assertEqual(
            "6bed3890d327cbd7f33c6fb3c14b306484aa9f1ccca001710ec164f4d03671bd",
            manifest["rayjoin_lsi_gen100000_stream.json"]["sha256"],
        )
        self.assertEqual(
            "d5ba3289e346febf86492d2f5d7abdab1a14977a5b6518fc813fd665a90b63a0",
            manifest["rayjoin_pip_gen100000_stream.json"]["sha256"],
        )
        self.assertEqual(12629271, manifest["rayjoin_lsi_gen100000_stream.json"]["bytes"])
        self.assertEqual(7059404, manifest["rayjoin_pip_gen100000_stream.json"]["bytes"])
        self.assertTrue(all(len(row["sha256"]) == 64 for row in manifest.values()))

    def test_rayjoin_and_rtdl_tables_keep_lsi_pip_directionality(self) -> None:
        rayjoin_logs = {
            (row["workload"], row["mode"]): row for row in self.payload["rayjoin_original_logs"]
        }
        self.assertEqual(6, len(rayjoin_logs))
        self.assertEqual(0.819, rayjoin_logs[("lsi", "rt")]["query_ms"])
        self.assertEqual(0.83, rayjoin_logs[("pip", "rt")]["query_ms"])

        rtdl_rows = {
            (row["workload"], row["backend"]): row for row in self.payload["rtdl_same_stream_results"]
        }
        self.assertEqual(8921, rtdl_rows[("lsi", "optix")]["count"])
        self.assertEqual(8686, rtdl_rows[("pip", "embree")]["count"])
        self.assertFalse(rtdl_rows[("lsi", "optix")]["row_stream_materialized"])

        direct = {
            (row["workload"], row["rtdl_backend"]): row for row in self.payload["direct_comparison"]
        }
        self.assertGreater(direct[("lsi", "optix")]["rayjoin_rt_over_rtdl"], 1.0)
        self.assertLess(direct[("pip", "optix")]["rayjoin_rt_over_rtdl"], 0.1)
        self.assertGreater(direct[("pip", "optix")]["rayjoin_rt_faster_than_rtdl"], 10.0)
        self.assertIn("RayJoin RT faster", direct[("pip", "optix")]["readout"])

    def test_interpretation_distinguishes_lsi_win_from_pip_debt(self) -> None:
        self.assertIn("Reasonable strong RTDL result", self.payload["interpretation"]["lsi"])
        self.assertIn("not good enough for RTDL", self.payload["interpretation"]["pip"])
        self.assertIn("optimization debt", self.payload["interpretation"]["pip"])

    def test_markdown_contains_direction_rule_and_claim_boundary(self) -> None:
        markdown = markdown_v2_13_rayjoin_authors_code_packet(self.payload)
        self.assertIn("Direction Rule", markdown)
        self.assertIn("Values below 1 mean RayJoin RT is faster", markdown)
        self.assertIn("RayJoin Authors-Code Comparison Packet", markdown)
        self.assertIn("rayjoin_lsi_gen100000_stream.json", markdown)
        self.assertIn("Validation status: `accept`", markdown)

    def test_script_writes_packet_artifacts(self) -> None:
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
            markdown = out_md.read_text(encoding="utf-8")
            self.assertEqual("accept", payload["validation"]["status"])
            self.assertIn("Goal4367 RayJoin Authors-Code Comparison Packet", markdown)

    def test_committed_packet_artifacts_are_current(self) -> None:
        committed = json.loads(REPORT_JSON.read_text(encoding="utf-8"))
        self.assertEqual(self.payload["version"], committed["version"])
        self.assertEqual("accept", committed["validation"]["status"])
        report = REPORT_MD.read_text(encoding="utf-8")
        self.assertIn("Goal4367 RayJoin Authors-Code Comparison Packet", report)
        self.assertIn("RayJoin RT / RTDL", report)
        self.assertIn("not broad public speedup wording", report)


if __name__ == "__main__":
    unittest.main()
