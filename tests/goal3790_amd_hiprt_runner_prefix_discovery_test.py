from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "goal3785_amd_hiprt_functional_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal3790_amd_hiprt_runner_prefix_discovery_2026-06-07.md"
GOAL3785_REPORT = ROOT / "docs" / "reports" / "goal3785_amd_hiprt_functional_pod_runner_2026-06-07.md"


def _runner_module():
    spec = importlib.util.spec_from_file_location("goal3785_runner_for_goal3790", RUNNER)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load Goal3785 runner")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Goal3790AmdHiprtRunnerPrefixDiscoveryTest(unittest.TestCase):
    def test_find_valid_prefix_accepts_version_suffixed_sdk_root(self) -> None:
        runner = _runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            invalid = root / "hiprtSdk-old"
            valid = root / "hiprtSdk-2.2.synthetic"
            (valid / "hiprt").mkdir(parents=True)
            (valid / "hiprt" / "hiprt.h").write_text("// synthetic\n", encoding="utf-8")

            discovered = runner.find_valid_hiprt_prefix((str(invalid), str(valid)))
            self.assertEqual(discovered, str(valid))

    def test_glob_candidate_expansion_ignores_archives(self) -> None:
        runner = _runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = root / "hiprtSdk-2.2.synthetic"
            valid.mkdir()
            archive = root / "hiprtSdk-2.2.synthetic.zip"
            archive.write_text("archive placeholder\n", encoding="utf-8")

            candidates = runner.expand_hiprt_prefix_candidates((str(root / "hiprtSdk-*"),))
            self.assertEqual(candidates, (str(valid),))

    def test_resolve_explicit_prefix_is_recorded_even_when_invalid(self) -> None:
        runner = _runner_module()
        with tempfile.TemporaryDirectory() as tmp:
            explicit = str(Path(tmp) / "missing")
            resolved = runner.resolve_hiprt_prefix(explicit)
            self.assertEqual(resolved["hiprt_prefix"], explicit)
            self.assertEqual(resolved["source"], "explicit_or_environment")
            self.assertFalse(resolved["valid_header"])
            self.assertEqual(resolved["candidates"], ())

    def test_non_amd_control_artifact_can_record_prefix_resolution(self) -> None:
        runner = _runner_module()
        artifact = runner.build_non_amd_control_artifact(
            hardware_vendor="nvidia",
            gpu="NVIDIA RTX A5000",
            git_commit="synthetic",
            reason="unit-test negative control",
        )
        artifact["hiprt_prefix_resolution"] = {
            "hiprt_prefix": "/synthetic/hiprtSdk",
            "source": "auto_discovered",
            "valid_header": True,
            "candidates": ("/synthetic/hiprtSdk",),
        }
        self.assertEqual(artifact["hiprt_prefix_resolution"]["source"], "auto_discovered")
        self.assertEqual(artifact["status"], "reject_non_amd_hardware")
        self.assertFalse(artifact["focused_tests_passed"])

    def test_reports_document_autodiscovery_and_boundaries(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        runner_text = GOAL3785_REPORT.read_text(encoding="utf-8")
        for phrase in (
            "auto-discovers common HIPRT SDK locations",
            "hiprt_prefix_resolution",
            "Actual AMD evidence still requires",
            "does not authorize AMD performance",
        ):
            self.assertIn(phrase, text)
        self.assertIn("The runner auto-discovers common HIPRT SDK locations", runner_text)
        self.assertIn("--hiprt-prefix /path/to/hiprtSdk", runner_text)


if __name__ == "__main__":
    unittest.main()
