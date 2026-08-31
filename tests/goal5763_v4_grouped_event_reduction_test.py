from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path
import unittest

from rtdsl.v4_grouped_event_reduction import (
    EventFieldProjection,
    EventFieldSource,
    EventProducerCompletionKind,
    GroupedEventReductionError,
    GroupedEventReductionSchema,
    I64LookupTable,
    compile_grouped_event_reduction,
    materialize_verified_grouped_event_batch,
    product_source_has_forbidden_identity_dispatch,
    reference_grouped_i64x2_count_sum,
    verify_event_producer_evidence,
)


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()).hexdigest()


def _receipt() -> dict[str, object]:
    body: dict[str, object] = {
        "schema": "rtdl.physical_execution.traversal_receipt.v1",
        "provider_library": "librtdl_optix",
        "provider_library_path": "/frozen/librtdl_optix.so",
        "provider_library_sha256": "a" * 64,
        "route_identity": "v4_callback_ir:custom_aabb_bounded_relation_v1",
        "semantic_digest": "b" * 64,
        "output_digest": "c" * 64,
        "nonce": {"hi": 1, "lo": 2},
        "physical_executor_classification": "optix_traversal_observed",
        "expected_program_bundles": ["v4_custom_aabb_bounded_relation_composed"],
        "expected_program_bundle_ids": [123],
        "expected_program_observed_at_receipt_edge": True,
        "native_snapshot": {
            "successful_launch_count": 2,
            "complete_context_launch_count": 2,
            "failed_launch_count": 0,
            "incomplete_context_launch_count": 0,
            "pending_context_at_finish": 0,
            "session_error": 0,
            "first_traversable": 11,
            "last_traversable": 12,
        },
        "claim_rules": {"output_digest_bound": True},
    }
    body["receipt_sha256"] = _digest(body)
    return body


def _case():
    rows = ((10, 20), (11, 21), (12, 22))
    producer = verify_event_producer_evidence(
        rows,
        producer_contract_sha256="d" * 64,
        maximum_event_rows=8,
        traversal_receipt=_receipt(),
        completion_kind=EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION,
        semantic_completion_authority_sha256="e" * 64,
    )
    source_groups = I64LookupTable.from_rows(((10, 1), (11, 1), (12, 2)))
    item_groups = I64LookupTable.from_rows(((20, 7), (21, 7), (22, 9)))
    values = I64LookupTable.from_rows(((10, 4), (11, 3), (12, -2)))
    schema = GroupedEventReductionSchema(
        producer_contract_sha256="d" * 64,
        maximum_event_rows=8,
        key0=EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, source_groups.table_sha256),
        key1=EventFieldProjection(
            EventFieldSource.ITEM_LOOKUP, item_groups.table_sha256),
        signed_value=EventFieldProjection(
            EventFieldSource.SOURCE_LOOKUP, values.table_sha256),
    )
    tables = (source_groups, item_groups, values)
    batch = materialize_verified_grouped_event_batch(
        schema, producer, lookup_tables=tables)
    return producer, schema, tables, batch


class Goal5763V4GroupedEventReductionTest(unittest.TestCase):
    def test_closed_projection_and_route_independent_exact_reduction(self) -> None:
        _, _, _, batch = _case()
        self.assertEqual(
            reference_grouped_i64x2_count_sum(batch),
            ((1, 7, 2, 7), (2, 9, 1, -2)),
        )
        self.assertEqual(batch.event_id, (0, 1, 2))
        self.assertEqual(batch.key0, (1, 1, 2))

    def test_compiler_reuses_checked_numba_device_partner(self) -> None:
        producer, schema, tables, _ = _case()
        compiled = compile_grouped_event_reduction(
            schema, producer, lookup_tables=tables)
        metadata = compiled.to_dict()
        self.assertEqual(
            metadata["physical_stages"][-1],
            "numba_cuda_checked_grouped_i64x2_count_sum",
        )
        self.assertEqual(
            metadata["action_program"]["signed_overflow_policy"],
            "fail_closed",
        )
        self.assertFalse(metadata["application_or_publication_identity_used"])

    def test_template_identity_is_stable_while_instance_identity_is_bound(self) -> None:
        producer, schema, tables, _ = _case()
        first = compile_grouped_event_reduction(
            schema, producer, lookup_tables=tables).to_dict()
        other = verify_event_producer_evidence(
            ((10, 20), (11, 21), (12, 22)),
            producer_contract_sha256="d" * 64,
            maximum_event_rows=8,
            traversal_receipt=_receipt(),
            completion_kind=(
                EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION),
            semantic_completion_authority_sha256="f" * 64,
        )
        second = compile_grouped_event_reduction(
            schema, other, lookup_tables=tables).to_dict()
        self.assertEqual(
            first["template_contract_sha256"],
            second["template_contract_sha256"],
        )
        self.assertNotEqual(
            first["action_semantic_digest"], second["action_semantic_digest"])

    def test_behavioral_optix_receipt_is_mandatory(self) -> None:
        receipt = _receipt()
        receipt["physical_executor_classification"] = "no_optix_launch_observed"
        receipt["receipt_sha256"] = _digest({
            key: value for key, value in receipt.items()
            if key != "receipt_sha256"
        })
        with self.assertRaisesRegex(
                GroupedEventReductionError, "behavioral_optix_receipt"):
            verify_event_producer_evidence(
                ((1, 2),), producer_contract_sha256="d" * 64,
                maximum_event_rows=1, traversal_receipt=receipt,
                completion_kind=EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION,
                semantic_completion_authority_sha256="e" * 64)

    def test_receipt_digest_tamper_fails_closed(self) -> None:
        receipt = _receipt()
        receipt["output_digest"] = "e" * 64
        with self.assertRaisesRegex(
                GroupedEventReductionError, "traversal_receipt_digest"):
            verify_event_producer_evidence(
                ((1, 2),), producer_contract_sha256="d" * 64,
                maximum_event_rows=1, traversal_receipt=receipt,
                completion_kind=EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION,
                semantic_completion_authority_sha256="e" * 64)

    def test_direct_relation_requires_receipt_bound_rows(self) -> None:
        with self.assertRaisesRegex(
                GroupedEventReductionError, "direct_relation_output_binding"):
            verify_event_producer_evidence(
                ((1, 2),), producer_contract_sha256="d" * 64,
                maximum_event_rows=1, traversal_receipt=_receipt())

    def test_forged_producer_evidence_fails_closed(self) -> None:
        producer, schema, tables, _ = _case()
        forged = replace(producer, producer_semantic_rows=((99, 100),))
        with self.assertRaisesRegex(GroupedEventReductionError, "producer_seal"):
            materialize_verified_grouped_event_batch(
                schema, forged, lookup_tables=tables)

    def test_event_capacity_fails_closed(self) -> None:
        with self.assertRaisesRegex(GroupedEventReductionError, "capacity_overflow"):
            verify_event_producer_evidence(
                ((1, 2), (2, 3)), producer_contract_sha256="d" * 64,
                maximum_event_rows=1, traversal_receipt=_receipt(),
                completion_kind=EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION,
                semantic_completion_authority_sha256="e" * 64)

    def test_duplicate_logical_event_fails_closed(self) -> None:
        with self.assertRaisesRegex(
                GroupedEventReductionError, "duplicate_logical_event"):
            verify_event_producer_evidence(
                ((1, 2), (1, 2)), producer_contract_sha256="d" * 64,
                maximum_event_rows=2, traversal_receipt=_receipt(),
                completion_kind=EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION,
                semantic_completion_authority_sha256="e" * 64)

    def test_missing_projection_key_fails_closed(self) -> None:
        producer, schema, tables, _ = _case()
        incomplete = I64LookupTable.from_rows(((10, 1), (11, 1)))
        changed = replace(
            schema,
            key0=EventFieldProjection(
                EventFieldSource.SOURCE_LOOKUP, incomplete.table_sha256),
        )
        with self.assertRaisesRegex(
                GroupedEventReductionError, "missing_projection_key"):
            materialize_verified_grouped_event_batch(
                changed, producer,
                lookup_tables=(incomplete, tables[1], tables[2]))

    def test_duplicate_lookup_key_fails_closed(self) -> None:
        with self.assertRaisesRegex(
                GroupedEventReductionError, "duplicate_lookup_key"):
            I64LookupTable.from_rows(((1, 2), (1, 3)))

    def test_mutated_compiler_batch_fails_closed(self) -> None:
        _, _, _, batch = _case()
        forged = replace(batch, signed_value=(4, 3, 99))
        with self.assertRaisesRegex(GroupedEventReductionError, "batch_seal"):
            reference_grouped_i64x2_count_sum(forged)

    def test_signed_overflow_is_rejected_by_reference_contract(self) -> None:
        producer = verify_event_producer_evidence(
            ((1, 10), (2, 11)), producer_contract_sha256="d" * 64,
            maximum_event_rows=2, traversal_receipt=_receipt(),
            completion_kind=EventProducerCompletionKind.VERIFIED_EXACT_PARTNER_COMPLETION,
            semantic_completion_authority_sha256="e" * 64)
        source_group = I64LookupTable.from_rows(((1, 5), (2, 5)))
        item_group = I64LookupTable.from_rows(((10, 6), (11, 6)))
        value = I64LookupTable.from_rows(((1, (1 << 63) - 1), (2, 1)))
        schema = GroupedEventReductionSchema(
            "d" * 64, 2,
            EventFieldProjection(
                EventFieldSource.SOURCE_LOOKUP, source_group.table_sha256),
            EventFieldProjection(
                EventFieldSource.ITEM_LOOKUP, item_group.table_sha256),
            EventFieldProjection(
                EventFieldSource.SOURCE_LOOKUP, value.table_sha256),
        )
        batch = materialize_verified_grouped_event_batch(
            schema, producer, lookup_tables=(source_group, item_group, value))
        with self.assertRaisesRegex(
                GroupedEventReductionError, "signed_reduction_overflow"):
            reference_grouped_i64x2_count_sum(batch)

    def test_product_source_has_no_identity_dispatch(self) -> None:
        source = Path(
            "src/rtdsl/v4_grouped_event_reduction.py").read_text(encoding="utf-8")
        self.assertFalse(product_source_has_forbidden_identity_dispatch(source))


if __name__ == "__main__":
    unittest.main()
