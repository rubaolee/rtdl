from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D

from examples.v2_0.research_benchmarks.raydb_style import rtdl_raydb_style_benchmark_app as raydb


ROOT = Path(__file__).resolve().parents[1]


def _rays() -> tuple[Ray3D, ...]:
    return (
        Ray3D(10, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 2.0),
        Ray3D(11, 0.20, 0.20, -1.0, 0.0, 0.0, 1.0, 2.0),
        Ray3D(12, 2.25, 0.25, -1.0, 0.0, 0.0, 1.0, 2.0),
    )


def _triangles() -> tuple[Triangle3D, ...]:
    return (
        Triangle3D(100, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        Triangle3D(101, 2.0, 0.0, 0.0, 3.0, 0.0, 0.0, 2.0, 1.0, 0.0),
    )


class Goal2685DeviceResidentHitStreamHandoffTest(unittest.TestCase):
    def test_contract_is_generic_and_claim_bounded(self) -> None:
        contract = rt.describe_generic_device_resident_hit_stream_handoff_3d()

        self.assertEqual(contract["contract_version"], rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION)
        self.assertEqual(contract["api_maturity"], "experimental_host_bridge_contract")
        self.assertEqual(contract["hit_stream_columns"], rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS)
        self.assertEqual(contract["typed_primitive_payload_columns"], rt.GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS)
        self.assertEqual(contract["overflow_policy"], "fail_closed_bounded_columns")
        self.assertFalse(contract["native_engine_app_specific_vocab_allowed"])
        self.assertFalse(contract["triton_replaces_rt_traversal"])
        self.assertTrue(contract["goal2685_host_bridge_only"])
        self.assertFalse(contract["native_device_column_output_proven_on_hardware"])
        self.assertFalse(contract["removes_host_materialization_bottleneck"])
        self.assertFalse(contract["true_zero_copy_claim_authorized"])
        self.assertFalse(contract["public_speedup_claim_authorized"])

        serialized = repr(contract).lower()
        for forbidden in ("raydb", "sql", "database", "table", "dbscan", "hausdorff"):
            self.assertNotIn(forbidden, serialized)

    def test_reference_hit_stream_columns_feed_partner_continuation(self) -> None:
        hit_stream = rt.run_generic_ray_triangle_hit_stream_3d(
            _rays(),
            _triangles(),
            backend="cpu",
            deduplicate_primitives=True,
        )
        hit_columns = rt.prepare_generic_hit_stream_columns_from_rows(hit_stream)
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            (7, 9),
            (3.0, 5.0),
            group_count=10,
        )
        continuation_inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            hit_columns,
            payload_columns,
        )

        self.assertEqual(continuation_inputs["group_ids"], (7, 9))
        self.assertEqual(continuation_inputs["values"], (3.0, 5.0))
        self.assertEqual(continuation_inputs["group_count"], 10)
        self.assertFalse(metadata["python_rebuilt_primitive_row_table"])
        self.assertTrue(metadata["materializes_host_rows_for_bridge"])
        self.assertTrue(metadata["host_hit_rows_materialized_before_handoff"])
        self.assertFalse(metadata["native_device_hit_stream_columns_ready"])
        self.assertFalse(metadata["removes_host_materialization_bottleneck"])

        reduced = rt.execute_v2_5_partner_continuation_reference(
            "segmented_sum_f64",
            continuation_inputs,
        )
        self.assertEqual(reduced["outputs"]["sums"][7], 3.0)
        self.assertEqual(reduced["outputs"]["sums"][9], 5.0)

    def test_native_hit_stream_wrappers_publish_top_level_row_schema_when_available(self) -> None:
        checked_backends: list[str] = []
        skip_reasons: dict[str, str] = {}
        for backend in ("embree", "optix"):
            try:
                hit_stream = rt.run_generic_ray_triangle_hit_stream_3d(
                    _rays(),
                    _triangles(),
                    backend=backend,
                    deduplicate_primitives=True,
                )
            except Exception as exc:
                skip_reasons[backend] = str(exc)
                continue
            with self.subTest(backend=backend):
                self.assertEqual(
                    tuple(hit_stream["row_schema"]),
                    rt.GENERIC_RAY_TRIANGLE_HIT_STREAM_3D_ROW_SCHEMA,
                )
                hit_columns = rt.prepare_generic_hit_stream_columns_from_rows(hit_stream)
                self.assertEqual(hit_columns.row_count, int(hit_stream["row_count"]))
                self.assertEqual(tuple(hit_columns.primitive_ids), (0, 1))
                checked_backends.append(backend)
        if not checked_backends:
            self.skipTest(f"No native hit-stream runtime available: {skip_reasons}")

    def test_overflow_is_fail_closed_before_column_handoff(self) -> None:
        overflow = rt.run_generic_ray_triangle_hit_stream_3d(
            _rays(),
            _triangles(),
            backend="cpu",
            max_rows=1,
            deduplicate_primitives=True,
        )

        with self.assertRaisesRegex(ValueError, "overflowed hit stream"):
            rt.prepare_generic_hit_stream_columns_from_rows(overflow)

    def test_native_device_columns_constructor_is_experimental_and_claim_bounded(self) -> None:
        owner = object()
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=(0, 1, 1),
            primitive_ids=(0, 1, 1),
            row_count=3,
            capacity=4,
            backend="optix",
            phase_timing_seconds={"rt_traversal": 0.001},
            native_symbol="rtdl_optix_run_ray_triangle_hit_stream_3d",
            owner=owner,
        )
        metadata = hit_columns.to_metadata()

        self.assertEqual(hit_columns.source_mode, "native_device_columns")
        self.assertFalse(hit_columns.materializes_host_rows_for_bridge)
        self.assertFalse(hit_columns.device_resident)
        self.assertFalse(metadata["removes_host_materialization_bottleneck"])
        self.assertFalse(metadata["native_device_column_output_proven_on_hardware"])
        self.assertEqual(metadata["ownership_lifetime_model"], "native_owner_state_machine_required_before_promotion")
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_native_device_columns_overflow_must_be_fail_closed(self) -> None:
        with self.assertRaisesRegex(ValueError, "overflowed hit-stream handoffs"):
            rt.prepare_generic_device_resident_hit_stream_columns(
                ray_ids=(0,),
                primitive_ids=(0,),
                row_count=1,
                capacity=1,
                overflow=True,
                backend="optix",
            )

    def test_payload_columns_reject_bad_shape_and_group_ids(self) -> None:
        with self.assertRaisesRegex(ValueError, "length must match"):
            rt.prepare_generic_typed_primitive_payload_columns(
                (0, 1),
                (1.0,),
                primitive_count=2,
                group_count=2,
            )
        with self.assertRaisesRegex(ValueError, r"group ids must be in \[0, group_count\)"):
            rt.prepare_generic_typed_primitive_payload_columns(
                (0, 2),
                (1.0, 1.0),
                group_count=2,
            )

    def test_payload_columns_can_skip_host_scan_only_with_explicit_bounds_contract(self) -> None:
        with self.assertRaisesRegex(ValueError, "group_count must be provided"):
            rt.prepare_generic_typed_primitive_payload_columns(
                (0, 1),
                (1.0, 1.0),
                group_id_bounds_validation="caller_asserted",
            )

        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            (0, 1),
            (1.0, 1.0),
            group_count=2,
            group_id_bounds_validation="caller_asserted",
        )
        metadata = payload_columns.to_metadata()
        self.assertEqual(metadata["group_id_bounds_validation"], "caller_asserted")
        self.assertTrue(metadata["group_id_bounds_validated"])
        self.assertFalse(metadata["host_scan_for_group_id_validation"])

    def test_default_payload_values_are_explicit_in_metadata(self) -> None:
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            (0, 1),
            group_count=2,
        )
        self.assertEqual(tuple(payload_columns.primitive_values), (1.0, 1.0))
        self.assertTrue(payload_columns.to_metadata()["default_primitive_values_used"])

    def test_gather_rejects_primitive_ids_outside_payload_range(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=(0, 1),
            primitive_ids=(0, 2),
            row_count=2,
            capacity=2,
            backend="optix",
        )
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            (0, 1),
            (1.0, 1.0),
            group_count=2,
        )

        with self.assertRaisesRegex(ValueError, r"primitive ids must be in \[0, primitive_count\)"):
            rt.gather_typed_payload_columns_for_hit_stream(hit_columns, payload_columns)

    def test_gathered_columns_feed_all_reference_reduction_modes(self) -> None:
        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=(0, 1, 2),
            primitive_ids=(0, 1, 1),
            row_count=3,
            capacity=3,
            backend="optix",
        )
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            (1, 1),
            (2.0, 3.0),
            group_count=2,
        )
        continuation_inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            hit_columns,
            payload_columns,
        )

        self.assertTrue(metadata["native_device_hit_stream_columns_ready"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        counted = rt.execute_v2_5_partner_continuation_reference(
            "segmented_count_i64",
            {"group_ids": continuation_inputs["group_ids"], "group_count": continuation_inputs["group_count"]},
        )
        summed = rt.execute_v2_5_partner_continuation_reference("segmented_sum_f64", continuation_inputs)
        minimum = rt.execute_v2_5_partner_continuation_reference("segmented_min_f64", continuation_inputs)
        maximum = rt.execute_v2_5_partner_continuation_reference("segmented_max_f64", continuation_inputs)

        self.assertEqual(counted["outputs"]["counts"], [0, 3])
        self.assertEqual(summed["outputs"]["sums"], [0.0, 8.0])
        self.assertEqual(minimum["outputs"]["mins"], [2.0])
        self.assertEqual(maximum["outputs"]["maxes"], [3.0])

    def test_cuda_torch_gather_branch_when_capable_hardware_is_available(self) -> None:
        try:
            import torch
        except Exception as exc:
            self.skipTest(f"torch unavailable: {exc}")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch unavailable")
        major, _minor = torch.cuda.get_device_capability()
        if major < 7:
            self.skipTest("Triton-capable CUDA gather evidence requires sm_70+ hardware")

        hit_columns = rt.prepare_generic_device_resident_hit_stream_columns(
            ray_ids=torch.tensor([0, 1], dtype=torch.int64, device="cuda"),
            primitive_ids=torch.tensor([0, 1], dtype=torch.int64, device="cuda"),
            row_count=2,
            capacity=2,
            backend="optix",
            owner="test_cuda_tensor_owner",
        )
        payload_columns = rt.prepare_generic_typed_primitive_payload_columns(
            torch.tensor([3, 4], dtype=torch.int64, device="cuda"),
            torch.tensor([10.0, 20.0], dtype=torch.float64, device="cuda"),
            group_count=5,
            group_id_bounds_validation="caller_asserted",
        )
        continuation_inputs, metadata = rt.gather_typed_payload_columns_for_hit_stream(
            hit_columns,
            payload_columns,
        )

        self.assertEqual(metadata["gather_mode"], "torch_index_select")
        self.assertEqual(continuation_inputs["group_ids"].detach().cpu().tolist(), [3, 4])
        self.assertEqual(continuation_inputs["values"].detach().cpu().tolist(), [10.0, 20.0])

    def test_raydb_device_handoff_reference_path_matches_cpu(self) -> None:
        fixture = raydb.make_fixture(copies=1)
        plan = raydb.make_plan("sum")
        result = raydb._run_paper_rt_device_hit_stream_triton_result_mode(
            fixture=fixture,
            plan=plan,
            mode="sum",
            copies=1,
            backend="cpu",
            backend_label="paper_rt_cpu_device_hit_stream_reference",
            allow_reference_fallback=True,
        )

        self.assertTrue(result["matches_cpu_reference"])
        metadata = result["metadata"]
        self.assertEqual(metadata["hit_stream_handoff_contract"], rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_HANDOFF_VERSION)
        self.assertEqual(metadata["hit_stream_column_schema"], list(rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS))
        self.assertEqual(
            metadata["typed_primitive_payload_column_schema"],
            list(rt.GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS),
        )
        self.assertFalse(metadata["python_rebuilt_primitive_row_table"])
        self.assertTrue(metadata["materializes_host_rows_for_legacy_bridge"])
        self.assertFalse(metadata["native_device_hit_stream_columns_ready"])
        self.assertFalse(metadata["hit_stream_handoff"]["removes_host_materialization_bottleneck"])
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_experimental_symbols_are_importable_but_not_stable_star_exports(self) -> None:
        for name in (
            "describe_generic_device_resident_hit_stream_handoff_3d",
            "prepare_generic_hit_stream_columns_from_rows",
            "prepare_generic_device_resident_hit_stream_columns",
            "prepare_generic_typed_primitive_payload_columns",
            "gather_typed_payload_columns_for_hit_stream",
        ):
            self.assertTrue(hasattr(rt, name))
            self.assertNotIn(name, rt.__all__)

        runner = ROOT / "scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py"
        source = runner.read_text()
        self.assertIn("PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND", source)
        self.assertIn(raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND, raydb.BACKENDS)
        self.assertIn("no_public_speedup_claim", source)


if __name__ == "__main__":
    unittest.main()
