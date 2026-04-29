import unittest
from unittest import mock

from examples import rtdl_hausdorff_distance_app as app


class _FakePreparedThreshold:
    def __init__(self, target, max_radius: float):
        self.target = target
        self.max_radius = max_radius

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def run(self, query_points, *, radius: float, threshold: int):
        raise AssertionError("Hausdorff threshold mode must use scalar counts")

    def count_threshold_reached(self, query_points, *, radius: float, threshold: int):
        self.query_count = len(query_points)
        self.radius = radius
        self.threshold = threshold
        return len(query_points)


class Goal1132HausdorffPhaseContractTest(unittest.TestCase):
    def test_optix_threshold_mode_reports_clean_phase_split(self) -> None:
        with mock.patch.object(app.rt, "prepare_optix_fixed_radius_count_threshold_2d", side_effect=_FakePreparedThreshold):
            payload = app.run_app(
                "optix",
                copies=2,
                optix_summary_mode="directed_threshold_prepared",
                hausdorff_threshold=0.4,
                require_rt_core=True,
            )

        self.assertTrue(payload["rt_core_accelerated"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "optix_threshold_count")
        self.assertIsNone(payload["hausdorff_distance"])
        self.assertTrue(payload["within_threshold"])
        self.assertTrue(payload["matches_oracle"])
        self.assertIn("input_construction_sec", payload["run_phases"])
        self.assertIn("optix_prepare_sec", payload["run_phases"])
        self.assertIn("optix_query_sec", payload["run_phases"])
        self.assertIn("python_postprocess_sec", payload["run_phases"])
        self.assertIn("validation_sec", payload["run_phases"])
        self.assertEqual(payload["directed_a_to_b"]["summary_mode"], "scalar_threshold_count")
        self.assertIn("optix_query_sec", payload["directed_a_to_b"]["run_phases"])

    def test_embree_directed_summary_reports_native_summary_phase(self) -> None:
        with mock.patch.object(
            app.rt,
            "directed_hausdorff_2d_embree",
            side_effect=(
                {"distance": 0.3, "source_id": 3, "target_id": 103, "row_count": 4},
                {"distance": 0.2, "source_id": 102, "target_id": 2, "row_count": 4},
            ),
        ):
            payload = app.run_app("embree", copies=1, embree_result_mode="directed_summary")

        self.assertFalse(payload["rt_core_accelerated"])
        self.assertTrue(payload["native_continuation_active"])
        self.assertEqual(payload["native_continuation_backend"], "embree_directed_hausdorff")
        self.assertIn("native_directed_summary_sec", payload["run_phases"])
        self.assertIn("validation_sec", payload["run_phases"])


if __name__ == "__main__":
    unittest.main()
