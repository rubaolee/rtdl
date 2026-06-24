from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/v4_section8_any_hit_flags_device_frontdoor_validation.py"


class V4Section8AnyHitFlagsDeviceFrontdoorValidationTest(unittest.TestCase):
    def test_dry_run_reports_claim_boundary_without_cuda(self) -> None:
        proc = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--dry-run",
                "--ray-count",
                "8192",
                "--repeat",
                "1",
            ],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual(
            "rtdl.v4.section8.ray_triangle_any_hit_flags_device_frontdoor.v1",
            payload["schema"],
        )
        self.assertEqual("dry_run", payload["status"])
        self.assertEqual("v4_ray_triangle_any_hit_flags_2d_device_arrays", payload["claim_boundary"]["measured_surface"])
        self.assertFalse(payload["claim_boundary"]["release_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["broad_v4_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["whole_app_speedup_claim_authorized"])
        self.assertFalse(payload["claim_boundary"]["tier3_callback_claim_authorized"])
        self.assertEqual([], payload["results"])


if __name__ == "__main__":
    unittest.main()
