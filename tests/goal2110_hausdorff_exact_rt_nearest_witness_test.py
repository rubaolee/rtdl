from __future__ import annotations

import ast
import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]


class Goal2110HausdorffExactRtNearestWitnessTest(unittest.TestCase):
    def test_python_example_exposes_exact_rt_method(self) -> None:
        source = (ROOT / "examples" / "rtdl_hausdorff_v2_function.py").read_text()
        tree = ast.parse(source)
        names = {node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)}
        self.assertIn("hausdorff_distance_2d_rt_nearest_witness", names)
        self.assertIn("_directed_rt_nearest_witness", names)
        self.assertIn("rtdl_rt_nearest_witness", source)
        self.assertIn("nearest_witness_rows", source)
        self.assertIn("rt_threshold_upper_bound", source)

    def test_language_lab_records_method_contracts(self) -> None:
        source = (ROOT / "examples" / "rtdl_hausdorff_v2_language_lab.py").read_text()
        self.assertIn("METHOD_METADATA", source)
        self.assertIn('"rtdl_v2_user_cuda"', source)
        self.assertIn('"rtdl_rt_threshold_search"', source)
        self.assertIn('"rtdl_rt_nearest_witness"', source)
        self.assertIn('"openmp_cpu"', source)
        self.assertIn('"cuda_cpp"', source)
        self.assertIn('"cupy_rawkernel"', source)
        self.assertIn("uses_rt_cores", source)

    def test_optix_binding_and_native_abi_are_present(self) -> None:
        optix_runtime = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text()
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text()
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text()
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text()
        core = (ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp").read_text()

        symbol = "rtdl_optix_run_prepared_fixed_radius_nearest_witness_2d"
        self.assertIn(symbol, optix_runtime)
        self.assertIn(symbol, api)
        self.assertIn(symbol, prelude)
        self.assertIn("run_prepared_fixed_radius_nearest_witness_2d_optix", workloads)
        self.assertIn("__raygen__frn_nearest_probe", core)
        self.assertIn("__intersection__frn_nearest_isect", core)
        self.assertIn("__anyhit__frn_nearest_anyhit", core)

    def test_local_optix_artifacts_record_exact_matching_results(self) -> None:
        artifact = ROOT / "docs" / "reports" / "hausdorff_v2_rt_nearest_witness_local_optix_512.json"
        data = json.loads(artifact.read_text())
        primary = data["primary"]
        self.assertEqual(primary["method"], "rtdl_rt_nearest_witness")
        self.assertTrue(primary["rt_core_accelerated"])
        self.assertTrue(primary["exact_value"])
        for comparison in data["comparisons"].values():
            self.assertTrue(comparison["matches_primary"])


if __name__ == "__main__":
    unittest.main()
