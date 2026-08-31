from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import inspect
import json
from pathlib import Path
import unittest

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from scripts import goal5793_x2_nist_normative_selection_client as client
from scripts import goal5793_x2_nist_normative_verifier as verifier
from scripts import goal5793_x2_offline_core as core
from tests.goal5793_x2_nist_normative_verifier_test import _certificates, _make_pulse


ROOT = Path(__file__).resolve().parents[1]


def _resign(response: dict, key) -> None:
    pulse = response["pulse"]
    signature = key.sign(verifier.serialize_signed_fields(pulse), padding.PKCS1v15(), hashes.SHA512())
    pulse["signatureValue"] = signature.hex()
    pulse["outputValue"] = verifier.recompute_output_value(pulse)


def _fixture(triplet_count: int = 3):
    root_pem, leaf_pem, leaf_key = _certificates()
    trust = verifier.build_synthetic_trust_bundle(root_pem)
    anchor_dt = datetime(2027, 1, 1, 0, 1, tzinfo=timezone.utc)
    previous = _make_pulse(
        index=100,
        timestamp_ms=core.parse_timestamp_ms("2027-01-01T00:00:00.000Z"),
        local_byte=1,
        next_local_byte=2,
        leaf_pem=leaf_pem,
        leaf_key=leaf_key,
        previous=None,
    )
    anchor = _make_pulse(
        index=101,
        timestamp_ms=core.parse_timestamp_ms("2027-01-01T00:01:00.000Z"),
        local_byte=2,
        next_local_byte=3,
        leaf_pem=leaf_pem,
        leaf_key=leaf_key,
        previous=previous,
    )
    chain = []
    prior = anchor
    for offset in range(1, 1441):
        stamp = anchor_dt + timedelta(minutes=offset)
        prior = _make_pulse(
            index=101 + offset,
            timestamp_ms=int(stamp.timestamp() * 1000),
            local_byte=(2 + offset) % 256,
            next_local_byte=(3 + offset) % 256,
            leaf_pem=leaf_pem,
            leaf_key=leaf_key,
            previous=prior,
        )
        chain.append({"response": prior, "leaf_certificate_pem": leaf_pem})
    target = chain[-1]["response"]
    base = dict(json.loads((ROOT / core.S0_PROTOCOL_PATH).read_text(encoding="utf-8"))["deferred_entropy"]["known_answer_test"]["inputs"])
    base.pop("counter")
    base.update(
        ordered_triplet_count=triplet_count,
        anchor_chain_index=2,
        anchor_pulse_index=101,
        anchor_timestamp_ms=core.parse_timestamp_ms("2027-01-01T00:01:00.000Z"),
        anchor_certificate_id=anchor["pulse"]["certificateId"],
        anchor_output_value=anchor["pulse"]["outputValue"],
        target_chain_index=2,
        target_pulse_index=1541,
        target_timestamp_ms=core.parse_timestamp_ms("2027-01-02T00:01:00.000Z"),
        target_certificate_id=target["pulse"]["certificateId"],
        target_output_value=target["pulse"]["outputValue"],
    )
    request_uri = f"{client.API_BASE}/pulse/time/{base['target_timestamp_ms']}"
    bundle = lambda response: {"response": response, "leaf_certificate_pem": leaf_pem}
    return {
        "fixture": {
            "schema": "rtdl.goal5793.x2.nistir_normative_offline_selection_fixture.v1",
            "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
            "synthetic_fixture": True,
            "triplets": [[f"A{i}", f"B{i}", f"C{i}"] for i in range(triplet_count)],
            "base_inputs": base,
            "not_before_ms": core.parse_timestamp_ms("2027-01-01T00:00:30.000Z"),
            "root_certificate_pem": root_pem,
            "trust_bundle": trust,
            "previous": bundle(previous),
            "anchor": bundle(anchor),
            "target_chain_bundles": chain,
            "target_attempts": [
                {"scheduled_offset_seconds": 0, "request_uri": request_uri, "response": target, "error": None}
            ],
        },
        "leaf_key": leaf_key,
    }


class Goal5793X2NistNormativeSelectionClientTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        built = _fixture()
        cls.fixture = built["fixture"]
        cls.leaf_key = built["leaf_key"]

    def test_01_all_1442_pulses_are_normatively_authenticated_before_mapping(self) -> None:
        receipt = client.rehearse_normative_offline_selection(
            self.fixture,
            trusted_trust_bundle_sha256=self.fixture["trust_bundle"]["trust_bundle_sha256"],
        )
        self.assertEqual(receipt["pulse_authentication_count"], 1442)
        self.assertEqual(receipt["pulse_evidence"]["anchor_to_target_chain_pulse_count"], 1440)
        self.assertTrue(receipt["pulse_evidence"]["every_intermediate_signature_and_output_verified"])
        self.assertTrue(receipt["pulse_evidence"]["every_adjacent_previous_and_precommitment_link_verified"])
        self.assertFalse(receipt["scientific_selection_made"])
        self.assertEqual(receipt["activity"]["network_calls"], 0)

    def test_02_resigned_middle_chain_link_attack_fails(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        attacked = fixture["target_chain_bundles"][700]["response"]
        attacked["pulse"]["listValues"][0]["value"] = "ff" * 64
        _resign(attacked, self.leaf_key)
        with self.assertRaisesRegex(core.X2Error, "NISTIR_PREVIOUS_OUTPUT_LINK_MISMATCH"):
            client.rehearse_normative_offline_selection(
                fixture,
                trusted_trust_bundle_sha256=self.fixture["trust_bundle"]["trust_bundle_sha256"],
            )

    def test_03_next_closest_is_rejected_and_same_exact_uri_retained(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        exact = fixture["target_attempts"][0]
        wrong = copy.deepcopy(exact["response"])
        wrong["pulse"]["timeStamp"] = "2027-01-02T00:02:00.000Z"
        fixture["target_attempts"] = [
            {"scheduled_offset_seconds": 0, "request_uri": exact["request_uri"], "response": wrong, "error": None},
            {"scheduled_offset_seconds": 15, "request_uri": exact["request_uri"], "response": exact["response"], "error": None},
        ]
        receipt = client.rehearse_normative_offline_selection(
            fixture,
            trusted_trust_bundle_sha256=self.fixture["trust_bundle"]["trust_bundle_sha256"],
        )
        self.assertEqual(receipt["target_attempt_audit"][0]["classification"], "NEXT_CLOSEST_OR_NONEXACT_REJECTED__SAME_TARGET_RETAINED")

    def test_04_zero_cardinality_performs_no_authentication_or_hash(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["triplets"] = []
        fixture["base_inputs"]["ordered_triplet_count"] = 0
        fixture["target_chain_bundles"] = []
        receipt = client.rehearse_normative_offline_selection(
            fixture,
            trusted_trust_bundle_sha256=self.fixture["trust_bundle"]["trust_bundle_sha256"],
        )
        self.assertEqual(receipt["pulse_authentication_count"], 0)
        self.assertEqual(receipt["mapping_result"]["hash_evaluation_count"], 0)

    def test_05_client_is_offline_and_uses_shared_canonical_and_normative_verifier(self) -> None:
        source = inspect.getsource(client)
        self.assertIn("goal5793_x1_canonical", source)
        self.assertIn("goal5793_x2_nist_normative_verifier", source)
        for token in ("requests", "urllib", "http.client", "socket", "subprocess", "paramiko"):
            self.assertNotIn(f"import {token}", source)


if __name__ == "__main__":
    unittest.main()
