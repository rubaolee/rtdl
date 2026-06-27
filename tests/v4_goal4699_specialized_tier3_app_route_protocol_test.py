from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import rtdsl.v4 as v4


SCRIPT = ROOT / "scripts" / "v4_goal4699_specialized_tier3_app_route_protocol.py"


class V4Goal4699SpecializedTier3AppRouteProtocolTest(unittest.TestCase):
    def test_protocol_freezes_weighted_sum_route_and_denominators(self) -> None:
        validation = v4.validate_v4_goal4699_specialized_tier3_app_route_protocol()
        protocol = validation["protocol"]

        self.assertEqual("passed", validation["status"])
        self.assertEqual((), validation["missing_or_invalid"])
        self.assertEqual("v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays", protocol["selected_surface"])
        self.assertIn("Tier-2 built-in", protocol["primary_performance_denominator"])
        self.assertEqual((32768, 131072, 262144), protocol["ray_counts"])
        self.assertLessEqual(protocol["callback_over_tier2_pass_ratio_max"], 1.20)
        self.assertLessEqual(protocol["callback_over_tier2_hard_kill_ratio"], 1.50)

    def test_protocol_keeps_release_and_support_flags_false(self) -> None:
        protocol = v4.v4_goal4699_specialized_tier3_app_route_protocol().as_dict()

        self.assertFalse(protocol["tier3_public_support_authorized"])
        self.assertFalse(protocol["app_level_speed_claim_authorized"])
        self.assertFalse(protocol["release_authorized"])
        self.assertFalse(protocol["performance_claim_authorized"])
        self.assertTrue(protocol["pod_required_for_next_goal"])

    def test_script_emits_json_and_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            json_out = tmp_path / "protocol.json"
            md_out = tmp_path / "protocol.md"
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--json-out",
                    str(json_out),
                    "--md-out",
                    str(md_out),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(json_out.read_text(encoding="utf-8"))
            stdout_payload = json.loads(proc.stdout)
            markdown = md_out.read_text(encoding="utf-8")

        self.assertEqual("passed", payload["validation_status"])
        self.assertEqual("passed", stdout_payload["validation_status"])
        self.assertIn("not authorize public Tier-3 support", markdown)


if __name__ == "__main__":
    unittest.main()
