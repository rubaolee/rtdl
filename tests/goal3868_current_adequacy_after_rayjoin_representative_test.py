from __future__ import annotations

import unittest

import rtdsl as rt


class Goal3868CurrentAdequacyAfterRayJoinRepresentativeTest(unittest.TestCase):
    def test_spatial_rayjoin_adequacy_cites_representative_scale_row(self) -> None:
        spatial = {row["app"]: row for row in rt.current_benchmark_adequacy()}["spatial_rayjoin"]
        self.assertIn("Goal3866", spatial["evidence_refs"])
        self.assertIn("Goal3867", spatial["evidence_refs"])
        self.assertIn("Goal3936", spatial["evidence_refs"])
        self.assertIn("current all-app scale row", spatial["current_performance_reading"])
        self.assertIn("source_dirty is empty", spatial["current_performance_reading"])
        self.assertIn("0.155315ms/request", spatial["current_performance_reading"])
        self.assertIn("252.436x/202.372x", spatial["current_performance_reading"])
        self.assertIn("clean current", spatial["current_recommended_path"])
        self.assertIn("confirmed by Goal3936", spatial["next_generic_runtime_action"])
        self.assertFalse(spatial["public_speedup_claim_authorized"])
        self.assertFalse(spatial["paper_reproduction_claim_authorized"])

    def test_current_adequacy_validation_still_passes_without_authorizing_claims(self) -> None:
        validation = rt.validate_current_benchmark_adequacy()
        self.assertEqual(validation["status"], "accept")
        self.assertEqual(validation["errors"], ())
        summary = rt.summarize_current_benchmark_adequacy()
        self.assertEqual(summary["app_count"], 10)
        self.assertFalse(summary["release_authorized"])
        self.assertFalse(summary["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
