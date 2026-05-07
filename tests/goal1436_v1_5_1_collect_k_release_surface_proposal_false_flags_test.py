import unittest
from unittest import mock

import rtdsl as rt
from rtdsl import v1_5_1_collect_k_bounded as collect_k


class Goal1436V151CollectKReleaseSurfaceProposalFalseFlagsTest(unittest.TestCase):
    def test_release_surface_proposal_explicitly_blocks_whole_app_speedup_claim(self) -> None:
        proposal = rt.validate_v1_5_1_collect_k_bounded_release_surface_proposal()

        self.assertIs(proposal["whole_app_speedup_claim_authorized_by_this_proposal"], False)

    def test_release_surface_proposal_validator_rejects_whole_app_speedup_claim_flag(self) -> None:
        original = collect_k.v1_5_1_collect_k_bounded_release_surface_proposal

        def tampered() -> dict[str, object]:
            proposal = original()
            proposal["whole_app_speedup_claim_authorized_by_this_proposal"] = True
            return proposal

        with mock.patch.object(
            collect_k,
            "v1_5_1_collect_k_bounded_release_surface_proposal",
            tampered,
        ):
            with self.assertRaisesRegex(ValueError, "whole_app_speedup_claim_authorized_by_this_proposal"):
                collect_k.validate_v1_5_1_collect_k_bounded_release_surface_proposal()


if __name__ == "__main__":
    unittest.main()
