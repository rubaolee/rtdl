from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from scripts.rtdl_v2_10_pod_validation_bundle import _run_step


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

    def _get_env(self) -> dict[str, str]:
        import os
        env = os.environ.copy()
        for k in list(env.keys()):
            if k.upper() == "PYTHONPATH":
                pythonpath = env.pop(k)
                break
        else:
            pythonpath = ""
        src_path = str(ROOT / "src")
        root_path = str(ROOT)
        if pythonpath:
            env["PYTHONPATH"] = f"{src_path}{os.pathsep}{root_path}{os.pathsep}{pythonpath}"
        else:
            env["PYTHONPATH"] = f"{src_path}{os.pathsep}{root_path}"
        return env

    def test_local_preflight_bundle_runs_without_hardware_flags(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output-dir", str(RUN_DIR)],
            cwd=ROOT,
            env=self._get_env(),
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
        self.assertFalse(summary["rayjoin_public_cdb_fixture_request"]["materialize_requested"])
        self.assertFalse(summary["rayjoin_public_cdb_fixture_request"]["download_hidden_by_bundle"])
        self.assertEqual(
            [
                "source_tree_doctor",
                "benchmark_evidence_index",
                "front_door_dry_run",
                "scale_profile_dry_run",
            ],
            [step["name"] for step in summary["steps"]],
        )
        self.assertTrue(all(step["json_parseable"] for step in summary["steps"]))
        self.assertIn(summary["steps"][2]["json_source"], {"stdout", "artifact"})
        self.assertIn(summary["steps"][3]["json_source"], {"stdout", "artifact"})

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
        self.assertIn("--materialize-rayjoin-public-cdb", docs)
        self.assertIn("bundle_summary.json", docs)
        self.assertNotIn("examples/v2_0", docs)

    def test_explicit_rayjoin_fixture_flag_is_passed_to_scale_profile_dry_run(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--materialize-rayjoin-public-cdb",
                "--output-dir",
                str(RUN_DIR),
            ],
            cwd=ROOT,
            env=self._get_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=120,
            check=False,
        )

        self.assertEqual(0, result.returncode, result.stderr)
        summary = json.loads((RUN_DIR / "bundle_summary.json").read_text(encoding="utf-8"))
        self.assertTrue(summary["rayjoin_public_cdb_fixture_request"]["materialize_requested"])
        self.assertFalse(summary["rayjoin_public_cdb_fixture_request"]["download_hidden_by_bundle"])
        scale_step = next(step for step in summary["steps"] if step["name"] == "scale_profile_dry_run")
        self.assertIn("--materialize-rayjoin-public-cdb", scale_step["command"])
        self.assertTrue(scale_step["json_parseable"])

        dry_run = json.loads((RUN_DIR / "scale_profile_dry_run.json").read_text(encoding="utf-8"))
        self.assertEqual("dry_run_planned", dry_run["rayjoin_public_cdb_fixture"]["status"])

    def test_step_parser_falls_back_to_declared_artifact_when_stdout_has_progress(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact = Path(tmp) / "artifact.json"
            step = _run_step(
                "synthetic_progress_stdout",
                [
                    sys.executable,
                    "-c",
                    (
                        "import json, pathlib, sys; "
                        "pathlib.Path(sys.argv[1]).write_text(json.dumps({'release_authorized': False}), "
                        "encoding='utf-8'); "
                        "print('[progress] not json')"
                    ),
                    str(artifact),
                ],
                output_path=None,
                json_artifact_path=artifact,
                timeout_sec=10,
            )

        self.assertEqual("pass", step["status"])
        self.assertFalse(step["stdout_json_parseable"])
        self.assertTrue(step["json_parseable"])
        self.assertEqual("artifact", step["json_source"])
        self.assertEqual((), step["claim_flag_violations"])


if __name__ == "__main__":
    unittest.main()
