import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_codex_authored import CODEX_AUTHORED_KERNELS
from examples.rtdl_gemini_authored import GEMINI_AUTHORED_KERNELS
from examples.rtdl_goal10_reference import point_nearest_segment_reference
from examples.rtdl_goal10_reference import segment_polygon_anyhit_rows_reference
from examples.rtdl_goal10_reference import segment_polygon_hitcount_reference
from examples.rtdl_language_reference import county_soil_overlay_reference
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from tests._embree_support import embree_available


class EmbreeBaselineIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not embree_available():
            raise unittest.SkipTest("Embree is not installed in the current environment")

    def test_representative_cases_match_across_backends(self) -> None:
        kernels = {
            "lsi": county_zip_join_reference,
            "pip": point_in_counties_reference,
            "overlay": county_soil_overlay_reference,
            "ray_tri_hitcount": ray_triangle_hitcount_reference,
            "segment_polygon_hitcount": segment_polygon_hitcount_reference,
            "segment_polygon_anyhit_rows": segment_polygon_anyhit_rows_reference,
            "point_nearest_segment": point_nearest_segment_reference,
        }
        for workload in rt.BASELINE_WORKLOAD_ORDER:
            for dataset in rt.representative_dataset_names(workload):
                kernel = kernels[workload]
                result = rt.run_baseline_case(kernel, dataset, backend="both")
                self.assertTrue(result["parity"], msg=f"{workload} dataset {dataset} parity failed")

    def test_authored_examples_execute_on_embree(self) -> None:
        workload_to_dataset = {
            "lsi": "authored_lsi_minimal",
            "pip": "authored_pip_minimal",
            "overlay": "authored_overlay_minimal",
        }
        for kernel in CODEX_AUTHORED_KERNELS + GEMINI_AUTHORED_KERNELS:
            workload = rt.infer_workload(kernel)
            result = rt.run_baseline_case(kernel, workload_to_dataset[workload], backend="both")
            self.assertTrue(result["parity"], msg=f"{kernel.__name__} parity failed")

    def test_goal10_examples_execute_through_baseline_runner(self) -> None:
        result_a = rt.run_baseline_case(
            segment_polygon_hitcount_reference,
            "authored_segment_polygon_minimal",
            backend="both",
        )
        result_b = rt.run_baseline_case(
            segment_polygon_anyhit_rows_reference,
            "authored_segment_polygon_minimal",
            backend="both",
        )
        result_c = rt.run_baseline_case(
            point_nearest_segment_reference,
            "authored_point_nearest_segment_minimal",
            backend="both",
        )
        self.assertTrue(result_a["parity"])
        self.assertTrue(result_b["parity"])
        self.assertTrue(result_c["parity"])

    def test_benchmark_json_and_summary(self) -> None:
        payload = rt.run_baseline_benchmark(
            workloads=("lsi",),
            backends=("cpu", "embree"),
            iterations=1,
            warmup=1,
        )
        output_path = Path("build/test_embree_baseline_benchmark.json")
        rt.write_baseline_benchmark_json(payload, output_path)
        self.assertTrue(output_path.exists())
        parsed = json.loads(output_path.read_text(encoding="utf-8"))
        self.assertEqual(parsed["suite"], "rtdl_embree_baseline")
        self.assertEqual(len(parsed["records"]), 4)
        summary = rt.summarize_baseline_benchmark(parsed)
        self.assertIn("RTDL Embree Baseline Summary", summary)
        self.assertIn("lsi :: authored_lsi_minimal", summary)
