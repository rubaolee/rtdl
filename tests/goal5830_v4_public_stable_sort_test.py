from __future__ import annotations

import dataclasses
import hashlib
import itertools
import random
import unittest

from examples.current.v4_public_stable_sort import (
    StableSortMappingError,
    encode_stable_sort,
    geometry_relation_reference,
    predecessor_relation_oracle,
    primitive_index_attack_rows,
    stable_sort_from_relation,
    stable_sort_oracle,
)
from rtdsl.v4 import (
    AnyHitProtocolProof,
    BoundedRelationProtocol,
    CompilerProtocolProjection,
    ProtocolLifecycleError,
    compile_protocol_program,
    standard_protocol_physical_plan,
    verify_protocol_contract,
)


def _sha(label: str) -> str:
    return hashlib.sha256(label.encode("utf-8")).hexdigest()


def _proof(protocol: BoundedRelationProtocol) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=_sha("goal5830-test-order-independence-proof"),
        proof_kind="external_machine_checked_order_independence_v1",
    )


class Goal5830PublicStableSortTests(unittest.TestCase):
    def assert_mapping_matches_oracles(
        self,
        values,
        *,
        indexed_order=None,
        source_order=None,
    ):
        encoding = encode_stable_sort(
            values,
            indexed_order=indexed_order,
            source_order=source_order,
        )
        pairwise = predecessor_relation_oracle(values)
        self.assertEqual(geometry_relation_reference(encoding), pairwise)
        outcome = stable_sort_from_relation(values, pairwise)
        self.assertEqual(outcome.sorted_records, stable_sort_oracle(values))
        self.assertEqual(
            outcome.sorted_values,
            tuple(value for value, _item_id in stable_sort_oracle(values)),
        )
        return encoding, outcome

    def test_main_duplicate_key_example_is_exact_and_stable(self):
        values = (2, 1, 2, 0)
        encoding, outcome = self.assert_mapping_matches_oracles(
            values,
            indexed_order=(2, 0, 3, 1),
            source_order=(3, 2, 1, 0),
        )
        self.assertEqual(encoding.order_codes, (10, 6, 12, 3))
        self.assertEqual(encoding.capacity, 10)
        self.assertEqual(
            predecessor_relation_oracle(values),
            (
                (0, 0), (0, 1), (0, 3),
                (1, 1), (1, 3),
                (2, 0), (2, 1), (2, 2), (2, 3),
                (3, 3),
            ),
        )
        self.assertEqual(outcome.ranks_by_item_id, (2, 1, 3, 0))
        self.assertEqual(outcome.sorted_records, ((0, 3), (1, 1), (2, 0), (2, 2)))

    def test_duplicate_stability_monotone_signed_and_singleton(self):
        cases = (
            (5,) * 8,
            tuple(range(8)),
            tuple(reversed(range(8))),
            (-2, 0, -2, 1),
            (7,),
        )
        for values in cases:
            with self.subTest(values=values):
                _encoding, outcome = self.assert_mapping_matches_oracles(values)
                equal_key_ids = [
                    item_id for value, item_id in outcome.sorted_records
                    if value == values[0]
                ]
                expected_equal_key_ids = [
                    item_id for item_id, value in enumerate(values)
                    if value == values[0]
                ]
                self.assertEqual(equal_key_ids, expected_equal_key_ids)

    def test_exact_binary32_quarter_grid_boundary(self):
        encoding, _outcome = self.assert_mapping_matches_oracles((1_398_101, 0))
        self.assertEqual(encoding.order_codes, ((1 << 22) - 1, 1))
        with self.assertRaisesRegex(
            StableSortMappingError, "exact binary32 quarter grid",
        ):
            encode_stable_sort((0, 1_398_101))

    def test_invalid_application_inputs_fail_before_rtdl(self):
        invalid = ((), (1, True), (1, 2.0), ("1", 2))
        for values in invalid:
            with self.subTest(values=values):
                with self.assertRaises(StableSortMappingError):
                    encode_stable_sort(values)
        with self.assertRaisesRegex(StableSortMappingError, "indexed_order"):
            encode_stable_sort((2, 1, 0), indexed_order=(0, 0, 2))
        with self.assertRaisesRegex(StableSortMappingError, "source_order"):
            encode_stable_sort((2, 1, 0), source_order=(0, 1))
        with self.assertRaisesRegex(StableSortMappingError, "integer item ids"):
            encode_stable_sort((2, 1), indexed_order=(False, True))
        with self.assertRaisesRegex(StableSortMappingError, "binary32 domain"):
            encode_stable_sort((0, 10 ** 1000))

    def test_256_frozen_random_cases_match_pair_and_sort_oracles(self):
        for seed in range(256):
            generator = random.Random(seed)
            count = 1 + seed % 64
            values = tuple(generator.randint(-32, 32) for _ in range(count))
            indexed = list(range(count))
            sources = list(range(count))
            generator.shuffle(indexed)
            generator.shuffle(sources)
            with self.subTest(seed=seed, count=count):
                self.assert_mapping_matches_oracles(
                    values,
                    indexed_order=indexed,
                    source_order=sources,
                )

    def test_exhaustive_small_signed_duplicate_arrays(self):
        case_count = 0
        for count in range(1, 7):
            for values in itertools.product(range(-2, 3), repeat=count):
                self.assert_mapping_matches_oracles(values)
                case_count += 1
        self.assertEqual(case_count, 19_530)

    def test_all_main_case_physical_orders_preserve_logical_relation(self):
        values = (2, 1, 2, 0)
        expected = predecessor_relation_oracle(values)
        permutations = tuple(itertools.permutations(range(4)))
        for indexed_order in permutations:
            for source_order in permutations:
                encoding = encode_stable_sort(
                    values,
                    indexed_order=indexed_order,
                    source_order=source_order,
                )
                self.assertEqual(geometry_relation_reference(encoding), expected)

    def test_primitive_position_is_not_application_item_identity(self):
        values = (2, 1, 2, 0)
        indexed_order = (2, 0, 3, 1)
        correct = predecessor_relation_oracle(values)
        wrong = primitive_index_attack_rows(correct, indexed_order)
        self.assertEqual(
            wrong,
            (
                (0, 1), (0, 2), (0, 3),
                (1, 2), (1, 3),
                (2, 0), (2, 1), (2, 2), (2, 3),
                (3, 2),
            ),
        )
        with self.assertRaises(StableSortMappingError):
            stable_sort_from_relation(values, wrong)
        self.assertEqual(
            stable_sort_from_relation(values, correct).sorted_records,
            stable_sort_oracle(values),
        )

    def test_incomplete_relation_cannot_be_consumed_as_a_sort(self):
        values = (2, 1, 2, 0)
        complete = list(predecessor_relation_oracle(values))
        complete.remove((2, 0))
        with self.assertRaisesRegex(StableSortMappingError, "unique ranks"):
            stable_sort_from_relation(values, complete)

    def test_public_standard_protocol_accepts_without_knowing_sorting(self):
        # Negative control: admission validates the declared callback protocol,
        # not this application's sorting theorem.
        protocol = BoundedRelationProtocol(capacity=10, minimum_overlap_f32=0.25)
        plan = standard_protocol_physical_plan(protocol)
        verified = compile_protocol_program(
            protocol,
            physical_plan=plan,
            any_hit_proof=_proof(protocol),
        )
        self.assertEqual(verified.identity.family, protocol.family)

        # A complete, capacity-10 relation can still encode the wrong total
        # order.  Here the equal-valued records 0 and 2 are reversed.  The
        # generic protocol admits the callback shape; only the application
        # oracle knows that the resulting order is not stable.
        wrong_rows = tuple(
            row
            for source_id, predecessors in (
                (0, (3, 1, 2, 0)),
                (1, (3, 1)),
                (2, (3, 1, 2)),
                (3, (3,)),
            )
            for row in ((source_id, predecessor_id) for predecessor_id in predecessors)
        )
        self.assertEqual(len(wrong_rows), protocol.capacity)
        wrong_outcome = stable_sort_from_relation((2, 1, 2, 0), wrong_rows)
        self.assertEqual(
            wrong_outcome.sorted_records,
            ((0, 3), (1, 1), (2, 2), (2, 0)),
        )
        self.assertNotEqual(
            wrong_outcome.sorted_records, stable_sort_oracle((2, 1, 2, 0)))

    def test_mutated_public_physical_plan_rejects_before_materialization(self):
        protocol = BoundedRelationProtocol(capacity=10, minimum_overlap_f32=0.25)
        plan = standard_protocol_physical_plan(protocol)
        with self.assertRaisesRegex(
            ProtocolLifecycleError, "PL034_PHYSICAL_PLAN_MISMATCH",
        ):
            compile_protocol_program(
                protocol,
                physical_plan=dataclasses.replace(
                    plan,
                    output_contract="canonical_u32_primitive_position_rows",
                ),
                any_hit_proof=_proof(protocol),
            )

    def test_exact_cp002_compiler_projection_rejects_before_native_load(self):
        """The sorting attack's attr0 substitution is live in admission."""

        from rtdsl import v4_callback_lifecycle as lifecycle

        protocol = BoundedRelationProtocol(capacity=10, minimum_overlap_f32=0.25)
        plan = standard_protocol_physical_plan(protocol)
        verified = compile_protocol_program(
            protocol, physical_plan=plan, any_hit_proof=_proof(protocol))
        executable_sha = _sha("goal5830-same-executable")
        declaration = lifecycle._declared_protocol_contract(
            verified, executable_sha256=executable_sha)
        projection = CompilerProtocolProjection(
            family=declaration.family,
            task_semantics_sha256=declaration.task_semantics_sha256,
            role_effects=declaration.role_effects,
            attribute_abi_ownership=(("attr0", "primitive_index_u32"),),
            physical_bindings=declaration.physical_bindings,
            continuation_policy=declaration.continuation_policy,
            actual_executable_sha256=executable_sha,
            generated_device_source_sha256=_sha("goal5830-device"),
            generated_host_source_sha256=_sha("goal5830-host"),
        )
        decision = verify_protocol_contract(declaration, projection)
        self.assertEqual(decision.verdict, "REJECT")
        self.assertEqual(len(decision.findings), 1)
        self.assertEqual(
            decision.findings[0].reason_id,
            "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
        )


if __name__ == "__main__":
    unittest.main()
