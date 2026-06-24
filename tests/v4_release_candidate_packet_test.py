from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "future" / "v4" / "v4_0_release_candidate_packet_2026-06-24.md"
CALL_FOR_REVIEW = ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_0_release_candidate_2026-06-24.md"


class V4ReleaseCandidatePacketTest(unittest.TestCase):
    def test_packet_states_candidate_scope_and_non_authorization(self) -> None:
        text = PACKET.read_text(encoding="utf-8")

        self.assertIn("engineering release candidate packet, not a release authorization", text)
        self.assertIn("v4_fixed_radius_count_threshold_2d_device_arrays", text)
        self.assertIn("v4_closest_hit_grouped_argmin_3d_device_arrays", text)
        self.assertIn("v4_ray_triangle_any_hit_flags_2d_device_arrays", text)
        self.assertIn("final GPU catalog gate", text)
        self.assertIn("v4_final_release_scope_catalog_gate_gpu_32768_2026-06-24.json", text)
        self.assertIn("v4_local_full_test_sweep_2026-06-24.md", text)
        self.assertIn("serious validation size", text)
        self.assertIn("status: `passed`", text)
        self.assertIn("release authorized: `false`", text)
        self.assertIn("No functions with semantic types found", text)
        self.assertIn("does not authorize V4 release", text)

    def test_review_packet_preserves_release_boundary(self) -> None:
        text = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn("not a release authorization", text)
        self.assertIn("approve_release_candidate_not_authorized", text)
        self.assertIn("reject_release_candidate_overclaims", text)
        self.assertIn("does not authorize V4 release", text)


if __name__ == "__main__":
    unittest.main()
