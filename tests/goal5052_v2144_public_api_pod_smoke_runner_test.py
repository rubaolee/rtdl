from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal5052_v2144_public_api_pod_smoke.py"
RUNNER = ROOT / "scripts" / "goal5052_v2144_public_api_pod_smoke_runner.sh"


class Goal5052V2144PublicApiPodSmokeRunnerTest(unittest.TestCase):
    def test_runner_script_has_strict_pod_command_and_boundaries(self) -> None:
        text = RUNNER.read_text(encoding="utf-8")
        self.assertIn("already-running RTX-class Linux POD", text)
        self.assertIn("RTDL_OPTIX_LIBRARY", text)
        self.assertIn("goal5052_v2144_public_api_pod_smoke.py", text)
        self.assertIn("--strict", text)
        self.assertIn("no public speedup or true-zero-copy claims", text)

    def test_python_smoke_script_uses_public_apis(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("rt.numba_partner_continuation", text)
        self.assertIn("rt.run_numba_partner_continuation", text)
        self.assertIn("_run_public_device_order_by_native_lexsort", text)
        self.assertIn("public_device_order_by_used", text)
        self.assertNotIn("run_cuda_lexsort_i64_f64_i64_i64_device(", text)
        self.assertNotIn("public_speedup_claim_authorized\": True", text)

    def test_local_non_strict_run_writes_machine_readable_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "goal5052_smoke.json"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--output-json",
                    str(output),
                ],
                cwd=str(ROOT),
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual("rtdl.goal5052.v2_14_4_public_api_pod_smoke.v1", payload["schema"])
        self.assertIn(payload["overall_status"], ("pass", "partial_skip"))
        self.assertFalse(payload["strict"])
        self.assertEqual(
            {
                "public_speedup_claim": True,
                "true_zero_copy_claim": True,
                "author_parity_claim": True,
                "device_group_by_public_ready": True,
            },
            payload["not_authorized"],
        )
        self.assertEqual(
            {
                "public_numba_partner_continuation_cuda",
                "rayjoin_public_device_order_by_native_cuda_path",
            },
            {step["label"] for step in payload["steps"]},
        )


if __name__ == "__main__":
    unittest.main()
