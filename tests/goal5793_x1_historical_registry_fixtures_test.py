from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts import goal5793_x1_build_historical_registry_fixtures as builder
from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]


class HistoricalRegistryFixturesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.first = builder.build_outputs()
        cls.second = builder.build_outputs()

    def test_outputs_are_deterministic(self) -> None:
        self.assertEqual(self.first, self.second)
        self.assertEqual(set(self.first), {
            builder.AUTHORITY_NAME,
            builder.PIN_NAME,
            builder.FIXTURES_NAME,
            builder.ENVELOPE_NAME,
        })

    def test_exact_registry_module_is_hard_pinned(self) -> None:
        self.assertEqual(
            hashlib.sha256(builder.REGISTRY_PATH.read_bytes()).hexdigest(),
            builder.EXPECTED_REGISTRY_SHA256,
        )

    def test_all_seven_full_fixtures_verify_against_external_pin(self) -> None:
        registry = builder._load_registry()
        authority = json.loads(self.first[builder.AUTHORITY_NAME])
        pin = json.loads(self.first[builder.PIN_NAME])
        fixtures = json.loads(self.first[builder.FIXTURES_NAME])
        self.assertEqual(fixtures["historical_fixture_count"], 7)
        self.assertEqual(
            fixtures["fixtures_sha256"],
            seal_document(
                fixtures,
                seal_field="fixtures_sha256",
                domain="rtdl.goal5793.x1.historical_registry_fixtures",
                version=1,
            ),
        )
        for row in fixtures["rows"]:
            verified = registry.verify_registered_input(
                row["payload"],
                row["registry_receipt"],
                registry_authority=authority,
                registry_stage_pin=pin,
                trusted_stage_pin_sha256=pin["stage_pin_sha256"],
            )
            self.assertEqual(
                verified["status"], "EXACT_REGISTERED_TEMPLATE_AND_SEVEN_SLOTS"
            )
            self.assertEqual(
                hashlib.sha256(canonical_json_bytes(row["payload"])).hexdigest(),
                row["payload_canonical_sha256"],
            )

    def test_scope_cannot_be_mistaken_for_future_evidence(self) -> None:
        fixtures = json.loads(self.first[builder.FIXTURES_NAME])
        self.assertEqual(
            fixtures["status"],
            "FORMAL_HISTORICAL_FIXTURES__NOT_FUTURE_GENERALIZATION_EVIDENCE",
        )
        scope = fixtures["scope"]
        self.assertTrue(scope["historical_positive_replay_only"])
        self.assertFalse(scope["future_candidate_authority_issued"])
        self.assertFalse(scope["publication_authorized"])
        for key, value in scope.items():
            if key.endswith("_count"):
                self.assertEqual(value, 0)

    def test_runner_envelope_has_no_in_band_trust_root(self) -> None:
        envelope = json.loads(self.first[builder.ENVELOPE_NAME])
        self.assertEqual(set(envelope), {"schema", "payload", "registry_receipt"})
        self.assertEqual(
            envelope["schema"], "rtdl.goal5793.x1.runner_candidate_envelope.v1"
        )
        for key in ("registry_authority", "registry_stage_pin", "trusted_stage_pin_sha256"):
            self.assertNotIn(key, envelope["payload"])

    def test_authority_drift_does_not_validate_under_old_pin(self) -> None:
        registry = builder._load_registry()
        authority = json.loads(self.first[builder.AUTHORITY_NAME])
        pin = json.loads(self.first[builder.PIN_NAME])
        envelope = json.loads(self.first[builder.ENVELOPE_NAME])
        forged = deepcopy(authority)
        forged["templates"][0]["facade"]["geometry_family"] = "hostile"
        forged["authority_sha256"] = registry.canonical.seal_document(
            forged,
            seal_field="authority_sha256",
            domain="rtdl.goal5793.x1.registry_derivation_authority",
            version=1,
        )
        with self.assertRaises(registry.RegistryDerivationError):
            registry.verify_registered_input(
                envelope["payload"],
                envelope["registry_receipt"],
                registry_authority=forged,
                registry_stage_pin=pin,
                trusted_stage_pin_sha256=pin["stage_pin_sha256"],
            )

    def test_create_only_preflights_all_outputs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5793_x1_registry_write_") as td:
            root = Path(td)
            blocker = root / builder.PIN_NAME
            blocker.write_bytes(b"existing")
            with self.assertRaises(FileExistsError):
                builder.write_create_only(root, self.first)
            self.assertEqual(blocker.read_bytes(), b"existing")
            self.assertFalse((root / builder.AUTHORITY_NAME).exists())


if __name__ == "__main__":
    unittest.main()
