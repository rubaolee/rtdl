from __future__ import annotations

import dataclasses
import hashlib
from pathlib import Path
import unittest

from rtdsl.v4_bounded_relation import (
    BoundedRelationEmissionSchema,
    BoundedRelationError,
    RelationDuplicatePolicy,
    compile_bounded_relation_contract,
    materialize_bounded_relation,
    verify_precanonical_bounded_relation,
    verify_bounded_relation_schema,
)
from rtdsl.v4_bounded_relation_optix_compiler import (
    _inline_wrapper,
    generate_bounded_relation_numba_leaf,
)
from rtdsl.v4_bounded_relation_optix_wrapper_codegen import (
    generate_trusted_bounded_relation_wrapper_v1,
)
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_ir import AnyHitDeliveryContract, CallbackRole
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    verify_typed_physical_schema,
)
from rtdsl.v4_inline_cuda_codegen import (
    InlineCudaCodegenError,
    lower_formal_leaves_to_inline_cuda,
)
from rtdsl.v4_box_relation_callback import (
    is_exact_standard_relation_callback,
)
from scripts.goal5760_m2_consumer_fixtures import (
    compile_callback,
    exact_relation,
    physical_schema,
    polygon_set_jaccard_candidate_boxes,
)


ROOT = Path(__file__).resolve().parents[1]


def _target():
    return ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256="a" * 64,
        supports_custom_aabb=True, supports_builtin_triangle=True,
    )


def _proof(callback):
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256="b" * 64,
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _compiled(*, capacity=64, minimum_overlap=0.0,
              duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP):
    callback = compile_callback()
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=_target())
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity,
        minimum_overlap_f32=minimum_overlap,
        duplicate_policy=duplicate_policy,
    )
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    return authority, proof, abi, contract


class Goal5760BoundedRelationTests(unittest.TestCase):
    def test_fused_fast_path_requires_exact_standard_semantics(self):
        callback = compile_callback()
        self.assertTrue(is_exact_standard_relation_callback(callback))
        changed_manifest = dataclasses.replace(
            callback.program.manifest,
            linkage_selection_reason="explanatory prose may differ",
        )
        prose_only = dataclasses.replace(
            callback,
            program=dataclasses.replace(
                callback.program, manifest=changed_manifest),
        )
        self.assertTrue(is_exact_standard_relation_callback(prose_only))
        semantic_change = dataclasses.replace(
            prose_only,
            program=dataclasses.replace(
                prose_only.program,
                manifest=dataclasses.replace(
                    changed_manifest,
                    resources=dataclasses.replace(
                        changed_manifest.resources,
                        max_trace_depth=2,
                    ),
                ),
            ),
        )
        self.assertFalse(is_exact_standard_relation_callback(semantic_change))

    def test_schema_and_wrapper_are_deterministic_app_neutral_true_optix(self):
        authority, proof, abi, contract = _compiled()
        first = generate_trusted_bounded_relation_wrapper_v1(
            authority, contract, abi, any_hit_proof_authority=proof)
        second = generate_trusted_bounded_relation_wrapper_v1(
            authority, contract, abi, any_hit_proof_authority=proof)
        self.assertEqual(first, second)
        source = first.source
        for required in (
            "optixTrace", "optixReportIntersection",
            "atomicCAS(", "atomicAdd(params.event_count, 1u)",
            "params.overflowed",
            "reverse_orientation == 0u", "optixGetAttribute_0()",
            "output_intersection_count",
            "params.primitives[primitive_index].item_id",
        ):
            self.assertIn(required, source)
        for forbidden in ("librts", "polygon", "jaccard", "paper"):
            self.assertNotIn(forbidden, source.lower())

    def test_checked_u32_payload_add_is_guarded_before_arithmetic(self):
        authority, proof, abi, _ = _compiled()
        leaf = generate_bounded_relation_numba_leaf(
            authority, abi, CallbackRole.ANY_HIT,
            any_hit_proof_authority=proof)
        source = leaf.generated_source
        guard = source.index("if 1 > 4294967295 - in_payload_hit_count:")
        addition = source.index("in_payload_hit_count + 1")
        self.assertLess(guard, addition)

    def test_inline_staging_keeps_dynamic_any_hit_overflow_guard(self):
        authority, proof, abi, contract = _compiled()
        leaves = tuple(
            generate_bounded_relation_numba_leaf(
                authority, abi, role,
                any_hit_proof_authority=proof)
            for role in CallbackRole)
        wrapper = generate_trusted_bounded_relation_wrapper_v1(
            authority, contract, abi,
            any_hit_proof_authority=proof)
        lowered, _definition_sha256, identities = _inline_wrapper(
            wrapper, abi, leaves)
        self.assertEqual(len(identities), 7)
        self.assertIn("4294967295", lowered.source)
        self.assertIn("status_error_code[0] = 4;", lowered.source)

    def test_staged_guard_proof_is_exact_and_fails_on_drift(self):
        authority, proof, abi, _ = _compiled()
        leaf = generate_bounded_relation_numba_leaf(
            authority, abi, CallbackRole.BOUNDS,
            any_hit_proof_authority=proof)
        with self.assertRaisesRegex(
                InlineCudaCodegenError, "failure-guard proof drift"):
            lower_formal_leaves_to_inline_cuda(
                (leaf,),
                proven_failure_guards_by_role={
                    CallbackRole.BOUNDS.value: frozenset({(2, 999)}),
                },
            )

    def test_capacity_overflow_rejects_partial_result(self):
        with self.assertRaisesRegex(BoundedRelationError, "capacity_overflow"):
            materialize_bounded_relation(
                ((1, 2), (3, 4)), capacity=2,
                duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
                observed_raw_count=3, overflowed=True)

    def test_duplicate_policy_is_explicit_and_canonical(self):
        rows = ((4, 9), (1, 2), (4, 9), (1, 1))
        self.assertEqual(
            materialize_bounded_relation(
                rows, capacity=8,
                duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP),
            ((1, 1), (1, 2), (4, 9)),
        )
        with self.assertRaisesRegex(BoundedRelationError, "duplicate_row"):
            materialize_bounded_relation(
                rows, capacity=8,
                duplicate_policy=RelationDuplicatePolicy.REJECT)

    def test_precanonical_native_projection_is_verified_not_trusted(self):
        self.assertEqual(
            verify_precanonical_bounded_relation(
                ((1, 2), (4, 9)), capacity=2,
                observed_unique_count=2),
            ((1, 2), (4, 9)),
        )
        for invalid in (((4, 9), (1, 2)), ((1, 2), (1, 2))):
            with self.assertRaisesRegex(
                    BoundedRelationError, "precanonical_order"):
                verify_precanonical_bounded_relation(
                    invalid, capacity=2, observed_unique_count=2)
        with self.assertRaisesRegex(BoundedRelationError, "unique_count"):
            verify_precanonical_bounded_relation(
                ((1, 2),), capacity=2, observed_unique_count=2)

    def test_schema_capacity_and_threshold_forgery_fail_closed(self):
        authority, _, _, _ = _compiled()
        with self.assertRaisesRegex(BoundedRelationError, "capacity"):
            verify_bounded_relation_schema(
                authority.physical,
                dataclasses.replace(authority.schema, capacity=0))
        with self.assertRaisesRegex(BoundedRelationError, "minimum_overlap"):
            verify_bounded_relation_schema(
                authority.physical,
                dataclasses.replace(
                    authority.schema, minimum_overlap_f32=float("nan")))
        with self.assertRaisesRegex(
                BoundedRelationError, "minimum_overlap_f32_exactness"):
            verify_bounded_relation_schema(
                authority.physical,
                dataclasses.replace(
                    authority.schema, minimum_overlap_f32=0.1))

    def test_two_librts_contracts_use_same_relation_semantics(self):
        indexed = ((0.0, 0.0, 2.0, 2.0, 10),
                   (4.0, 4.0, 6.0, 6.0, 20),
                   (2.0, 0.0, 3.0, 1.0, 30))
        sources = ((1.0, 1.0, 2.5, 2.5, 100),
                   (5.0, 5.0, 7.0, 7.0, 200))
        prepared_query = exact_relation(sources, indexed, minimum_overlap=0.0)
        overlap_filter = exact_relation(sources, indexed, minimum_overlap=0.75)
        self.assertEqual(prepared_query, ((100, 10), (100, 30), (200, 20)))
        self.assertEqual(overlap_filter, ((100, 10), (200, 20)))
        first = _compiled(capacity=16, minimum_overlap=0.0)[0]
        second = _compiled(capacity=16, minimum_overlap=0.75)[0]
        self.assertEqual(
            first.physical.callback.ir_sha256,
            second.physical.callback.ir_sha256)
        self.assertNotEqual(first.schema.schema_sha256, second.schema.schema_sha256)

    def test_true_non_librts_polygon_jaccard_consumer_is_real(self):
        source_path = ROOT / "examples/current/features/spatial/rtdl_polygon_set_jaccard.py"
        source = source_path.read_text(encoding="utf-8")
        self.assertIn("collect_polygon_pair_candidates_bounded_optix", source)
        indexed, sources = polygon_set_jaccard_candidate_boxes()
        self.assertEqual(
            exact_relation(sources, indexed),
            ((1, 10), (2, 10), (2, 11)),
        )

    def test_native_exports_one_generic_symbol_and_two_pass_orientation(self):
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text()
        implementation = (
            ROOT / "src/native/optix/rtdl_optix_v4_callback_poc.cpp").read_text()
        symbol = "rtdl_optix_v4_run_bounded_relation_callback_v1"
        self.assertEqual(api.count(symbol), 1)
        self.assertIn("launch_pass(indexed, sources, indexed_accel, 0u)", implementation)
        self.assertIn("launch_pass(sources, indexed, source_accel, 1u)", implementation)
        self.assertIn("OPTIX_PRIMITIVE_TYPE_FLAGS_CUSTOM", implementation)
        for forbidden in ("librts", "polygon", "jaccard"):
            self.assertNotIn(forbidden, implementation.lower())


if __name__ == "__main__":
    unittest.main()
