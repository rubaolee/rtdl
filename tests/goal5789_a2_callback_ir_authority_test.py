from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest

from scripts import goal5789_a2_build_contract_evidence as builder
from scripts import goal5789_a2_independent_compatibility_checker as checker
from scripts import goal5789_a2_materialize_callback_ir_authority as materializer
from scripts import goal5789_a2_independent_recount as independent_recount
from scripts import goal5789_a2_adversarial_binding_audit as adversarial_audit
from scripts import goal5789_independent_compatibility_checker as v1


ROOT = Path(__file__).resolve().parents[1]


def _load_bytes(payloads: dict[str, bytes], name: str) -> dict[str, object]:
    value = json.loads(payloads[name])
    assert isinstance(value, dict)
    return value


def _seal_certificate(certificate: dict[str, object]) -> None:
    certificate["certificate_sha256"] = checker.certificate_digest(certificate)


def _seal_binding(binding: dict[str, object]) -> None:
    binding["authority_sha256"] = v1.nested_authority_digest(binding)


def _seal_bundle(authority: dict[str, object]) -> None:
    authority["authority_sha256"] = checker.authority_digest(authority)


def _seal_callback_authority(authority: dict[str, object]) -> None:
    authority["authority_sha256"] = checker.callback_authority_digest(authority)


def _seal_pin(pin: dict[str, object]) -> None:
    pin["pin_sha256"] = checker.callback_pin_digest(pin)


def _seal_result(result: dict[str, object]) -> None:
    result.pop("result_sha256", None)
    result["result_sha256"] = checker.digest(result)


def _coherently_relabel_multiplicity(
    certificate: dict[str, object], authority: dict[str, object]
) -> None:
    """Construct the disclosed jointly-wrong semantic/physical-authority control.

    Callback identities and the reviewed pair-to-program mapping stay exact.
    Only the mutually trusted semantic/physical declaration is coherently
    replaced, demonstrating the remaining authority-TCB ceiling without
    weakening the new Callback-program binding.
    """

    replacement = "JOINTLY_WRONG_BUT_MUTUALLY_CONSISTENT_MULTIPLICITY"
    contract_id = certificate["semantic_request"]["contract_id"]
    encoding_id = certificate["physical_encoding"]["encoding_id"]
    certificate["semantic_request"]["policy"]["multiplicity"] = replacement
    certificate["physical_encoding"]["guarantees"]["multiplicity"] = replacement
    certificate["canonical_candidates"][0]["guarantees"]["multiplicity"] = replacement
    authority["semantic_authority"]["contracts"][contract_id]["policy"][
        "multiplicity"
    ] = replacement
    authority["physical_authority"]["encodings"][encoding_id]["guarantees"][
        "multiplicity"
    ] = replacement
    _seal_binding(authority["semantic_authority"])
    _seal_binding(authority["physical_authority"])
    _seal_bundle(authority)
    _seal_certificate(certificate)


class Goal5789A2CallbackIRAuthorityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.callback_authority, cls.callback_pin = materializer.build_outputs()
        cls.payloads = builder.build_payloads(cls.callback_authority, cls.callback_pin)
        cls.authority = _load_bytes(cls.payloads, "AUTHORITY_BUNDLE.json")
        cls.inventory = _load_bytes(cls.payloads, "BOUNDED_INVENTORY.json")
        cls.certificates = {
            row["unit_id"]: _load_bytes(cls.payloads, f"certificates/{row['unit_id']}.json")
            for row in cls.inventory["inventory"]
        }

    def _evaluate(
        self,
        certificate: dict[str, object],
        authority: dict[str, object] | None = None,
        callback_authority: dict[str, object] | None = None,
        callback_pin: dict[str, object] | None = None,
    ) -> dict[str, object]:
        return checker.evaluate_certificate(
            certificate,
            self.authority if authority is None else authority,
            self.callback_authority if callback_authority is None else callback_authority,
            self.callback_pin if callback_pin is None else callback_pin,
        )

    def _assert_callback_reject(
        self, certificate: dict[str, object], reason: str, **kwargs: object
    ) -> None:
        result = self._evaluate(certificate, **kwargs)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertFalse(result["reference_admission_complete"])
        self.assertTrue(
            any(reason in item for item in result["semantic_compatible"]["reasons"]),
            result["semantic_compatible"]["reasons"],
        )

    def test_authority_is_real_frozen_source_and_executed_leaf_backed(self) -> None:
        expected = {
            "builtin_triangle_adjacency": (
                "135e5b5de7fec664d66608015868a337321de80e6ad1ac8fb4b8085360e2a5b5",
                "e89ddea0580fe0ad017e649de8dbe3d08409174e9cfdb3f662afbc1344d989be",
                4,
            ),
            "builtin_triangle_count": (
                "fedb71e837dedce85608e94e9f75a2fa9bb702077a8bb9a2ddc6ebaa4258adc3",
                "49c63a2ed9e1cfa8beb47dc7595ce82d5eee63523b3efbb619ff50de0453bf5c",
                4,
            ),
            "builtin_triangle_keyed": (
                "2362a9ef9c63e65d0632d0ac1ef7fea154cf9bf136368286c6fff6a34d68e9f5",
                "a35b97894e268da0159de36e4c595527918c53a372214550d671d170b8b1fcea",
                4,
            ),
            "custom_aabb_box_relation": (
                "54d76a4e128f6d78b7a3efffadd886c91f21d35bab01d30a6edb0a31188bf74b",
                "a1d2f7bf1225c76a25473f9583e3ba95588e0275fb6a389d4dcf95bb1521a456",
                7,
            ),
            "custom_aabb_spatial_candidate": (
                "97964948dc822cb90f744a1d8ce76536bcc46dfd20667fb209aef1d6007e0ced",
                "a1d2f7bf1225c76a25473f9583e3ba95588e0275fb6a389d4dcf95bb1521a456",
                7,
            ),
        }
        self.assertEqual(self.callback_authority["source_archive"]["file_sha256"], materializer.SOURCE_ARCHIVE_SHA256)
        self.assertEqual(self.callback_authority["execution_evidence_archive"]["file_sha256"], materializer.EVIDENCE_ARCHIVE_SHA256)
        rows_by_alias = {
            row["alias"]: row for row in self.callback_authority["programs"].values()
        }
        self.assertEqual(
            set(self.callback_authority["programs"]), checker.EXPECTED_PROGRAM_SHA256S
        )
        self.assertEqual(
            checker.canonical_bytes(self.callback_authority["admitted_bindings"]),
            checker.canonical_bytes(checker.EXPECTED_ADMITTED_BINDINGS),
        )
        for alias, (ir_sha, effect_sha, role_count) in expected.items():
            row = rows_by_alias[alias]
            self.assertEqual(row["verified_summary"]["ir_sha256"], ir_sha)
            self.assertEqual(row["verified_summary"]["effect_digest"], effect_sha)
            self.assertEqual(len(row["executed_leaf_evidence"]), role_count)
            self.assertEqual(
                sorted(item["role"] for item in row["executed_leaf_evidence"]),
                sorted(item["role"] for item in row["callback_contract"]["roles"]),
            )

    def test_successor_vector_is_computed_not_forced_and_preserves_6_9_0(self) -> None:
        self.assertEqual(self.inventory["predecessor"]["compatible_count"], 6)
        self.assertEqual(self.inventory["predecessor"]["unknown_count"], 9)
        self.assertEqual(self.inventory["predecessor"]["incompatible_count"], 0)
        self.assertEqual(self.inventory["successor"]["compatible_count"], 6)
        self.assertEqual(self.inventory["successor"]["unknown_count"], 9)
        self.assertEqual(self.inventory["successor"]["incompatible_count"], 0)
        self.assertTrue(self.inventory["successor"]["counts_were_not_forced"])
        self.assertEqual(self.inventory["successor"]["callback_authority_bound_count"], 6)
        self.assertEqual(self.inventory["successor"]["callback_authority_unbound_count"], 9)
        self.assertEqual(self.inventory["successor"]["callback_authority_coverage_denominator"], 15)
        self.assertFalse(
            self.inventory["claim_boundary"][
                "callback_summary_source_backed_and_authority_bound_for_all_inventory_rows"
            ]
        )
        self.assertTrue(
            self.inventory["claim_boundary"][
                "callback_summary_source_backed_and_authority_bound_for_compatible_rows"
            ]
        )
        self.assertFalse(
            self.inventory["claim_boundary"]["unbound_unknown_callback_integrity_claimed"]
        )
        for row in self.inventory["inventory"]:
            result = self._evaluate(self.certificates[row["unit_id"]])
            self.assertEqual(result["semantic_compatible"]["verdict"], row["semantic_compatible"])
            if row["semantic_compatible"] == checker.COMPATIBLE:
                self.assertTrue(result["reference_admission_complete"])
            else:
                self.assertIsNone(self.certificates[row["unit_id"]]["callback_contract"])
                self.assertIn(
                    "callback_authority_not_established_for_semantic_physical_pair",
                    result["semantic_compatible"]["reasons"],
                )

    def test_unbound_callback_unknown_never_masks_proven_incompatibility(self) -> None:
        certificate = deepcopy(self.certificates["triangle__com_dblp__rt_1a2"])
        certificate["physical_encoding"]["geometry_family"] = "contradictory_family"
        _seal_certificate(certificate)
        result = self._evaluate(certificate)
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
        self.assertFalse(result["reference_admission_complete"])
        self.assertIn(
            "callback_authority_not_established_for_semantic_physical_pair",
            result["semantic_compatible"]["reasons"],
        )
        self.assertTrue(
            any(
                reason in {
                    "physical_guarantee_authority_mismatch",
                    "gas_geometry_family_mismatch",
                    "unsupported_physical_schema",
                }
                for reason in result["semantic_compatible"]["reasons"]
            ),
            result["semantic_compatible"]["reasons"],
        )

    def test_original_empty_effect_attack_passes_v1_and_fails_a2(self) -> None:
        old_certificate = json.loads(
            (ROOT / "history/internal_docs/goal5789_contract_evidence_20260816/certificates/triangle__com_dblp__rt_2a1.json").read_text(encoding="utf-8")
        )
        old_authority = json.loads(
            (ROOT / "history/internal_docs/goal5789_contract_evidence_20260816/AUTHORITY_BUNDLE.json").read_text(encoding="utf-8")
        )
        for row in old_certificate["callback_contract"]["roles"]:
            row["effects"] = []
        old_certificate["certificate_sha256"] = v1.certificate_digest(old_certificate)
        self.assertEqual(
            v1.evaluate_certificate(old_certificate, old_authority)["semantic_compatible"]["verdict"],
            v1.COMPATIBLE,
        )
        successor = deepcopy(self.certificates["triangle__com_dblp__rt_2a1"])
        for row in successor["callback_contract"]["roles"]:
            row["effects"] = []
        _seal_certificate(successor)
        self._assert_callback_reject(successor, "callback_contract_authority_mismatch")

    def test_digest_role_effect_and_resource_mutations_fail_closed(self) -> None:
        baseline = self.certificates["triangle__com_dblp__rt_2a1"]
        mutations = []
        for key in ("ir_sha256", "effect_digest"):
            value = deepcopy(baseline)
            value["callback_contract"][key] = hashlib.sha256(f"wrong-{key}".encode()).hexdigest()
            mutations.append(value)
        value = deepcopy(baseline)
        value["callback_contract"]["roles"][0]["effects"] = ["ignore"]
        mutations.append(value)
        value = deepcopy(baseline)
        value["callback_contract"]["roles"].append({"role": "closest_hit", "effects": ["payload"]})
        mutations.append(value)
        for key in (
            "payload_u32_slots",
            "attribute_u32_slots",
            "trace_depth",
            "callable_depth",
            "total_static_iterations",
            "helper_call_depth",
        ):
            value = deepcopy(baseline)
            value["callback_contract"][key] = 1_000_000_000 if key == "total_static_iterations" else 0
            if value["callback_contract"][key] == baseline["callback_contract"][key]:
                value["callback_contract"][key] = 1
            mutations.append(value)
        for mutated in mutations:
            _seal_certificate(mutated)
            self._assert_callback_reject(mutated, "callback_contract_authority_mismatch")

    def test_numeric_bool_and_float_aliases_do_not_pass_exact_callback_binding(self) -> None:
        baseline = self.certificates["triangle__com_dblp__rt_2a1"]
        for key in (
            "payload_u32_slots",
            "attribute_u32_slots",
            "trace_depth",
            "callable_depth",
            "total_static_iterations",
            "helper_call_depth",
        ):
            for replacement in (False, True, float(baseline["callback_contract"][key])):
                if type(replacement) is int:
                    continue
                mutated = deepcopy(baseline)
                mutated["callback_contract"][key] = replacement
                _seal_certificate(mutated)
                self._assert_callback_reject(mutated, "callback_contract")

    def test_all_same_family_whole_callback_swaps_are_rejected(self) -> None:
        by_family: dict[str, list[dict[str, object]]] = {}
        for certificate in self.certificates.values():
            family = certificate["physical_encoding"]["geometry_family"]
            by_family.setdefault(family, []).append(certificate)
        checked = 0
        for certificates in by_family.values():
            for recipient in certificates:
                for donor in certificates:
                    if donor["callback_contract"] == recipient["callback_contract"]:
                        continue
                    mutated = deepcopy(recipient)
                    mutated["callback_contract"] = deepcopy(donor["callback_contract"])
                    _seal_certificate(mutated)
                    result = self._evaluate(mutated)
                    self.assertEqual(result["semantic_compatible"]["verdict"], checker.INCOMPATIBLE)
                    self.assertFalse(result["reference_admission_complete"])
                    checked += 1
        self.assertGreater(checked, 0)

    def test_authority_missing_or_mutated_while_external_pin_is_fixed_rejects(self) -> None:
        certificate = self.certificates["triangle__com_dblp__rt_2a1"]
        missing = deepcopy(self.callback_authority)
        program_sha = certificate["callback_contract"]["authority_program_sha256"]
        del missing["programs"][program_sha]
        _seal_callback_authority(missing)
        self._assert_callback_reject(
            certificate,
            "callback_authority_binding_identity_mismatch",
            callback_authority=missing,
        )
        mutated = deepcopy(self.callback_authority)
        row = mutated["programs"][program_sha]
        row["callback_contract"]["total_static_iterations"] = 1_000_000_000
        _seal_callback_authority(mutated)
        self._assert_callback_reject(
            certificate,
            "callback_authority_binding_identity_mismatch",
            callback_authority=mutated,
        )

    def test_callback_authority_claim_boundary_cannot_be_resigned_to_overclaim(self) -> None:
        certificate = self.certificates["triangle__com_dblp__rt_2a1"]
        callback_authority = deepcopy(self.callback_authority)
        callback_authority["claim_boundary"]["semantic_soundness_claimed"] = True
        callback_authority["claim_boundary"]["execution_authorized"] = True
        _seal_callback_authority(callback_authority)
        pin = deepcopy(self.callback_pin)
        pin["callback_authority"]["file_sha256"] = checker.file_digest_from_object(
            callback_authority
        )
        pin["callback_authority"]["size_bytes"] = len(
            checker.pretty_json_bytes(callback_authority)
        )
        pin["callback_authority"]["authority_sha256"] = callback_authority[
            "authority_sha256"
        ]
        _seal_pin(pin)
        authority = deepcopy(self.authority)
        binding = authority["callback_ir_authority_binding"]
        binding["callback_authority_file_sha256"] = checker.file_digest_from_object(
            callback_authority
        )
        binding["callback_authority_sha256"] = callback_authority["authority_sha256"]
        binding["callback_authority_pin_file_sha256"] = checker.file_digest_from_object(pin)
        binding["callback_authority_pin_sha256"] = pin["pin_sha256"]
        _seal_binding(binding)
        _seal_bundle(authority)
        self._assert_callback_reject(
            certificate,
            "callback_authority_claim_boundary_not_exact",
            authority=authority,
            callback_authority=callback_authority,
            callback_pin=pin,
        )
        with self.assertRaisesRegex(RuntimeError, "claim boundary"):
            builder.build_payloads(callback_authority, pin)

    def test_coordinated_certificate_and_bundle_resign_cannot_bypass_fixed_pin(self) -> None:
        certificate = deepcopy(self.certificates["triangle__com_dblp__rt_2a1"])
        callback_authority = deepcopy(self.callback_authority)
        authority = deepcopy(self.authority)
        new_id = "goal5789-a2.callback.attacker.same_program.v1"
        certificate["callback_contract"]["callback_authority_id"] = new_id
        _seal_certificate(certificate)
        program_sha = certificate["callback_contract"]["authority_program_sha256"]
        row = callback_authority["programs"][program_sha]
        row["callback_authority_id"] = new_id
        row["callback_contract"]["callback_authority_id"] = new_id
        for admitted in callback_authority["admitted_bindings"]:
            if admitted["authority_program_sha256"] == program_sha:
                admitted["callback_authority_id"] = new_id
        _seal_callback_authority(callback_authority)
        binding = authority["callback_ir_authority_binding"]
        binding["callback_authority_file_sha256"] = checker.file_digest_from_object(callback_authority)
        binding["callback_authority_sha256"] = callback_authority["authority_sha256"]
        _seal_binding(binding)
        _seal_bundle(authority)
        self._assert_callback_reject(
            certificate,
            "callback_authority_pin_identity_mismatch",
            authority=authority,
            callback_authority=callback_authority,
        )

    def test_full_reroot_cannot_turn_a_summary_lie_into_a_full_program_projection(self) -> None:
        baseline = self.certificates["particle__microfluidics_5000"]
        for key, replacement in (
            ("payload_u32_slots", 2),
            ("attribute_u32_slots", 1),
            ("helper_call_depth", 1),
        ):
            certificate = deepcopy(baseline)
            callback_authority = deepcopy(self.callback_authority)
            pin = deepcopy(self.callback_pin)
            authority = deepcopy(self.authority)
            program_sha = certificate["callback_contract"]["authority_program_sha256"]
            program_row = callback_authority["programs"][program_sha]
            program_row["verified_summary"][key] = replacement
            program_row["callback_contract"][key] = replacement
            certificate["callback_contract"][key] = replacement
            _seal_callback_authority(callback_authority)
            pin["callback_authority"]["file_sha256"] = checker.file_digest_from_object(callback_authority)
            pin["callback_authority"]["size_bytes"] = len(checker.pretty_json_bytes(callback_authority))
            pin["callback_authority"]["authority_sha256"] = callback_authority["authority_sha256"]
            _seal_pin(pin)
            binding = authority["callback_ir_authority_binding"]
            binding["callback_authority_file_sha256"] = checker.file_digest_from_object(callback_authority)
            binding["callback_authority_sha256"] = callback_authority["authority_sha256"]
            binding["callback_authority_pin_file_sha256"] = checker.file_digest_from_object(pin)
            binding["callback_authority_pin_sha256"] = pin["pin_sha256"]
            _seal_binding(binding)
            _seal_bundle(authority)
            _seal_certificate(certificate)
            self._assert_callback_reject(
                certificate,
                "callback_authority_verified_program_mismatch",
                authority=authority,
                callback_authority=callback_authority,
                callback_pin=pin,
            )

    def test_jointly_wrong_semantic_and_physical_authorities_remain_disclosed_tcb_ceiling(self) -> None:
        certificate = deepcopy(self.certificates["triangle__com_dblp__rt_2a1"])
        authority = deepcopy(self.authority)
        _coherently_relabel_multiplicity(certificate, authority)
        result = self._evaluate(
            certificate,
            authority=authority,
        )
        self.assertEqual(result["semantic_compatible"]["verdict"], checker.COMPATIBLE)
        self.assertTrue(result["reference_admission_complete"])
        self.assertTrue(self.inventory["claim_boundary"]["authority_producer_is_tcb"])
        self.assertFalse(self.inventory["claim_boundary"]["jointly_wrong_authorities_detected"])

    def test_a2_checker_imports_no_product_app_or_builder(self) -> None:
        tree = ast.parse(
            (ROOT / "scripts/goal5789_a2_independent_compatibility_checker.py").read_text(encoding="utf-8")
        )
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.append(node.module)
        self.assertFalse(any(name == "rtdsl" or name.startswith("rtdsl.") for name in imports))
        self.assertFalse(any("Paper-reproduction-apps" in name for name in imports))
        self.assertFalse(any("build_contract_evidence" in name for name in imports))

    def test_materializer_rejects_preloaded_rtdsl_module_instead_of_misclaiming_frozen_source(self) -> None:
        self.assertNotIn("rtdsl.fake_preloaded_a2", sys.modules)
        sys.modules["rtdsl.fake_preloaded_a2"] = types.ModuleType("rtdsl.fake_preloaded_a2")
        try:
            with self.assertRaisesRegex(RuntimeError, "fresh interpreter"):
                materializer.build_outputs()
        finally:
            del sys.modules["rtdsl.fake_preloaded_a2"]

    def test_independent_recount_reconstructs_full_program_resources_and_exact_coverage(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_recount_test_") as temporary:
            root = Path(temporary)
            (root / "CALLBACK_IR_AUTHORITY.json").write_bytes(
                checker.pretty_json_bytes(self.callback_authority)
            )
            (root / "CALLBACK_IR_AUTHORITY_PIN.json").write_bytes(
                checker.pretty_json_bytes(self.callback_pin)
            )
            for relative, payload in self.payloads.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            result = independent_recount.recount(root)
        self.assertEqual(result["successor_counts"], {"compatible": 6, "unknown": 9, "incompatible": 0})
        self.assertEqual(
            result["callback_authority_coverage"],
            {
                "bound_inventory_count": 6,
                "unbound_inventory_count": 9,
                "inventory_denominator": 15,
                "all_inventory_rows_bound": False,
                "unbound_unknown_callback_integrity_claimed": False,
            },
        )

    def test_independent_recount_rehashes_frozen_predecessor_terminal_and_work_roots(self) -> None:
        independent_recount._validate_frozen_predecessor_and_work_roots()
        attacks = (
            (
                independent_recount.EXPECTED_PREDECESSOR_MANIFEST,
                "file_sha256",
                "predecessor delivery manifest identity",
            ),
            (
                independent_recount.EXPECTED_TERMINAL_IDENTITY,
                "terminal_sha256",
                "terminal seal identity",
            ),
            (
                independent_recount.EXPECTED_WORK_AUTHORITY_IDENTITY,
                "work_authority_sha256",
                "work authority seal identity",
            ),
        )
        for identity, field, expected_error in attacks:
            with self.subTest(field=field):
                original = identity[field]
                identity[field] = "0" * 64
                try:
                    with self.assertRaisesRegex(RuntimeError, expected_error):
                        independent_recount._validate_frozen_predecessor_and_work_roots()
                finally:
                    identity[field] = original

    def test_independent_recount_rejects_coordinated_real_program_or_heldout_pair_substitution(self) -> None:
        substitutions = (
            (
                "triangle.rt2a1.weighted_count.v1",
                "builtin_triangle.weighted_count.v1",
                "c126a788b5e451fc0d76b4c48610bb2e6d6dbbf22fdb0b1c656deac97babc671",
            ),
            (
                "librts.inclusive_aabb_relation.v1",
                "custom_aabb.inclusive_relation.v1",
                "c3a17d90e2c8895f6ec14b0c07bafdc734d7ec233b3397bdc99fd478b9941c26",
            ),
            (
                "particle.closest_face_projection.v1",
                "builtin_triangle.closest_face_projection.v1",
                "92697debe1e25227ec770b4d339c7cd248b16b7185612516841f3986a208ea30",
            ),
        )
        attacks: list[tuple[str, dict[str, object]]] = []
        for contract_id, encoding_id, replacement_program in substitutions:
            authority = deepcopy(self.callback_authority)
            for binding in authority["admitted_bindings"]:
                if (
                    binding["semantic_contract_id"] == contract_id
                    and binding["physical_encoding_id"] == encoding_id
                ):
                    binding["authority_program_sha256"] = replacement_program
                    binding["callback_authority_id"] = authority["programs"][
                        replacement_program
                    ]["callback_authority_id"]
                    break
            else:
                self.fail(f"missing baseline binding: {contract_id}/{encoding_id}")
            attacks.append((contract_id, authority))
        heldout_removed = deepcopy(self.callback_authority)
        for binding in heldout_removed["admitted_bindings"]:
            if binding["semantic_contract_id"] == "rtxrmq.leftmost_argmin.v1":
                binding["semantic_contract_id"] = "invented.unused.semantic.contract.v1"
                break
        attacks.append(("rtxrmq_pair_removed", heldout_removed))

        for label, callback_authority in attacks:
            with self.subTest(label=label), tempfile.TemporaryDirectory(
                prefix="goal5789_a2_recount_mapping_attack_"
            ) as temporary:
                root = Path(temporary)
                _seal_callback_authority(callback_authority)
                pin = deepcopy(self.callback_pin)
                pin["callback_authority"]["file_sha256"] = checker.file_digest_from_object(
                    callback_authority
                )
                pin["callback_authority"]["size_bytes"] = len(
                    checker.pretty_json_bytes(callback_authority)
                )
                pin["callback_authority"]["authority_sha256"] = callback_authority[
                    "authority_sha256"
                ]
                _seal_pin(pin)
                (root / "CALLBACK_IR_AUTHORITY.json").write_bytes(
                    checker.pretty_json_bytes(callback_authority)
                )
                (root / "CALLBACK_IR_AUTHORITY_PIN.json").write_bytes(
                    checker.pretty_json_bytes(pin)
                )
                for relative, payload in self.payloads.items():
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
                with self.assertRaisesRegex(
                    RuntimeError, "admitted pair-to-program mapping"
                ):
                    independent_recount.recount(root)

    def test_independent_recount_rejects_resigned_overclaim_and_extra_result_claim(self) -> None:
        callback_authority = deepcopy(self.callback_authority)
        callback_authority["claim_boundary"]["semantic_soundness_claimed"] = True
        callback_authority["claim_boundary"]["execution_authorized"] = True
        _seal_callback_authority(callback_authority)
        pin = deepcopy(self.callback_pin)
        pin["callback_authority"]["file_sha256"] = checker.file_digest_from_object(
            callback_authority
        )
        pin["callback_authority"]["size_bytes"] = len(
            checker.pretty_json_bytes(callback_authority)
        )
        pin["callback_authority"]["authority_sha256"] = callback_authority[
            "authority_sha256"
        ]
        _seal_pin(pin)
        with tempfile.TemporaryDirectory(
            prefix="goal5789_a2_recount_overclaim_"
        ) as temporary:
            root = Path(temporary)
            (root / "CALLBACK_IR_AUTHORITY.json").write_bytes(
                checker.pretty_json_bytes(callback_authority)
            )
            (root / "CALLBACK_IR_AUTHORITY_PIN.json").write_bytes(
                checker.pretty_json_bytes(pin)
            )
            for relative, payload in self.payloads.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            with self.assertRaisesRegex(RuntimeError, "claim boundary"):
                independent_recount.recount(root)

        with tempfile.TemporaryDirectory(
            prefix="goal5789_a2_recount_extra_result_claim_"
        ) as temporary:
            root = Path(temporary)
            (root / "CALLBACK_IR_AUTHORITY.json").write_bytes(
                checker.pretty_json_bytes(self.callback_authority)
            )
            (root / "CALLBACK_IR_AUTHORITY_PIN.json").write_bytes(
                checker.pretty_json_bytes(self.callback_pin)
            )
            for relative, payload in self.payloads.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            result_path = root / "results/triangle__com_dblp__rt_2a1.json"
            result = json.loads(result_path.read_bytes())
            result["authorizes_universal_semantic_soundness"] = True
            _seal_result(result)
            result_path.write_bytes(checker.pretty_json_bytes(result))
            with self.assertRaisesRegex(RuntimeError, "top-level schema"):
                independent_recount.recount(root)

    def test_independent_recount_rejects_resigned_producer_metadata_and_leaf_manifest_lies(self) -> None:
        metadata = deepcopy(self.callback_authority)
        program_sha = self.certificates["triangle__com_dblp__rt_2a1"][
            "callback_contract"
        ]["authority_program_sha256"]
        metadata_row = metadata["programs"][program_sha]
        metadata_row["alias"] = "fabricated_alias"
        metadata_row["compile_entrypoint"] = "attacker.fake:compile"
        metadata_row["selected_constructor_source_paths"] = [
            "src/rtdsl/v4_callback_ir.py"
        ]
        manifest = deepcopy(self.callback_authority)
        manifest["execution_leaf_manifest"]["entries_sha256"] = "0" * 64
        for label, callback_authority, expected_error in (
            ("producer_metadata", metadata, "producer metadata"),
            ("leaf_manifest", manifest, "leaf manifest authority identity"),
        ):
            with self.subTest(label=label), tempfile.TemporaryDirectory(
                prefix="goal5789_a2_recount_metadata_attack_"
            ) as temporary:
                root = Path(temporary)
                _seal_callback_authority(callback_authority)
                pin = deepcopy(self.callback_pin)
                pin["callback_authority"]["file_sha256"] = checker.file_digest_from_object(
                    callback_authority
                )
                pin["callback_authority"]["size_bytes"] = len(
                    checker.pretty_json_bytes(callback_authority)
                )
                pin["callback_authority"]["authority_sha256"] = callback_authority[
                    "authority_sha256"
                ]
                _seal_pin(pin)
                (root / "CALLBACK_IR_AUTHORITY.json").write_bytes(
                    checker.pretty_json_bytes(callback_authority)
                )
                (root / "CALLBACK_IR_AUTHORITY_PIN.json").write_bytes(
                    checker.pretty_json_bytes(pin)
                )
                for relative, payload in self.payloads.items():
                    path = root / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(payload)
                with self.assertRaisesRegex(RuntimeError, expected_error):
                    independent_recount.recount(root)

    def test_formal_adversarial_matrix_runs_159_baseline_attack_and_tcb_control_cases(self) -> None:
        with tempfile.TemporaryDirectory(prefix="goal5789_a2_hostile_test_") as temporary:
            root = Path(temporary)
            (root / "CALLBACK_IR_AUTHORITY.json").write_bytes(
                checker.pretty_json_bytes(self.callback_authority)
            )
            (root / "CALLBACK_IR_AUTHORITY_PIN.json").write_bytes(
                checker.pretty_json_bytes(self.callback_pin)
            )
            for relative, payload in self.payloads.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(payload)
            result = adversarial_audit.audit(root)
        self.assertEqual(result["case_count"], 159)
        self.assertEqual(result["passed_count"], 159)
        self.assertEqual(result["failed_count"], 0)
        self.assertTrue(
            result["claim_boundary"][
                "callback_pair_to_program_mapping_is_fixed_and_substitution_rejected"
            ]
        )
        self.assertTrue(
            result["claim_boundary"][
                "jointly_wrong_semantic_and_physical_authorities_can_remain_mutually_consistent"
            ]
        )
        self.assertFalse(result["claim_boundary"]["jointly_wrong_authority_detection_claimed"])


if __name__ == "__main__":
    unittest.main()
