from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "scripts" / "v4_section8_fixed_radius_count_threshold_validation.py"
HOT_PATH_HARNESS = ROOT / "scripts" / "v4_section8_prepared_hot_path_validation.py"


def _load_harness():
    spec = importlib.util.spec_from_file_location("v4_section8_harness_for_test", HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_hot_path_harness():
    spec = importlib.util.spec_from_file_location("v4_section8_hot_path_harness_for_test", HOT_PATH_HARNESS)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V4Section8ValidationHarnessTest(unittest.TestCase):
    def test_correctness_requires_oracle_and_same_counts(self) -> None:
        harness = _load_harness()
        rows = [
            {
                "route": "optix_rows",
                "signature": {
                    "point_count": 16,
                    "outlier_count": 4,
                    "threshold_reached_count": None,
                    "matches_oracle": True,
                },
            },
            {
                "route": "optix_fused_prepared_scalar",
                "signature": {
                    "point_count": 16,
                    "outlier_count": 4,
                    "threshold_reached_count": 12,
                    "matches_oracle": True,
                },
            },
        ]
        self.assertTrue(harness._correctness_details(rows)["correctness_passed"])

        rows[1]["signature"]["outlier_count"] = 5
        self.assertFalse(harness._correctness_details(rows)["correctness_passed"])

    def test_gate_requires_two_sizes_and_fused_native_route(self) -> None:
        harness = _load_harness()

        def size(copy_count: int, scalar_speedup: float, summary_speedup: float) -> dict[str, object]:
            return {
                "copies": copy_count,
                "correctness_passed": True,
                "comparisons": {
                    "optix_fused_prepared_scalar": {
                        "speedup_over_optix_rows_median": scalar_speedup,
                    },
                    "optix_fused_prepared_summary": {
                        "speedup_over_optix_rows_median": summary_speedup,
                    },
                },
                "route_results": [
                    {
                        "route": "optix_rows",
                        "tier": "tier1_separated",
                        "native_continuation_active": False,
                    },
                    {
                        "route": "optix_fused_prepared_scalar",
                        "tier": "tier2_fused_native_primitive",
                        "native_continuation_active": True,
                        "native_continuation_backend": "optix_threshold_count",
                        "generic_primitive": "fixed_radius_count_threshold_2d",
                    },
                    {
                        "route": "optix_fused_prepared_summary",
                        "tier": "tier2_fused_native_primitive",
                        "native_continuation_active": True,
                        "native_continuation_backend": "optix_threshold_count",
                        "summary_primitive": "fixed_radius_count_threshold_2d",
                    },
                ],
            }

        passed = harness._evaluate_gate([size(8192, 2.1, 1.6), size(32768, 2.4, 1.8)])
        self.assertEqual("pass", passed["status"])
        self.assertTrue(passed["v4_tier2_thesis_locally_validated"])

        failed = harness._evaluate_gate([size(8192, 2.1, 1.6), size(32768, 1.9, 1.8)])
        self.assertEqual("fail", failed["status"])
        self.assertFalse(failed["v4_tier2_thesis_locally_validated"])

    def test_prepared_hot_path_gate_requires_two_summary_wins(self) -> None:
        harness = _load_hot_path_harness()

        def size(copy_count: int, speedup: float) -> dict[str, object]:
            return {
                "copies": copy_count,
                "correctness_passed": True,
                "routes": {
                    "summary_prepared_hot": {
                        "native_continuation_active": True,
                        "generic_primitive": "FIXED_RADIUS_COUNT_THRESHOLD_2D",
                    }
                },
                "comparisons": {
                    "summary_prepared_hot": {
                        "speedup_over_rows_emit_reduce_median": speedup,
                    }
                },
            }

        passed = harness._evaluate_gate([size(8192, 1.6), size(32768, 1.7)])
        self.assertEqual("pass", passed["status"])

        failed = harness._evaluate_gate([size(8192, 1.6), size(32768, 1.49)])
        self.assertEqual("fail", failed["status"])

    def test_outlier_density_summary_honors_prepared_optix_mode(self) -> None:
        from examples.current.apps.ml import rtdl_outlier_detection_app as app

        expected = app.expected_tiled_density_rows(copies=1)
        with mock.patch.object(app, "_run_optix_prepared_density_summary", return_value=expected) as prepared:
            with mock.patch.object(app, "_run_optix_density_summary", return_value=expected) as unprepared:
                payload = app.run_app(
                    backend="optix",
                    copies=1,
                    output_mode="density_summary",
                    optix_summary_mode="rt_count_threshold_prepared",
                )
        self.assertTrue(payload["matches_oracle"])
        self.assertEqual("FIXED_RADIUS_COUNT_THRESHOLD_2D", payload["generic_primitive"])
        self.assertEqual("REDUCE_INT(COUNT)", payload["summary_primitive"])
        prepared.assert_called_once()
        unprepared.assert_not_called()

    def test_outlier_full_mode_uses_tiled_oracle_not_quadratic_bruteforce(self) -> None:
        from examples.current.apps.ml import rtdl_outlier_detection_app as app

        neighbor_rows = (
            {"query_id": 1, "neighbor_id": 1, "distance": 0.0},
            {"query_id": 1, "neighbor_id": 2, "distance": 0.1},
            {"query_id": 1, "neighbor_id": 3, "distance": 0.1},
            {"query_id": 2, "neighbor_id": 1, "distance": 0.1},
            {"query_id": 2, "neighbor_id": 2, "distance": 0.0},
            {"query_id": 2, "neighbor_id": 3, "distance": 0.1},
            {"query_id": 3, "neighbor_id": 1, "distance": 0.1},
            {"query_id": 3, "neighbor_id": 2, "distance": 0.1},
            {"query_id": 3, "neighbor_id": 3, "distance": 0.0},
            {"query_id": 4, "neighbor_id": 4, "distance": 0.0},
            {"query_id": 4, "neighbor_id": 5, "distance": 0.1},
            {"query_id": 4, "neighbor_id": 6, "distance": 0.1},
            {"query_id": 5, "neighbor_id": 4, "distance": 0.1},
            {"query_id": 5, "neighbor_id": 5, "distance": 0.0},
            {"query_id": 5, "neighbor_id": 6, "distance": 0.1},
            {"query_id": 6, "neighbor_id": 4, "distance": 0.1},
            {"query_id": 6, "neighbor_id": 5, "distance": 0.1},
            {"query_id": 6, "neighbor_id": 6, "distance": 0.0},
            {"query_id": 7, "neighbor_id": 7, "distance": 0.0},
            {"query_id": 8, "neighbor_id": 8, "distance": 0.0},
        )
        with mock.patch.object(app, "_run_rows", return_value=neighbor_rows):
            with mock.patch.object(app, "brute_force_outlier_rows", side_effect=AssertionError("quadratic oracle")):
                payload = app.run_app(backend="optix", copies=1, output_mode="full")
        self.assertTrue(payload["matches_oracle"])


if __name__ == "__main__":
    unittest.main()
