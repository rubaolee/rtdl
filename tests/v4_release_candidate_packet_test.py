from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / "future" / "v4" / "v4_0_development_state_decision_packet_2026-06-24.md"
CALL_FOR_REVIEW = ROOT / "future" / "v4" / "reviews" / "call_for_review_v4_0_release_candidate_2026-06-24.md"


class V4ReleaseCandidatePacketTest(unittest.TestCase):
    def test_packet_states_candidate_scope_and_non_authorization(self) -> None:
        text = PACKET.read_text(encoding="utf-8")

        self.assertIn("development-state decision packet, not a release authorization", text)
        self.assertIn("development_state_documentation_disclosure_not_release", text)
        self.assertIn("v4_fixed_radius_count_threshold_2d_device_arrays", text)
        self.assertIn("v4_closest_hit_grouped_argmin_3d_device_arrays", text)
        self.assertIn("v4_ray_triangle_any_hit_flags_2d_device_arrays", text)
        self.assertIn("v4_ray_triangle_primitive_grouped_i64_reduction_3d_device_arrays", text)
        self.assertIn("v4_point_group_nearest_witness_2d_device_arrays", text)
        self.assertIn("v4_ray_triangle_any_hit_weighted_sum_3d_device_arrays", text)
        self.assertIn("Final `goal4623` GPU catalog gate", text)
        self.assertIn("v4_goal4623_final_catalog_gpu_32768_include_candidates_2026-06-24.json", text)
        self.assertIn("measured surfaces: `5/5` passed", text)
        self.assertIn("candidate surfaces: `1/1` passed as candidate only", text)
        self.assertIn("all five measured surfaces", text)
        self.assertIn("release authorization false", text)
        self.assertIn("No functions with semantic types found", text)
        self.assertIn("does not authorize:", text)
        self.assertIn("V4 release candidate", text)

    def test_review_packet_preserves_release_boundary(self) -> None:
        text = CALL_FOR_REVIEW.read_text(encoding="utf-8")

        self.assertIn("not a release authorization", text)
        self.assertIn("development_state_documentation_disclosure_not_release", text)
        self.assertIn("reject_goal4623_overclaims_or_insufficient_evidence", text)
        self.assertIn("does not authorize V4 release", text)


if __name__ == "__main__":
    unittest.main()
