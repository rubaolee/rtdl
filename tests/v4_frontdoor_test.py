from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


README = ROOT / "future" / "v4" / "README.md"
QUICKSTART = ROOT / "future" / "v4" / "examples" / "v4_frontdoor_quickstart.py"


class V4FrontDoorTest(unittest.TestCase):
    def test_claim_boundary_lists_measured_surfaces_without_release_claims(self) -> None:
        boundary = v4.claim_boundary_v4()

        self.assertEqual("v4_development_front_door_not_release", boundary["status"])
        self.assertEqual("torch", boundary["measured_partner"])
        self.assertEqual(3, len(boundary["measured_surfaces"]))
        self.assertIn("v4_fixed_radius_count_threshold_2d_device_arrays", boundary["measured_surfaces"])
        self.assertIn("v4_closest_hit_grouped_argmin_3d_device_arrays", boundary["measured_surfaces"])
        self.assertIn("v4_ray_triangle_any_hit_flags_2d_device_arrays", boundary["measured_surfaces"])
        self.assertFalse(boundary["release_claim_authorized"])
        self.assertFalse(boundary["broad_v4_speedup_claim_authorized"])
        self.assertFalse(boundary["tier3_callback_claim_authorized"])
        self.assertFalse(boundary["raw_optix_callback_claim_authorized"])
        self.assertFalse(boundary["app_specific_native_kernel_authorized"])

    def test_frontdoor_catalog_and_planner_are_reachable(self) -> None:
        rows = v4.measured_operator_catalog_v4()
        self.assertEqual(3, len(rows))

        plan = v4.plan_operator_request_v4("any-hit", partner="torch")
        self.assertEqual("tier2_measured_ready", plan.status)
        self.assertEqual("v4_ray_triangle_any_hit_flags_2d_device_arrays", plan.api_surface)

    def test_readme_points_users_at_unified_frontdoor(self) -> None:
        text = README.read_text(encoding="utf-8")
        self.assertIn("import rtdsl.v4 as rtdl_v4", text)
        self.assertIn("V4.0 does not expose raw OptiX callbacks", text)
        self.assertIn("not a release announcement", text)
        self.assertIn("embedding/C-ABI claims", text)

    def test_quickstart_runs_without_cuda(self) -> None:
        proc = subprocess.run(
            [sys.executable, str(QUICKSTART)],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        payload = json.loads(proc.stdout)
        self.assertEqual("ok", payload["status"])
        self.assertEqual("v4_development_front_door_not_release", payload["front_door_status"])
        self.assertEqual(3, payload["measured_surface_count"])
        self.assertEqual(3, payload["catalog_operator_count"])
        self.assertEqual("tier2_measured_ready", payload["tier2_plan_status"])
        self.assertEqual("rejected_action_shaped_callback_deferred", payload["complex_callback_status"])
        self.assertFalse(payload["release_claim_authorized"])
        self.assertFalse(payload["tier3_callback_claim_authorized"])
        self.assertFalse(payload["app_specific_native_kernel_authorized"])


if __name__ == "__main__":
    unittest.main()

