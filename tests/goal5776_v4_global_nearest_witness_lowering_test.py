from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
LOWERING = ROOT / "src/rtdsl/v4_global_nearest_witness_lowering.py"
APP = ROOT / "Paper-reproduction-apps/x-hd-paper/v4_whole_app.py"


class Goal5776GlobalWitnessLoweringTest(unittest.TestCase):
    def test_lowering_is_app_neutral_and_bounded_output(self) -> None:
        source = LOWERING.read_text(encoding="utf-8")
        lowered = source.lower()
        for forbidden in ("x-hd", "x_hd", "dragon", "happybuddha", "paper app"):
            self.assertNotIn(forbidden, lowered)
        self.assertIn("compile_canonical_callback()", source)
        self.assertIn("VerifiedExactPredicateWitnessAuthority", source)
        self.assertIn("consume_verified_multiround_spatial_executable", source)
        self.assertIn("bounded_witness_host_projection_rows", source)
        self.assertIn("full_nearest_state_host_projection_used", source)
        self.assertIn("OptixTraversalAuditSession", source)

    def test_xhd_frontdoor_uses_verified_device_global_witness(self) -> None:
        source = APP.read_text(encoding="utf-8")
        self.assertIn("prepare_verified_global_nearest_witness_v4", source)
        self.assertIn("bounded_device_global_witness_used", source)
        self.assertIn("full_per_query_host_projection_used", source)
        self.assertNotIn("maximum_candidate_capacity=437645", source)


if __name__ == "__main__":
    unittest.main()
