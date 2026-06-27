from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_HOST_FALLBACK,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
    V4RtBarnesHutNativeRouteUnavailable,
    inspect_v4_rt_barneshut_native_feasibility,
    run_v4_rt_barneshut_native_author_route,
    validate_v4_rt_barneshut_native_feasibility,
)


API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "v4_rt_barneshut_native_fallback_route_probe.py"


class V4Goal4764RtBarnesHutNativeFallbackRouteTest(unittest.TestCase):
    def test_source_tree_contains_author_semantics_host_fallback(self) -> None:
        api = API.read_text(encoding="utf-8")

        self.assertIn("rtdl_rt_barneshut_author_host_fallback_forces", api)
        self.assertIn("kRtBarnesHutAuthorImplementationStatusHostFallback", api)
        self.assertIn("kRtBarnesHutAuthorBucketSize = 32", api)
        self.assertIn("kRtBarnesHutAuthorThreshold = 0.5", api)
        self.assertIn("RT-BarnesHut author 3D fallback only supports theta=0.5", api)

    def test_feasibility_status_records_fallback_or_candidate_without_public_claim(self) -> None:
        feasibility = inspect_v4_rt_barneshut_native_feasibility(ROOT)
        validate_v4_rt_barneshut_native_feasibility(feasibility)

        self.assertIn(
            feasibility.status,
            {
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_HOST_FALLBACK_AVAILABLE,
                V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
            },
        )
        self.assertTrue(feasibility.claim_boundary["native_v4_checksum_route_available"])
        self.assertFalse(feasibility.claim_boundary["rt_core_execution_authorized"])
        self.assertFalse(feasibility.claim_boundary["native_v4_operator_available"])
        self.assertFalse(feasibility.claim_boundary["public_rt_barneshut_paper_reproduction_claim_authorized"])

    def test_python_route_requires_explicit_device_columns(self) -> None:
        with self.assertRaises(V4RtBarnesHutNativeRouteUnavailable):
            run_v4_rt_barneshut_native_author_route()

    def test_probe_script_preserves_non_rt_core_boundary(self) -> None:
        text = PROBE.read_text(encoding="utf-8")

        self.assertIn("native RT-BarnesHut author-semantics ABI checksum route", text)
        self.assertIn("not a public speed claim", text)
        self.assertIn("passes_float_output_tolerance", text)

    def test_implementation_status_code_is_stable(self) -> None:
        self.assertEqual(V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_HOST_FALLBACK, 2)


if __name__ == "__main__":
    unittest.main()
