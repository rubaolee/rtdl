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
        self.assertEqual(contract["hit_stream_columns"], rt.GENERIC_DEVICE_RESIDENT_HIT_STREAM_COLUMNS)
        self.assertEqual(contract["typed_primitive_payload_columns"], rt.GENERIC_TYPED_PRIMITIVE_PAYLOAD_COLUMNS)
        self.assertEqual(contract["overflow_policy"], "fail_closed_bounded_columns")
        self.assertFalse(contract["native_engine_app_specific_vocab_allowed"])
        self.assertFalse(contract["triton_replaces_rt_traversal"])
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
        self.assertFalse(metadata["native_device_hit_stream_columns_ready"])

        reduced = rt.execute_v2_5_partner_continuation_reference(
            "segmented_sum_f64",
            continuation_inputs,
        )
        self.assertEqual(reduced["outputs"]["sums"][7], 3.0)
        self.assertEqual(reduced["outputs"]["sums"][9], 5.0)

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
        self.assertFalse(metadata["true_zero_copy_authorized"])

    def test_public_exports_and_pod_runner_exist(self) -> None:
        for name in (
            "describe_generic_device_resident_hit_stream_handoff_3d",
            "prepare_generic_hit_stream_columns_from_rows",
            "prepare_generic_device_resident_hit_stream_columns",
            "prepare_generic_typed_primitive_payload_columns",
            "gather_typed_payload_columns_for_hit_stream",
        ):
            self.assertIn(name, rt.__all__)

        runner = ROOT / "scripts/goal2685_raydb_device_hit_stream_handoff_pod_runner.py"
        source = runner.read_text()
        self.assertIn("PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND", source)
        self.assertIn(raydb.PAPER_RT_OPTIX_DEVICE_HIT_STREAM_TRITON_BACKEND, raydb.BACKENDS)
        self.assertIn("no_public_speedup_claim", source)


if __name__ == "__main__":
    unittest.main()
