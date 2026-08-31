from __future__ import annotations

import base64
import copy
import gzip
import json
import re
import unittest

from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document
from scripts import goal5799_a1_build_post_self_review_repair as repair
from scripts import goal5799_a1_independent_verify_post_self_review_repair as independent


def _set_path(document, path, value):
    current = document
    for key in path[:-1]:
        current = current[key]
    current[path[-1]] = value


class Goal5799A1PostSelfReviewRepairTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        repair.verify_inputs()
        cls.contract = repair.build_contract()
        cls.registry = repair.build_registry_amendment()
        cls.bridge = repair.build_receipt_bridge()

    def _reseal_contract(self, document):
        semantic = {
            key: copy.deepcopy(value)
            for key, value in document.items()
            if key not in {"control_leaf_manifest", "contract_sha256"}
        }
        manifest = repair._control_manifest(semantic)
        document["control_leaf_manifest"] = {
            "scope": "every populated leaf in the semantic body excluding this manifest and the self-seal",
            "leaf_count": len(manifest),
            "non_decision_bearing_leaf_count": 0,
            "rows": manifest,
            "rows_sha256": repair.sha(canonical_json_bytes(manifest)),
        }
        document["contract_sha256"] = seal_document(
            document,
            seal_field="contract_sha256",
            domain=f"{repair.DOMAIN}.contract.v1",
            version=1,
        )

    def test_01_contract_manifest_covers_every_semantic_leaf(self) -> None:
        semantic = {
            key: value
            for key, value in self.contract.items()
            if key not in {"control_leaf_manifest", "contract_sha256"}
        }
        leaves = list(repair._walk_leaves(semantic))
        manifest = self.contract["control_leaf_manifest"]
        self.assertEqual(manifest["leaf_count"], len(leaves))
        self.assertEqual(manifest["non_decision_bearing_leaf_count"], 0)
        self.assertGreater(len(leaves), 150)
        repair.validate_contract_document(self.contract)

    def test_02_original_17_attacks_reject_even_after_manifest_rebuild_and_reseal(self) -> None:
        attacks = {
            "same_timer_boundaries_false": [("symmetry", "same_timer_boundaries"), False],
            "same_data_and_oracle_false": [("symmetry", "same_data_and_exact_oracle"), False],
            "postresult_optimization_allowed": [("symmetry", "forbid_per_arm_postresult_optimization"), False],
            "engineering_fields_arbitrary": [("symmetry", "arm_engineering_ledger_fields"), list("abcdefgh")],
            "ptx_identity_false": [("structural_cache_hit_assertions", "exact_ptx_identity"), False],
            "launch_identity_false": [("structural_cache_hit_assertions", "same_launch_and_synchronization_counts"), False],
            "phase_mutual_exclusion_false": [("phase_attribution", "mutually_exclusive_phases_required"), False],
            "residual_causal_guard_false": [("phase_attribution", "subtraction_residual_is_not_causal_attribution"), False],
            "unaccounted_may_drop": [("phase_attribution", "unaccounted_time_must_be_named_not_dropped"), False],
            "amortization_disabled": [("amortization", "publish_build_cold_absolute_times"), False],
            "diagnostic_label_disabled": [("publication", "every_diagnostic_number_prefixed_UNREGISTERED_DIAGNOSTIC"), False],
            "anonymity_substitution_allowed": [("anonymity", "one_gate_may_substitute_for_the_other"), True],
            "goal5803_cutoff_moved": [("goal5803_descope", "decision_cutoff"), "2099-01-01T00:00:00Z"],
            "v11_withdrawal_erased": [("publication", "v11_withdrawal_sentence"), ""],
            "steady_bound_loosened": [("comparative_gates", "STEADY_E2E", "decision"), "95_PERCENT_CI_UPPER_BOUND_LE_9.99"],
            "deployment_bound_loosened": [("comparative_gates", "DEPLOYMENT_COLD", "decision"), "95_PERCENT_CI_UPPER_BOUND_LE_9.99"],
            "prepare_bound_loosened": [("comparative_gates", "PREPARE", "decision"), "95_PERCENT_CI_UPPER_BOUND_LE_9.99"],
        }
        rejected = 0
        for _, (path, value) in attacks.items():
            mutated = copy.deepcopy(self.contract)
            _set_path(mutated, path, value)
            self._reseal_contract(mutated)
            with self.assertRaises(repair.RepairError):
                repair.validate_contract_document(mutated)
            rejected += 1
        self.assertEqual(rejected, 17)

    def test_03_every_semantic_leaf_mutation_changes_whole_file_identity(self) -> None:
        original = repair._payload(self.contract)
        original_sha = repair.sha(original)
        semantic = {
            key: value
            for key, value in self.contract.items()
            if key not in {"control_leaf_manifest", "contract_sha256"}
        }
        for path, value in repair._walk_leaves(semantic):
            mutated = copy.deepcopy(self.contract)
            if isinstance(value, bool):
                replacement = not value
            elif isinstance(value, int):
                replacement = value + 1
            elif isinstance(value, float):
                replacement = value + 0.125
            elif value is None:
                replacement = "MUTATED"
            else:
                replacement = str(value) + "__MUTATED"
            _set_path(mutated, path, replacement)
            self._reseal_contract(mutated)
            self.assertNotEqual(repair.sha(repair._payload(mutated)), original_sha, repair._pointer(path))

    def test_04_registry_counts_and_claim_boundary_are_corrected(self) -> None:
        self.assertEqual(
            self.registry["counts"],
            {
                "provider_records": 200,
                "selection_eligible_records": 0,
                "alias_components": 194,
                "multi_record_alias_components": 5,
                "records_in_multi_record_alias_components": 11,
                "terminal_pdf_conservative_alias_rows": 2,
            },
        )
        self.assertEqual(
            self.registry["terminology"]["semantic_unique_scientific_work_count"],
            "UNKNOWN__NOT_INFERRED_FROM_PROVIDER_RECORD_COUNT",
        )
        self.assertTrue(all(row["selection_eligible"] is False for row in self.registry["rows"]))

    def test_05_terminal_pdf_and_shared_fallback_aliases_are_explicit(self) -> None:
        terminal_pdf = []
        for row in self.registry["rows"]:
            terminal_pdf.extend(
                alias
                for alias in row["matching_aliases"]
                if alias["kind"] == "doi_conservative_terminal_pdf_stripped"
            )
        self.assertEqual(
            sorted(alias["value"] for alias in terminal_pdf),
            ["10.1051/0004-6361/201834962", "10.1051/0004-6361/201936150"],
        )
        self.assertEqual(sum(not component["is_single_record_component"] for component in self.registry["components"]), 5)

    def test_06_bridge_contains_144_exact_raw_receipts_and_rebuilds_ledger(self) -> None:
        self.assertEqual(self.bridge["scope"]["raw_receipt_count"], 144)
        compressed = base64.b64decode(self.bridge["compressed_container_base64"], validate=True)
        self.assertEqual(repair.sha(compressed), self.bridge["compression"]["compressed_sha256"])
        container_payload = gzip.decompress(compressed)
        self.assertEqual(len(container_payload), self.bridge["compression"]["uncompressed_bytes"])
        self.assertEqual(repair.sha(container_payload), self.bridge["compression"]["uncompressed_sha256"])
        container = json.loads(container_payload)
        entries = container["entries"]
        self.assertEqual(
            [
                {"member": entry["member"], "raw_bytes": entry["raw_bytes"], "raw_sha256": entry["raw_sha256"]}
                for entry in entries
            ],
            self.bridge["entry_manifest"],
        )
        rebuilt = []
        for entry in entries:
            raw = base64.b64decode(entry["raw_base64"], validate=True)
            self.assertEqual(len(raw), entry["raw_bytes"])
            self.assertEqual(repair.sha(raw), entry["raw_sha256"])
            rebuilt.append(repair._phase_row(json.loads(raw)))
        ledger = json.loads(repair.V1_LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(rebuilt, ledger["rows"])

    def test_07_bridge_byte_attack_rejects_hash_recount(self) -> None:
        compressed = base64.b64decode(self.bridge["compressed_container_base64"], validate=True)
        container = json.loads(gzip.decompress(compressed))
        entry = copy.deepcopy(container["entries"][0])
        raw = bytearray(base64.b64decode(entry["raw_base64"], validate=True))
        raw[0] ^= 1
        self.assertNotEqual(repair.sha(bytes(raw)), entry["raw_sha256"])

    def test_08_all_formal_and_external_authorizations_remain_false(self) -> None:
        authorization = self.contract["authorization"]
        for key in (
            "goal5802_formal_worker_zero",
            "goal5802_pod_gpu_timing",
            "goal5803",
            "network_provider_query",
            "external_contact_or_participant",
            "submission_or_public_claim",
        ):
            self.assertFalse(authorization[key])

    def test_09_stored_core_and_closeout_if_present_are_byte_exact(self) -> None:
        if repair.CONTRACT.exists():
            self.assertEqual(repair.verify_core_stored()["status"], "CORE_POSTWRITE_VERIFY_PASS")
        if repair.CFR.exists():
            self.assertEqual(repair.verify_closeout_stored()["status"], "CLOSEOUT_POSTWRITE_VERIFY_PASS")
            cfr = repair.CFR.read_text(encoding="utf-8", errors="strict")
            self.assertTrue(cfr.startswith("# SEND ONLY THIS FILE"))
            self.assertIn(repair.PINS[repair.PREDECESSOR_CFR][1], cfr)

    def test_10_independent_verifier_rebuilds_all_three_repairs(self) -> None:
        verification = independent.build_verification(
            "1e5de461860713c70885b88c082bcb97ba0eb6abb451897ae44263ee3bd46d08",
            "87e8e02b48867cdfac15f113eb27cf1c11a7ed042971609e5a46aafda93838fb",
            "f21aadf5c1596b97db5ffe7001f555f8ddf443e1a15b569d6cc1eb7d71946ad2",
        )
        self.assertEqual(
            verification["status"],
            "PASS__INDEPENDENT_POST_SELF_REVIEW_REPAIR_VERIFICATION",
        )
        self.assertFalse(verification["imports_repair_builder"])
        self.assertEqual(verification["contract"]["semantic_leaf_count"], 170)
        self.assertEqual(verification["registry"]["alias_components"], 194)
        self.assertEqual(verification["receipt_bridge"]["raw_receipts"], 144)

    def test_11_sole_cfr_recovers_nested_predecessor_and_all_repair_authorities(self) -> None:
        if not repair.CFR.exists():
            self.skipTest("closeout CFR has not been written")
        text = repair.CFR.read_text(encoding="utf-8", errors="strict")
        checks = [
            ("predecessor Goal5799 sole CFR — superseded for sending", repair.PREDECESSOR_CFR),
            ("repaired exact-authority performance/evidence contract", repair.CONTRACT),
            ("exposure registry alias/count amendment", repair.REGISTRY_AMENDMENT),
            ("144-receipt byte bridge", repair.RECEIPT_BRIDGE),
            ("independent verification", repair.INDEPENDENT_VERIFICATION),
        ]
        for title, path in checks:
            start = text.index("## Embedded: " + title)
            match = re.search(r"(?m)^(`{8,})[^\n]*\n", text[start:])
            self.assertIsNotNone(match)
            fence = match.group(1)
            body_start = start + match.end()
            body_end = text.index(fence, body_start)
            self.assertEqual(text[body_start:body_end].encode("utf-8"), path.read_bytes())
        predecessor_start = text.index("## Embedded: predecessor Goal5799 sole CFR")
        predecessor_fence = re.search(r"(?m)^(`{8,})[^\n]*\n", text[predecessor_start:]).group(1)
        self.assertGreater(len(predecessor_fence), 8)


if __name__ == "__main__":
    unittest.main()
