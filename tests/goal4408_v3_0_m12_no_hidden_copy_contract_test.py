from __future__ import annotations

import json
from pathlib import Path
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
M11_EVIDENCE_JSON = ROOT / "docs/reports/goal4407_v3_0_m11_no_hidden_copy_evidence_65536_2026-06-15.json"
M12_REPORT = ROOT / "docs/reports/goal4408_v3_0_m12_no_hidden_copy_contract_2026-06-15.md"


class Goal4408V30M12NoHiddenCopyContractTest(unittest.TestCase):
    def test_classifier_accepts_small_non_column_launch_parameter_copy(self) -> None:
        classification = rt.classify_no_hidden_copy_transfer_snapshot(
            {
                "total_calls": 1,
                "total_bytes": 96,
                "host_to_device_calls": 1,
                "host_to_device_bytes": 96,
                "device_to_host_calls": 0,
                "device_to_device_calls": 0,
                "unknown_calls": 0,
            },
            min_named_column_bytes=262_144,
        )
        self.assertEqual(rt.V3_NO_HIDDEN_COPY_CONTRACT_VERSION, classification["contract_version"])
        self.assertTrue(classification["no_hidden_column_copy_ready"])
        self.assertTrue(classification["true_zero_copy_ready"])
        self.assertEqual((), classification["disallowed_reasons"])

    def test_classifier_rejects_hidden_copy_shapes(self) -> None:
        cases = (
            (
                {"device_to_host_calls": 1, "device_to_host_bytes": 64},
                "device_to_host_copy_observed",
            ),
            (
                {"device_to_device_calls": 1, "device_to_device_bytes": 64},
                "device_to_device_copy_observed",
            ),
            (
                {"unknown_calls": 1, "unknown_bytes": 64},
                "unknown_direction_copy_observed",
            ),
            (
                {"host_to_device_calls": 1, "host_to_device_bytes": 8192},
                "host_to_device_bytes_exceed_allowed_launch_parameter_scope",
            ),
            (
                {"host_to_device_calls": 1, "host_to_device_bytes": 262_144},
                "host_to_device_bytes_reach_named_column_size",
            ),
        )
        for overrides, reason in cases:
            snapshot = {
                "total_calls": 1,
                "total_bytes": max(int(overrides.get("host_to_device_bytes", 0) or 0), 64),
                "host_to_device_calls": 0,
                "host_to_device_bytes": 0,
                "device_to_host_calls": 0,
                "device_to_device_calls": 0,
                "unknown_calls": 0,
            }
            snapshot.update(overrides)
            classification = rt.classify_no_hidden_copy_transfer_snapshot(
                snapshot,
                min_named_column_bytes=262_144,
            )
            self.assertFalse(classification["no_hidden_column_copy_ready"])
            self.assertIn(reason, classification["disallowed_reasons"])

    def test_named_column_byte_descriptor_helper_is_app_agnostic(self) -> None:
        self.assertEqual(
            128,
            rt.min_named_column_bytes_from_descriptors(
                {
                    "candidate_ids": {"row_count": 32, "element_size": 4},
                    "weights": {"nbytes": 1024},
                }
            ),
        )
        self.assertEqual(
            256,
            rt.min_named_column_bytes_from_descriptors(
                (
                    {"name": "labels", "bytes": 512},
                    {"name": "roots", "byte_count": 256},
                )
            ),
        )
        with self.assertRaisesRegex(GraphValidationError, "no named column byte sizes"):
            rt.min_named_column_bytes_from_descriptors({"labels": {"dtype": "u32"}})

    def test_metadata_annotation_is_copy_on_write_and_records_contract_source(self) -> None:
        metadata = {
            "same_stream_evidence": {
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(),
            }
        }
        classification = rt.classify_no_hidden_copy_transfer_snapshot(
            _snapshot(),
            min_named_column_bytes=262_144,
        )
        annotated = rt.annotate_no_hidden_copy_metadata(metadata, classification)
        self.assertIsNot(metadata, annotated)
        self.assertNotIn("true_zero_copy_ready", metadata["same_stream_evidence"])
        evidence = annotated["same_stream_evidence"]
        self.assertTrue(evidence["true_zero_copy_ready"])
        self.assertEqual(
            rt.V3_NO_HIDDEN_COPY_READINESS_SOURCE,
            evidence["true_zero_copy_readiness_source"],
        )
        self.assertEqual(
            rt.V3_NO_HIDDEN_COPY_CONTRACT_VERSION,
            evidence["no_hidden_copy_contract_version"],
        )

    def test_generic_payload_validator_accepts_synthetic_payload_and_m11_artifact(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_no_hidden_copy_payload(
            payload,
            expected_version="unit.no_hidden_copy",
            expected_status="unit_ready",
            required_partners=("cupy", "numba"),
        )
        self.assertTrue(validation["true_zero_copy_ready"])
        self.assertFalse(validation["public_claim_authorized"])

        m11_payload = json.loads(M11_EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_no_hidden_copy_payload(
            m11_payload,
            expected_version=rt.V3_M11_NO_HIDDEN_COPY_VERSION,
            expected_status=rt.V3_M11_NO_HIDDEN_COPY_STATUS,
            required_partners=rt.V3_M11_PARTNERS,
        )
        self.assertTrue(validation["no_hidden_column_copy_ready"])

    def test_generic_payload_validator_rejects_public_promotion(self) -> None:
        payload = _synthetic_payload()
        payload["claim_boundary"] = dict(payload["claim_boundary"])
        payload["claim_boundary"]["true_zero_copy_public_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "must not authorize"):
            rt.validate_no_hidden_copy_payload(
                payload,
                expected_version="unit.no_hidden_copy",
                expected_status="unit_ready",
                required_partners=("cupy", "numba"),
            )

    def test_summary_and_report_capture_m12_contract_boundary(self) -> None:
        ready = rt.classify_no_hidden_copy_transfer_snapshot(
            _snapshot(),
            min_named_column_bytes=262_144,
        )
        blocked = rt.classify_no_hidden_copy_transfer_snapshot(
            {**_snapshot(), "device_to_host_calls": 1, "device_to_host_bytes": 64},
            min_named_column_bytes=262_144,
        )
        summary = rt.summarize_no_hidden_copy_classifications((ready, blocked))
        self.assertFalse(summary["no_hidden_column_copy_ready"])
        self.assertTrue(summary["any_device_to_host_copy_observed"])

        report = M12_REPORT.read_text(encoding="utf-8")
        self.assertIn("M12 No-Hidden-Copy Contract", report)
        self.assertIn("app-agnostic", report)
        self.assertIn("public speedup claim", report)


def _snapshot() -> dict[str, object]:
    return {
        "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
        "total_calls": 1,
        "total_bytes": 96,
        "host_to_device_calls": 1,
        "host_to_device_bytes": 96,
        "device_to_host_calls": 0,
        "device_to_host_bytes": 0,
        "device_to_device_calls": 0,
        "device_to_device_bytes": 0,
        "unknown_calls": 0,
        "unknown_bytes": 0,
    }


def _synthetic_payload() -> dict[str, object]:
    return {
        "version": "unit.no_hidden_copy",
        "status": "unit_ready",
        "partner_rows": tuple(_synthetic_row(partner) for partner in ("cupy", "numba")),
        "comparison": {
            "same_stream_ready": True,
            "transfer_counter_observed": True,
            "no_hidden_column_copy_ready": True,
            "true_zero_copy_ready": True,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "same_stream_public_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
        },
    }


def _synthetic_row(partner: str) -> dict[str, object]:
    classification = rt.classify_no_hidden_copy_transfer_snapshot(
        _snapshot(),
        min_named_column_bytes=262_144,
    )
    metadata = rt.annotate_no_hidden_copy_metadata(
        {
            "same_stream_evidence": {
                "transfer_counter_observed": True,
                "transfer_counter_snapshot": _snapshot(),
            }
        },
        classification,
    )
    return {
        "partner": partner,
        "validation_signature": (65085,),
        "same_stream_ready": True,
        "transfer_counter_observed": True,
        "no_hidden_column_copy_ready": True,
        "true_zero_copy_ready": True,
        "transfer_counter_classification": classification,
        "metadata": metadata,
        "instrumentation": {
            "claim_readiness": {
                "same_stream_ready": True,
                "true_zero_copy_ready": True,
            }
        },
        "public_claim_authorized": False,
    }


if __name__ == "__main__":
    unittest.main()
