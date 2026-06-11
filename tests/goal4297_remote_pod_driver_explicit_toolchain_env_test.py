from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rtdl_remote_pod_validation_driver.py"
REPORT = ROOT / "docs" / "reports" / "goal4297_remote_pod_driver_explicit_toolchain_env_2026-06-11.md"
ARTIFACTS = ROOT / "docs" / "reports" / "goal4297_remote_driver_fresh_clone_artifacts_2026-06-11"


class Goal4297RemotePodDriverExplicitToolchainEnvTest(unittest.TestCase):
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
                "--build-optix",
                "--run-hardware",
                "--run-partner-comparison",
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

    def test_driver_exports_separate_native_and_numba_cuda_prefixes(self) -> None:
        payload = self._dry_run(
            "--cuda-prefix",
            "/usr/local/cuda-12.8",
            "--numba-cuda-prefix",
            "/opt/numba-cuda",
            "--rayjoin-public-cdb-dir",
            "/data/rayjoin_public_cdb",
        )
        script = str(payload["remote_script"])

        self.assertIn("export RTDL_CUDA_PREFIX='/usr/local/cuda-12.8'", script)
        self.assertIn('export PATH="$RTDL_CUDA_PREFIX/bin:$PATH"', script)
        self.assertIn("export NUMBA_CUDA_PREFIX='/opt/numba-cuda'", script)
        self.assertIn('export CUDA_HOME="$NUMBA_CUDA_PREFIX"', script)
        self.assertIn('export CUDA_PATH="$NUMBA_CUDA_PREFIX"', script)
        self.assertIn('export LD_LIBRARY_PATH="$NUMBA_CUDA_PREFIX/nvvm/lib64:${LD_LIBRARY_PATH:-}"', script)
        self.assertIn("export RTDL_RAYJOIN_PUBLIC_CDB_DIR='/data/rayjoin_public_cdb'", script)
        self.assertIn('CUDA_PREFIX="${RTDL_CUDA_PREFIX:-${CUDA_HOME:-/usr/local/cuda}}"', script)

    def test_report_records_orchestration_only_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("--cuda-prefix", text)
        self.assertIn("--numba-cuda-prefix", text)
        self.assertIn("--rayjoin-public-cdb-dir", text)
        self.assertIn("does not install dependencies", text)
        self.assertIn("does not install dependencies, choose", text)
        self.assertIn("A40 Fresh-Clone Execution", text)

    def test_fresh_driver_artifacts_show_end_to_end_pass(self) -> None:
        before = json.loads((ARTIFACTS / "bootstrap_probe_before_build.json").read_text(encoding="utf-8"))
        after = json.loads((ARTIFACTS / "bootstrap_probe_after_setup.json").read_text(encoding="utf-8"))
        bundle = json.loads((ARTIFACTS / "bundle_summary.json").read_text(encoding="utf-8"))
        scale = json.loads((ARTIFACTS / "scale_profile_summary.json").read_text(encoding="utf-8"))
        partner = json.loads((ARTIFACTS / "large_scale_partner_comparison.json").read_text(encoding="utf-8"))

        self.assertEqual("not_ready", before["status"])
        self.assertEqual("ready", after["status"])
        self.assertEqual("/usr/local/cuda-12.8/bin/nvcc", after["checks"]["nvcc"]["path"])
        self.assertTrue(after["checks"]["nvcc"]["probe"]["ok"])
        self.assertEqual("pass", bundle["status"])
        self.assertTrue(all(step["status"] == "pass" for step in bundle["steps"]))
        self.assertEqual(7, len(bundle["steps"]))
        self.assertTrue(scale["all_pass"])
        self.assertEqual("e6d474e3", scale["runtime_environment"]["source_commit_short"])
        self.assertTrue(scale["runtime_environment"]["working_tree_clean"])
        self.assertTrue(partner["summary"]["all_match_cpu_oracle"])
        self.assertTrue(partner["summary"]["all_partner_contract_totals_meet_one_second_floor"])
        self.assertEqual([], partner["summary"]["subsecond_hot_total_rows"])
        self.assertFalse(bundle["release_authorized"])
        self.assertFalse(bundle["public_speedup_claim_authorized"])
        self.assertFalse(bundle["broad_rt_core_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
