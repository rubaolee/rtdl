from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_v2_10_pod_validation_bundle.py"
RUN_DIR = ROOT / "scratch" / "goal4280_bundle_test"


class Goal4280V210PodValidationBundleTest(unittest.TestCase):
    def setUp(self) -> None:
        if RUN_DIR.exists():
            shutil.rmtree(RUN_DIR)

    def tearDown(self) -> None:
        if RUN_DIR.exists():
            shutil.rmtree(RUN_DIR)

    def test_local_preflight_bundle_runs_without_hardware_flags(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir", str(RUN_DIR)],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("[v2.10-pod-bundle] start source_tree_doctor", result.stdout)
        self.assertIn("[v2.10-pod-bundle] done scale_profile_dry_run", result.stdout)

        summary = json.loads((RUN_DIR / "bundle_summary.json").read_text(encoding="utf-8"))
        self.assertEqual("pass", summary["status"])
        self.assertFalse(summary["hardware_steps_requested"]["front_door"])
        self.assertFalse(summary["hardware_steps_requested"]["scale_profile"])
        self.assertFalse(summary["hardware_steps_requested"]["partner_comparison"])
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])
        self.assertFalse(summary["broad_rt_core_claim_authorized"])
        self.assertFalse(summary["paper_reproduction_claim_authorized"])
        self.assertEqual(
            [
                "source_tree_doctor",
                "benchmark_evidence_index",
                "front_door_dry_run",
                "scale_profile_dry_run",
            ],
            [step["name"] for step in summary["steps"]],
        )

        for artifact in (
            "source_tree_doctor.json",
            "benchmark_evidence_index.json",
            "front_door_dry_run.json",
            "scale_profile_dry_run.json",
        ):
            self.assertTrue((RUN_DIR / artifact).is_file(), artifact)

    def test_runbook_and_evidence_docs_link_bundle(self) -> None:
        docs = "\n".join(
            [
                (ROOT / "docs" / "audit" / "runbooks" / "v2_10_pod_validation_bundle.md").read_text(
                    encoding="utf-8"
                ),
                (ROOT / "docs" / "learn" / "benchmark_evidence_index.md").read_text(
                    encoding="utf-8"
                ),
            ]
        )

        self.assertIn("scripts/rtdl_v2_10_pod_validation_bundle.py", docs)
        self.assertIn("--run-front-door", docs)
        self.assertIn("--run-scale-profile", docs)
        self.assertIn("bundle_summary.json", docs)
        self.assertNotIn("examples/v2_0", docs)


if __name__ == "__main__":
    unittest.main()
