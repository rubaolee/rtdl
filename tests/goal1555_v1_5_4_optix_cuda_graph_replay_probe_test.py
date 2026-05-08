from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1555_v1_5_4_optix_cuda_graph_replay_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal1555_v1_5_4_optix_cuda_graph_replay_feasibility_2026-05-08.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal1555_v1_5_4_optix_cuda_graph_replay_probe_2026-05-08.json"


class Goal1555V154OptixCudaGraphReplayProbeTest(unittest.TestCase):
    def test_native_probe_exports_cuda_graph_replay_path(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_cuda_graph_replay_probe", text)
        self.assertIn("cuStreamBeginCapture", text)
        self.assertIn("cuGraphInstantiate", text)
        self.assertIn("cuGraphLaunch", text)
        self.assertIn("cuGraphExecDestroy", text)
        self.assertIn("commands_per_replay", text)

    def test_python_probe_bounds_the_claim(self) -> None:
        text = PROBE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_cuda_graph_replay_probe", text)
        self.assertIn("CUDA graph replay feasibility only", text)
        self.assertIn("not a COLLECT_K_BOUNDED", text)
        self.assertIn("not authorize a collect-k speedup claim", text)
        self.assertIn("--commands-per-replay", text)

    def test_measured_artifact_records_batched_replay_signal(self) -> None:
        data = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        by_commands = {case["commands_per_replay"]: case for case in data["cases"]}

        self.assertLess(by_commands[1]["direct_over_graph_speedup"], 1.0)
        self.assertGreater(by_commands[4]["direct_over_graph_speedup"], 1.0)
        self.assertGreater(by_commands[8]["direct_over_graph_speedup"], 1.0)
        self.assertGreater(by_commands[16]["direct_over_graph_speedup"], 1.0)
        self.assertEqual(by_commands[16]["final_value_hex"], "0x5a5aa50f")

    def test_report_keeps_claim_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Accepted as a feasibility finding", text)
        self.assertIn("not as a collect-k optimization", text)
        self.assertIn("single-command case is negative", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
