from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
import gc
import hashlib
import pickle
import unittest
from unittest.mock import patch
import weakref

import rtdsl.v4_semantic_physical_admission as admission_module
from rtdsl.v4_semantic_physical_admission import (
    AdmissionRuleId,
    AdmissionVerdict,
    PhysicalEncodingEligibility,
    SemanticPhysicalAdmissionError,
    _issue_compiler_physical_guarantee_registry,
    canonical_candidates_from_registry,
    evaluate_semantic_physical_admission,
    issue_registered_physical_guarantee_authority,
    issue_semantic_requirement_authority,
    live_family_binding_from_mapping,
    physical_guarantee_registry_entry,
    reverify_semantic_physical_admission,
    verify_semantic_physical_admission,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _fixture():
    policy = {
        "input_type": "finite_u32_weighted_edges",
        "output_type": "checked_u64_scalar",
        "exactness": "exact_checked_integer_reduction",
        "tie_policy": "not_applicable_scalar",
        "order_policy": "commutative_checked_reduction",
        "multiplicity": "registered_weighted_hit_multiplicity",
        "numeric_precision": "u32_inputs_checked_u64_accumulator",
        "overflow_policy": "fail_closed_before_u64_wraparound",
    }
    sources = {kind: f"provider/{kind}.py" for kind in (
        "encode", "ray", "trace", "continuation", "decode")}
    source_manifest = {path: _sha(path) for path in sources.values()}
    graph = {
        "encode": (["semantic_input"], ["geometry", "query_state"]),
        "ray": (["query_state"], ["ray"]),
        "trace": (["geometry", "ray"], ["hit_stream"]),
        "continuation": (["hit_stream"], ["candidate_output"]),
        "decode": (["candidate_output"], ["semantic_output"]),
    }
    semantic = {
        "contract_id": "checked.weighted-count.v1",
        "algorithm_identity": "checked_weighted_count",
        "declared_domain_sha256": _sha("declared-domain"),
        "policy": deepcopy(policy),
        "required_hit_semantics": ["primitive_index_u32", "weight_u32"],
        "orientation_contract_sha256": _sha("orientation-contract"),
        "specification_source_sha256": _sha("independent-specification"),
    }
    physical = {
        "encoding_id": "builtin-triangle.checked-weighted-count.v1",
        "supported_algorithm_identity": semantic["algorithm_identity"],
        "supported_domain_sha256": semantic["declared_domain_sha256"],
        "orientation_contract_sha256": semantic["orientation_contract_sha256"],
        "geometry_family": "builtin-triangle",
        "schema_sha256": _sha("live-family-schema"),
        "callback_ir_sha256": _sha("callback-ir"),
        "effect_digest": _sha("callback-effects"),
        "guarantees": deepcopy(policy),
        "maps": [
            {
                "kind": kind,
                "source_id": sources[kind],
                "source_sha256": source_manifest[sources[kind]],
                "consumes": consumes,
                "produces": produces,
            }
            for kind, (consumes, produces) in graph.items()
        ],
        "hit_semantics": ["primitive_index_u32", "weight_u32"],
        "gas_graph_depth": 1,
        "gas_sbt_record_stride": 1,
        "gas_update_policy": "static",
        "buffer_contract_sha256": _sha("buffer-contract"),
        "required_target_capabilities": [
            "optix", "builtin-triangle", "bound-program-bundle"],
        "source_manifest": source_manifest,
    }
    binding = {
        "callback_ir_sha256": physical["callback_ir_sha256"],
        "effect_digest": physical["effect_digest"],
        "family_schema_sha256": physical["schema_sha256"],
        "target_sha256": _sha("exact-target"),
        "target_provider": "optix",
        "target_capabilities": [
            "optix", "builtin-triangle", "bound-program-bundle"],
        "canonical_artifact_sha256": _sha("inert-plan-or-contract"),
        "canonical_template_id": "canonical.checked-weighted-count.v1",
        "family_authority_sha256": _sha("family-authority"),
        "family_authority_nonce": "family-authority-nonce-0001",
    }
    candidate = {
        "template_id": binding["canonical_template_id"],
        "canonical": True,
        "algorithm_identity": semantic["algorithm_identity"],
        "declared_domain_sha256": semantic["declared_domain_sha256"],
        "orientation_contract_sha256": semantic["orientation_contract_sha256"],
        "geometry_family": physical["geometry_family"],
        "schema_sha256": physical["schema_sha256"],
        "guarantees": deepcopy(policy),
    }
    return semantic, physical, binding, [candidate]


def _authority_fixture(
    semantic=None,
    physical=None,
    binding=None,
    *,
    eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
    extra_entries=(),
):
    if semantic is None or physical is None or binding is None:
        semantic, physical, binding, _ = _fixture()
    semantic_authority = issue_semantic_requirement_authority(
        semantic,
        oracle_source_sha256=_sha("independent-oracle"),
        issuer_domain="app.test.semantic.v1",
    )
    entry = physical_guarantee_registry_entry(
        "compiler.test.primary.v1", physical,
        eligibility=eligibility,
        canonical_template_id=(
            binding["canonical_template_id"]
            if eligibility is PhysicalEncodingEligibility.CANONICAL_PRODUCTION
            else None),
        classifier_source_sha256=_sha("classifier-source"),
    )
    registry = _issue_compiler_physical_guarantee_registry(
        (entry, *extra_entries),
        registry_source_sha256=_sha("compiler-registry-source"),
    )
    physical_authority = issue_registered_physical_guarantee_authority(
        registry, entry.entry_id)
    live = live_family_binding_from_mapping(binding)
    candidates = canonical_candidates_from_registry(
        registry, live_binding=live,
        geometry_family=physical["geometry_family"],
    )
    return semantic_authority, physical_authority, binding, candidates


class Goal5790A1SemanticPhysicalAdmissionTest(unittest.TestCase):
    def test_compatible_sole_candidate_mints_live_nonexecutable_authority(self):
        semantic, physical, binding, candidates = _fixture()
        decision = evaluate_semantic_physical_admission(
            semantic, physical,
            live_binding=binding,
            canonical_candidates=candidates,
        )
        self.assertEqual(decision.verdict, AdmissionVerdict.COMPATIBLE)
        self.assertEqual(decision.matching_candidate_count, 1)
        self.assertEqual(
            decision.canonical_template_id,
            "canonical.checked-weighted-count.v1")
        self.assertFalse(decision.executable)

        semantic_authority, physical_authority, binding, candidates = (
            _authority_fixture(semantic, physical, binding))
        authority = verify_semantic_physical_admission(
            semantic_authority, physical_authority,
            live_binding=binding,
        )
        self.assertTrue(authority.authorizes_executable_issuance)
        self.assertFalse(authority.executable)
        self.assertIs(
            reverify_semantic_physical_admission(
                authority, semantic_authority, physical_authority,
                live_binding=binding,
            ),
            authority,
        )

    def test_absent_semantic_authority_is_unknown_and_cannot_mint(self):
        _, physical, binding, candidates = _fixture()
        decision = evaluate_semantic_physical_admission(
            None, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(decision.verdict, AdmissionVerdict.UNKNOWN)
        self.assertIn(
            AdmissionRuleId.SEMANTIC_REQUIREMENT_UNKNOWN,
            {item.rule_id for item in decision.findings})
        _, physical_authority, binding, candidates = _authority_fixture()
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.AUTHORITY_NOT_LIVE.value):
            verify_semantic_physical_admission(
                None, physical_authority, live_binding=binding)

    def test_policy_mismatch_is_named_incompatible_and_cannot_mint(self):
        cases = {
            "exactness": AdmissionRuleId.EXACTNESS_POLICY_MISMATCH,
            "tie_policy": AdmissionRuleId.TIE_POLICY_MISMATCH,
            "multiplicity": AdmissionRuleId.MULTIPLICITY_POLICY_MISMATCH,
            "overflow_policy": AdmissionRuleId.OVERFLOW_POLICY_MISMATCH,
            "numeric_precision": (
                AdmissionRuleId.NUMERIC_PRECISION_POLICY_MISMATCH),
            "order_policy": AdmissionRuleId.ORDER_POLICY_MISMATCH,
        }
        for key, expected in cases.items():
            with self.subTest(key=key):
                semantic, physical, binding, candidates = _fixture()
                physical["guarantees"][key] = "attacker_selected_policy"
                decision = evaluate_semantic_physical_admission(
                    semantic, physical, live_binding=binding,
                    canonical_candidates=candidates)
                self.assertEqual(
                    decision.verdict, AdmissionVerdict.INCOMPATIBLE)
                self.assertEqual(
                    [(item.rule_id, item.path) for item in decision.findings],
                    [(expected, f"physical_guarantee.guarantees.{key}")],
                )
                with self.assertRaisesRegex(
                        SemanticPhysicalAdmissionError, expected.value):
                    semantic_authority, physical_authority, _, registered = (
                        _authority_fixture(semantic, physical, binding))
                    verify_semantic_physical_admission(
                        semantic_authority, physical_authority,
                        live_binding=binding)

    def test_missing_map_source_is_unknown_while_digest_mismatch_is_incompatible(self):
        semantic, physical, binding, candidates = _fixture()
        source_id = physical["maps"][0]["source_id"]
        del physical["source_manifest"][source_id]
        missing = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(missing.verdict, AdmissionVerdict.UNKNOWN)
        self.assertIn(
            AdmissionRuleId.MAP_SOURCE_UNKNOWN,
            {item.rule_id for item in missing.findings})

        semantic, physical, binding, candidates = _fixture()
        physical["maps"][0]["source_sha256"] = _sha("different-source")
        mismatch = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(mismatch.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertIn(
            AdmissionRuleId.MAP_SOURCE_DIGEST_MISMATCH,
            {item.rule_id for item in mismatch.findings})

        semantic, physical, binding, candidates = _fixture()
        physical["source_manifest"]["independent/oracle.py"] = _sha(
            "independent/oracle.py")
        unused = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(unused.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertIn(
            AdmissionRuleId.MAP_SOURCE_UNUSED,
            {item.rule_id for item in unused.findings})

    def test_algorithm_and_domain_are_bound_by_the_physical_guarantee(self):
        cases = (
            ("algorithm_identity", "algorithm.attacker.v1",
             AdmissionRuleId.ALGORITHM_IDENTITY_MISMATCH,
             "physical_guarantee.supported_algorithm_identity"),
            ("declared_domain_sha256", _sha("attacker-domain"),
             AdmissionRuleId.DECLARED_DOMAIN_MISMATCH,
             "physical_guarantee.supported_domain_sha256"),
            ("orientation_contract_sha256", _sha("swapped-orientation"),
             AdmissionRuleId.ORIENTATION_CONTRACT_MISMATCH,
             "physical_guarantee.orientation_contract_sha256"),
        )
        for field, value, rule, path in cases:
            with self.subTest(field=field):
                semantic, physical, binding, candidates = _fixture()
                semantic[field] = value
                candidates[0][field] = value
                decision = evaluate_semantic_physical_admission(
                    semantic, physical, live_binding=binding,
                    canonical_candidates=candidates)
                self.assertEqual(decision.verdict, AdmissionVerdict.INCOMPATIBLE)
                self.assertIn((rule, path), [
                    (item.rule_id, item.path) for item in decision.findings])
                with self.assertRaisesRegex(
                        SemanticPhysicalAdmissionError, rule.value):
                    semantic_authority, physical_authority, _, registered = (
                        _authority_fixture(semantic, physical, binding))
                    verify_semantic_physical_admission(
                        semantic_authority, physical_authority,
                        live_binding=binding)

    def test_zero_and_multiple_canonical_matches_fail_closed(self):
        semantic, physical, binding, candidates = _fixture()
        zero = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=[])
        self.assertEqual(zero.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertIn(
            AdmissionRuleId.CANONICAL_CANDIDATE_UNSUPPORTED,
            {item.rule_id for item in zero.findings})

        duplicate = deepcopy(candidates[0])
        duplicate["template_id"] = "canonical.second-weighted-count.v1"
        many = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=[candidates[0], duplicate])
        self.assertEqual(many.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertEqual(many.matching_candidate_count, 2)
        self.assertIn(
            AdmissionRuleId.CANONICAL_CANDIDATE_AMBIGUOUS,
            {item.rule_id for item in many.findings})

    def test_live_binding_must_match_callback_schema_target_and_canonical_plan(self):
        semantic, physical, binding, candidates = _fixture()
        binding["callback_ir_sha256"] = _sha("another-callback")
        binding["canonical_template_id"] = "canonical.another-template.v1"
        binding["target_provider"] = "cuda"
        decision = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        rules = {item.rule_id for item in decision.findings}
        self.assertEqual(decision.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertIn(AdmissionRuleId.CALLBACK_BINDING_MISMATCH, rules)
        self.assertIn(AdmissionRuleId.TARGET_PROVIDER_MISMATCH, rules)
        self.assertIn(AdmissionRuleId.CANONICAL_LIVE_BINDING_MISMATCH, rules)

    def test_inputs_are_snapshotted_against_post_admission_mutation(self):
        semantic, physical, binding, candidates = _fixture()
        fresh_binding = deepcopy(binding)
        semantic_authority, physical_authority, live, registered = (
            _authority_fixture(semantic, physical, binding))
        authority = verify_semantic_physical_admission(
            semantic_authority, physical_authority, live_binding=live)

        semantic["policy"]["tie_policy"] = "mutated"
        physical["source_manifest"].clear()
        binding["target_capabilities"].clear()
        candidates[0]["guarantees"]["tie_policy"] = "mutated"

        self.assertEqual(
            dict(authority.semantic_requirement.policy)["tie_policy"],
            "not_applicable_scalar")
        self.assertTrue(authority.physical_guarantee.source_manifest)
        self.assertTrue(authority.live_binding.target_capabilities)
        self.assertIs(
            reverify_semantic_physical_admission(
                authority, semantic_authority, physical_authority,
                live_binding=fresh_binding,
                ),
            authority,
        )

    def test_raw_and_synchronously_rewritten_mappings_never_mint_authority(self):
        semantic, physical, binding, candidates = _fixture()
        semantic["policy"]["exactness"] = "synchronized_false_claim"
        physical["guarantees"]["exactness"] = "synchronized_false_claim"
        candidates[0]["guarantees"]["exactness"] = "synchronized_false_claim"
        decision = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(decision.verdict, AdmissionVerdict.COMPATIBLE)
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.AUTHORITY_NOT_LIVE.value):
            verify_semantic_physical_admission(
                semantic, physical, live_binding=binding)

    def test_semantic_physical_and_registry_capabilities_are_noncopyable(self):
        semantic_authority, physical_authority, _, _ = _authority_fixture()
        registry = physical_authority.registry
        for name, authority in (
            ("semantic", semantic_authority),
            ("physical", physical_authority),
            ("registry", registry),
        ):
            with self.subTest(authority=name):
                with self.assertRaisesRegex(TypeError, "process-local"):
                    pickle.dumps(authority)

        copied_semantic = replace(semantic_authority)
        copied_physical = replace(physical_authority)
        semantic, physical, binding, candidates = _fixture()
        del semantic, physical
        for sem, phys in (
            (copied_semantic, physical_authority),
            (semantic_authority, copied_physical),
        ):
            with self.assertRaisesRegex(
                    SemanticPhysicalAdmissionError,
                    AdmissionRuleId.AUTHORITY_NOT_LIVE.value):
                verify_semantic_physical_admission(
                    sem, phys, live_binding=binding)

    def test_live_capabilities_do_not_survive_a_process_identity_change(self):
        semantic, physical, binding, _ = _authority_fixture()
        admission = verify_semantic_physical_admission(
            semantic, physical, live_binding=binding)
        original_pid = admission_module.os.getpid()
        checks = (
            lambda: admission_module.reverify_semantic_requirement_authority(
                semantic),
            lambda: admission_module.reverify_physical_guarantee_registry(
                physical.registry),
            lambda: admission_module.reverify_registered_physical_guarantee_authority(
                physical),
            lambda: reverify_semantic_physical_admission(
                admission, semantic, physical, live_binding=binding),
        )
        with patch.object(
                admission_module.os, "getpid", return_value=original_pid + 1):
            for check in checks:
                with self.subTest(check=check):
                    with self.assertRaisesRegex(
                            SemanticPhysicalAdmissionError,
                            AdmissionRuleId.AUTHORITY_NOT_LIVE.value):
                        check()

    def test_internal_registry_issuer_is_not_on_public_surface_and_snapshots_are_inert(self):
        semantic_authority, physical_authority, _, _ = _authority_fixture()
        self.assertNotIn(
            "_issue_compiler_physical_guarantee_registry",
            admission_module.__all__)
        self.assertNotIn(
            "verify_semantic_physical_admission", admission_module.__all__)
        self.assertNotIn(
            "reverify_semantic_physical_admission", admission_module.__all__)
        semantic_snapshot = semantic_authority.to_dict()
        registry_snapshot = physical_authority.registry.to_dict()
        physical_snapshot = physical_authority.to_dict()
        self.assertEqual(
            semantic_snapshot["authority_sha256"],
            semantic_authority.authority_sha256)
        self.assertEqual(
            registry_snapshot["registry_sha256"],
            physical_authority.registry.registry_sha256)
        self.assertEqual(
            physical_snapshot["entry_sha256"],
            physical_authority.entry.entry_sha256)
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.AUTHORITY_NOT_LIVE.value):
            verify_semantic_physical_admission(
                semantic_snapshot, physical_snapshot,
                live_binding=_fixture()[2])

    def test_invalid_source_manifest_digest_is_incompatible_and_unregistrable(self):
        semantic, physical, binding, candidates = _fixture()
        source_id = physical["maps"][0]["source_id"]
        physical["maps"][0]["source_sha256"] = "not-a-digest"
        physical["source_manifest"][source_id] = "not-a-digest"
        decision = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(decision.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertIn(
            AdmissionRuleId.DIGEST_INVALID,
            {finding.rule_id for finding in decision.findings})
        entry = physical_guarantee_registry_entry(
            "compiler.test.bad_digest.v1", physical,
            eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
            canonical_template_id=binding["canonical_template_id"],
            classifier_source_sha256=_sha("classifier-source"))
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.DIGEST_INVALID.value):
            _issue_compiler_physical_guarantee_registry(
                (entry,), registry_source_sha256=_sha("registry-source"))

    def test_diagnostic_registry_entry_is_truthful_but_never_executable(self):
        semantic, physical, binding, _ = _fixture()
        canonical = physical_guarantee_registry_entry(
            "compiler.test.canonical.v1", physical,
            eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
            canonical_template_id=binding["canonical_template_id"],
            classifier_source_sha256=_sha("canonical-classifier"))
        diagnostic = physical_guarantee_registry_entry(
            "compiler.test.diagnostic.v1", physical,
            eligibility=PhysicalEncodingEligibility.DIAGNOSTIC_NONREGISTRABLE,
            canonical_template_id=None,
            classifier_source_sha256=_sha("diagnostic-classifier"))
        registry = _issue_compiler_physical_guarantee_registry(
            (canonical, diagnostic),
            registry_source_sha256=_sha("mixed-registry"))
        semantic_authority = issue_semantic_requirement_authority(
            semantic, oracle_source_sha256=_sha("independent-oracle"),
            issuer_domain="app.test.semantic.v1")
        physical_authority = issue_registered_physical_guarantee_authority(
            registry, diagnostic.entry_id)
        live = live_family_binding_from_mapping(binding)
        candidates = canonical_candidates_from_registry(
            registry, live_binding=live,
            geometry_family=physical["geometry_family"])
        self.assertEqual(len(candidates), 1)
        self.assertEqual(
            evaluate_semantic_physical_admission(
                semantic, physical, live_binding=live,
                canonical_candidates=candidates).verdict,
            AdmissionVerdict.COMPATIBLE)
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.PHYSICAL_AUTHORITY_NONCANONICAL.value):
            verify_semantic_physical_admission(
                semantic_authority, physical_authority,
                live_binding=live)

    def test_registry_is_the_authority_for_zero_and_multiple_candidates(self):
        semantic, physical, binding, _ = _fixture()
        semantic_authority = issue_semantic_requirement_authority(
            semantic, oracle_source_sha256=_sha("independent-oracle"),
            issuer_domain="app.test.semantic.v1")
        diagnostic = physical_guarantee_registry_entry(
            "compiler.test.diagnostic_only.v1", physical,
            eligibility=PhysicalEncodingEligibility.DIAGNOSTIC_NONREGISTRABLE,
            canonical_template_id=None,
            classifier_source_sha256=_sha("diagnostic-classifier"))
        zero_registry = _issue_compiler_physical_guarantee_registry(
            (diagnostic,), registry_source_sha256=_sha("zero-registry"))
        zero_authority = issue_registered_physical_guarantee_authority(
            zero_registry, diagnostic.entry_id)
        live = live_family_binding_from_mapping(binding)
        zero_candidates = canonical_candidates_from_registry(
            zero_registry, live_binding=live,
            geometry_family=physical["geometry_family"])
        self.assertEqual(zero_candidates, ())
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.CANONICAL_CANDIDATE_UNSUPPORTED.value):
            verify_semantic_physical_admission(
                semantic_authority, zero_authority,
                live_binding=live)

        entries = tuple(
            physical_guarantee_registry_entry(
                f"compiler.test.canonical_{index}.v1", physical,
                eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
                canonical_template_id=(
                    binding["canonical_template_id"] + f".{index}"),
                classifier_source_sha256=_sha(f"classifier-{index}"))
            for index in range(2))
        many_registry = _issue_compiler_physical_guarantee_registry(
            entries, registry_source_sha256=_sha("many-registry"))
        many_authority = issue_registered_physical_guarantee_authority(
            many_registry, entries[0].entry_id)
        many_candidates = canonical_candidates_from_registry(
            many_registry, live_binding=live,
            geometry_family=physical["geometry_family"])
        self.assertEqual(len(many_candidates), 2)
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.CANONICAL_CANDIDATE_AMBIGUOUS.value):
            verify_semantic_physical_admission(
                semantic_authority, many_authority,
                live_binding=live)

    def test_equal_looking_reconstruction_and_pickle_do_not_create_authority(self):
        semantic, physical, binding, _ = _fixture()
        semantic_authority, physical_authority, binding, candidates = (
            _authority_fixture(semantic, physical, binding))
        authority = verify_semantic_physical_admission(
            semantic_authority, physical_authority, live_binding=binding)
        copied = replace(authority)
        with self.assertRaisesRegex(
                SemanticPhysicalAdmissionError,
                AdmissionRuleId.AUTHORITY_NOT_LIVE.value):
            reverify_semantic_physical_admission(
                copied, semantic_authority, physical_authority,
                live_binding=binding)
        with self.assertRaisesRegex(TypeError, "process-local"):
            pickle.dumps(authority)

    def test_live_registry_does_not_keep_a_dead_authority(self):
        semantic_authority, physical_authority, binding, candidates = (
            _authority_fixture())
        authority = verify_semantic_physical_admission(
            semantic_authority, physical_authority, live_binding=binding)
        reference = weakref.ref(authority)
        del authority
        gc.collect()
        self.assertIsNone(reference())

    def test_malformed_mapping_is_a_stable_fail_closed_decision(self):
        semantic, physical, binding, candidates = _fixture()
        del semantic["algorithm_identity"]
        decision = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        self.assertEqual(decision.verdict, AdmissionVerdict.INCOMPATIBLE)
        self.assertEqual(
            decision.findings[0].rule_id,
            AdmissionRuleId.MALFORMED_INPUT)

    def test_decision_and_authority_identities_are_deterministic(self):
        semantic, physical, binding, candidates = _fixture()
        first = evaluate_semantic_physical_admission(
            semantic, physical, live_binding=binding,
            canonical_candidates=candidates)
        second = evaluate_semantic_physical_admission(
            deepcopy(semantic), deepcopy(physical),
            live_binding=deepcopy(binding),
            canonical_candidates=deepcopy(candidates))
        self.assertEqual(first.decision_sha256, second.decision_sha256)
        left_semantic, left_physical, left_binding, left_candidates = (
            _authority_fixture(semantic, physical, binding))
        left = verify_semantic_physical_admission(
            left_semantic, left_physical, live_binding=left_binding)
        right_semantic, right_physical, right_binding, right_candidates = (
            _authority_fixture(
                deepcopy(semantic), deepcopy(physical), deepcopy(binding)))
        right = verify_semantic_physical_admission(
            right_semantic, right_physical,
            live_binding=right_binding)
        self.assertEqual(left.admission_sha256, right.admission_sha256)
        self.assertEqual(left.authority_nonce, right.authority_nonce)
        self.assertIsNot(left, right)


if __name__ == "__main__":
    unittest.main()
