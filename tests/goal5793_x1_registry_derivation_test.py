from __future__ import annotations

from copy import deepcopy
import hashlib
import inspect
from pathlib import Path
import unittest

from scripts import goal5793_x1_generic_examiner as examiner
from scripts import goal5793_x1_registry_derivation as registry
from scripts.goal5793_x1_canonical import canonical_json_bytes, seal_document


ROOT = Path(__file__).resolve().parents[1]
ALL_ROWS = (*registry.POSITIVE_IDS, registry.HELD_OUT_ROW)


def _context():
    return registry.historical_registry_context()


def _verify(payload, receipt, context=None):
    authority, stage_pin, trusted = context or _context()
    return registry.verify_registered_input(
        payload, receipt, authority, stage_pin, trusted
    )


def _examine(payload, receipt, context=None):
    authority, stage_pin, trusted = context or _context()
    return examiner.examine(
        payload,
        receipt,
        registry_authority=authority,
        registry_stage_pin=stage_pin,
        trusted_stage_pin_sha256=trusted,
    )


def _fixture_for_authority(authority):
    certificate_path = (
        registry.A2_ROOT / "certificates/particle__microfluidics_5000.json"
    )
    certificate, reference_authority = registry._normalize_a2_to_v1(
        registry._json(certificate_path),
        registry._json(registry.A2_ROOT / "AUTHORITY_BUNDLE.json"),
    )
    template = registry._match_template(certificate, authority)
    slots = registry._identity_slots(certificate, template)
    payload = {
        "schema": registry.EXAM_INPUT_SCHEMA,
        **registry._product_sections(certificate, authority, template, slots),
        "reference_certificate": certificate,
        "reference_authority": reference_authority,
    }
    return payload, registry._receipt(payload, authority, template, slots)


class RegistryDerivationTest(unittest.TestCase):
    def test_authority_rebuilds_to_four_templates_and_seven_provenances(self) -> None:
        first = registry.build_registry_authority()
        second = registry.build_registry_authority()
        self.assertEqual(canonical_json_bytes(first), canonical_json_bytes(second))
        self.assertEqual(first["template_count"], 4)
        self.assertEqual(first["row_provenance_count"], 7)
        self.assertEqual(
            first["authority_sha256"],
            seal_document(
                first,
                seal_field="authority_sha256",
                domain="rtdl.goal5793.x1.registry_derivation_authority",
                version=1,
            ),
        )
        provenance = [
            row
            for template in first["templates"]
            for row in template["row_provenance"]
        ]
        self.assertCountEqual(provenance, ALL_ROWS)

    def test_exact_seven_slots_and_frozen_facades(self) -> None:
        authority = registry.build_registry_authority()
        self.assertEqual(
            tuple(authority["allowed_postfreeze_slots"]),
            registry.ALLOWED_IDENTITY_SLOTS,
        )
        for template in authority["templates"]:
            self.assertEqual(
                tuple(template["allowed_postfreeze_slots"]),
                registry.ALLOWED_IDENTITY_SLOTS,
            )
            self.assertEqual(
                set(template["facade"]), {"family", "admit", "compile", "run"}
            )
            self.assertIn(template["facade"]["family"], {
                "builtin_triangle", "triangle_reduction", "bounded_relation"
            })

    def test_authority_reports_35_reached_not_39_of_39(self) -> None:
        summary = registry.build_registry_authority()[
            "declaration_rule_replay_summary"
        ]
        self.assertEqual(summary, registry.DECLARATION_RULE_REPLAY_SUMMARY)
        self.assertEqual(summary["enum_total"], 39)
        self.assertEqual(summary["declaration_reached_count"], 35)
        self.assertEqual(len(summary["REACHED"]), 35)
        self.assertEqual(
            summary["UNREACHABLE_BY_CURRENT_CODE"],
            ["SP022_SEMANTIC_GUARANTEE_MISMATCH"],
        )
        self.assertEqual(len(summary["AUTHORITY_ONLY"]), 3)

    def test_all_seven_real_rows_verify_and_public_exam_compatible(self) -> None:
        for row_id in ALL_ROWS:
            with self.subTest(row_id=row_id):
                payload, receipt = registry.historical_registered_fixture(row_id)
                validation = _verify(payload, receipt)
                self.assertEqual(
                    validation["status"],
                    "EXACT_REGISTERED_TEMPLATE_AND_SEVEN_SLOTS",
                )
                self.assertEqual(
                    tuple(validation["identity_slots"]),
                    registry.ALLOWED_IDENTITY_SLOTS,
                )
                result = _examine(payload, receipt)
                self.assertEqual(result["status"], "VALID_LAYERED_EXAMINATION", result)
                self.assertEqual(
                    result["final_verdict"], "COMPATIBLE_FOR_DECLARED_DOMAIN", result
                )
                self.assertEqual(
                    result["registry_validation"]["receipt_sha256"],
                    receipt["receipt_sha256"],
                )

    def test_public_exam_rejects_missing_receipt(self) -> None:
        payload, _ = registry.historical_registered_fixture(ALL_ROWS[0])
        authority, stage_pin, trusted = _context()
        result = examiner.examine(
            payload,
            registry_authority=authority,
            registry_stage_pin=stage_pin,
            trusted_stage_pin_sha256=trusted,
        )
        self.assertEqual(result["status"], examiner.INFRA_INVALID)
        self.assertIn(
            "registry_receipt_required_for_controlling_path", result["reasons"]
        )

    def test_arbitrary_family_sha_and_nonce_rejected_even_with_forged_receipt_seal(self) -> None:
        payload, receipt = registry.historical_registered_fixture(ALL_ROWS[0])
        forged_payload = deepcopy(payload)
        forged_payload["live_binding"]["family_authority_sha256"] = "a" * 64
        forged_payload["live_binding"]["family_authority_nonce"] = "attacker-nonce"
        forged = deepcopy(receipt)
        forged["family_authority_sha256"] = "a" * 64
        forged["family_authority_nonce"] = "attacker-nonce"
        forged["exam_projection_sha256"] = registry._digest(
            forged_payload,
            "rtdl.goal5793.x1.registry.exam_projection",
            "complete_generic_exam_input",
        )
        forged["receipt_sha256"] = seal_document(
            forged,
            seal_field="receipt_sha256",
            domain="rtdl.goal5793.x1.registry_derivation_receipt",
            version=1,
        )
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "registered_projection_mismatch:live_binding",
        ):
            _verify(forged_payload, forged)
        result = _examine(forged_payload, forged)
        self.assertEqual(result["status"], examiner.INFRA_INVALID)

    def test_each_identity_slot_is_rederived_not_trusted(self) -> None:
        payload, receipt = registry.historical_registered_fixture(ALL_ROWS[0])
        for slot in registry.ALLOWED_IDENTITY_SLOTS:
            with self.subTest(slot=slot):
                forged = deepcopy(receipt)
                forged["identity_slots"][slot] = "f" * 64
                forged["receipt_sha256"] = seal_document(
                    forged,
                    seal_field="receipt_sha256",
                    domain="rtdl.goal5793.x1.registry_derivation_receipt",
                    version=1,
                )
                with self.assertRaisesRegex(
                    registry.RegistryDerivationError, "registry_receipt_mismatch"
                ):
                    _verify(payload, forged)

    def test_non_slot_semantic_or_geometry_change_cannot_match_template(self) -> None:
        for section, field, value in (
            ("semantic_request", "algorithm_identity", "hostile.algorithm"),
            ("physical_encoding", "geometry_family", "hostile_geometry"),
        ):
            with self.subTest(section=section, field=field):
                payload, receipt = registry.historical_registered_fixture(ALL_ROWS[0])
                payload["reference_certificate"][section][field] = value
                with self.assertRaisesRegex(
                    registry.RegistryDerivationError,
                    "(registry_template_match_count:0|"
                    "scientific_family_has_no_frozen_facade)",
                ):
                    _verify(payload, receipt)

    def test_registry_authority_requires_exact_out_of_band_stage_pin(self) -> None:
        payload, receipt = registry.historical_registered_fixture(ALL_ROWS[0])
        authority, stage_pin, trusted = _context()
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "external_registry_authority_required",
        ):
            registry.verify_registered_input(
                payload, receipt, None, stage_pin, trusted
            )
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "out_of_band_trusted_stage_pin_mismatch",
        ):
            registry.verify_registered_input(
                payload, receipt, authority, stage_pin, "0" * 64
            )

    def test_same_examiner_accepts_separately_pinned_future_template_authority(self) -> None:
        authority, _, _ = _context()
        baseline_payload, baseline_receipt = registry.historical_registered_fixture(
            ALL_ROWS[0]
        )
        old_sha = baseline_receipt["template_sha256"]
        changed = deepcopy(authority)
        template = next(
            row for row in changed["templates"]
            if row["template_sha256"] == old_sha
        )
        template["scientific_projection"]["callback_program_structure"][
            "manifest"
        ]["resources"]["max_static_loop_trip_count"] += 1
        projection = template["scientific_projection"]
        template["facade"] = registry._classify_facade(projection)
        template["template_sha256"] = registry._digest(
            {"scientific_projection": projection, "facade": template["facade"]},
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        for row in changed["row_roots"]:
            if row["template_sha256"] == old_sha:
                row["template_sha256"] = template["template_sha256"]
        changed["status"] = "SYNTHETIC_SEPARATELY_PINNED_FUTURE_TEMPLATE_TEST"
        changed["authority_sha256"] = seal_document(
            changed,
            seal_field="authority_sha256",
            domain="rtdl.goal5793.x1.registry_derivation_authority",
            version=1,
        )
        stage_pin = registry._build_stage_pin(
            changed,
            stage_id="synthetic-future-presearch-stage",
            frozen_stage_root_sha256=hashlib.sha256(
                b"synthetic reviewed stage root"
            ).hexdigest(),
        )
        context = (changed, stage_pin, stage_pin["stage_pin_sha256"])
        payload, receipt = _fixture_for_authority(changed)
        result = _examine(payload, receipt, context)
        self.assertEqual(result["status"], "VALID_LAYERED_EXAMINATION", result)
        self.assertEqual(
            result["registry_validation"]["registry_stage_id"],
            "synthetic-future-presearch-stage",
        )

        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "external_registry_stage_pin_required",
        ):
            registry.verify_registered_input(
                payload, receipt, changed, None, stage_pin["stage_pin_sha256"]
            )
        drifted = deepcopy(changed)
        drifted["future_boundary"] += " drift"
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "registry_authority_seal_mismatch",
        ):
            registry.verify_registered_input(
                payload, receipt, drifted, stage_pin, stage_pin["stage_pin_sha256"]
            )
        resealed_drift = deepcopy(changed)
        resealed_drift["future_boundary"] += " resealed drift"
        resealed_drift["authority_sha256"] = seal_document(
            resealed_drift,
            seal_field="authority_sha256",
            domain="rtdl.goal5793.x1.registry_derivation_authority",
            version=1,
        )
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "registry_stage_pin_authority_mismatch",
        ):
            registry.verify_registered_input(
                payload,
                receipt,
                resealed_drift,
                stage_pin,
                stage_pin["stage_pin_sha256"],
            )

    def test_matcher_and_verifier_do_not_read_forbidden_metadata(self) -> None:
        # The receipt truthfully reports candidate metadata as unused, so audit
        # the matcher (the only family-selection path), not output field labels.
        source = inspect.getsource(registry._match_template)
        for forbidden in (
            "candidate_id",
            "citation_key",
            "source_index",
            "role_assignment",
            "expected_disposition",
            "selected_index",
            "performance_expectation",
            "implementation_ease",
        ):
            self.assertNotIn(forbidden, source)

    def test_identity_slot_substitution_does_not_select_facade_or_template(self) -> None:
        certificate = registry._json(
            registry.A2_ROOT / "certificates/particle__microfluidics_5000.json"
        )
        authority = registry._json(registry.A2_ROOT / "AUTHORITY_BUNDLE.json")
        normalized, _ = registry._normalize_a2_to_v1(certificate, authority)
        callback_authority = registry._json(
            registry.A2_ROOT / "CALLBACK_IR_AUTHORITY.json"
        )
        program_sha = certificate["callback_contract"]["authority_program_sha256"]
        program = callback_authority["programs"][program_sha]["callback_program"]
        baseline = registry._scientific_projection(normalized, program)
        baseline_facade = registry._classify_facade(baseline)
        baseline_sha = registry._digest(
            {"scientific_projection": baseline, "facade": baseline_facade},
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )

        mutated = deepcopy(normalized)
        mutated["callback_contract"]["ir_sha256"] = "1" * 64
        mutated["callback_contract"]["effect_digest"] = "2" * 64
        mutated["physical_encoding"]["schema_sha256"] = "3" * 64
        for candidate in mutated["canonical_candidates"]:
            candidate["schema_sha256"] = "3" * 64
        mutated["target_contract"]["native_sha256"] = "4" * 64
        for path in list(mutated["evidence_contract"]["source_pins"]):
            mutated["evidence_contract"]["source_pins"][path] = "5" * 64
        for edge in mutated["physical_encoding"]["maps"]:
            edge["source_sha256"] = "5" * 64
        mutated_program = deepcopy(program)
        mutated_program["source_sha256"] = "6" * 64
        mutated_program["normalized_source"] = "different byte identity"
        projection = registry._scientific_projection(mutated, mutated_program)
        facade = registry._classify_facade(projection)
        template_sha = registry._digest(
            {"scientific_projection": projection, "facade": facade},
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        self.assertEqual(facade, baseline_facade)
        self.assertEqual(template_sha, baseline_sha)

    def test_coherent_source_path_renaming_changes_slot_not_template(self) -> None:
        certificate = registry._json(
            registry.A2_ROOT / "certificates/particle__microfluidics_5000.json"
        )
        authority = registry._json(registry.A2_ROOT / "AUTHORITY_BUNDLE.json")
        normalized, _ = registry._normalize_a2_to_v1(certificate, authority)
        callback_authority = registry._json(
            registry.A2_ROOT / "CALLBACK_IR_AUTHORITY.json"
        )
        program_sha = certificate["callback_contract"]["authority_program_sha256"]
        program = callback_authority["programs"][program_sha]["callback_program"]
        baseline_projection = registry._scientific_projection(normalized, program)
        baseline_template = {
            "scientific_projection": baseline_projection,
            "facade": registry._classify_facade(baseline_projection),
        }
        baseline_sha = registry._digest(
            baseline_template,
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        baseline_slots = registry._identity_slots(normalized, baseline_template)

        changed = deepcopy(normalized)
        source_pins = changed["evidence_contract"]["source_pins"]
        renamed = {f"future/{index}.py": digest for index, digest in enumerate(
            source_pins.values()
        )}
        path_map = dict(zip(source_pins, renamed))
        changed["evidence_contract"]["source_pins"] = renamed
        changed["semantic_request"]["specification_source_pin"] = path_map[
            changed["semantic_request"]["specification_source_pin"]
        ]
        changed["physical_encoding"]["provider_source_pin"] = path_map[
            changed["physical_encoding"]["provider_source_pin"]
        ]
        for edge in changed["physical_encoding"]["maps"]:
            edge["source_pin"] = path_map[edge["source_pin"]]
        changed_projection = registry._scientific_projection(changed, program)
        changed_template = {
            "scientific_projection": changed_projection,
            "facade": registry._classify_facade(changed_projection),
        }
        changed_sha = registry._digest(
            changed_template,
            "rtdl.goal5793.x1.registry.family_template",
            "identity_free_scientific_family_template",
        )
        changed_slots = registry._identity_slots(changed, changed_template)
        self.assertEqual(changed_sha, baseline_sha)
        self.assertNotEqual(changed_slots["source_digest"], baseline_slots["source_digest"])

    def test_unknown_callback_semantic_key_fails_closed(self) -> None:
        authority = registry._json(registry.A2_ROOT / "CALLBACK_IR_AUTHORITY.json")
        program = deepcopy(next(iter(authority["programs"].values()))["callback_program"])
        program["profile"] = "must-not-be-silently-erased"
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            "callback_program_schema_mismatch:program",
        ):
            registry._callback_program_structure(program)
        nested = deepcopy(next(iter(authority["programs"].values()))["callback_program"])
        nested["functions"][0]["profile"] = "semantic"
        with self.assertRaisesRegex(
            registry.RegistryDerivationError,
            r"callback_program_schema_mismatch:program.functions\[0\]",
        ):
            registry._callback_program_structure(nested)

    def test_callback_program_projection_keeps_structure_but_no_identity_keys(self) -> None:
        authority = registry.build_registry_authority()

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        for template in authority["templates"]:
            program = template["scientific_projection"]["callback_program_structure"]
            self.assertIn("functions", program)
            self.assertIn("resources", program["manifest"])
            observed = set(keys(program))
            self.assertNotIn("normalized_source", observed)
            self.assertNotIn("source_sha256", observed)
            self.assertNotIn("proof_sha256", observed)
            self.assertNotIn("profile", observed)

    def test_postreview_packet_and_dependency_bytes_are_exact(self) -> None:
        self.assertEqual(
            hashlib.sha256(registry.PACKET_MANIFEST_PATH.read_bytes()).hexdigest(),
            registry.EXPECTED_PACKET_MANIFEST_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(registry.CANONICAL_PATH.read_bytes()).hexdigest(),
            registry.EXPECTED_CANONICAL_SHA256,
        )
        self.assertEqual(
            hashlib.sha256(registry.V1_CHECKER_PATH.read_bytes()).hexdigest(),
            registry.EXPECTED_V1_CHECKER_SHA256,
        )


if __name__ == "__main__":
    unittest.main()
