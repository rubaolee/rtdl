import unittest
from pathlib import Path
import json

from rtdsl.optix_runtime import (
    OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL,
    OptixNativeDevicePairColumnOutput,
    PairColumnStreamCapacityStatus,
)


ROOT = Path(__file__).resolve().parents[1]
SLICE_ARTIFACT = ROOT / "docs" / "reports" / "goal3394_optix_exact_membership_device_columns_live_probe_2026-06-04.json"
FULL_ARTIFACT = ROOT / "docs" / "reports" / "goal3398_full_br_county_exact_device_columns_2026-06-04.json"
OVERFLOW_ARTIFACT = ROOT / "docs" / "reports" / "goal3400_exact_device_columns_overflow_probe_2026-06-04.json"


class _DummyOwner:
    handle_value = 0


class Goal3403PairColumnCapacityStatusContractTest(unittest.TestCase):
    def test_capacity_status_accepts_success_and_reports_no_retry_hint(self):
        status = PairColumnStreamCapacityStatus(capacity=11316, row_count=11316, required_capacity=11316)

        self.assertFalse(status.overflowed)
        self.assertIsNone(status.retry_capacity_hint)
        self.assertEqual(
            status.to_metadata(),
            {
                "capacity": 11316,
                "row_count": 11316,
                "required_capacity": 11316,
                "overflowed": False,
                "overflow_policy": "fail_closed",
                "retry_capacity_hint": None,
                "partial_result_returned": False,
            },
        )

    def test_capacity_status_requires_fail_closed_overflow(self):
        status = PairColumnStreamCapacityStatus(
            capacity=100,
            row_count=0,
            required_capacity=11316,
            overflowed=True,
        )

        self.assertEqual(status.retry_capacity_hint, 11316)
        with self.assertRaisesRegex(RuntimeError, "required_capacity=11316"):
            status.raise_if_overflowed(operation="exact device columns")

        with self.assertRaisesRegex(ValueError, "must not expose partial rows"):
            PairColumnStreamCapacityStatus(capacity=100, row_count=1, required_capacity=11316, overflowed=True)
        with self.assertRaisesRegex(ValueError, "must require more than capacity"):
            PairColumnStreamCapacityStatus(capacity=100, row_count=0, required_capacity=100, overflowed=True)
        with self.assertRaisesRegex(ValueError, "must fit within capacity"):
            PairColumnStreamCapacityStatus(capacity=100, row_count=101, required_capacity=101, overflowed=False)

    def test_exact_pair_column_output_metadata_carries_capacity_plan(self):
        output = OptixNativeDevicePairColumnOutput(
            library=object(),
            owner=_DummyOwner(),
            left_ids_device_ptr=0,
            right_ids_device_ptr=0,
            row_count=0,
            capacity=100,
            candidate_event_count=11316,
            overflow=True,
            device_ordinal=0,
            traversal_seconds=0.0,
            native_symbol=OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL,
            field_names=("point_id", "shape_id"),
        )

        self.assertEqual(output.required_capacity, 11316)
        self.assertEqual(output.retry_capacity_hint, 11316)
        metadata = output.to_metadata()

        for scope in (
            metadata["capacity_status"],
            metadata["runtime"]["capacity_status"],
            metadata["typed_result_stream"]["capacity_status"],
            metadata["v2_8_typed_producer_metadata"]["capacity_status"],
        ):
            self.assertEqual(scope["capacity"], 100)
            self.assertEqual(scope["row_count"], 0)
            self.assertEqual(scope["required_capacity"], 11316)
            self.assertTrue(scope["overflowed"])
            self.assertEqual(scope["retry_capacity_hint"], 11316)
            self.assertFalse(scope["partial_result_returned"])

        producer = metadata["v2_8_typed_producer_metadata"]
        self.assertEqual(producer["required_capacity"], 11316)
        self.assertEqual(producer["retry_capacity_hint"], 11316)
        self.assertFalse(producer["release_authorized"])
        self.assertFalse(producer["true_zero_copy_claim_authorized"])

    def test_overflowed_cupy_wrap_error_includes_retry_guidance(self):
        output = OptixNativeDevicePairColumnOutput(
            library=object(),
            owner=object(),
            left_ids_device_ptr=0,
            right_ids_device_ptr=0,
            row_count=0,
            capacity=100,
            candidate_event_count=11316,
            overflow=True,
            device_ordinal=0,
            traversal_seconds=0.0,
            native_symbol=OPTIX_CLOSED_SHAPE_MEMBERSHIP_EXACT_DEVICE_COLUMNS_SYMBOL,
            field_names=("point_id", "shape_id"),
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "cannot wrap an overflowed device pair-column stream; capacity=100 required_capacity=11316",
        ):
            output.as_cupy_columns()

    def test_refreshed_pod_artifacts_carry_capacity_status(self):
        slice_payload = json.loads(SLICE_ARTIFACT.read_text(encoding="utf-8"))
        full_payload = json.loads(FULL_ARTIFACT.read_text(encoding="utf-8"))
        overflow_payload = json.loads(OVERFLOW_ARTIFACT.read_text(encoding="utf-8"))

        for payload, expected in ((slice_payload, 11316), (full_payload, 47262)):
            self.assertEqual(payload["rtdl_commit"][:8], "8bdc8a64")
            for status in (
                payload["metadata"]["capacity_status"],
                payload["metadata"]["runtime"]["capacity_status"],
                payload["metadata"]["typed_result_stream"]["capacity_status"],
                payload["metadata"]["v2_8_typed_producer_metadata"]["capacity_status"],
            ):
                self.assertEqual(status["capacity"], expected)
                self.assertEqual(status["row_count"], expected)
                self.assertEqual(status["required_capacity"], expected)
                self.assertFalse(status["overflowed"])
                self.assertIsNone(status["retry_capacity_hint"])
                self.assertFalse(status["partial_result_returned"])

        self.assertEqual(overflow_payload["rtdl_commit"][:8], "8bdc8a64")
        overflow_status = overflow_payload["capacity_status"]
        self.assertEqual(overflow_status["capacity"], 100)
        self.assertEqual(overflow_status["row_count"], 0)
        self.assertEqual(overflow_status["required_capacity"], 11316)
        self.assertTrue(overflow_status["overflowed"])
        self.assertEqual(overflow_status["retry_capacity_hint"], 11316)
        self.assertFalse(overflow_status["partial_result_returned"])


if __name__ == "__main__":
    unittest.main()
