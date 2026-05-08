from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1559_v1_5_4_optix_collect_k_level_graph_update_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal1559_v1_5_4_optix_collect_k_level_graph_update_diagnostic_2026-05-08.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal1559_v1_5_4_optix_collect_k_level_graph_update_probe_2026-05-08.json"


class Goal1559V154OptixCollectKLevelGraphUpdateProbeTest(unittest.TestCase):
    def test_native_probe_uses_graph_exec_kernel_node_updates(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_level_graph_update_probe", text)
        self.assertIn("cuGraphGetNodes", text)
        self.assertIn("cuGraphNodeGetType", text)
        self.assertIn("CU_GRAPH_NODE_TYPE_KERNEL", text)
        self.assertIn("CUDA_KERNEL_NODE_PARAMS", text)
        self.assertIn("cuGraphExecKernelNodeSetParams", text)
        self.assertIn("expected exactly four kernel nodes", text)

    def test_python_probe_keeps_claim_boundary_diagnostic(self) -> None:
        text = PROBE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_level_graph_update_probe", text)
        self.assertIn("not a production", text)
        self.assertIn("not a public speedup claim", text)
        self.assertIn("--target-pair-counts", text)

    def test_measured_artifact_records_successful_graph_exec_updates(self) -> None:
        data = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        by_target = {case["target_pair_count"]: case for case in data["cases"]}

        for target_pair_count in (4, 16):
            with self.subTest(target_pair_count=target_pair_count):
                case = by_target[target_pair_count]
                self.assertEqual(case["initial_pair_count"], 1)
                self.assertEqual(case["kernel_node_count"], 4)
                self.assertEqual(case["first_pair_count"], 4096)
                self.assertGreater(case["direct_over_graph_update_speedup"], 1.0)

    def test_report_keeps_next_step_and_claim_boundary_clear(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Accepted as a diagnostic engineering result", text)
        self.assertIn("cuGraphExecKernelNodeSetParams", text)
        self.assertIn("RTDL_OPTIX_COLLECT_K_LEVEL_GRAPH_REPLAY=1", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
