import subprocess
import sys
import unittest
from pathlib import Path

import rtdsl as rt
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app


ROOT = Path(__file__).resolve().parents[1]


class Goal816PolygonOverlapRtCoreBoundaryTest(unittest.TestCase):
    def test_polygon_apps_are_not_optix_exposed(self) -> None:
        for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
            with self.subTest(app=app):
                self.assertEqual(rt.app_engine_support(app, "optix").status, "not_exposed_by_app_cli")
                self.assertEqual(rt.optix_app_performance_support(app).performance_class, "not_optix_exposed")
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "exclude_from_rtx_app_benchmark")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "needs_optix_app_surface")

    def test_require_rt_core_rejects_pair_overlap(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "no OptiX RT-core surface today"):
            pair_app.run_case(require_rt_core=True)

    def test_require_rt_core_rejects_jaccard(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "no OptiX RT-core surface today"):
            jaccard_app.run_case(require_rt_core=True)

    def test_payloads_record_no_rt_core_acceleration(self) -> None:
        pair_payload = pair_app.run_case("cpu_python_reference", output_mode="summary")
        jaccard_payload = jaccard_app.run_case("cpu_python_reference")
        self.assertFalse(pair_payload["rt_core_accelerated"])
        self.assertFalse(jaccard_payload["rt_core_accelerated"])
        self.assertEqual(pair_payload["optix_performance"]["class"], "not_optix_exposed")
        self.assertEqual(jaccard_payload["optix_performance"]["class"], "not_optix_exposed")

    def test_pair_cli_require_rt_core_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_polygon_pair_overlap_area_rows.py",
                "--require-rt-core",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no OptiX RT-core surface today", result.stderr)

    def test_jaccard_cli_require_rt_core_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_polygon_set_jaccard.py",
                "--require-rt-core",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no OptiX RT-core surface today", result.stderr)


if __name__ == "__main__":
    unittest.main()
