from __future__ import annotations

import json
import unittest

from scripts import goal5839_build_discovery_deviation_authority as deviations


class Goal5839DiscoveryDeviationAuthorityTest(unittest.TestCase):
    def test_stored_authority_rebuilds_byte_identically(self) -> None:
        expected = deviations.build_authority()
        stored = json.loads(deviations.OUTPUT_PATH.read_text(encoding="ascii"))
        deviations.validate_authority(stored)
        self.assertEqual(deviations._serialized(stored), deviations._serialized(expected))

    def test_order_nonconformance_is_not_hidden(self) -> None:
        authority = deviations.build_authority()
        row = authority["deviations"][0]
        self.assertEqual(row["id"], "D001_DISCOVERY_ORDER_NONCONFORMANCE")
        self.assertFalse(
            row["effect_assessment"]["fully_preregistered_execution_order_claim_allowed"]
        )

    def test_aborted_run_cannot_be_used_as_empty_search_result(self) -> None:
        authority = deviations.build_authority()
        row = authority["deviations"][1]
        self.assertFalse(row["observed"]["result_file_created"])
        self.assertFalse(row["effect_assessment"]["empty_results_inferred"])
        self.assertTrue(row["effect_assessment"]["query_attempts_repeated_by_repaired_run"])

    def test_repair_does_not_authorize_query_or_provider_substitution(self) -> None:
        authority = deviations.build_authority()
        continuation = authority["continuation_authority"]
        self.assertFalse(continuation["provider_substitution_allowed"])
        self.assertFalse(continuation["query_substitution_allowed"])
        self.assertFalse(authority["claim_boundary"]["paper_ready_result"])


if __name__ == "__main__":
    unittest.main()
