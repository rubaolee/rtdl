import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1632_v1_6_x_optix_collect_k_output_indexed_fused_negative_probe_2026-05-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1632_output_indexed_fused_probe_segment131072_repeats100.json"


class Goal1632OptixCollectKOutputIndexedFusedNegativeProbeTest(unittest.TestCase):
    def test_artifact_records_slower_fused_path_with_parity(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["probe"], "goal1567_v1_5_4_optix_collect_k_output_indexed_fused_probe")
        self.assertEqual(payload["repeats"], 100)
        self.assertEqual([case["pair_count"] for case in payload["cases"]], [1, 2, 4])
        for case in payload["cases"]:
            self.assertEqual(case["segment_capacity"], 131072)
            self.assertEqual(case["mismatch_count"], 0)
            self.assertLess(case["reference_over_fused_speedup"], 1.0)
            self.assertGreater(case["fused_per_replay_us"], case["reference_per_replay_us"])

    def test_report_rejects_production_selection_and_preserves_claim_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`output_indexed_fused_not_selected`", text)
        self.assertIn("Do not integrate the output-indexed fused materialize+mark path", text)
        self.assertIn("final count/prefix/compact sequence", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("true zero-copy wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)
        self.assertIn("release action", text)


if __name__ == "__main__":
    unittest.main()
