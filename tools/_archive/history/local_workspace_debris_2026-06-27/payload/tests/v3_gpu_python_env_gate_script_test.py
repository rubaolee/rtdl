import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = REPO_ROOT / "docs" / "rebuild" / "v3" / "v3_setup_and_rerun_runbook_2026-06-20.md"


class V3GpuPythonEnvGateScriptTest(unittest.TestCase):
    def test_dry_run_reports_required_packages(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "v3_gpu_python_env_gate.py"),
                "--dry-run",
            ],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "dry_run")
        self.assertEqual(payload["required_packages"]["cupy-cuda12x"], "14.1.1")
        self.assertEqual(payload["required_packages"]["torch"], "2.6.0+cu124")
        self.assertEqual(payload["required_packages"]["nvidia-cuda-nvcc-cu12"], "12.4.131")
        self.assertIn("NUMBA_CUDA_PREFIX", payload["env"])

    def test_staged_installer_records_pod_package_set(self):
        installer = (REPO_ROOT / "scripts" / "v3_install_gpu_pod_env.sh").read_text(encoding="utf-8")
        self.assertIn("--accept-experimental-pod-gate", installer)
        self.assertIn("torch==2.6.0+cu124", installer)
        self.assertIn("cupy-cuda12x==14.1.1", installer)
        self.assertIn("nvidia-cuda-nvrtc-cu12==12.9.86", installer)
        self.assertIn("v3_gpu_python_env_gate.py --pretty", installer)

    def test_runbook_names_current_phoenix_rerun_contract(self):
        text = RUNBOOK.read_text(encoding="utf-8")
        self.assertIn("Current Phoenix Rerun Contract", text)
        self.assertIn("phoenix_v3_m7_row_classification_packet_2026-06-20.json", text)
        self.assertIn("v3_benchmark_app_classification_2026-06-20.json", text)
        self.assertIn("scripts/v3_release_wording_gate.py --pretty", text)
        self.assertIn("Phoenix M7-qualified release rows: 13", text)
        self.assertIn("barnes_hut_fused_partner_vector_accumulation", text)
        self.assertIn("not release authorization", text)
        self.assertIn("broad_v3_faster_than_v2_claim_authorized: false", text)


if __name__ == "__main__":
    unittest.main()
