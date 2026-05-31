from pathlib import Path
from collections.abc import Mapping, Sequence
import unittest

import rtdsl as rt
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_hit_columns
from tests.goal2740_hit_stream_cross_partner_transfer_plan_test import _device_payload_columns


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal2879_torch_carrier_seam_authority_provenance_2026-05-31.md"


class Goal2879TorchCarrierSeamAuthorityProvenanceTest(unittest.TestCase):
    def test_torch_carrier_metadata_cannot_carry_authority_fields(self) -> None:
        adapter = rt.describe_v2_5_hit_stream_torch_carrier_adapter(
            _device_hit_columns(),
            _device_payload_columns(),
        )

        self.assertIn(
            "transfer_copy_lifetime_authority",
            rt.GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS,
        )
        self.assertNotIn("transfer_copy_lifetime_authority", adapter)
        self.assertEqual("triton_launch_carrier_only", adapter["carrier_metadata_scope"])
        self.assertEqual("neutral_buffer_seam_only", adapter["authoritative_metadata_origin"])
        self.assertEqual(
            (),
            _key_hits(adapter, rt.GENERIC_HIT_STREAM_TORCH_CARRIER_FORBIDDEN_AUTHORITY_FIELDS),
        )

    def test_authority_validation_reports_seam_only_provenance(self) -> None:
        validation = rt.validate_v2_5_hit_stream_neutral_seam_authority(
            _device_hit_columns(),
            _device_payload_columns(),
        )

        self.assertEqual("accept", validation["status"])
        self.assertEqual("neutral_buffer_seam", validation["transfer_copy_lifetime_authority"])
        self.assertEqual((), validation["torch_carrier_forbidden_authority_field_hits"])
        self.assertEqual("triton_launch_carrier_only", validation["torch_carrier_metadata_scope"])
        self.assertEqual(
            "neutral_buffer_seam_only",
            validation["torch_carrier_authoritative_metadata_origin"],
        )
        self.assertEqual((), validation["neutral_seam_missing_authority_fields"])

    def test_transfer_plan_still_allows_triton_carrier_but_not_other_partners(self) -> None:
        triton = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_sum_f64",
            partner="triton",
        )
        numba = rt.plan_v2_5_hit_stream_partner_transfer(
            _device_hit_columns(),
            _device_payload_columns(),
            operation="segmented_count_i64",
            partner="numba",
        )

        self.assertTrue(triton["torch_carrier_allowed"])
        self.assertEqual("cuda_array_interface_to_torch_carrier", triton["carrier_protocol"])
        self.assertFalse(numba["torch_carrier_allowed"])
        self.assertEqual("cuda_array_interface_descriptor", numba["carrier_protocol"])

    def test_readiness_indexes_goal2879(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=ROOT)
        validation = rt.validate_v2_5_internal_readiness_packet(repo_root=ROOT)
        path = "docs/reports/goal2879_torch_carrier_seam_authority_provenance_2026-05-31.md"

        self.assertEqual("accept", validation["status"])
        self.assertTrue(packet["required_report_presence"][path])
        self.assertIn("keep_goal2879_torch_carrier_seam_authority_provenance_green", packet["allowed_next_actions"])

    def test_report_records_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "Goal2879",
            "triton_launch_carrier_only",
            "neutral_buffer_seam_only",
            "not a v2.5 release authorization",
            "not true-zero-copy wording",
            "not package-install wording",
        ):
            self.assertIn(phrase, text)


def _key_hits(payload: object, keys: Sequence[str], *, prefix: str = "") -> tuple[str, ...]:
    hits: list[str] = []
    key_set = set(keys)
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if str(key) in key_set:
                hits.append(path)
            hits.extend(_key_hits(value, keys, prefix=path))
    elif isinstance(payload, Sequence) and not isinstance(payload, (str, bytes, bytearray)):
        for index, value in enumerate(payload):
            path = f"{prefix}[{index}]" if prefix else f"[{index}]"
            hits.extend(_key_hits(value, keys, prefix=path))
    return tuple(hits)


if __name__ == "__main__":
    unittest.main()
