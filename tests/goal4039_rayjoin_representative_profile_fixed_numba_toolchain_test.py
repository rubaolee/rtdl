from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal4039_rayjoin_representative_profile_fixed_numba_toolchain_2026-06-08.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal4039_rayjoin_representative_profile_fixed_numba_toolchain_pod.json"
LOG = ROOT / "docs" / "reports" / "goal4039_rayjoin_representative_profile_fixed_numba_toolchain_pod.log"


class Goal4039RayJoinRepresentativeProfileFixedNumbaToolchainTest(unittest.TestCase):
    def test_artifact_records_counts_routes_and_boundaries(self) -> None:
        payload = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.goal3866.rayjoin_representative_scale_profile.v1")
        self.assertEqual(payload["gpu"], "NVIDIA RTX 4000 Ada Generation, 550.127.05")
        self.assertTrue(payload["all_counts_match"])
        self.assertTrue(payload["numba_reference_available_for_custom_logic"])
        self.assertFalse(payload["cupy_required_for_reference_route"])
        self.assertFalse(payload["raw_cuda_kernel_required_for_reference_route"])

        cases = {row["workload"]: row for row in payload["cases"]}
        self.assertEqual(cases["pip"]["recommended_route"], "numba_cuda_jit_scalar_count")
        self.assertEqual(cases["lsi"]["recommended_route"], "rtdl_optix_prepared_scalar_count")
        self.assertEqual(cases["overlay_seed"]["recommended_route"], "rtdl_optix_prepared_scalar_count")
        self.assertLess(cases["pip"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertGreater(cases["lsi"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(cases["overlay_seed"]["rtdl_optix_speedup_vs_numba"], 200.0)

        batch = payload["pip_batch_executor"]
        self.assertEqual(batch["largest_request_count"], 100)
        self.assertEqual(batch["recommended_route"], "rtdl_optix_prepared_pip_batch_executor")
        self.assertTrue(batch["throughput_evidence_not_one_shot_latency"])
        self.assertLess(batch["largest_request_per_request_ms_median"], batch["single_ms_median"])

        boundary = payload["claim_boundary"]
        for flag in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "whole_app_speedup_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "paper_reproduction_claim_authorized",
            "true_zero_copy_claim_authorized",
            "automatic_partner_selection_authorized",
            "app_specific_native_engine_logic_allowed",
        ):
            self.assertFalse(boundary[flag])

    def test_report_and_log_capture_toolchain_repair(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        log = LOG.read_text(encoding="utf-8")
        for fragment in (
            "CUDA 12.4 nvcc/NVVM",
            "CUDA_ERROR_UNSUPPORTED_PTX_VERSION",
            "PIP one-shot scalar count",
            "LSI scalar count",
            "Overlay active count",
            "does not authorize release action",
        ):
            self.assertIn(fragment, text)
        self.assertIn("Numba PIP baseline start", log)
        self.assertIn("RTDL/OptiX route start", log)

    def test_current_registries_include_goal4039_without_auto_dispatch(self) -> None:
        scale = next(row for row in rt.current_benchmark_scale_profiles() if row["app"] == "spatial_rayjoin")
        route = rt.explain_current_benchmark_route("spatial_rayjoin")
        adequacy = next(row for row in rt.current_benchmark_adequacy() if row["app"] == "spatial_rayjoin")

        self.assertIn("Goal4039", scale["evidence_refs"])
        self.assertIn("Goal4039", route["evidence_refs"])
        self.assertIn("Goal4039", adequacy["evidence_refs"])
        self.assertEqual(route["decision_kind"], "mixed_explicit")
        self.assertFalse(route["automatic_partner_selection_authorized"])
        self.assertFalse(adequacy["automatic_partner_selection_authorized"])


if __name__ == "__main__":
    unittest.main()
