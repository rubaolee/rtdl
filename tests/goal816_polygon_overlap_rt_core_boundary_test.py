import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock

import rtdsl as rt
from examples import rtdl_polygon_pair_overlap_area_rows as pair_app
from examples import rtdl_polygon_set_jaccard as jaccard_app


ROOT = Path(__file__).resolve().parents[1]


class Goal816PolygonOverlapRtCoreBoundaryTest(unittest.TestCase):
    @staticmethod
    def _fake_optix_rows(kernel, **_inputs):
        if kernel.__name__ == "polygon_edge_intersections_embree_kernel":
            return (
                {"left_id": 1, "right_id": 10, "x": 1.0, "y": 1.0},
                {"left_id": 2, "right_id": 11, "x": 5.0, "y": 1.0},
            )
        if kernel.__name__ == "polygon_point_in_polygon_positive_embree_kernel":
            return ()
        raise AssertionError(f"unexpected kernel {kernel.__name__}")

    def test_polygon_apps_are_optix_native_assisted_but_not_claim_ready(self) -> None:
        for app in ("polygon_pair_overlap_area_rows", "polygon_set_jaccard"):
            with self.subTest(app=app):
                self.assertEqual(rt.app_engine_support(app, "optix").status, "direct_cli_native_assisted")
                self.assertEqual(rt.optix_app_performance_support(app).performance_class, "python_interface_dominated")
                self.assertEqual(rt.optix_app_benchmark_readiness(app).status, "needs_real_rtx_artifact")
                self.assertEqual(rt.rt_core_app_maturity(app).current_status, "rt_core_partial_ready")

    def test_require_rt_core_is_optix_only(self) -> None:
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            pair_app.run_case("embree", require_rt_core=True)
        with self.assertRaisesRegex(ValueError, "only meaningful with --backend optix"):
            jaccard_app.run_case("embree", require_rt_core=True)

    def test_require_rt_core_allows_optix_native_assisted_surface(self) -> None:
        with mock.patch.object(rt, "run_optix", side_effect=self._fake_optix_rows):
            pair_payload = pair_app.run_case("optix", require_rt_core=True)
            jaccard_payload = jaccard_app.run_case("optix", require_rt_core=True)
        self.assertFalse(pair_payload["rt_core_accelerated"])
        self.assertFalse(jaccard_payload["rt_core_accelerated"])
        self.assertTrue(pair_payload["rt_core_candidate_discovery_active"])
        self.assertTrue(jaccard_payload["rt_core_candidate_discovery_active"])

    def test_payloads_record_no_rt_core_acceleration(self) -> None:
        pair_payload = pair_app.run_case("cpu_python_reference", output_mode="summary")
        jaccard_payload = jaccard_app.run_case("cpu_python_reference")
        self.assertFalse(pair_payload["rt_core_accelerated"])
        self.assertFalse(jaccard_payload["rt_core_accelerated"])
        self.assertFalse(pair_payload["rt_core_candidate_discovery_active"])
        self.assertFalse(jaccard_payload["rt_core_candidate_discovery_active"])
        self.assertEqual(pair_payload["optix_performance"]["class"], "python_interface_dominated")
        self.assertEqual(jaccard_payload["optix_performance"]["class"], "python_interface_dominated")

    def test_pair_cli_require_rt_core_with_cpu_backend_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_polygon_pair_overlap_area_rows.py",
                "--backend",
                "cpu_python_reference",
                "--require-rt-core",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only meaningful with --backend optix", result.stderr)

    def test_jaccard_cli_require_rt_core_with_cpu_backend_exits_nonzero(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "examples/rtdl_polygon_set_jaccard.py",
                "--backend",
                "cpu_python_reference",
                "--require-rt-core",
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only meaningful with --backend optix", result.stderr)


if __name__ == "__main__":
    unittest.main()
