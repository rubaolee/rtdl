from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl import optix_runtime


ROOT = Path(__file__).resolve().parents[1]
OPTIX_RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
OPTIX_PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal2744NativeHitStreamReleaseEnforcementAuditTest(unittest.TestCase):
    def test_release_symbol_is_declared_exported_and_named_consistently(self) -> None:
        release_symbol = "rtdl_optix_release_ray_triangle_hit_stream_device_columns"
        self.assertEqual(
            optix_runtime.OPTIX_RELEASE_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL,
            release_symbol,
        )

        self.assertIn(release_symbol, OPTIX_PRELUDE.read_text(encoding="utf-8"))
        self.assertIn(
            f'extern "C" int {release_symbol}',
            OPTIX_API.read_text(encoding="utf-8"),
        )
        self.assertIn(
            "release_ray_triangle_hit_stream_device_columns_optix(owner_handle)",
            OPTIX_API.read_text(encoding="utf-8"),
        )

    def test_native_owner_release_path_deletes_the_owner_object(self) -> None:
        workloads = OPTIX_WORKLOADS.read_text(encoding="utf-8")

        self.assertIn("NativeRayTriangleHitStreamDeviceColumnsOwner", workloads)
        self.assertIn("columns_out->owner_handle = owner.release();", workloads)
        self.assertIn(
            "delete reinterpret_cast<NativeRayTriangleHitStreamDeviceColumnsOwner*>(owner_handle);",
            workloads,
        )

    def test_python_runtime_requires_release_symbol_before_native_device_output(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        method_start = source.index("def ray_triangle_hit_stream_device_columns(")
        method_end = source.index("def ray_triangle_prepared_primitive_grouped_i64_reduction", method_start)
        method = source[method_start:method_end]

        self.assertIn("release_symbol = _find_optional_backend_symbol", method)
        self.assertIn("OPTIX_RELEASE_RAY_TRIANGLE_HIT_STREAM_3D_DEVICE_COLUMNS_SYMBOL", method)
        self.assertIn("if release_symbol is None:", method)
        self.assertIn("Rebuild it with 'make build-optix' from current main.", method)
        self.assertLess(
            method.index("if release_symbol is None:"),
            method.index("status = run_symbol("),
        )

    def test_python_owner_close_is_idempotent_and_invokes_release_symbol(self) -> None:
        source = OPTIX_RUNTIME.read_text(encoding="utf-8")
        owner_start = source.index("class _OptixNativeHitStreamDeviceColumnsOwner:")
        owner_end = source.index("class PreparedOptixStaticTriangleScene3D:", owner_start)
        owner_class = source[owner_start:owner_end]

        self.assertIn("def close(self) -> None:", owner_class)
        self.assertIn("if self._closed:", owner_class)
        self.assertIn("self._closed = True", owner_class)
        self.assertIn("self._owner_handle = ctypes.c_void_p()", owner_class)
        self.assertIn("release_symbol(handle, error, len(error))", owner_class)
        self.assertIn("def __del__(self):", owner_class)

    def test_handoff_metadata_exposes_close_support_but_not_zero_copy_promotion(self) -> None:
        class _Owner:
            def close(self) -> None:
                pass

        handoff = rt.prepare_native_device_hit_stream_columns_from_abi(
            ray_ids_device_ptr=0x274400,
            primitive_ids_device_ptr=0x274800,
            row_count=1,
            capacity=1,
            overflow=False,
            hit_event_count=1,
            owner=_Owner(),
            native_device_column_output_proven_on_hardware=True,
        )
        metadata = handoff.to_metadata()

        self.assertTrue(metadata["owner_close_supported"])
        self.assertEqual(metadata["handoff_after_owner_close_allowed"], False)
        self.assertTrue(metadata["native_device_column_output_proven_on_hardware"])
        self.assertFalse(metadata["true_zero_copy_authorized"])


if __name__ == "__main__":
    unittest.main()
