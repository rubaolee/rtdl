import unittest
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
REPORT = ROOT / "docs" / "reports" / "goal1640_v1_6_x_optix_collect_k_graph_full_scale_diagnostic_2026-05-09.md"
REPLAY_ARTIFACT = ROOT / "docs" / "reports" / "goal1640_level_graph_pair1_segment131072_repeats1000.json"
UPDATE_ARTIFACT = ROOT / "docs" / "reports" / "goal1640_level_graph_update_pair1_segment131072_repeats1000.json"


class Goal1640OptixCollectKGraphProbeGuardrailExtensionTest(unittest.TestCase):
    def test_graph_diagnostic_guardrails_cover_final_pair_scale_without_production_flag(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("collect-k graph replay probe total block count must be in 1..4096", text)
        self.assertIn("collect-k graph update probe total block count must be in 1..4096", text)
        self.assertNotIn("RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY", text)
        self.assertNotIn("collect_k_use_level_graph_replay", text)

    def test_full_scale_replay_and_update_artifacts_are_positive_but_bounded(self) -> None:
        replay = json.loads(REPLAY_ARTIFACT.read_text(encoding="utf-8"))["cases"][0]
        update = json.loads(UPDATE_ARTIFACT.read_text(encoding="utf-8"))["cases"][0]

        self.assertEqual(replay["pair_count"], 1)
        self.assertEqual(replay["segment_capacity"], 131072)
        self.assertEqual(replay["first_pair_count"], 262144)
        self.assertGreater(replay["direct_over_graph_speedup"], 1.0)

        self.assertEqual(update["target_pair_count"], 1)
        self.assertEqual(update["segment_capacity"], 131072)
        self.assertEqual(update["kernel_node_count"], 4)
        self.assertEqual(update["first_pair_count"], 262144)
        self.assertGreater(update["direct_over_graph_update_speedup"], 1.0)

    def test_report_keeps_production_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("`full_scale_graph_diagnostic_positive_but_insufficient`", text)
        self.assertIn("Production effect: none", text)
        self.assertIn("does not yet solve the Goal1637 bottleneck", text)
        self.assertIn("full steady-state production dependency chain", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
