from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import v3_phoenix_aabb_raw_oracle_evidence as oracle


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v3_phoenix_aabb_raw_oracle_evidence.py"


class V3PhoenixAabbRawOracleEvidenceTest(unittest.TestCase):
    def test_cpu_oracle_fixture_exercises_overlap_zero_touch_and_duplicate_pressure(self) -> None:
        fixture = oracle.fixture_catalog()[0]
        rows = oracle.cpu_oracle_rows(
            fixture["indexed_boxes"],
            fixture["query_boxes"],
            indexed_ids=fixture["indexed_ids"],
            query_ids=fixture["query_ids"],
        )

        self.assertIn((201, 101), rows)
        self.assertIn((201, 102), rows)
        self.assertIn((201, 105), rows)
        self.assertIn((202, 102), rows)
        self.assertIn((202, 103), rows)
        self.assertIn((202, 105), rows)
        self.assertNotIn((203, 101), rows)
        self.assertIn((204, 104), rows)
        self.assertIn((205, 101), rows)
        self.assertIn((205, 102), rows)
        self.assertIn((205, 105), rows)

    def test_cpu_backend_payload_matches_independent_oracle_without_release_claims(self) -> None:
        payload = oracle.build_payload(("cpu",))

        self.assertEqual(payload["status"], "aabb_raw_oracle_pass_not_m7")
        self.assertFalse(payload["raw_aabb_oracle_closes_correctness_blocker"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["failed_checks"], [])
        self.assertEqual({row["backend"] for row in payload["observed_rows"]}, {"cpu"})
        self.assertTrue(all(row["matches_independent_cpu_oracle"] for row in payload["observed_rows"]))
        self.assertIsNone(payload["capacity_pressure"])
        self.assertEqual(len(payload["source_manifest_sha256"]), 64)

    def test_rendered_markdown_keeps_boundary(self) -> None:
        payload = oracle.build_payload(("cpu",))
        markdown = oracle.render_markdown(payload)

        self.assertIn("not release evidence and not a performance claim", markdown)
        self.assertIn("Release authorized: `false`", markdown)
        self.assertIn("M7 promotion authorized: `false`", markdown)
        self.assertIn("Goal-Level Decision Self-Audit", markdown)

    def test_script_writes_requested_outputs_for_cpu_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmpdir = Path(tmp)
            json_out = tmpdir / "packet.json"
            md_out = tmpdir / "packet.md"
            evidence_dir = tmpdir / "evidence"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--backends",
                    "cpu",
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                    "--evidence-dir",
                    str(evidence_dir),
                ],
                cwd=ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(payload["status"], "aabb_raw_oracle_pass_not_m7")
            self.assertTrue((evidence_dir / "summary.json").exists())
            self.assertIn("Phoenix V3 AABB Raw Oracle Evidence", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
