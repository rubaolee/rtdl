import ast
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal1863_segment_polygon_hitcount_v2_partner_perf.py"
REPORT = ROOT / "docs" / "reports" / "goal2052_segment_polygon_hitcount_cupy_l4_runner_repair_2026-05-15.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2052_segment_polygon_hitcount_cupy_l4_2048.json"
ARTIFACT_4096 = ROOT / "docs" / "reports" / "goal2052_segment_polygon_hitcount_cupy_l4_4096_capacity32768.json"


class Goal2052SegmentPolygonHitcountCupyL4RunnerRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script_text = SCRIPT.read_text(encoding="utf-8")
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        cls.artifact_4096 = json.loads(ARTIFACT_4096.read_text(encoding="utf-8"))
        cls.tree = ast.parse(cls.script_text)

    def _ray_column_dtype_literals(self):
        dtypes = {}
        for node in ast.walk(self.tree):
            if not isinstance(node, ast.Dict):
                continue
            for key, value in zip(node.keys, node.values):
                if not isinstance(key, ast.Constant) or key.value not in {"ox", "oy", "dx", "dy", "tmax"}:
                    continue
                if not isinstance(value, ast.Call) or len(value.args) < 2:
                    continue
                dtype = value.args[1]
                if (
                    isinstance(dtype, ast.Subscript)
                    and isinstance(dtype.value, ast.Name)
                    and dtype.value.id == "runtime"
                    and isinstance(dtype.slice, ast.Constant)
                ):
                    dtypes[key.value] = dtype.slice.value
        return dtypes

    def test_runner_uses_float32_for_optix_ray_columns(self):
        self.assertEqual(
            self._ray_column_dtype_literals(),
            {
                "ox": "float32",
                "oy": "float32",
                "dx": "float32",
                "dy": "float32",
                "tmax": "float32",
            },
        )

    def test_runner_exposes_explicit_output_capacity_for_large_runs(self):
        self.assertIn('parser.add_argument("--output-capacity"', self.script_text)
        self.assertIn("output_capacity = args.output_capacity if args.output_capacity is not None else args.count * 2", self.script_text)
        self.assertIn('--output-capacity must be at least --count', self.script_text)

    def test_artifact_records_l4_success_and_parity(self):
        self.assertEqual(self.artifact["status"], "pass")
        self.assertEqual(self.artifact["count"], 2048)
        self.assertEqual(self.artifact["gpu"], "NVIDIA L4, 570.195.03")
        self.assertEqual(self.artifact["source_commit_label"], "5ef65173-plus-goal2052-runner-float32")
        self.assertTrue(self.artifact["parity"]["strict_counts_match"])
        self.assertEqual(self.artifact["parity"]["expected_row_count"], 2048)
        self.assertIn("cupy", self.artifact["partners"])

    def test_prepared_partner_path_beats_same_contract_prepared_baseline(self):
        prepared_baseline = self.artifact["prepared_baseline"]["query_summary"]["median_s"]
        partner = self.artifact["partners"]["cupy"]
        unprepared_partner = partner["query_summary"]["median_s"]
        prepared_partner = partner["goal1886_prepared_reuse"]["query_summary"]["median_s"]

        self.assertLess(prepared_partner, prepared_baseline)
        self.assertLess(prepared_partner, unprepared_partner)
        self.assertLess(partner["goal1886_prepared_reuse"]["query_median_ratio_vs_v1_8_prepared_native"], 1.0)
        self.assertTrue(partner["goal1886_prepared_reuse"]["prepared_scene_reused"])
        self.assertTrue(partner["goal1886_prepared_reuse"]["witness_output_columns_reused"])

    def test_explicit_capacity_4096_artifact_passes_and_beats_prepared_baseline(self):
        self.assertEqual(self.artifact_4096["status"], "pass")
        self.assertEqual(self.artifact_4096["count"], 4096)
        self.assertEqual(self.artifact_4096["output_capacity"], 32768)
        self.assertEqual(self.artifact_4096["source_commit_label"], "5ef65173-plus-goal2052-runner-float32-capacity")
        self.assertTrue(self.artifact_4096["parity"]["strict_counts_match"])

        prepared_baseline = self.artifact_4096["prepared_baseline"]["query_summary"]["median_s"]
        prepared_partner = self.artifact_4096["partners"]["cupy"]["goal1886_prepared_reuse"]["query_summary"]["median_s"]
        self.assertLess(prepared_partner, prepared_baseline)
        self.assertLess(
            self.artifact_4096["partners"]["cupy"]["goal1886_prepared_reuse"][
                "query_median_ratio_vs_v1_8_prepared_native"
            ],
            1.0,
        )

    def test_claim_boundary_remains_bounded(self):
        boundary = self.artifact["claim_boundary"]
        self.assertTrue(boundary["same_contract_timing_row"])
        self.assertTrue(boundary["partner_output_columns_true_zero_copy_authorized"])
        self.assertFalse(boundary["v2_0_release_authorized"])
        self.assertFalse(boundary["whole_app_speedup_claim_authorized"])
        self.assertFalse(boundary["broad_rt_core_speedup_claim_authorized"])
        self.assertFalse(boundary["package_install_claim_authorized"])

    def test_report_names_warmup_and_blocks_overclaims(self):
        required = [
            "float64 partner tensors",
            "requires float32 ray columns",
            "first sample includes setup/JIT/cache effects",
            "adds an explicit `--output-capacity` override",
            "partner segment/polygon column adapter overflowed",
            "4096-Row L4 Validation With Explicit Capacity",
            "about 3.7x faster",
            "v2.0 release readiness",
            "whole-app speedup across all RTDL apps",
            "broad RT-core speedup",
            "same-contract v1.8 prepared OptiX row path",
        ]
        for phrase in required:
            self.assertIn(phrase, self.report)


if __name__ == "__main__":
    unittest.main()
