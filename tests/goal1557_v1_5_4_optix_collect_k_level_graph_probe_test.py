from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[1]
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1557_v1_5_4_optix_collect_k_level_graph_probe.py"
REPORT = ROOT / "docs" / "reports" / "goal1557_v1_5_4_optix_collect_k_level_graph_replay_diagnostic_2026-05-08.md"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal1557_v1_5_4_optix_collect_k_level_graph_probe_2026-05-08.json"


class Goal1557V154OptixCollectKLevelGraphProbeTest(unittest.TestCase):
    def test_native_probe_uses_real_collect_k_level_kernels(self) -> None:
        text = API.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_level_graph_replay_probe", text)
        self.assertIn("ensure_collect_k_row_width2_final_compact_kernels", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_level_counts_derived", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_mark_counts_level_counts", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_prefix_offsets_level", text)
        self.assertIn("collect_k_bounded_i64_row_width2_final_compact_level_derived", text)
        self.assertIn("cuStreamBeginCapture", text)
        self.assertIn("cuGraphLaunch", text)

    def test_python_probe_keeps_claim_boundary_diagnostic(self) -> None:
        text = PROBE.read_text(encoding="utf-8")

        self.assertIn("rtdl_optix_collect_k_level_graph_replay_probe", text)
        self.assertIn("actual four-kernel collect-k compact-level sequence", text)
        self.assertIn("not a production", text)
        self.assertIn("not a public speedup claim", text)

    def test_measured_artifact_records_real_kernel_graphability(self) -> None:
        data = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        by_pair_count = {case["pair_count"]: case for case in data["cases"]}

        for pair_count in (1, 4, 16):
            with self.subTest(pair_count=pair_count):
                case = by_pair_count[pair_count]
                self.assertGreater(case["direct_over_graph_speedup"], 1.0)
                self.assertEqual(case["first_pair_count"], 4096)

    def test_report_keeps_production_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Accepted as a diagnostic engineering result", text)
        self.assertIn("does not alter the production", text)
        self.assertIn("remaining production challenge is parameterization", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
