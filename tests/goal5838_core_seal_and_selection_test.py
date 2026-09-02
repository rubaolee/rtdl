from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import unittest
from unittest import mock

from scripts import goal5838_freeze_generic_core as freeze
from scripts import goal5838_select_challenge as select


ROOT = Path(__file__).resolve().parents[1]


def _pulse(index: int, timestamp: str, local: str, previous=None) -> dict:
    output = f"{index:0128x}"
    list_values = [
        {
            "uri": "https://beacon.nist.gov/beacon/2.0/chain/2/pulse/1"
            if previous is None else previous["pulse"]["uri"],
            "type": "previous",
            "value": "00" * 64
            if previous is None else previous["pulse"]["outputValue"],
        },
        *[
            {"uri": f"https://example.invalid/{kind}", "type": kind, "value": "00" * 64}
            for kind in ("hour", "day", "month", "year")
        ],
    ]
    return {
        "pulse": {
            "uri": f"https://beacon.nist.gov/beacon/2.0/chain/2/pulse/{index}",
            "version": "2.0",
            "cipherSuite": 0,
            "period": 60000,
            "certificateId": freeze.PINNED_CERTIFICATE_ID,
            "chainIndex": 2,
            "pulseIndex": index,
            "timeStamp": timestamp,
            "localRandomValue": local,
            "external": {"sourceId": "00" * 64, "statusCode": 0, "value": "00" * 64},
            "listValues": list_values,
            "precommitmentValue": "00" * 64,
            "statusCode": 0,
            "signatureValue": "00" * 512,
            "outputValue": output,
        }
    }


class Goal5838CoreSealAndSelectionTest(unittest.TestCase):
    def test_01_candidate_table_is_complete_sorted_and_unselected(self) -> None:
        table = freeze.build_challenge_table()
        self.assertEqual(table["eligible_candidate_count"], 10)
        ids = [row["candidate_id"] for row in table["eligible_candidates"]]
        self.assertEqual(ids, sorted(ids, key=lambda value: value.encode("utf-8")))
        self.assertEqual([row["stable_index"] for row in table["eligible_candidates"]], list(range(10)))
        self.assertIsNone(table["selection"]["selected_candidate_id"])
        self.assertEqual(len(table["excluded_exact_preexisting_topologies"]), 2)

    def test_02_table_mutation_breaks_seal(self) -> None:
        table = freeze.build_challenge_table()
        original = table["challenge_table_sha256"]
        table["eligible_candidates"][0]["continuation"] = "attacked"
        self.assertNotEqual(
            original,
            freeze.seal_document(
                table,
                "challenge_table_sha256",
                "rtdl.goal5838.prospective_challenge_table.v1",
            ),
        )

    def test_03_selection_mapping_is_deterministic_and_binds_core(self) -> None:
        first = select.select_index(
            table_sha256="11" * 32,
            core_seal_sha256="22" * 32,
            local_random_value="33" * 64,
            candidate_count=10,
        )
        repeat = select.select_index(
            table_sha256="11" * 32,
            core_seal_sha256="22" * 32,
            local_random_value="33" * 64,
            candidate_count=10,
        )
        changed = select.select_index(
            table_sha256="11" * 32,
            core_seal_sha256="23" * 32,
            local_random_value="33" * 64,
            candidate_count=10,
        )
        self.assertEqual(first, repeat)
        self.assertNotEqual(first["digest_sha256"], changed["digest_sha256"])

    def test_04_wrong_or_next_closest_timestamp_is_rejected(self) -> None:
        response = _pulse(100, "2026-09-02T19:01:00.000Z", "44" * 64)
        with self.assertRaisesRegex(select.Goal5838SelectionError, "wrong timestamp"):
            select.verify_signed_pulse(
                response,
                b"invalid",
                expected_timestamp_ms=freeze.TARGET_TIMESTAMP_MS,
            )

    def test_05_precommitment_and_previous_link_are_enforced(self) -> None:
        target_random = "55" * 64
        previous = _pulse(100, "2026-09-02T18:59:00.000Z", "44" * 64)
        target = _pulse(101, "2026-09-02T19:00:00.000Z", target_random, previous)
        previous["pulse"]["precommitmentValue"] = hashlib.sha512(
            bytes.fromhex(target_random)
        ).hexdigest()
        select.verify_adjacent_precommitment(previous, target)
        attacked = copy.deepcopy(target)
        attacked["pulse"]["localRandomValue"] = "56" * 64
        with self.assertRaisesRegex(select.Goal5838SelectionError, "precommitment"):
            select.verify_adjacent_precommitment(previous, attacked)

    def test_06_signature_failure_is_fail_closed(self) -> None:
        response = _pulse(100, "2026-09-02T19:00:00.000Z", "44" * 64)
        fake_der = b"not-a-certificate"
        with mock.patch.object(select.ssl, "PEM_cert_to_DER_cert", return_value=fake_der):
            with self.assertRaisesRegex(select.Goal5838SelectionError, "DER identity"):
                select.verify_signed_pulse(
                    response,
                    b"fake pem",
                    expected_timestamp_ms=freeze.TARGET_TIMESTAMP_MS,
                )

    def test_07_stored_seal_verifier_passes_after_generation(self) -> None:
        if freeze.SEAL_PATH.exists() and freeze.TABLE_PATH.exists():
            receipt = freeze.verify_stored()
            self.assertEqual(receipt["frozen_core_file_count"], 3)
            self.assertEqual(receipt["selected_candidate_count"], 0)

    def test_08_protocol_freezes_one_exact_target_and_no_fallback(self) -> None:
        protocol = freeze.PROTOCOL_PATH.read_text(encoding="utf-8")
        self.assertIn(str(freeze.TARGET_TIMESTAMP_MS), protocol)
        self.assertIn(freeze.PINNED_CERTIFICATE_ID, protocol)
        self.assertIn("never replaced", protocol)
        source = (ROOT / "scripts/goal5838_select_challenge.py").read_text(encoding="utf-8")
        self.assertNotIn("pulse/last", source)
        self.assertNotIn("time/next", source)

    def test_09_stored_seal_rejects_selection_client_drift(self) -> None:
        if not freeze.SEAL_PATH.exists() or not freeze.TABLE_PATH.exists():
            self.skipTest("seal not generated yet")
        real_sha = freeze.sha256_path

        def attacked(relative):
            if str(relative) == "scripts/goal5838_select_challenge.py":
                return "00" * 32
            return real_sha(relative)

        with mock.patch.object(freeze, "sha256_path", side_effect=attacked):
            with self.assertRaisesRegex(freeze.Goal5838SealError, "selection client drift"):
                freeze.verify_stored()


if __name__ == "__main__":
    unittest.main()
