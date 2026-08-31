from __future__ import annotations

import copy
import hashlib
import inspect
import struct
import unittest
from datetime import datetime, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from scripts import goal5793_x2_nist_normative_verifier as verifier
from scripts.goal5793_x2_offline_core import X2Error


ROOT = Path(__file__).resolve().parents[1]
ZERO512 = "0" * 128


def _independent_nistir_signed_serialization(pulse: dict) -> bytes:
    """Test-side recount that does not call the product serialization helpers."""

    lp = lambda payload: struct.pack(">Q", len(payload)) + payload
    hash_field = lambda value: lp(bytes.fromhex(value))
    external = pulse["external"]
    indexed = {row["type"]: row for row in pulse["listValues"]}
    return b"".join(
        [
            lp(pulse["uri"].encode("utf-8")),
            lp(pulse["version"].encode("utf-8")),
            struct.pack(">I", pulse["cipherSuite"]),
            struct.pack(">I", pulse["period"]),
            hash_field(pulse["certificateId"]),
            struct.pack(">Q", pulse["chainIndex"]),
            struct.pack(">Q", pulse["pulseIndex"]),
            lp(pulse["timeStamp"].encode("utf-8")),
            hash_field(pulse["localRandomValue"]),
            hash_field(external["sourceId"]),
            struct.pack(">Q", external["statusCode"]),
            hash_field(external["value"]),
            *(hash_field(indexed[kind]["value"]) for kind in verifier.LIST_VALUE_ORDER),
            hash_field(pulse["precommitmentValue"]),
            struct.pack(">I", pulse["statusCode"]),
        ]
    )


def _certificates() -> tuple[bytes, bytes, rsa.RSAPrivateKey]:
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    root_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Goal5793 X2 Normative Synthetic Root")])
    leaf_name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "Goal5793 X2 Normative Synthetic Leaf")])
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2030, 1, 1, tzinfo=timezone.utc)
    root = (
        x509.CertificateBuilder()
        .subject_name(root_name)
        .issuer_name(root_name)
        .public_key(root_key.public_key())
        .serial_number(101)
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=True,
                crl_sign=True,
                encipher_only=None,
                decipher_only=None,
            ),
            critical=True,
        )
        .sign(root_key, hashes.SHA256())
    )
    leaf = (
        x509.CertificateBuilder()
        .subject_name(leaf_name)
        .issuer_name(root_name)
        .public_key(leaf_key.public_key())
        .serial_number(102)
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=True,
                content_commitment=False,
                key_encipherment=False,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=None,
                decipher_only=None,
            ),
            critical=True,
        )
        .sign(root_key, hashes.SHA256())
    )
    return (
        root.public_bytes(serialization.Encoding.PEM),
        leaf.public_bytes(serialization.Encoding.PEM),
        leaf_key,
    )


def _make_pulse(
    *,
    index: int,
    timestamp_ms: int,
    local_byte: int,
    next_local_byte: int,
    leaf_pem: bytes,
    leaf_key: rsa.RSAPrivateKey,
    previous: dict | None,
) -> dict:
    previous_uri = previous["pulse"]["uri"] if previous else "https://synthetic.invalid/chain/2/pulse/0"
    previous_output = previous["pulse"]["outputValue"] if previous else ZERO512
    local_random = f"{local_byte:02x}" * 64
    next_random = bytes([next_local_byte]) * 64
    list_values = [
        {"uri": previous_uri, "type": "previous", "value": previous_output},
        {"uri": previous_uri, "type": "hour", "value": ZERO512},
        {"uri": previous_uri, "type": "day", "value": ZERO512},
        {"uri": previous_uri, "type": "month", "value": ZERO512},
        {"uri": previous_uri, "type": "year", "value": ZERO512},
    ]
    pulse = {
        "uri": f"https://synthetic.invalid/chain/2/pulse/{index}",
        "version": "2.0",
        "cipherSuite": 0,
        "period": 60000,
        "certificateId": verifier.pem_certificate_id(leaf_pem),
        "chainIndex": 2,
        "pulseIndex": index,
        "timeStamp": datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
        "localRandomValue": local_random,
        "external": {"sourceId": "33" * 64, "statusCode": 0, "value": "44" * 64},
        "listValues": list_values,
        "precommitmentValue": hashlib.sha512(next_random).hexdigest(),
        "statusCode": 0,
        # Placeholder satisfies the outer response schema; F20 is not part of
        # the signed F1..F19 preimage and is replaced immediately below.
        "signatureValue": "00" * 256,
        "outputValue": ZERO512,
    }
    signature = leaf_key.sign(verifier.serialize_signed_fields(pulse), padding.PKCS1v15(), hashes.SHA512())
    pulse["signatureValue"] = signature.hex()
    pulse["outputValue"] = verifier.recompute_output_value(pulse)
    return {"pulse": pulse}


class Goal5793X2NistNormativeVerifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root_pem, cls.leaf_pem, cls.leaf_key = _certificates()
        cls.trust = verifier.build_synthetic_trust_bundle(cls.root_pem)
        start = 1_800_000_000_000
        cls.first = _make_pulse(
            index=100,
            timestamp_ms=start,
            local_byte=0x11,
            next_local_byte=0x22,
            leaf_pem=cls.leaf_pem,
            leaf_key=cls.leaf_key,
            previous=None,
        )
        cls.second = _make_pulse(
            index=101,
            timestamp_ms=start + 60_000,
            local_byte=0x22,
            next_local_byte=0x33,
            leaf_pem=cls.leaf_pem,
            leaf_key=cls.leaf_key,
            previous=cls.first,
        )
        cls.third = _make_pulse(
            index=102,
            timestamp_ms=start + 120_000,
            local_byte=0x33,
            next_local_byte=0x44,
            leaf_pem=cls.leaf_pem,
            leaf_key=cls.leaf_key,
            previous=cls.second,
        )

    def _verify(self, response: dict | None = None, *, trust: dict | None = None, leaf_pem: bytes | None = None):
        return verifier.verify_normative_pulse(
            response or self.first,
            leaf_certificate_pem=leaf_pem or self.leaf_pem,
            root_certificate_pem=self.root_pem,
            trust_bundle=trust or self.trust,
            trusted_trust_bundle_sha256=(trust or self.trust)["trust_bundle_sha256"],
        )

    def test_01_exact_normative_sources_and_conflicts_are_exposed(self) -> None:
        observed = verifier.assert_normative_source_identity(ROOT)
        self.assertEqual(observed["status"], "EXACT_RECOVERED_NORMATIVE_SOURCE_BYTES_MATCH")
        boundary = verifier.source_interpretation_boundary()
        self.assertEqual([row["axis"] for row in boundary["conflicts"]], [
            "noninteger_length_prefix",
            "external_statusCode_serialization",
            "certificate_identifier_preimage",
        ])
        self.assertFalse(boundary["source_conflict_hidden"])
        self.assertFalse(boundary["post_observation_variant_choice_allowed"])

    def test_02_exact_nistir_serialization_kat(self) -> None:
        kat = verifier.serialization_known_answer()
        self.assertEqual(kat["serialized_bytes"], 850)
        self.assertEqual(kat["serialized_sha512"], kat["expected_serialized_sha512"])
        self.assertTrue(kat["matches_expected"])

    def test_03_valid_pulse_and_three_pulse_chain_pass(self) -> None:
        receipt = self._verify()
        self.assertTrue(receipt["pulse"]["signature_verified"])
        self.assertTrue(receipt["pulse"]["output_recomputed"])
        chain = verifier.verify_normative_chain(
            [
                {"response": self.first, "leaf_certificate_pem": self.leaf_pem},
                {"response": self.second, "leaf_certificate_pem": self.leaf_pem},
                {"response": self.third, "leaf_certificate_pem": self.leaf_pem},
            ],
            root_certificate_pem=self.root_pem,
            trust_bundle=self.trust,
            trusted_trust_bundle_sha256=self.trust["trust_bundle_sha256"],
        )
        self.assertEqual((chain["pulse_count"], chain["adjacent_link_count"]), (3, 2))
        self.assertTrue(chain["all_precommitments_verified"])

    def test_03b_independent_test_side_serialization_recount_matches(self) -> None:
        kat = verifier.serialization_known_answer()
        independent = _independent_nistir_signed_serialization(kat["pulse"])
        self.assertEqual(independent, verifier.serialize_signed_fields(kat["pulse"]))
        self.assertEqual(hashlib.sha512(independent).hexdigest(), kat["expected_serialized_sha512"])

    def test_04_xsd_der_certificate_identifier_variant_is_rejected(self) -> None:
        mutated = copy.deepcopy(self.first)
        mutated["pulse"]["certificateId"] = verifier.der_certificate_id(self.leaf_pem)
        with self.assertRaisesRegex(X2Error, "XSD_DER_VARIANT_NOT_ACCEPTED"):
            self._verify(mutated)

    def test_05_wrong_signature_and_output_are_rejected(self) -> None:
        wrong_signature = copy.deepcopy(self.first)
        raw = bytearray.fromhex(wrong_signature["pulse"]["signatureValue"])
        raw[0] ^= 1
        wrong_signature["pulse"]["signatureValue"] = bytes(raw).hex()
        wrong_signature["pulse"]["outputValue"] = verifier.recompute_output_value(wrong_signature["pulse"])
        with self.assertRaisesRegex(X2Error, "NISTIR_PULSE_SIGNATURE_INVALID"):
            self._verify(wrong_signature)
        wrong_output = copy.deepcopy(self.first)
        wrong_output["pulse"]["outputValue"] = "ff" * 64
        with self.assertRaisesRegex(X2Error, "NISTIR_OUTPUT_RECOMPUTATION_MISMATCH"):
            self._verify(wrong_output)

    def test_06_wrong_previous_and_precommitment_links_are_rejected(self) -> None:
        wrong_previous = copy.deepcopy(self.second)
        wrong_previous["pulse"]["listValues"][0]["value"] = "aa" * 64
        with self.assertRaisesRegex(X2Error, "NISTIR_PREVIOUS_OUTPUT_LINK_MISMATCH"):
            verifier.verify_adjacent_pulses(self.first, wrong_previous)
        wrong_precommitment = copy.deepcopy(self.first)
        wrong_precommitment["pulse"]["precommitmentValue"] = "bb" * 64
        with self.assertRaisesRegex(X2Error, "NISTIR_PRECOMMITMENT_LINK_MISMATCH"):
            verifier.verify_adjacent_pulses(wrong_precommitment, self.second)

    def test_07_list_value_set_and_order_are_exact(self) -> None:
        missing = copy.deepcopy(self.first["pulse"])
        missing["listValues"] = missing["listValues"][:-1]
        with self.assertRaisesRegex(X2Error, "NISTIR_LIST_VALUE_SET_INVALID"):
            verifier.serialize_signed_fields(missing)
        reordered = copy.deepcopy(self.first["pulse"])
        reordered["listValues"][0], reordered["listValues"][1] = reordered["listValues"][1], reordered["listValues"][0]
        with self.assertRaisesRegex(X2Error, "NISTIR_LIST_VALUE_ORDER_INVALID"):
            verifier.serialize_signed_fields(reordered)

    def test_08_trust_bundle_drift_and_authorization_escalation_fail(self) -> None:
        drift = copy.deepcopy(self.trust)
        drift["root"]["pem_sha256"] = "0" * 64
        with self.assertRaisesRegex(X2Error, "NISTIR_TRUST_BUNDLE_SEAL_MISMATCH"):
            self._verify(trust=drift)
        escalation = copy.deepcopy(self.trust)
        escalation["authorization"]["beacon"] = True
        escalation["trust_bundle_sha256"] = ""
        escalation["trust_bundle_sha256"] = verifier.seal_document(
            escalation,
            seal_field="trust_bundle_sha256",
            domain=verifier.TRUST_BUNDLE_DOMAIN,
            version=1,
        )
        with self.assertRaisesRegex(X2Error, "NISTIR_TRUST_BUNDLE_AUTHORIZATION_ESCALATION"):
            self._verify(trust=escalation)
        resealed_root_replacement = verifier.build_synthetic_trust_bundle(_certificates()[0])
        with self.assertRaisesRegex(X2Error, "NISTIR_OUT_OF_BAND_TRUST_BUNDLE_PIN_MISMATCH"):
            verifier.verify_normative_pulse(
                self.first,
                leaf_certificate_pem=self.leaf_pem,
                root_certificate_pem=self.root_pem,
                trust_bundle=resealed_root_replacement,
                trusted_trust_bundle_sha256=self.trust["trust_bundle_sha256"],
            )

    def test_09_module_has_no_network_or_activity_path_and_imports_shared_canonical(self) -> None:
        source = inspect.getsource(verifier)
        self.assertIn("from scripts.goal5793_x1_canonical import", source)
        for token in ("requests", "urllib", "http.client", "socket", "subprocess", "paramiko", "cupy", "cuda"):
            self.assertNotIn(f"import {token}", source)
        self.assertNotIn("TERMINAL_SOURCE_DRIFT", source)


if __name__ == "__main__":
    unittest.main()
