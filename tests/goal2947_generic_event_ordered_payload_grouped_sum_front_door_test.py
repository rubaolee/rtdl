from __future__ import annotations

import json
import os
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.reference import Ray3D
from rtdsl.reference import Triangle3D


ROOT = Path(__file__).resolve().parents[1]
GENERIC_PRIMITIVES = ROOT / "src" / "rtdsl" / "generic_primitives.py"
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal2947_generic_event_ordered_payload_grouped_sum_front_door_smoke.py"
REPORT = ROOT / "docs" / "reports" / "goal2947_generic_event_ordered_payload_grouped_sum_front_door_2026-06-01.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2947_generic_event_ordered_payload_grouped_sum_front_door_pod"
    / "goal2947_payload_grouped_sum_smoke.json"
)


def _fixture() -> tuple[tuple[Ray3D, ...], tuple[Triangle3D, ...]]:
    triangles = (
        Triangle3D(0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0, 0.0),
        Triangle3D(1, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0),
    )
    rays = (
        Ray3D(0, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
        Ray3D(1, 2.0, 2.0, -1.0, 0.0, 0.0, 1.0, 4.0),
        Ray3D(2, 0.25, 0.25, -1.0, 0.0, 0.0, 1.0, 4.0),
    )
    return rays, triangles


class Goal2947GenericEventOrderedPayloadGroupedSumFrontDoorTest(unittest.TestCase):
    def test_operation_is_declared_and_supported_only_by_cupy_preview(self) -> None:
        operation = "hit_stream_primitive_payload_grouped_sum_f64"
        contract = rt.v2_5_partner_continuation_contract()
        operations = {row["name"]: row for row in contract["operations"]}

        self.assertIn(operation, operations)
        self.assertEqual("hit_stream_payload_reduction", operations[operation]["category"])
        self.assertIn("primitive payload columns", operations[operation]["behavior"])
        self.assertIn(operation, rt.V2_5_CUPY_PREVIEW_OPERATIONS)
        self.assertNotIn(operation, rt.V2_5_PARTNER_PREVIEW_KERNEL_OPERATIONS)
        self.assertEqual(rt.plan_v2_5_partner_support(operation, "cupy")["status"], rt.V2_5_SUPPORT_STATUS_PREVIEW)
        self.assertEqual(rt.plan_v2_5_partner_support(operation, "triton")["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)
        self.assertEqual(rt.plan_v2_5_partner_support(operation, "numba")["status"], rt.V2_5_SUPPORT_STATUS_UNSUPPORTED)

    def test_reference_semantics_map_primitive_payloads(self) -> None:
        result = rt.execute_v2_5_partner_continuation_reference(
            "hit_stream_primitive_payload_grouped_sum_f64",
            {
                "ray_ids": [0, 2, 0, 2],
                "primitive_ids": [0, 1, 0, 1],
                "row_count": 4,
                "hit_event_count": 4,
                "overflow": False,
                "primitive_group_ids": [0, 2],
                "primitive_values": [10.5, 1.25],
                "primitive_count": 2,
                "group_count": 3,
            },
        )

        self.assertEqual([2, 0, 2], result["outputs"]["group_hit_counts"])
        self.assertEqual([21.0, 0.0, 2.5], result["outputs"]["group_payload_sums"])

    def test_front_door_is_exported_and_app_agnostic(self) -> None:
        source = GENERIC_PRIMITIVES.read_text(encoding="utf-8")
        runtime = OPTIX_RUNTIME.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIn("prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", source)
        self.assertIn("run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", source)
        self.assertIn("hit_stream_primitive_payload_grouped_sum_f64", source)
        self.assertIn('"grouping_key": "primitive_group_ids[primitive_id]"', source)
        self.assertIn('"reduced_value": "primitive_values[primitive_id]"', source)
        self.assertIn('"native_engine_app_specific_vocab_allowed": False', source)
        self.assertIn("rtdl_hit_stream_event_ordered_primitive_payload_grouped_sum_f64", runtime)
        self.assertIn("prepare_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", init_source)
        self.assertIn("run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", init_source)

    def test_unsupported_partner_fails_closed_before_optix_runtime(self) -> None:
        rays, triangles = _fixture()
        with self.assertRaisesRegex(ValueError, "partner='cupy'"):
            rt.run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
                rays,
                triangles,
                primitive_group_ids=(0, 2),
                primitive_values=(10.5, 1.25),
                group_count=3,
                partner="triton",
            )

    def test_report_and_script_document_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        script = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("Goal2947", report)
        self.assertIn("payload-mapped", report)
        self.assertIn("Triton and Numba fail closed", report)
        self.assertIn("not a v2.5 release authorization", report)
        self.assertIn("run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d", script)
        self.assertIn('"public_speedup_claim_authorized": False', script)

    def test_pod_artifact_records_payload_grouped_sum_when_available(self) -> None:
        if not POD_ARTIFACT.exists():
            self.skipTest("Goal2947 pod artifact has not been imported yet")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        summary = payload["summary"]

        self.assertEqual("pass", payload["status"])
        self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual("hit_stream_primitive_payload_grouped_sum_f64", metadata["operation"])
        self.assertEqual("cupy_conformance", metadata["selected_partner"])
        self.assertEqual("cuda_event_cross_stream", metadata["producer_consumer_stream_ordering"])
        self.assertTrue(metadata["event_or_same_stream_ordering_proven"])
        self.assertTrue(metadata["device_resident_payload_columns_for_partner"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertEqual(4, summary["row_count"])
        self.assertEqual([2, 0, 2], payload["group_hit_counts"])
        self.assertEqual([21.0, 0.0, 2.5], payload["group_payload_sums"])

    def test_runtime_smoke_uses_front_door_when_cuda_available(self) -> None:
        if not os.environ.get("RTDL_OPTIX_LIBRARY") and not (ROOT / "build/librtdl_optix.so").exists():
            self.skipTest("OptiX backend library is not configured")
        try:
            import cupy  # noqa: F401
            import torch
        except Exception as exc:  # pragma: no cover - local non-CUDA hosts skip here.
            self.skipTest(f"CUDA partner dependencies unavailable: {exc}")
        if not torch.cuda.is_available():
            self.skipTest("CUDA torch is not available")

        rays, triangles = _fixture()
        result = rt.run_generic_ray_triangle_event_ordered_payload_grouped_sum_3d(
            rays,
            triangles,
            primitive_group_ids=(0, 2),
            primitive_values=(10.5, 1.25),
            group_count=3,
            max_rows=8,
            partner="cupy",
            return_device_buffers=True,
        )
        hit_buffers = result["hit_buffers"]
        output_buffers = result["output_buffers"]
        try:
            self.assertEqual(result["summary"]["row_count"], 4)
            self.assertEqual(result["group_hit_counts"], (2, 0, 2))
            self.assertEqual(result["group_payload_sums"], (21.0, 0.0, 2.5))
            self.assertEqual(result["metadata"]["selected_partner"], "cupy_conformance")
            self.assertFalse(result["metadata"]["true_zero_copy_authorized"])
        finally:
            output_buffers.close()
            hit_buffers.close()


if __name__ == "__main__":
    unittest.main()
