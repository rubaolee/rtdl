import unittest

from scripts import goal1505_v1_5_4_optix_collect_k_evidence_summary as summary_script


class Goal1505V154OptixCollectKEvidenceSummaryTest(unittest.TestCase):
    def test_summary_validates_committed_optix_collect_k_artifacts(self) -> None:
        summary = summary_script.validate_summary(summary_script.build_summary())

        self.assertEqual(summary["goal"], "Goal1505")
        self.assertEqual(len(summary["source_artifacts"]), 5)
        self.assertTrue(
            all(artifact["measured_on_real_nvidia"] for artifact in summary["source_artifacts"])
        )

        scope = summary["evidence_scope"]
        self.assertEqual(scope["row_width2_fast_path_max_candidate_count"], 131072)
        self.assertTrue(scope["dynamic_row_width_validated"])
        self.assertTrue(scope["int64_max_pair_validated"])
        self.assertTrue(scope["overflow_fail_closed_validated"])
        self.assertTrue(any("Blackwell" in device for device in scope["measured_devices"]))
        self.assertTrue(any("Ada" in device for device in scope["measured_devices"]))

    def test_summary_keeps_all_public_claims_unauthorized(self) -> None:
        summary = summary_script.build_summary()

        for flag, value in summary["claim_authorization"].items():
            with self.subTest(flag=flag):
                self.assertFalse(value)
        self.assertIn("does not authorize public speedup wording", summary["claim_boundary"])
        self.assertIn("not a release action", summary_script.to_markdown(summary))

    def test_summary_rejects_claim_expansion(self) -> None:
        summary = summary_script.build_summary()
        summary["claim_authorization"]["stable_public_primitive_authorized"] = True

        with self.assertRaisesRegex(ValueError, "stable_public_primitive_authorized"):
            summary_script.validate_summary(summary)


if __name__ == "__main__":
    unittest.main()
