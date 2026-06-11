from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_remote_pod_validation_driver.py"
RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "v2_10_remote_pod_validation_driver.md"
BUNDLE_RUNBOOK = ROOT / "docs" / "audit" / "runbooks" / "v2_10_pod_validation_bundle.md"
REPORT = ROOT / "docs" / "reports" / "goal4286_remote_pod_validation_driver_2026-06-11.md"


class Goal4286RemotePodValidationDriverTest(unittest.TestCase):
    def _dry_run(self, *extra: str) -> dict[str, object]:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--target",
                "root@example.invalid",
                "--port",
                "22022",
                "--identity-file",
                "~/.ssh/id_ed25519",
                "--json",
                *extra,
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        return json.loads(result.stdout)

    def test_default_is_dry_run_and_non_authorizing(self) -> None:
        payload = self._dry_run()

        self.assertEqual("rtdl_remote_pod_validation_driver", payload["tool"])
        self.assertEqual("dry_run", payload["mode"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_speedup_claim_authorized"])
        self.assertFalse(payload["broad_rt_core_claim_authorized"])
        self.assertTrue(payload["uses_fresh_mktemp_workdir"])
        self.assertFalse(payload["destructive_checkout"])

    def test_remote_script_has_progress_and_no_destructive_checkout(self) -> None:
        payload = self._dry_run("--build-optix", "--run-hardware", "--run-partner-comparison")
        script = str(payload["remote_script"])

        self.assertIn("[rtdl-remote-pod] start", script)
        self.assertIn("mktemp -d /root/rtdl_v2_10_validation", script)
        self.assertIn("git clone --depth 1", script)
        self.assertIn("rtdl_pod_bootstrap_probe.py", script)
        self.assertIn("make build-optix", script)
        self.assertIn("rtdl_v2_10_pod_validation_bundle.py", script)
        self.assertIn("--run-front-door --run-scale-profile --run-partner-comparison", script)
        self.assertNotIn("git reset --hard", script)
        self.assertNotIn("rm -rf", script)

    def test_runbooks_and_report_document_boundary(self) -> None:
        runbook = RUNBOOK.read_text(encoding="utf-8")
        bundle = BUNDLE_RUNBOOK.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("dry-run unless `--execute`", runbook)
        self.assertIn("v2.10 Remote Pod Validation Driver", bundle)
        self.assertIn("does not install CUDA", report)
        self.assertIn("does not mutate", report)


if __name__ == "__main__":
    unittest.main()
