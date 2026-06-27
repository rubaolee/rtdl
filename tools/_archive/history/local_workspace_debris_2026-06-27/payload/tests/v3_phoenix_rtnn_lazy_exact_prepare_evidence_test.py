import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v3_phoenix_rtnn_lazy_exact_prepare_evidence.py"
PACKET_JSON = (
    ROOT
    / "docs"
    / "rebuild"
    / "v3"
    / "phoenix_v3_rtnn_lazy_exact_prepare_evidence_2026-06-21.json"
)
PACKET_MD = PACKET_JSON.with_suffix(".md")


class V3PhoenixRtnnLazyExactPrepareEvidenceTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.payload = json.loads(PACKET_JSON.read_text(encoding="utf-8"))
        cls.text = PACKET_MD.read_text(encoding="utf-8")

    def test_packet_records_small_generic_optimization_not_m7(self) -> None:
        payload = self.payload
        self.assertEqual(
            payload["status"],
            "rtnn_lazy_exact_prepare_reduces_prepare_not_m7_wall_floor_not_met",
        )
        self.assertEqual(
            payload["generic_capability"],
            "fixed_radius_neighbors_3d_lazy_exact_search_device_materialization",
        )
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertFalse(payload["m7_promotion_authorized"])
        self.assertEqual(payload["m7_qualified_release_rows_added"], 0)
        self.assertEqual(payload["failed_checks"], [])
        self.assertTrue(all(payload["checks"].values()))

    def test_comparisons_show_real_but_insufficient_movement(self) -> None:
        comparisons = self.payload["comparisons"]
        self.assertGreater(comparisons["self_query_prepare_reduction_prepatch_to_lazy"], 1.0)
        self.assertLess(comparisons["self_query_prepare_reduction_prepatch_to_lazy"], 1.2)
        self.assertGreater(comparisons["self_query_cold_plus_query_reduction_prepatch_to_lazy"], 1.0)
        self.assertLess(comparisons["self_query_cold_plus_query_reduction_prepatch_to_lazy"], 1.2)
        self.assertGreater(comparisons["lazy_self_query_over_cupy_hot_speedup"], 19.0)
        self.assertLess(comparisons["lazy_self_query_over_cupy_cold_plus_query_speedup"], 2.0)
        self.assertLess(comparisons["lazy_self_query_over_cupy_runner_wall_speedup"], 2.0)

    def test_parity_and_markdown_boundaries_are_visible(self) -> None:
        self.assertTrue(self.payload["parity"]["integer_signature_match_with_cupy"])
        self.assertTrue(self.payload["parity"]["integer_signature_match_with_lazy_old_prepared_query"])
        self.assertLess(self.payload["parity"]["sum_distance_relative_error"], 1.0e-4)
        for phrase in (
            "M7 rows added by this packet: 0",
            "Self-query prepare reduction from lazy exact: `1.111x`",
            "Lazy self-query over CuPy runner-wall speedup: `1.076x`",
            "Do not call lazy exact a major V3 performance row.",
            "Goal-Level Decision Audit",
        ):
            self.assertIn(phrase, self.text)

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
            rebuilt = json.loads(json_out.read_text(encoding="utf-8"))
            self.assertEqual(rebuilt["status"], self.payload["status"])
            self.assertEqual(rebuilt["comparisons"], self.payload["comparisons"])
            self.assertIn("Phoenix V3 RTNN Lazy Exact Prepare Evidence", md_out.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
