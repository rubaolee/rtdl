from __future__ import annotations

from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rtdsl.v4_rt_barneshut_native_route import (  # noqa: E402
    V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_RT_CORE,
    V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
    inspect_v4_rt_barneshut_native_feasibility,
    validate_v4_rt_barneshut_native_feasibility,
)


API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PROBE = ROOT / "scripts" / "v4_rt_barneshut_native_fallback_route_probe.py"


class V4Goal4765RtBarnesHutNativeRtCoreCandidateTest(unittest.TestCase):
    def test_source_tree_contains_author_rt_core_candidate_path(self) -> None:
        api = API.read_text(encoding="utf-8")

        self.assertIn("kRtBarnesHutAuthorImplementationStatusRtCore = 3", api)
        self.assertIn("__raygen__rt_barneshut_author3d", api)
        self.assertIn("__intersection__rt_barneshut_author3d_isect", api)
        self.assertIn("__closesthit__rt_barneshut_author3d_ch", api)
        self.assertIn("rtdl_rt_barneshut_author_rt_core_forces", api)
        self.assertIn("RTDL_RT_BARNESHUT_AUTHOR_FORCE_FALLBACK", api)

    def test_feasibility_detects_rt_core_candidate_without_public_claim(self) -> None:
        feasibility = inspect_v4_rt_barneshut_native_feasibility(ROOT)
        validate_v4_rt_barneshut_native_feasibility(feasibility)

        self.assertEqual(
            feasibility.status,
            V4_RT_BARNESHUT_NATIVE_ROUTE_STATUS_RT_CORE_CANDIDATE_AVAILABLE,
        )
        self.assertTrue(feasibility.claim_boundary["rt_core_candidate_available"])
        self.assertFalse(feasibility.claim_boundary["rt_core_execution_authorized"])
        self.assertFalse(feasibility.claim_boundary["public_rt_barneshut_paper_reproduction_claim_authorized"])
        self.assertFalse(feasibility.claim_boundary["v2_v3_v4_author_speed_table_authorized"])

    def test_probe_can_force_fallback_but_defaults_to_goal4765(self) -> None:
        text = PROBE.read_text(encoding="utf-8")

        self.assertIn("--force-fallback", text)
        self.assertIn('"Goal4764" if args.force_fallback else "Goal4765"', text)
        self.assertIn("goal4765_rt_core_candidate_attempted", text)

    def test_rt_core_status_code_is_stable(self) -> None:
        self.assertEqual(V4_RT_BARNESHUT_NATIVE_IMPLEMENTATION_STATUS_RT_CORE, 3)


if __name__ == "__main__":
    unittest.main()
