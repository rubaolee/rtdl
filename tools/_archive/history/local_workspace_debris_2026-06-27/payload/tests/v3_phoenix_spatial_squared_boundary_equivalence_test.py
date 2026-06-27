from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_spatial_squared_boundary_equivalence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_spatial_squared_boundary_equivalence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixSpatialSquaredBoundaryEquivalenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.markdown = PACKET_MD.read_text(encoding="utf-8")

    def test_guarded_equivalence_passes_without_authorizing_claims(self) -> None:
        packet = self.packet
        self.assertEqual(
            packet["status"],
            "spatial_guarded_squared_boundary_equivalence_pass_not_release",
        )
        self.assertEqual(packet["optimization"], "exact_f64_guarded_squared_boundary_predicate")
        self.assertEqual(packet["generic_capability"], "point_location_topology_stream")
        self.assertEqual(packet["failed_checks"], [])
        self.assertTrue(all(packet["checks"].values()))
        self.assertFalse(packet["release_authorized"])
        self.assertFalse(packet["public_speedup_claim_authorized"])
        self.assertFalse(packet["m7_promotion_authorized"])
        self.assertEqual(packet["m7_qualified_release_rows_added"], 0)

    def test_records_pure_squared_risk_and_guarded_zero_mismatch(self) -> None:
        packet = self.packet
        self.assertEqual(packet["case_counts"]["deterministic_cases"], 1260)
        self.assertEqual(packet["case_counts"]["random_cases"], 200000)
        self.assertEqual(packet["case_counts"]["total_cases"], 201260)
        self.assertEqual(packet["guarded_mismatch_count"], 0)
        self.assertEqual(packet["mismatch_count"], 0)
        self.assertEqual(packet["pure_squared_mismatch_count"], 10)
        self.assertEqual(packet["equivalence_scope"]["guard_tol"], 1.0e-6)
        self.assertIn("pure squared", packet["equivalence_scope"]["pure_squared_risk"])
        self.assertIn("fall back", packet["equivalence_scope"]["guarded_partition"])

    def test_markdown_explains_guarded_fallback(self) -> None:
        for phrase in (
            "Status: `spatial_guarded_squared_boundary_equivalence_pass_not_release`.",
            "Guarded mismatches: `0`",
            "Pure squared mismatches recorded: `10`",
            "Guard tolerance: `1e-06`.",
            "Was I foolish?",
        ):
            self.assertIn(phrase, self.markdown)

    def test_script_rebuilds_packet(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "packet.json"
            md_out = Path(tmp) / "packet.md"
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
            self.assertEqual(json.loads(json_out.read_text(encoding="utf-8")), self.packet)
            self.assertIn("Guarded mismatches", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
