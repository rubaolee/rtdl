import unittest
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1567_v1_5_4_optix_collect_k_output_indexed_fused_probe.py"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal1567_v1_5_4_optix_collect_k_output_indexed_fused_probe_2026-05-08.json"
REPORT = ROOT / "docs" / "reports" / "goal1567_v1_5_4_optix_collect_k_output_indexed_fused_negative_result_2026-05-08.md"


class Goal1567V154OptixCollectKOutputIndexedFusedProbeTest(unittest.TestCase):
    def test_kernel_uses_output_indexed_stable_merge_path(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        self.assertIn("collect_k_final_stable_partition", source)
        self.assertIn("collect_k_final_select_stable_output", source)
        self.assertIn("collect_k_bounded_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts", source)
        self.assertIn("collect_k_final_pair_compare", source)
        self.assertIn("shared_counts[threadIdx.x] = mark;", source)
        self.assertIn("block_counts[blockIdx.x] = shared_counts[0];", source)

    def test_probe_wires_reference_and_output_indexed_fused_paths(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe", source)
        self.assertIn("g_collect_k_i64_row_width2_final_output_indexed_materialize_mark_counts_level_counts", source)
        self.assertIn("launch_reference", source)
        self.assertIn("launch_fused", source)
        self.assertIn("mismatch_count_out", source)

    def test_python_probe_is_diagnostic_only(self) -> None:
        source = PROBE.read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe", source)
        self.assertIn("not a \"", source)
        self.assertIn("\"production", source)
        self.assertIn("not a public speedup claim", source)

    def test_measured_artifact_records_parity_but_regression(self) -> None:
        data = json.loads(JSON_ARTIFACT.read_text(encoding="utf-8"))
        by_pair = {case["pair_count"]: case for case in data["cases"]}
        for pair_count in (1, 4, 16):
            with self.subTest(pair_count=pair_count):
                case = by_pair[pair_count]
                self.assertEqual(case["mismatch_count"], 0)
                self.assertLess(case["reference_over_fused_speedup"], 1.0)

    def test_negative_report_rejects_production_promotion(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Do not promote this design", text)
        self.assertIn("extra merge-path binary searches", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
