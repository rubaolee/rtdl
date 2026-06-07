from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest

from rtdsl.v2_10_amd_hiprt_functional_validation import (
    V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION,
    validate_v2_10_amd_hiprt_functional_artifact,
)


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3785_amd_hiprt_functional_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3785_amd_hiprt_functional_pod_runner_2026-06-07.md"


def _runner_module():
    spec = importlib.util.spec_from_file_location("goal3785_runner", RUNNER)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load Goal3785 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal3785AmdHiprtFunctionalPodRunnerTest(unittest.TestCase):
    def test_hardware_vendor_classifier_is_fail_closed(self) -> None:
        runner = _runner_module()
        self.assertEqual(runner.classify_hardware_vendor("NVIDIA RTX A5000, 580.126.09"), "nvidia")
        self.assertEqual(runner.classify_hardware_vendor("AMD Instinct MI250"), "amd")
        self.assertEqual(runner.classify_hardware_vendor("Radeon PRO W7900"), "amd")
        self.assertEqual(runner.classify_hardware_vendor("unknown gpu"), "unknown")

    def test_non_amd_control_artifact_rejects_as_amd_evidence(self) -> None:
        runner = _runner_module()
        artifact = runner.build_non_amd_control_artifact(
            hardware_vendor="nvidia",
            gpu="NVIDIA RTX A5000",
            git_commit="synthetic",
            reason="unit-test negative control",
        )
        self.assertEqual(artifact["status"], "reject_non_amd_hardware")
        self.assertFalse(artifact["focused_tests_passed"])
        for value in artifact["claim_boundary"].values():
            self.assertFalse(value)
        verdict = validate_v2_10_amd_hiprt_functional_artifact(artifact)
        self.assertEqual(verdict["status"], "reject")
        self.assertIn("hardware_vendor must be amd", "\n".join(verdict["errors"]))

    def test_synthetic_amd_pass_artifact_validates(self) -> None:
        runner = _runner_module()
        artifact = runner.build_amd_functional_artifact(
            gpu="AMD Radeon PRO W7900",
            driver="synthetic-rocm",
            hiprt_sdk="/opt/hiprt",
            hiprt_library="/workspace/build/librtdl_hiprt.so",
            git_commit="synthetic",
            build_command="make build-hiprt HIPRT_PREFIX=/opt/hiprt",
            focused_tests_passed=True,
            command_results=(),
        )
        self.assertEqual(artifact["version"], V2_10_AMD_HIPRT_FUNCTIONAL_VALIDATION_VERSION)
        verdict = validate_v2_10_amd_hiprt_functional_artifact(artifact)
        self.assertEqual(verdict["status"], "accept")
        self.assertEqual(verdict["errors"], ())

    def test_runner_report_records_command_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("Goal3785", text)
        self.assertIn("goal3785_amd_hiprt_functional_pod_runner.py", text)
        self.assertIn("--allow-non-amd-control", text)
        self.assertIn("not AMD hardware evidence", text)
        self.assertIn("does not authorize AMD performance", text)


if __name__ == "__main__":
    unittest.main()
