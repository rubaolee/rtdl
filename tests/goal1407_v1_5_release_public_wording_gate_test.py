import unittest

import rtdsl as rt


class Goal1407V15ReleasePublicWordingGateTest(unittest.TestCase):
    def test_release_public_wording_gate_is_complete_but_not_tag_authorization(self):
        gate = rt.validate_v1_5_release_public_wording_gate()

        self.assertEqual(gate["status"], "release_candidate_docs_ready")
        self.assertTrue(gate["release_docs_and_public_wording_complete"])
        self.assertTrue(gate["explicit_release_approval_required"])
        self.assertFalse(gate["public_release_authorized_by_this_gate"])
        self.assertFalse(gate["release_tag_action_authorized_by_this_gate"])
        self.assertFalse(gate["public_speedup_wording_authorized_by_this_gate"])

    def test_release_public_wording_docs_and_scope_are_accounted(self):
        gate = rt.validate_v1_5_release_public_wording_gate()

        self.assertEqual(
            tuple(gate["required_docs"]),
            rt.V1_5_RELEASE_PUBLIC_WORDING_REQUIRED_DOCS,
        )
        self.assertEqual(gate["included_app_count"], 14)
        self.assertEqual(gate["excluded_app_count"], 4)
        self.assertEqual(set(gate["excluded_apps"]), {
            "apple_rt_demo",
            "hiprt_ray_triangle_hitcount",
            "polygon_set_jaccard",
            "segment_polygon_anyhit_rows",
        })
        self.assertEqual(gate["missing_required_phrases"], ())
        self.assertEqual(gate["present_forbidden_phrases"], ())

    def test_release_public_wording_preserves_gate_dependencies(self):
        gate = rt.validate_v1_5_release_public_wording_gate()

        self.assertTrue(gate["correctness_gate_complete"])
        self.assertTrue(gate["support_maturity_gate_complete"])
        self.assertTrue(gate["benchmark_evidence_gate_complete"])
        self.assertIn("standalone Embree+OptiX", gate["allowed_public_statement"])
        self.assertIn("14 included app contracts", gate["allowed_public_statement"])
        self.assertIn("no new whole-app speedup claim", gate["allowed_public_statement"])


if __name__ == "__main__":
    unittest.main()
