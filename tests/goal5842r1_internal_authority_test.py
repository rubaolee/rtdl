from __future__ import annotations

import copy
import unittest

from scripts import goal5842r1_build_internal_authority as authority


class Goal5842R1InternalAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rebuilt = authority.build_authority()

    def test_stored_authority_rebuilds_exactly(self) -> None:
        stored = authority._load(authority.AUTHORITY_PATH)
        self.assertEqual(stored, self.rebuilt)
        self.assertEqual(stored["authority_sha256"], authority._authority_seal(stored))

    def test_completion_is_implementation_bounded(self) -> None:
        self.assertEqual(
            self.rebuilt["status"],
            "PASS__GOAL5842R1_INTERNAL_IMPLEMENTATION_REPAIR_COMPLETE__"
            "FRESH_FAIR_BASELINE_AND_EXTERNAL_REVIEW_PENDING",
        )
        completion = self.rebuilt["completion"]
        self.assertEqual(completion["accepted_complete_repeat_count"], 3)
        self.assertTrue(completion["all_complete_repeats_exact_oracle"])
        self.assertTrue(completion["all_complete_repeats_one_true_optix_launch"])
        self.assertFalse(completion["completion_depends_on_performance_threshold"])

    def test_claim_blockers_remain_explicit(self) -> None:
        boundary = self.rebuilt["claim_boundary"]
        self.assertTrue(boundary["goal5842r1_internal_implementation_repair_complete"])
        self.assertFalse(boundary["goal5842_v12_modified"])
        for name in (
            "fresh_fair_direct_pyoptix_rtdl_baseline_complete",
            "second_hardware_generation_r1_replication_complete",
            "external_review_or_consensus",
            "public_performance_claim_authorized",
            "manuscript_performance_wording_authorized",
            "human_authoring_evidence_complete",
            "hardware_independent_timing_claimed",
            "arbitrary_application_performance_claimed",
            "private_audit_bypass_supported",
        ):
            self.assertIs(boundary[name], False, name)

    def test_authority_seal_rejects_semantic_drift(self) -> None:
        changed = copy.deepcopy(self.rebuilt)
        changed["completion"]["accepted_complete_repeat_count"] = 2
        self.assertNotEqual(
            changed["authority_sha256"], authority._authority_seal(changed)
        )


if __name__ == "__main__":
    unittest.main()
