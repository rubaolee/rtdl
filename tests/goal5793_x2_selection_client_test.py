from __future__ import annotations

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from scripts import goal5793_x2_nist_synthetic_crypto as crypto
from scripts import goal5793_x2_offline_core as core
from scripts import goal5793_x2_selection_client as client


ROOT = Path(__file__).resolve().parents[1]


def _name(value: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, value)])


def _authority():
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    start, end = datetime(2026, 1, 1, tzinfo=timezone.utc), datetime(2030, 1, 1, tzinfo=timezone.utc)
    root_name, leaf_name = _name("X2 Test Root"), _name("X2 Test Leaf")
    root = (
        x509.CertificateBuilder().subject_name(root_name).issuer_name(root_name).public_key(root_key.public_key())
        .serial_number(41).not_valid_before(start).not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
        .add_extension(x509.KeyUsage(True, False, False, False, False, True, True, None, None), critical=True)
        .sign(root_key, hashes.SHA256())
    )
    leaf = (
        x509.CertificateBuilder().subject_name(leaf_name).issuer_name(root_name).public_key(leaf_key.public_key())
        .serial_number(42).not_valid_before(start).not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.KeyUsage(True, False, False, False, False, False, False, None, None), critical=True)
        .sign(root_key, hashes.SHA256())
    )
    root_pem = root.public_bytes(serialization.Encoding.PEM)
    leaf_pem = leaf.public_bytes(serialization.Encoding.PEM)
    pin = hashlib.sha256(root.public_bytes(serialization.Encoding.DER)).hexdigest()
    return root_pem, leaf_pem, pin, leaf, leaf_key


def _pulse(leaf, key, *, index: int, timestamp: str, output_seed: str, previous=None):
    local_hex = output_seed * 128 if len(output_seed) == 1 else output_seed
    local = bytes.fromhex(local_hex)
    values = [] if previous is None else [{"uri": previous["pulse"]["uri"], "type": "previous", "value": previous["pulse"]["outputValue"]}]
    pulse = {
        "uri": f"https://synthetic.invalid/chain/2/pulse/{index}", "version": "2.0", "cipherSuite": 0,
        "period": 60000, "certificateId": crypto.certificate_id(leaf), "chainIndex": 2, "pulseIndex": index,
        "timeStamp": timestamp, "localRandomValue": local.hex(),
        "external": {"sourceId": "3" * 128, "statusCode": 0, "value": "4" * 128},
        "listValues": values, "precommitmentValue": hashlib.sha512(local).hexdigest(), "statusCode": 0,
        "signatureValue": "", "outputValue": "0" * 128,
    }
    signature = key.sign(crypto.signed_pulse_bytes(pulse), padding.PKCS1v15(), hashes.SHA512())
    pulse["signatureValue"] = signature.hex()
    pulse["outputValue"] = crypto.synthetic_output_value(pulse, signature)
    return {"pulse": pulse}


def _fixture(triplet_count: int = 3):
    root_pem, leaf_pem, pin, leaf, key = _authority()
    previous = _pulse(leaf, key, index=100, timestamp="2027-01-01T00:00:00.000Z", output_seed="1")
    anchor = _pulse(leaf, key, index=101, timestamp="2027-01-01T00:01:00.000Z", output_seed="2", previous=previous)
    chain = []
    prior = anchor
    anchor_dt = datetime(2027, 1, 1, 0, 1, tzinfo=timezone.utc)
    for offset in range(1, 1441):
        timestamp = (anchor_dt + timedelta(minutes=offset)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
        seed = hashlib.sha512(f"goal5793-chain-{offset}".encode("ascii")).hexdigest()
        prior = _pulse(leaf, key, index=101 + offset, timestamp=timestamp, output_seed=seed, previous=prior)
        chain.append(prior)
    target = chain[-1]
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
    bundle = lambda response: {"response": response, "leaf_certificate_pem": leaf_pem, "root_certificate_pem": root_pem}
    return {
        "schema": "rtdl.goal5793.x2.synthetic_selection_fixture.v1", "mode": "OFFLINE_SYNTHETIC_FIXTURES_ONLY",
        "synthetic_fixture": True, "triplets": [[f"A{i}", f"B{i}", f"C{i}"] for i in range(triplet_count)],
        "base_inputs": base, "not_before_ms": core.parse_timestamp_ms("2027-01-01T00:00:30.000Z"),
        "trusted_root_sha256": pin, "previous": bundle(previous), "anchor": bundle(anchor),
        "target_leaf_certificate_pem": leaf_pem, "target_root_certificate_pem": root_pem,
        "target_chain_responses": chain,
        "target_attempts": [{"scheduled_offset_seconds": 0, "request_uri": f"{client.API_BASE}/pulse/time/{base['target_timestamp_ms']}", "response": target, "error": None}],
    }


class Goal5793X2SelectionClientTest(unittest.TestCase):
    def test_01_authenticated_synthetic_rehearsal_is_not_a_selection(self):
        receipt = client.rehearse_synthetic_selection(_fixture())
        self.assertEqual(receipt["pulse_authentication_count"], 1442)
        self.assertEqual(receipt["pulse_evidence"]["anchor_to_target_chain_pulse_count"], 1440)
        self.assertFalse(receipt["scientific_selection_made"])
        self.assertFalse(receipt["live_nist_acceptance_usable"])
        self.assertEqual(receipt["activity"]["network_calls"], 0)

    def test_02_next_closest_is_recorded_rejected_then_exact_same_uri_accepted(self):
        fixture = _fixture()
        wrong = copy.deepcopy(fixture["target_attempts"][0]["response"])
        wrong["pulse"]["timeStamp"] = "2027-01-02T00:02:00.000Z"
        exact = fixture["target_attempts"][0]
        fixture["target_attempts"] = [
            {"scheduled_offset_seconds": 0, "request_uri": exact["request_uri"], "response": wrong, "error": None},
            {"scheduled_offset_seconds": 15, "request_uri": exact["request_uri"], "response": exact["response"], "error": None},
        ]
        receipt = client.rehearse_synthetic_selection(fixture)
        self.assertEqual(receipt["target_attempt_audit"][0]["classification"], "NEXT_CLOSEST_OR_NONEXACT_REJECTED__SAME_TARGET_RETAINED")

    def test_03_target_uri_drift_rejected(self):
        fixture = _fixture()
        fixture["target_attempts"][0]["request_uri"] += "?alternate=true"
        with self.assertRaisesRegex(core.X2Error, "TARGET_REQUEST_URI_DRIFT"):
            client.rehearse_synthetic_selection(fixture)

    def test_04_pulse_frame_crossbind_drift_rejected(self):
        fixture = _fixture()
        fixture["base_inputs"]["target_output_value"] = "f" * 128
        with self.assertRaisesRegex(core.X2Error, "SELECTION_PULSE_FRAME_CROSSBIND_MISMATCH"):
            client.rehearse_synthetic_selection(fixture)

    def test_05_triplet_count_drift_rejected(self):
        fixture = _fixture()
        fixture["base_inputs"]["ordered_triplet_count"] += 1
        with self.assertRaisesRegex(core.X2Error, "SELECTION_TRIPLET_COUNT_CROSSBIND_MISMATCH"):
            client.rehearse_synthetic_selection(fixture)

    def test_06_zero_cardinality_makes_no_pulse_or_hash_request(self):
        fixture = _fixture(0)
        fixture["target_chain_responses"] = []
        receipt = client.rehearse_synthetic_selection(fixture)
        self.assertEqual(receipt["pulse_authentication_count"], 0)
        self.assertEqual(receipt["mapping_result"]["hash_evaluation_count"], 0)
        self.assertEqual(receipt["activity"]["live_beacon_requests"], 0)

    def test_07_middle_chain_link_mutation_is_rejected(self):
        fixture = _fixture()
        fixture["target_chain_responses"][700]["pulse"]["listValues"][0]["value"] = "f" * 128
        with self.assertRaisesRegex(core.X2Error, "TARGET_CHAIN_LINK_MISMATCH"):
            client.rehearse_synthetic_selection(fixture)


if __name__ == "__main__":
    unittest.main()
