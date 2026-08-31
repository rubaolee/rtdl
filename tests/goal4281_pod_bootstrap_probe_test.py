from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_pod_bootstrap_probe.py"
RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "v2_10_pod_bootstrap_probe.md"
BUNDLE_RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "v2_10_pod_validation_bundle.md"


class Goal4281PodBootstrapProbeTest(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=60,
            check=False,
        )

    def test_json_output_contains_probe_contract_and_non_authorizing_flags(self) -> None:
        result = self._run("--json")

        self.assertEqual(0, result.returncode, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual("rtdl_pod_bootstrap_probe", payload["tool"])
        self.assertIn(payload["status"], {"ready", "not_ready"})
        self.assertIn("nvidia_smi", payload["checks"])
        self.assertIn("nvcc", payload["checks"])
        self.assertIn("optix_headers", payload["checks"])
        self.assertIn("rtdl_optix_library", payload["checks"])
        self.assertIn("make build-optix", payload["recommended_build_command"])
        self.assertIn("rtdl_v2_10_pod_validation_bundle.py", payload["recommended_validation_command"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])

    def test_text_output_is_human_readable(self) -> None:
        result = self._run()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("RTDL Pod Bootstrap Probe", result.stdout)
        self.assertIn("nvidia_smi", result.stdout)
        self.assertIn("optix headers", result.stdout)
        self.assertIn("validate:", result.stdout)

    def test_strict_mode_matches_readiness_status(self) -> None:
        payload = json.loads(self._run("--json").stdout)
        strict = self._run("--json", "--strict")

        expected = 0 if payload["status"] == "ready" else 1
        self.assertEqual(expected, strict.returncode)

    def test_runbooks_wire_probe_before_bundle(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")
        bundle = BUNDLE_RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("scripts/rtdl_pod_bootstrap_probe.py", text)
        self.assertIn("--json --strict", text)
        self.assertIn("does not install packages", text)
        self.assertIn("$HOME/vendor/optix-dev", text)
        self.assertNotIn("/home/lestat/vendor/optix-dev", text)
        self.assertIn("scripts/rtdl_pod_bootstrap_probe.py", bundle)
        self.assertIn("Before running the hardware bundle", bundle)

    def test_probe_uses_generic_home_candidate_not_local_user_path(self) -> None:
        source = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('Path.home() / "vendor" / "optix-dev"', source)
        self.assertNotIn("/home/lestat/vendor/optix-dev", source)


if __name__ == "__main__":
    unittest.main()
