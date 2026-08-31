from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from scripts import goal5793_x2_nist_synthetic_crypto as crypto
from scripts.goal5793_x2_offline_core import X2Error


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = ROOT / "tests" / "fixtures" / "goal5793_x2_nist"
FIXTURE_IDENTITIES = {
    "synthetic_leaf.pem": (1066, "61cae48dc6d57175be7d74517f5f7e28fea72a8b1207d27b0335a342688039c6"),
    "synthetic_pulse.json": (1775, "0135f68f0bf7378e03b75b333d37b0f939f274abf3f3696c8134ef0054973d85"),
    "synthetic_root.pem": (1074, "b7bfaa902571161aee98f65bcb88e7d594e0219a947c73ac7ba481ef772383e9"),
}
FIXTURE_ROOT_DER_SHA256 = "8617b41c9932815421140e72213439ca0a041d9b16731a61060bc7dcf92ffd0a"


def _name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def _certificates(*, digital_signature: bool = True):
    root_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    leaf_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    end = datetime(2030, 1, 1, tzinfo=timezone.utc)
    root_name = _name("Goal5793 X2 Synthetic Root")
    leaf_name = _name("Goal5793 X2 Synthetic Leaf")
    root = (
        x509.CertificateBuilder()
        .subject_name(root_name)
        .issuer_name(root_name)
        .public_key(root_key.public_key())
        .serial_number(1)
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=True, path_length=1), critical=True)
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
        .serial_number(2 if digital_signature else 3)
        .not_valid_before(start)
        .not_valid_after(end)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(
            x509.KeyUsage(
                digital_signature=digital_signature,
                content_commitment=False,
                key_encipherment=not digital_signature,
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
    root_pem = root.public_bytes(serialization.Encoding.PEM)
    leaf_pem = leaf.public_bytes(serialization.Encoding.PEM)
    root_pin = hashlib.sha256(root.public_bytes(serialization.Encoding.DER)).hexdigest()
    return root_pem, leaf_pem, root_pin, leaf_key, leaf


def _pulse(leaf: x509.Certificate, key: rsa.RSAPrivateKey, *, timestamp: str = "2027-01-01T00:00:00.000Z"):
    local = bytes.fromhex("2" * 128)
    pulse = {
        "uri": "https://synthetic.invalid/chain/2/pulse/100",
        "version": "2.0",
        "cipherSuite": 0,
        "period": 60000,
        "certificateId": crypto.certificate_id(leaf),
        "chainIndex": 2,
        "pulseIndex": 100,
        "timeStamp": timestamp,
        "localRandomValue": local.hex(),
        "external": {"sourceId": "3" * 128, "statusCode": 0, "value": "4" * 128},
        "listValues": [],
        "precommitmentValue": hashlib.sha512(local).hexdigest(),
        "statusCode": 0,
        "signatureValue": "",
        "outputValue": "0" * 128,
    }
    signature = key.sign(crypto.signed_pulse_bytes(pulse), padding.PKCS1v15(), hashes.SHA512())
    pulse["signatureValue"] = signature.hex()
    pulse["outputValue"] = crypto.synthetic_output_value(pulse, signature)
    return {"pulse": pulse}


def _resign(response, key):
    pulse = response["pulse"]
    signature = key.sign(crypto.signed_pulse_bytes(pulse), padding.PKCS1v15(), hashes.SHA512())
    pulse["signatureValue"] = signature.hex()
    pulse["outputValue"] = crypto.synthetic_output_value(pulse, signature)


class Goal5793X2NistSyntheticCryptoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root_pem, cls.leaf_pem, cls.root_pin, cls.leaf_key, cls.leaf = _certificates()
        cls.response = _pulse(cls.leaf, cls.leaf_key)

    def verify(self, response, *, leaf_pem=None, root_pin=None):
        return crypto.verify_synthetic_pulse(
            response,
            leaf_certificate_pem=leaf_pem or self.leaf_pem,
            root_certificate_pem=self.root_pem,
            trusted_root_sha256=root_pin or self.root_pin,
        )

    def test_01_valid_synthetic_chain_signature_output_and_precommitment(self) -> None:
        receipt = self.verify(self.response)
        self.assertTrue(receipt["synthetic_only"])
        self.assertFalse(receipt["nist_ir_8213_normative_serialization_claimed"])
        self.assertFalse(receipt["usable_for_live_nist_pulse_acceptance"])
        self.assertTrue(receipt["pulse"]["signature_verified"])

    def test_02_wrong_root_pin_rejected(self) -> None:
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_TRUST_ROOT_PIN_MISMATCH"):
            self.verify(self.response, root_pin="0" * 64)

    def test_03_wrong_certificate_identifier_rejected(self) -> None:
        response = copy.deepcopy(self.response)
        response["pulse"]["certificateId"] = "0" * 128
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_CERTIFICATE_IDENTIFIER_MISMATCH"):
            self.verify(response)

    def test_04_expired_at_pulse_time_rejected(self) -> None:
        response = _pulse(self.leaf, self.leaf_key, timestamp="2031-01-01T00:00:00.000Z")
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_CERTIFICATE_TIME_INVALID"):
            self.verify(response)

    def test_05_wrong_key_usage_rejected(self) -> None:
        root_pem, leaf_pem, root_pin, leaf_key, leaf = _certificates(digital_signature=False)
        response = _pulse(leaf, leaf_key)
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_CERTIFICATE_KEY_USAGE_INVALID"):
            crypto.verify_synthetic_pulse(
                response,
                leaf_certificate_pem=leaf_pem,
                root_certificate_pem=root_pem,
                trusted_root_sha256=root_pin,
            )

    def test_06_signature_mutation_rejected(self) -> None:
        response = copy.deepcopy(self.response)
        signature = bytearray.fromhex(response["pulse"]["signatureValue"])
        signature[0] ^= 1
        response["pulse"]["signatureValue"] = bytes(signature).hex()
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_PULSE_SIGNATURE_INVALID"):
            self.verify(response)

    def test_07_output_mutation_rejected(self) -> None:
        response = copy.deepcopy(self.response)
        response["pulse"]["outputValue"] = "f" * 128
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_OUTPUT_RECOMPUTATION_MISMATCH"):
            self.verify(response)

    def test_08_precommitment_mutation_rejected_even_when_resigned(self) -> None:
        response = copy.deepcopy(self.response)
        response["pulse"]["precommitmentValue"] = "f" * 128
        _resign(response, self.leaf_key)
        with self.assertRaisesRegex(X2Error, "SYNTHETIC_PRECOMMITMENT_MISMATCH"):
            self.verify(response)

    def test_09_fixed_assets_are_exact_and_independently_verifiable(self) -> None:
        for name, (expected_bytes, expected_sha256) in FIXTURE_IDENTITIES.items():
            payload = (FIXTURE_ROOT / name).read_bytes()
            self.assertEqual(len(payload), expected_bytes)
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected_sha256)
        response = json.loads((FIXTURE_ROOT / "synthetic_pulse.json").read_text(encoding="utf-8"))
        receipt = crypto.verify_synthetic_pulse(
            response,
            leaf_certificate_pem=(FIXTURE_ROOT / "synthetic_leaf.pem").read_bytes(),
            root_certificate_pem=(FIXTURE_ROOT / "synthetic_root.pem").read_bytes(),
            trusted_root_sha256=FIXTURE_ROOT_DER_SHA256,
        )
        self.assertEqual(receipt["status"], "SYNTHETIC_CERTIFICATE_SIGNATURE_OUTPUT_AND_PRECOMMITMENT_PASS")
        self.assertTrue(receipt["pulse"]["signature_verified"])
        self.assertFalse(receipt["usable_for_live_nist_pulse_acceptance"])


if __name__ == "__main__":
    unittest.main()
