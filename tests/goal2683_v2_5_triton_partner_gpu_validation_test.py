from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/goal2683_raydb_triton_front_door_pod_runner.py"


class Goal2683V25TritonPartnerGpuValidationTest(unittest.TestCase):
    def test_raydb_runner_dry_run_does_not_require_cuda(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--row-counts",
                "8,16",
                "--group-count",
                "4",
                "--repeats",
                "1",
            ],
            cwd=ROOT,
            env={"PYTHONPATH": "src:."},
            text=True,
            capture_output=True,
            check=True,
        )

        self.assertIn('"status": "dry_run"', completed.stdout)
        self.assertIn("Goal2683 RayDB v2.5 Triton public front-door app validation", completed.stdout)
        self.assertIn('"scope": "post_rt_generic_continuation_only"', completed.stdout)

    def test_raydb_runner_uses_app_public_front_door_not_low_level_dispatch(self):
        source = SCRIPT.read_text()

        self.assertIn("run_raydb_v2_5_partner_continuation_preview", source)
        self.assertIn('partner="triton"', source)
        self.assertIn("allow_reference_fallback=False", source)
        self.assertIn('"no_public_speedup_claim": True', source)
        self.assertNotIn("run_triton_partner_continuation(", source)
        self.assertNotIn("import cupy", source.lower())
        self.assertNotIn("partner=\"cupy\"", source.lower())


if __name__ == "__main__":
    unittest.main()
