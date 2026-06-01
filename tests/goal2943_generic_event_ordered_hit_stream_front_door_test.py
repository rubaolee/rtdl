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
INIT = ROOT / "src" / "rtdsl" / "__init__.py"
SCRIPT = ROOT / "scripts" / "goal2943_generic_event_ordered_hit_stream_front_door_smoke.py"
REPORT = ROOT / "docs" / "reports" / "goal2943_generic_event_ordered_hit_stream_front_door_2026-06-01.md"
POD_ARTIFACT = (
    ROOT
    / "docs"
    / "reports"
    / "goal2943_generic_event_ordered_hit_stream_front_door_pod"
    / "goal2943_front_door_smoke.json"
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


class Goal2943GenericEventOrderedHitStreamFrontDoorTest(unittest.TestCase):
    def test_front_door_is_exported_and_app_agnostic(self) -> None:
        source = GENERIC_PRIMITIVES.read_text(encoding="utf-8")
        init_source = INIT.read_text(encoding="utf-8")

        self.assertIn("run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d", source)
        self.assertIn("hit_stream_grouped_ray_id_primitive_i64", source)
        self.assertIn("plan_v2_5_partner_support", source)
        self.assertIn('"grouping_key": "ray_id"', source)
        self.assertIn('"reduced_value": "primitive_id"', source)
        self.assertIn('"native_engine_app_specific_vocab_allowed": False', source)
        self.assertIn('"rt_traversal_replacement_allowed": False', source)
        self.assertIn('"public_speedup_claim_authorized": False', source)
        self.assertIn("run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d", init_source)

    def test_unsupported_partner_fails_closed_before_optix_runtime(self) -> None:
        rays, triangles = _fixture()
        with self.assertRaisesRegex(ValueError, "partner='cupy'"):
            rt.run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(
                rays,
                triangles,
                partner="triton",
                group_count=3,
                max_rows=8,
            )

    def test_report_documents_user_facing_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2943", text)
        self.assertIn("user-facing front door", text)
        self.assertIn("event-ordered", text)
        self.assertIn("partner='cupy'", text)
        self.assertIn("Triton and Numba fail closed", text)
        self.assertIn("not a true-zero-copy claim", text)
        self.assertIn("not a public speedup claim", text)

    def test_script_uses_public_front_door_and_returns_device_buffers(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d", source)
        self.assertIn("return_device_buffers=True", source)
        self.assertIn("group_buffers.group_hit_counts", source)
        self.assertIn('"public_speedup_claim_authorized": False', source)

    def test_pod_artifact_records_front_door_execution_when_available(self) -> None:
        if not POD_ARTIFACT.exists():
            self.skipTest("Goal2943 pod artifact has not been imported yet")
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        metadata = payload["metadata"]
        summary = payload["summary"]

        self.assertEqual("pass", payload["status"])
        self.assertRegex(payload["source_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual([], payload["source_dirty"])
        self.assertEqual("run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d", metadata["front_door"])
        self.assertEqual("cupy_conformance", metadata["selected_partner"])
        self.assertEqual("hit_stream_grouped_ray_id_primitive_i64", metadata["operation"])
        self.assertEqual("cuda_event_cross_stream", metadata["producer_consumer_stream_ordering"])
        self.assertTrue(metadata["event_or_same_stream_ordering_proven"])
        self.assertTrue(metadata["device_resident_grouped_reduction_for_partner"])
        self.assertFalse(metadata["true_zero_copy_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertEqual(4, summary["row_count"])
        self.assertEqual([2, 0, 2], payload["group_hit_counts"])
        self.assertEqual([1, 0, 1], payload["group_primitive_id_sum"])

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
        result = rt.run_generic_ray_triangle_event_ordered_grouped_ray_id_reduction_3d(
            rays,
            triangles,
            partner="cupy",
            group_count=3,
            max_rows=8,
            return_device_buffers=True,
        )
        hit_buffers = result["hit_buffers"]
        group_buffers = result["group_buffers"]
        try:
            self.assertEqual(result["summary"]["row_count"], 4)
            self.assertEqual(group_buffers.group_hit_counts.cpu().tolist(), [2, 0, 2])
            self.assertEqual(result["metadata"]["selected_partner"], "cupy_conformance")
            self.assertFalse(result["metadata"]["true_zero_copy_authorized"])
        finally:
            group_buffers.close()
            hit_buffers.close()


if __name__ == "__main__":
    unittest.main()
