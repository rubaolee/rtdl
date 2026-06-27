from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SMOKE_DIR = ROOT / "future" / "v4" / "evidence" / "v4_goal4758_wheel_install_smoke_2026-06-26"
SUMMARY = SMOKE_DIR / "summary.json"
REPORT = SMOKE_DIR / "summary.md"
SCRIPT = ROOT / "scripts" / "v4_goal4758_installed_wheel_smoke.py"


class V4Goal4758InstalledWheelSmokeTest(unittest.TestCase):
    def test_installed_wheel_smoke_evidence_exists_and_passes(self) -> None:
        self.assertTrue(SCRIPT.exists())
        self.assertTrue(SUMMARY.exists())
        self.assertTrue(REPORT.exists())
        payload = json.loads(SUMMARY.read_text(encoding="utf-8"))

        self.assertEqual("passed", payload["status"])
        self.assertEqual("passed", payload["install_status"])
        self.assertEqual("passed", payload["smoke_status"])
        self.assertTrue(payload["venv_removed"])
        self.assertTrue(payload["no_cuda_required"])
        self.assertEqual(10, payload["matrix_apps"])
        self.assertEqual(30, payload["matrix_rows"])
        self.assertEqual(["cupy", "numba", "rtdl_native", "torch"], payload["measured_partners"])
        self.assertEqual("certified_partner_measured_ready", payload["cupy_grouped_vector_sum_status"])
        self.assertEqual("tier2_measured_ready", payload["numba_component_union_status"])
        self.assertFalse(payload["release_authorized"])
        self.assertFalse(payload["public_tag_authorized"])
        self.assertFalse(payload["broad_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
