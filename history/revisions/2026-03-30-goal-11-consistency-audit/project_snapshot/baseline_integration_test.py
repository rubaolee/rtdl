import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

import rtdsl as rt
from examples.rtdl_codex_authored import CODEX_AUTHORED_KERNELS
from examples.rtdl_gemini_authored import GEMINI_AUTHORED_KERNELS
from examples.rtdl_ray_tri_hitcount import ray_triangle_hitcount_reference
from tests._embree_support import embree_available


class EmbreeBaselineIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        if not embree_available():
            raise unittest.SkipTest("Embree is not installed in the current environment")

    def test_representative_cases_match_across_backends(self) -> None:
        for workload in rt.BASELINE_WORKLOAD_ORDER:
            for dataset in rt.representative_dataset_names(workload):
                if workload == "lsi":
                    from examples.rtdl_language_reference import county_zip_join_reference as kernel
                elif workload == "pip":
                    from examples.rtdl_language_reference import point_in_counties_reference as kernel
                elif workload == "overlay":
                    from examples.rtdl_language_reference import county_soil_overlay_reference as kernel
                else:
                    kernel = ray_triangle_hitcount_reference
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
