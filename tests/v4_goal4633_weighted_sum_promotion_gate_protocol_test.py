from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "v4_ray_triangle_weighted_sum_device_output_validation.py"
PROTOCOL = ROOT / "future" / "v4" / "v4_goal4633_weighted_sum_promotion_gate_protocol_2026-06-24.md"
CLAUDE_REVIEW = (
    ROOT
    / "future"
    / "v4"
    / "reviews"
    / "claude_v4_goal4633_weighted_sum_promotion_gate_protocol_review_2026-06-24.md"
)


def _load_script_module():
    spec = importlib.util.spec_from_file_location("v4_weighted_sum_validation", SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load weighted-sum validation script")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class V4Goal4633WeightedSumPromotionGateProtocolTest(unittest.TestCase):
    def test_protocol_applies_claude_comparable_route_amendment(self) -> None:
        text = PROTOCOL.read_text(encoding="utf-8")
        flattened = " ".join(text.split())

        self.assertIn("Same-Operator Comparable-Route Comparison", text)
        self.assertIn("host-materialization path versus the device-resident output path", text)
        self.assertIn("not a pure kernel-vs-kernel speedup figure", flattened)
        self.assertNotIn("## Same-Contract Comparison", text)

    def test_claude_review_is_recorded_without_release_authorization(self) -> None:
        text = CLAUDE_REVIEW.read_text(encoding="utf-8")

        self.assertIn("`approve_with_required_amendments`", text)
        self.assertIn("authorized proceeding to the Goal4633 POD", text)
        self.assertIn("V4 release", text)
        self.assertIn("did not authorize", text)

    def test_gate_script_uses_comparable_route_boundary_and_thresholds(self) -> None:
        module = _load_script_module()

        self.assertEqual(module.GOAL4633_PROMOTION_RAY_COUNTS, (32768, 131072, 262144, 524288))
        self.assertAlmostEqual(module.GOAL4633_MIN_PER_SHAPE_RATIO, 1.20)
        self.assertAlmostEqual(module.GOAL4633_MIN_GEOMEAN_RATIO, 1.50)
        self.assertGreater(module._geomean([2.0, 8.0]), 3.9)

        source = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("same_operator_comparable_route", source)
        self.assertIn("host_materialization_over_device_resident_median_ratio", source)
        self.assertNotIn("this same-contract comparison", source)


if __name__ == "__main__":
    unittest.main()
