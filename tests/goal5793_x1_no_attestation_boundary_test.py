from __future__ import annotations

from copy import deepcopy
import unittest

from scripts import goal5793_x1_build_no_attestation_boundary as boundary
from scripts.goal5793_x1_canonical import seal_document


def reseal(value: dict) -> dict:
    value["boundary_sha256"] = seal_document(
        value,
        seal_field="boundary_sha256",
        domain="rtdl.goal5793.x1.no_owner_memory_attestation_boundary",
        version=1,
    )
    return value


class NoAttestationBoundaryTest(unittest.TestCase):
    def test_exact_boundary_validates(self):
        value = boundary.build()
        self.assertEqual(boundary.validate(value), value)
        self.assertFalse(value["substitution_rules"]["owner_memory_attestation_provided"])
        self.assertTrue(value["substitution_rules"]["later_recalled_or_discovered_pre_x1_exposure_terminates_single_expansion"])

    def test_resealed_unseen_claim_escalation_rejected(self):
        value = deepcopy(boundary.build())
        value["substitution_rules"]["unseen_blind_or_held_out_claim_authorized"] = True
        with self.assertRaisesRegex(boundary.BoundaryError, "substitution_rules"):
            boundary.validate(reseal(value))

    def test_resealed_replacement_rescue_rejected(self):
        value = deepcopy(boundary.build())
        value["substitution_rules"]["replacement_after_late_exposure_discovery"] = True
        with self.assertRaisesRegex(boundary.BoundaryError, "substitution_rules"):
            boundary.validate(reseal(value))

    def test_resealed_x2_authorization_rejected(self):
        value = deepcopy(boundary.build())
        value["authorization"]["x2_search"] = True
        with self.assertRaisesRegex(boundary.BoundaryError, "authorization"):
            boundary.validate(reseal(value))


if __name__ == "__main__":
    unittest.main()
