from __future__ import annotations

import copy
from pathlib import Path
import tempfile
import unittest

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x3_build_provider_search_preaction as preaction
from scripts import goal5793_x3_capture_provider_search as capture
from scripts import goal5793_x3_provider_search_authority as authority


class Goal5793X3ProviderSearchPreactionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.document = preaction.build_authority()

    def test_01_deterministic_exact_seal(self) -> None:
        self.assertEqual(self.document, preaction.build_authority())
        self.assertEqual(
            self.document["preaction_authority_sha256"],
            seal_document(self.document, seal_field="preaction_authority_sha256", domain=preaction.DOMAIN, version=1),
        )

    def test_02_exact_schedule_is_complete(self) -> None:
        schedule = self.document["schedule"]
        self.assertEqual(schedule["provider_order"], list(core.PROVIDER_ORDER))
        self.assertEqual(schedule["term_order"], list(core.TERMS))
        self.assertEqual(schedule["query_count"], 22)
        self.assertEqual(schedule["retry_delay_seconds_including_initial"], [0, 3, 6, 12, 24, 48])
        self.assertFalse(schedule["redirects_followed"])
        self.assertFalse(schedule["second_query_round_or_rerun_allowed"])

    def test_03_only_exact_single_expansion_is_authorized(self) -> None:
        authorization = self.document["authorization"]
        self.assertEqual([key for key, value in authorization.items() if value], ["execute_exact_single_provider_expansion_once"])
        self.assertEqual(self.document["preaction_observation"]["live_provider_call_count"], 0)

    def test_04_source_or_policy_mutation_changes_seal(self) -> None:
        changed = copy.deepcopy(self.document)
        changed["preaction_authority_sha256"] = ""
        changed["schedule"]["term_order"][0] = "convenient result"
        self.assertNotEqual(
            seal_document(changed, seal_field="preaction_authority_sha256", domain=preaction.DOMAIN, version=1),
            self.document["preaction_authority_sha256"],
        )

    def test_05_coordinated_reseal_cannot_drop_required_source_or_predecessor(self) -> None:
        for field in ("predecessors", "implementation_and_tests"):
            changed = copy.deepcopy(self.document)
            changed[field].pop()
            changed["preaction_authority_sha256"] = seal_document(
                changed, seal_field="preaction_authority_sha256", domain=preaction.DOMAIN, version=1
            )
            with tempfile.TemporaryDirectory(prefix="goal5793_x3_preaction_attack_") as temp:
                path = Path(temp) / "authority.json"
                path.write_bytes(canonical_json_bytes(changed) + b"\n")
                with self.assertRaisesRegex(authority.X3SearchError, "PREACTION_.*_SET_MISMATCH"):
                    capture._verify_preaction(path)


if __name__ == "__main__":
    unittest.main()
