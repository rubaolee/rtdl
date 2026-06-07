from __future__ import annotations

import json
from pathlib import Path
import unittest

from rtdsl.v2_10_amd_hiprt_benchmark_parity import V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION
from rtdsl.v2_10_amd_hiprt_functional_validation import (
    V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
    build_v2_10_amd_hiprt_functional_validation_runbook,
    validate_v2_10_amd_hiprt_functional_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3784_amd_hiprt_functional_validation_runbook_2026-06-07.md"
A5000_CLOSEOUT = ROOT / "docs" / "reports" / "goal3783_v2_10_hiprt_parity_closeout_a5000.json"
GOAL3753_REPORT = ROOT / "docs" / "reports" / "goal3753_amd_hiprt_benchmark_parity_plan_2026-06-07.md"


def _accepted_amd_artifact() -> dict[str, object]:
    runbook = build_v2_10_amd_hiprt_functional_validation_runbook()
    apps = tuple(runbook["ready_for_amd_functional_pod_apps"])
    return {
        "goal": "Goal3784",
        "version": V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
        "hardware_vendor": "amd",
        "gpu": "AMD Radeon PRO functional validation pod",
        "driver": "recorded-by-pod",
        "backend_route": "AMD HIPRT functional pod evidence",
        "hiprt_sdk": "/root/vendor/hiprt-official",
        "hiprt_library": "/workspace/build/librtdl_hiprt.so",
        "git_commit": "recorded-by-pod",
        "build_command": "make build-hiprt HIPRT_PREFIX=/root/vendor/hiprt-official",
        "focused_test_modules": runbook["focused_test_modules"],
        "focused_tests_passed": True,
        "stage_counts": {
            "ready_for_amd_functional_pod": 10,
            "needs_generic_hiprt_extension": 0,
            "compatibility_only_not_amd_perf_ready": 0,
        },
        "ready_for_amd_functional_pod_apps": apps,
        "functional_results_by_app": {app: "pass" for app in apps},
        "parity_validation": {"status": "accept", "version": V2_10_AMD_HIPRT_BENCHMARK_PARITY_VERSION},
        "scoped_source_dirty": False,
        "claim_boundary": {
            "release_authorized": False,
            "amd_perf_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_claim_authorized": False,
            "paper_reproduction_claim_authorized": False,
            "zero_copy_claim_authorized": False,
            "app_specific_native_engine_logic_allowed": False,
        },
    }


class Goal3784AmdHiprtFunctionalValidationRunbookTest(unittest.TestCase):
    def test_runbook_covers_all_ten_apps_without_authorizing_claims(self) -> None:
        runbook = build_v2_10_amd_hiprt_functional_validation_runbook()
        self.assertEqual(runbook["version"], V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION)
        self.assertEqual(runbook["status"], "pending_actual_amd_hardware")
        self.assertEqual(runbook["stage_counts"]["ready_for_amd_functional_pod"], 10)
        self.assertEqual(runbook["stage_counts"]["needs_generic_hiprt_extension"], 0)
        self.assertEqual(runbook["stage_counts"]["compatibility_only_not_amd_perf_ready"], 0)
        self.assertEqual(len(runbook["ready_for_amd_functional_pod_apps"]), 10)
        self.assertIn("tests.goal3784_amd_hiprt_functional_validation_runbook_test", runbook["focused_test_modules"])
        for value in runbook["claim_boundary"].values():
            self.assertFalse(value)

    def test_validator_accepts_only_true_amd_functional_artifact_shape(self) -> None:
        verdict = validate_v2_10_amd_hiprt_functional_artifact(_accepted_amd_artifact())
        self.assertEqual(verdict["status"], "accept")
        self.assertEqual(verdict["errors"], ())

    def test_validator_rejects_nvidia_orochi_closeout_as_amd_evidence(self) -> None:
        if not A5000_CLOSEOUT.exists():
            self.skipTest("Goal3783 A5000 closeout artifact not present")
        artifact = json.loads(A5000_CLOSEOUT.read_text(encoding="utf-8"))
        verdict = validate_v2_10_amd_hiprt_functional_artifact(artifact)
        self.assertEqual(verdict["status"], "reject")
        joined = "\n".join(verdict["errors"])
        self.assertIn("hardware_vendor must be amd", joined)
        self.assertIn("NVIDIA/Orochi evidence", joined)

    def test_goal3753_report_is_refreshed_to_current_ten_ready_state(self) -> None:
        text = GOAL3753_REPORT.read_text(encoding="utf-8")
        self.assertIn("Ready for AMD functional pod | 10", text)
        self.assertNotIn("Ready for AMD functional pod | 7", text)
        self.assertNotIn("Needs generic HIPRT extension | 1", text)
        self.assertNotIn("Compatibility-only, not AMD perf ready | 2", text)
        self.assertIn("Goal3783", text)

    def test_report_records_runbook_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3784", text)
        self.assertIn("actual AMD hardware", text)
        self.assertIn("goal3784_amd_hiprt_functional_pod_validation.json", text)
        self.assertIn("10 / 10", text)
        self.assertIn("does not authorize AMD performance", text)
        self.assertIn("rejects the Goal3783 A5000", text)


if __name__ == "__main__":
    unittest.main()
