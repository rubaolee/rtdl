import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1638_v1_6_x_optix_collect_k_level_graph_final_pair_scale_probe_2026-05-09.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal1638_level_graph_pair1_segment65536_repeats1000.json"


class Goal1638OptixCollectKLevelGraphFinalPairScaleProbeTest(unittest.TestCase):
    def test_artifact_records_bounded_positive_diagnostic_signal(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        case = payload["cases"][0]

        self.assertEqual(payload["probe"], "goal1557_v1_5_4_optix_collect_k_level_graph_probe")
        self.assertEqual(payload["repeats"], 1000)
        self.assertEqual(case["pair_count"], 1)
        self.assertEqual(case["segment_capacity"], 65536)
        self.assertEqual(case["first_pair_count"], 131072)
        self.assertLess(case["graph_per_replay_us"], case["direct_per_replay_us"])
        self.assertGreater(case["direct_over_graph_speedup"], 1.0)

    def test_report_keeps_claim_boundary_and_next_direction_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`bounded_positive_diagnostic_not_production_ready`", text)
        self.assertIn("total block count guardrail is `1..512`", text)
        self.assertIn("does not yet justify reviving graph replay as a production", text)
        self.assertIn("prepared end-to-end stable-topology graph", text)
        self.assertIn("does not authorize public speedup wording", text)
        self.assertIn("stable `COLLECT_K_BOUNDED` promotion", text)


if __name__ == "__main__":
    unittest.main()
