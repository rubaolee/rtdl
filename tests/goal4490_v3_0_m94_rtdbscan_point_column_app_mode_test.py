from __future__ import annotations

import inspect
import sys
import types
import unittest
from unittest import mock

import numpy as np

import rtdsl as rt
from examples.current.research_benchmarks.rt_dbscan import rtdl_rt_dbscan_benchmark_app as app


class _FakeStream:
    def synchronize(self) -> None:
        return None


class _FakeCupy(types.SimpleNamespace):
    def __init__(self) -> None:
        super().__init__(
            cuda=types.SimpleNamespace(get_current_stream=lambda: _FakeStream()),
            asnumpy=lambda value: np.asarray(value),
        )


class _Context:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


class Goal4490M94RtDbscanPointColumnAppModeTest(unittest.TestCase):
    def test_coordinate_only_partner_helper_is_public_and_id_free(self) -> None:
        self.assertTrue(hasattr(rt, "point_rows_to_partner_coordinate_columns_3d"))
        self.assertIn("point_rows_to_partner_coordinate_columns_3d", rt.__all__)

        source = inspect.getsource(rt.point_rows_to_partner_coordinate_columns_3d)
        self.assertIn("_point_coordinate_columns_3d", source)
        adapter_source = inspect.getsource(sys.modules["rtdsl.partner_adapters"]._point_coordinate_columns_3d)
        self.assertIn('"x"', adapter_source)
        self.assertIn('"y"', adapter_source)
        self.assertIn('"z"', adapter_source)
        self.assertNotIn('"ids"', adapter_source)

    def test_app_exposes_explicit_point_column_mode_without_default_promotion(self) -> None:
        self.assertEqual(
            app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_POINT_COLUMNS_APP_MODE,
            "optix_rt_core_flags_cupy_point_columns_predicate_direct_status_column_signature_3d",
        )
        source = inspect.getsource(app.run_rt_dbscan_benchmark)

        self.assertIn("point_rows_to_partner_coordinate_columns_3d", source)
        self.assertIn(
            "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d",
            source,
        )
        self.assertIn('"point_coordinate_column_build_charged_in_total": use_point_column_direct_status', source)
        self.assertIn('"charged_predicate_direct_status_prepare_sec"', source)
        self.assertIn('"caller_owned_column_speedup_claim_authorized": False', source)
        self.assertIn('"column_prepare_speedup_claim_authorized": False', source)
        self.assertIn('"route_promotion_authorized": False', source)

    def test_mocked_point_column_mode_charges_app_constructed_columns(self) -> None:
        fake_columns = {"x": object(), "y": object(), "z": object()}
        fake_cupy = _FakeCupy()

        threshold_result = {
            "columns": {
                "threshold_flags": np.asarray([1, 0, 0], dtype=np.uint32),
                "neighbor_counts": np.asarray([1, 0, 0], dtype=np.uint32),
            },
            "metadata": {"path": "mock_threshold"},
        }
        signature_result = {
            "columns": {
                "label_counts": np.asarray([0, 1], dtype=np.uint64),
                "flag_true_count": np.asarray([1], dtype=np.uint64),
                "negative_label_count": np.asarray([2], dtype=np.uint64),
            },
            "metadata": {"status": "accept", "all_predicate_fast_path": False},
        }

        with mock.patch.dict(sys.modules, {"cupy": fake_cupy}):
            with mock.patch.object(
                app.rt,
                "point_rows_to_partner_coordinate_columns_3d",
                return_value=fake_columns,
            ) as build_columns:
                with mock.patch.object(
                    app.rt,
                    "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_point_columns_preview_3d",
                    return_value=_Context(),
                ) as prepare_columns:
                    with mock.patch.object(
                        app.rt,
                        "prepare_v2_8_fixed_radius_partition_convergence_predicate_direct_status_union_cupy_preview_3d",
                    ) as prepare_rows:
                        with mock.patch.object(
                            app.rt,
                            "allocate_fixed_radius_count_threshold_3d_partner_device_output_columns",
                            return_value={"threshold_flags": object(), "neighbor_counts": object()},
                        ):
                            with mock.patch.object(
                                app.rt,
                                "prepare_optix_fixed_radius_count_threshold_3d",
                                return_value=_Context(),
                            ):
                                with mock.patch.object(
                                    app.rt,
                                    "fixed_radius_count_threshold_3d_optix_prepared_self_partner_device_columns",
                                    return_value=threshold_result,
                                ):
                                    with mock.patch.object(
                                        app.rt,
                                        "run_v2_8_fixed_radius_partition_convergence_predicate_signature_cupy_prepared_direct_status_union_preview_3d",
                                        return_value=signature_result,
                                    ):
                                        payload = app.run_rt_dbscan_benchmark(
                                            mode=app.RT_DBSCAN_PREDICATE_DIRECT_STATUS_POINT_COLUMNS_APP_MODE,
                                            dataset="tiny",
                                            point_count=3,
                                            radius=0.2,
                                            min_neighbors=1,
                                            seed=20260519,
                                            partner="cupy",
                                            include_rows=False,
                                            validate=False,
                                            repeat=2,
                                            warmup=1,
                                        )

        metadata = payload["metadata"]
        build_columns.assert_called_once()
        prepare_columns.assert_called_once()
        self.assertIs(prepare_columns.call_args.args[0], fake_columns)
        prepare_rows.assert_not_called()
        self.assertEqual(
            "optix_rt_count_threshold_cupy_point_columns_predicate_direct_status_column_signature_3d",
            metadata["path"],
        )
        self.assertTrue(metadata["point_coordinate_column_build_charged_in_total"])
        self.assertFalse(metadata["point_coordinate_column_build_hidden"])
        self.assertFalse(metadata["caller_owned_column_speedup_claim_authorized"])
        self.assertFalse(metadata["column_prepare_speedup_claim_authorized"])
        self.assertGreaterEqual(
            metadata["charged_predicate_direct_status_prepare_sec"],
            metadata["prepared_predicate_direct_status_sec"],
        )
        self.assertEqual(
            metadata["prepared_query_repeat_protocol"]["prepare_sec"],
            metadata["charged_predicate_direct_status_prepare_sec"],
        )


if __name__ == "__main__":
    unittest.main()
