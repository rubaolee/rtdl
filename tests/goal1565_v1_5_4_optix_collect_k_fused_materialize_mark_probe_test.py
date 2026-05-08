import unittest
from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "goal1565_v1_5_4_optix_collect_k_fused_materialize_mark_probe.py"
JSON_ARTIFACT = ROOT / "docs" / "reports" / "goal1565_v1_5_4_optix_collect_k_fused_materialize_mark_probe_2026-05-08.json"
REPORT = ROOT / "docs" / "reports" / "goal1565_v1_5_4_optix_collect_k_fused_materialize_mark_negative_result_2026-05-08.md"


class Goal1565V154OptixCollectKFusedMaterializeMarkProbeTest(unittest.TestCase):
    def test_fused_kernel_uses_output_indexed_marks_and_atomic_counts(self) -> None:
        source = CORE.read_text(encoding="utf-8")
        self.assertIn("collect_k_bounded_i64_row_width2_final_materialize_mark_counts_level_counts", source)
        self.assertIn("marks[global_output_index] = mark;", source)
        self.assertIn("atomicAdd(&block_counts[pair_index * blocks_per_pair + output_block], 1u);", source)
        self.assertIn("collect_k_final_lower_bound(second_rows", source)
        self.assertIn("collect_k_final_upper_bound(first_rows", source)

    def test_native_probe_keeps_reference_and_fused_paths_separate(self) -> None:
        source = API.read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_collect_k_fused_materialize_mark_probe", source)
        self.assertIn("launch_reference", source)
        self.assertIn("launch_fused", source)
        self.assertIn("cuMemsetD32Async(fused_marks", source)
        self.assertIn("cuMemsetD32Async(fused_block_counts", source)
        self.assertIn("mismatch_count_out", source)

    def test_python_probe_keeps_claim_boundary_diagnostic(self) -> None:
        source = PROBE.read_text(encoding="utf-8")
        self.assertIn("rtdl_optix_collect_k_fused_materialize_mark_probe", source)
        self.assertIn("not a production", source)
        self.assertIn("not a public speedup claim", source)
        self.assertIn("--pair-counts", source)

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
        self.assertIn("Do not\npromote this atomic/reset fusion design", text)
        self.assertIn("stream resets plus atomic block-count accumulation", text)
        self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
