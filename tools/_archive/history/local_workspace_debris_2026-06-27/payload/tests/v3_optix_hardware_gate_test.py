import json
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class V3OptixHardwareGateTest(unittest.TestCase):
    def run_gate(self, sample: str, *, require_rt_hardware: bool = True):
        command = [
            sys.executable,
            str(REPO_ROOT / "scripts" / "v3_optix_hardware_gate.py"),
            "--sample-nvidia-smi",
            sample,
        ]
        if require_rt_hardware:
            command.append("--require-rt-hardware")
        return subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, check=False)

    def test_rtx_gpu_passes_rt_hardware_gate(self):
        completed = self.run_gate("NVIDIA RTX 4000 Ada Generation, 550.127.05, 8.9")
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["checks"]["rt_hardware_name_present"])

    def test_non_rt_gpu_fails_when_rt_hardware_required(self):
        completed = self.run_gate("NVIDIA A100-SXM4-40GB, 550.127.05, 8.0")
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertFalse(payload["checks"]["rt_hardware_name_present"])

    def test_empty_nvidia_smi_fails_closed(self):
        completed = self.run_gate("")
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertFalse(payload["checks"]["has_nvidia_gpu"])


if __name__ == "__main__":
    unittest.main()
