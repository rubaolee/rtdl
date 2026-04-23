import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_ann_candidate_app as ann_app
from examples import rtdl_barnes_hut_force_app as barnes_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app


ROOT = Path(__file__).resolve().parents[1]
CUDA_THROUGH_OPTIX_APPS = (
    "hausdorff_distance",
    "ann_candidate_search",
    "barnes_hut_force_app",
)


class Goal817CudaThroughOptixClaimGateTest(unittest.TestCase):
    def test_metadata_remains_cuda_through_optix_not_rt_core_ready(self) -> None:
        for app in CUDA_THROUGH_OPTIX_APPS:
            with self.subTest(app=app):
                self.assertEqual(rt.optix_app_performance_support(app).performance_class, "cuda_through_optix")
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "exclude_from_rtx_app_benchmark")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "needs_rt_core_redesign")

    def test_require_rt_core_rejects_optix_cuda_through_paths(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "CUDA-through-OptiX KNN rows"):
            hausdorff_app.run_app("optix", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "CUDA-through-OptiX KNN rows"):
            ann_app.run_app("optix", output_mode="rerank_summary", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "CUDA-through-OptiX radius candidate generation"):
            barnes_app.run_app("optix", output_mode="candidate_summary", require_rt_core=True)

    def test_require_rt_core_is_optix_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            hausdorff_app.run_app("embree", require_rt_core=True)
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            ann_app.run_app("embree", require_rt_core=True)
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            barnes_app.run_app("embree", require_rt_core=True)

    def test_cpu_payloads_record_no_rt_core_acceleration(self) -> None:
        self.assertFalse(hausdorff_app.run_app("cpu_python_reference")["rt_core_accelerated"])
        self.assertFalse(ann_app.run_app("cpu_python_reference", output_mode="rerank_summary")["rt_core_accelerated"])
        self.assertFalse(barnes_app.run_app("cpu_python_reference", output_mode="candidate_summary")["rt_core_accelerated"])

    def test_cli_require_rt_core_exits_nonzero_for_optix(self) -> None:
        cases = (
            ("examples/rtdl_hausdorff_distance_app.py", "CUDA-through-OptiX KNN rows"),
            ("examples/rtdl_ann_candidate_app.py", "CUDA-through-OptiX KNN rows"),
            ("examples/rtdl_barnes_hut_force_app.py", "CUDA-through-OptiX radius candidate generation"),
        )
        for script, expected in cases:
            with self.subTest(script=script):
                result = subprocess.run(
                    [
                        sys.executable,
                        script,
                        "--backend",
                        "optix",
                        "--require-rt-core",
                    ],
                    cwd=ROOT,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)


if __name__ == "__main__":
    unittest.main()
