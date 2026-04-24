import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_ann_candidate_app as ann_app
from examples import rtdl_barnes_hut_force_app as barnes_app
from examples import rtdl_hausdorff_distance_app as hausdorff_app


ROOT = Path(__file__).resolve().parents[1]
PREPARED_DECISION_APPS = (
    "hausdorff_distance",
    "ann_candidate_search",
    "barnes_hut_force_app",
)


class Goal817CudaThroughOptixClaimGateTest(unittest.TestCase):
    def test_metadata_promotes_only_bounded_prepared_decision_paths(self) -> None:
        for app in PREPARED_DECISION_APPS:
            with self.subTest(app=app):
                self.assertEqual(
                    rt.optix_app_performance_support(app).performance_class,
                    "optix_traversal_prepared_summary",
                )
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "needs_real_rtx_artifact")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "rt_core_partial_ready")

    def test_require_rt_core_rejects_default_optix_row_paths(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "directed_threshold_prepared"):
            hausdorff_app.run_app("optix", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "candidate_threshold_prepared"):
            ann_app.run_app("optix", output_mode="rerank_summary", require_rt_core=True)
        with self.assertRaisesRegex(RuntimeError, "node_coverage_prepared"):
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
            ("examples/rtdl_hausdorff_distance_app.py", "directed_threshold_prepared"),
            ("examples/rtdl_ann_candidate_app.py", "candidate_threshold_prepared"),
            ("examples/rtdl_barnes_hut_force_app.py", "node_coverage_prepared"),
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
