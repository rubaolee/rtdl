import ctypes
import json
import pathlib
import unittest

import rtdsl as rt
from rtdsl import hiprt_runtime
from rtdsl.engine_feature_matrix import NATIVE
from rtdsl.generic_primitives import run_generic_ray_triangle_closest_hit
from rtdsl.reference import ray_triangle_closest_hit_cpu
from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_benchmark_parity import summarize_v2_10_amd_hiprt_benchmark_parity
from rtdsl.v2_10_amd_hiprt_benchmark_parity import v2_10_amd_hiprt_benchmark_parity


ROOT = pathlib.Path(__file__).resolve().parents[1]
HIPRT_API = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_api.cpp"
HIPRT_CORE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_core.cpp"
HIPRT_KERNELS = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_kernels.cpp"
HIPRT_PRELUDE = ROOT / "src" / "native" / "hiprt" / "rtdl_hiprt_prelude.h"
HIPRT_RUNTIME = ROOT / "src" / "rtdsl" / "hiprt_runtime.py"
GENERIC_PRIMITIVES = ROOT / "src" / "rtdsl" / "generic_primitives.py"
REPORT = ROOT / "docs" / "reports" / "goal3775_hiprt_ray_triangle_closest_hit_3d_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3775_hiprt_ray_triangle_closest_hit_3d_a5000.json"


def _native_closest_hit_available() -> bool:
    try:
        rt.hiprt_context_probe()
        lib = hiprt_runtime._hiprt_lib()
    except Exception:
        return False
    return getattr(lib, "rtdl_hiprt_run_ray_closest_hit_3d", None) is not None


def _case():
    rays = (
        rt.Ray3D(id=7, ox=0.25, oy=0.25, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=10.0),
        rt.Ray3D(id=8, ox=3.0, oy=3.0, oz=-1.0, dx=0.0, dy=0.0, dz=1.0, tmax=10.0),
    )
    triangles = (
        rt.Triangle3D(
            id=77,
            x0=0.0,
            y0=0.0,
            z0=2.0,
            x1=1.0,
            y1=0.0,
            z1=2.0,
            x2=0.0,
            y2=1.0,
            z2=2.0,
        ),
        rt.Triangle3D(
            id=42,
            x0=0.0,
            y0=0.0,
            z0=0.0,
            x1=1.0,
            y1=0.0,
            z1=0.0,
            x2=0.0,
            y2=1.0,
            z2=0.0,
        ),
    )
    return rays, triangles


@rt.kernel(backend="rtdl", precision="float_approx")
def _ray_triangle_closest_hit_3d_kernel():
    rays = rt.input("rays", rt.Rays3D, layout=rt.Ray3DLayout, role="probe")
    triangles = rt.input("triangles", rt.Triangles3D, layout=rt.Triangle3DLayout, role="build")
    candidates = rt.traverse(rays, triangles, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.ray_triangle_closest_hit(exact=False))
    return rt.emit(hits, fields=["ray_id", "triangle_id", "t"])


class Goal3775HiprtRayTriangleClosestHitPortableTest(unittest.TestCase):
    def test_native_symbol_and_kernel_are_generic(self) -> None:
        prelude = HIPRT_PRELUDE.read_text(encoding="utf-8")
        api = HIPRT_API.read_text(encoding="utf-8")
        core = HIPRT_CORE.read_text(encoding="utf-8")
        kernels = HIPRT_KERNELS.read_text(encoding="utf-8")
        self.assertIn("struct RtdlRayClosestHitRow", prelude)
        self.assertIn("rtdl_hiprt_run_ray_closest_hit_3d", api)
        self.assertIn("copy_rows_to_heap(const std::vector<RtdlRayClosestHitRow>&", core)
        self.assertIn("RtdlRayClosestHit3DKernel", kernels)
        self.assertIn("const uint32_t* triangle_ids", kernels)
        for source in (prelude, api, core, kernels):
            self.assertNotIn("contact", source.lower())
            self.assertNotIn("manifold", source.lower())

    def test_python_runtime_and_generic_front_door_are_wired(self) -> None:
        runtime = HIPRT_RUNTIME.read_text(encoding="utf-8")
        generic = GENERIC_PRIMITIVES.read_text(encoding="utf-8")
        self.assertEqual(
            hiprt_runtime._RtdlRayClosestHitRow._fields_,
            [
                ("ray_id", ctypes.c_uint32),
                ("triangle_id", ctypes.c_uint32),
                ("t", ctypes.c_double),
            ],
        )
        self.assertEqual(ctypes.sizeof(hiprt_runtime._RtdlRayClosestHitRow), 16)
        self.assertTrue(hasattr(rt, "ray_triangle_closest_hit_hiprt"))
        self.assertIn("ray_triangle_closest_hit_hiprt", runtime)
        self.assertIn('backend must be one of: cpu, embree, optix, hiprt', generic)

    def test_feature_matrix_and_parity_record_goal3775_boundary(self) -> None:
        self.assertEqual(rt.engine_feature_support("ray_triangle_closest_hit_3d", "hiprt").status, NATIVE)
        self.assertEqual(
            V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION,
            "rtdl.v2_10.amd_hiprt_benchmark_parity_after_goal3782.v1",
        )
        rows = {row["app"]: row for row in v2_10_amd_hiprt_benchmark_parity()}
        contact = rows["contact_manifold"]
        self.assertIn("ray_triangle_closest_hit_3d", contact["required_engine_features"])
        self.assertEqual(contact["hiprt_feature_statuses"]["ray_triangle_closest_hit_3d"], NATIVE)
        self.assertEqual(contact["missing_generic_contracts"], ())
        self.assertEqual(contact["parity_stage"], "ready_for_amd_functional_pod")
        self.assertIn("Goal3775", contact["rationale"])
        summary = summarize_v2_10_amd_hiprt_benchmark_parity()
        self.assertEqual(summary["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(summary["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["amd_perf_claim_authorized"])

    def test_report_records_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3775", report)
        self.assertIn("ray_triangle_closest_hit_3d", report)
        self.assertIn("not AMD hardware evidence", report)
        self.assertIn("does not authorize", report)

    def test_artifact_records_clean_pod_evidence_when_present(self) -> None:
        if not ARTIFACT.exists():
            self.skipTest("Goal3775 pod artifact not generated yet")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertFalse(artifact["scoped_source_dirty"])
        self.assertTrue(artifact["sample"]["rows_match_reference"])
        self.assertEqual(artifact["contact_manifold_missing_generic_contracts"], ["bounded_contact_witness_collection"])
        self.assertIn("not AMD hardware evidence", artifact["backend_route"])
        for key, value in artifact["claim_boundary"].items():
            self.assertFalse(value, key)


@unittest.skipUnless(_native_closest_hit_available(), "HIPRT closest-hit symbol unavailable")
class Goal3775HiprtRayTriangleClosestHitNativeTest(unittest.TestCase):
    def test_direct_helper_and_compiled_run_match_cpu_reference(self) -> None:
        rays, triangles = _case()
        expected = ray_triangle_closest_hit_cpu(rays, triangles)
        direct = rt.ray_triangle_closest_hit_hiprt(rays, triangles)
        compiled = rt.run_hiprt(_ray_triangle_closest_hit_3d_kernel, rays=rays, triangles=triangles)
        generic = run_generic_ray_triangle_closest_hit(rays, triangles, backend="hiprt")
        for rows in (direct, compiled, generic):
            self.assertEqual(len(rows), len(expected))
            self.assertEqual(rows[0]["ray_id"], expected[0]["ray_id"])
            self.assertEqual(rows[0]["triangle_id"], 42)
            self.assertAlmostEqual(rows[0]["t"], expected[0]["t"], places=5)

    def test_empty_scene_returns_empty_rows(self) -> None:
        rays, _triangles = _case()
        self.assertEqual(rt.ray_triangle_closest_hit_hiprt(rays, ()), ())


if __name__ == "__main__":
    unittest.main()
