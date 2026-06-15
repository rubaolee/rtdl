from __future__ import annotations

from pathlib import Path
import json
import unittest

import rtdsl as rt
from rtdsl.v3_0_execution_graph import GraphValidationError


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "src/rtdsl/v3_0_m18_device_side_grouped_contract.py"
RUNTIME = ROOT / "src/rtdsl/optix_runtime.py"
CORE = ROOT / "src/native/optix/rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src/native/optix/rtdl_optix_workloads.cpp"
API = ROOT / "src/native/optix/rtdl_optix_api.cpp"
PRELUDE = ROOT / "src/native/optix/rtdl_optix_prelude.h"
RUNNER = ROOT / "scripts/v3_0_m18_device_side_grouped_contract_measure.py"
REPORT = ROOT / "docs/reports/goal4415_v3_0_m18_device_side_grouped_contract_2026-06-15.md"
EVIDENCE_JSON = (
    ROOT / "docs/reports/goal4415_v3_0_m18_device_side_grouped_contract_evidence_8192_2026-06-15.json"
)


class Goal4415V30M18DeviceSideGroupedContractTest(unittest.TestCase):
    def test_native_adds_app_agnostic_device_per_ray_grouped_argmin_contract(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        self.assertIn("closest_hit_grouped_argmin_min_key_per_ray_group", core)
        self.assertIn("closest_hit_grouped_argmin_min_index_per_ray_group", core)
        self.assertIn("per_ray_group_ids[idx]", core)
        self.assertIn("ray_group_ids[row.ray_id]", core)
        self.assertIn("ray_group_ids_are_per_ray_ordinal", workloads)
        self.assertIn("grouped_input_columns_partner_owned", workloads)
        self.assertIn("per-ray grouped argmin input count must match prepared ray batch count", workloads)
        self.assertIn("min_key_per_ray_group_fn", workloads)
        self.assertIn("min_index_per_ray_group_fn", workloads)
        self.assertIn("rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create_device_per_ray_groups", api)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_ray_batch_closest_hit_prepared_grouped_argmin_device", api)
        self.assertIn("rtdl_optix_closest_hit_grouped_argmin_inputs_3d_finalize", api)
        self.assertIn("rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create_device_per_ray_groups", prelude)
        m18_start = api.index("rtdl_optix_closest_hit_grouped_argmin_inputs_3d_create_device_per_ray_groups")
        m18_slice = api[m18_start : m18_start + 2400].lower()
        for forbidden in ("rayjoin", "rtnn", "dbscan"):
            self.assertNotIn(forbidden, m18_slice)

    def test_runtime_exposes_device_grouped_prepare_run_and_finalize(self) -> None:
        runtime = RUNTIME.read_text(encoding="utf-8")
        self.assertIn("prepare_closest_hit_device_per_ray_grouped_argmin_inputs", runtime)
        self.assertIn("from_device_per_ray_group_columns", runtime)
        self.assertIn("ray_closest_hit_prepared_grouped_argmin_device", runtime)
        self.assertIn("materialize_grouped_results", runtime)
        self.assertIn('"group_mapping_contract": "per_prepared_ray_ordinal"', runtime)
        self.assertIn('"per_group_results_downloaded_to_host": False', runtime)
        self.assertIn('"result_materialization_in_measured_window": False', runtime)
        self.assertIn("OPTIX_CLOSEST_HIT_GROUPED_ARGMIN_INPUTS_3D_CREATE_DEVICE_PER_RAY_GROUPS_SYMBOL", runtime)

    def test_m18_module_and_runner_define_two_partner_evidence(self) -> None:
        module = MODULE.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")
        self.assertIn('V3_M18_PARTNERS = ("cupy", "numba")', module)
        self.assertIn("device_side_prepared_ray_grouped_argmin_contract_pilot", module)
        self.assertIn("per_prepared_ray_ordinal", module)
        self.assertIn("measured_window_no_hidden_copy_ready", module)
        self.assertIn("result_materialization_after_measured_window", module)
        self.assertIn("measurement_methodology_limits", module)
        self.assertIn("LD_PRELOAD", runner)
        self.assertIn("run_v3_m18_device_side_grouped_contract_evidence_case", runner)

    def test_validator_accepts_synthetic_m18_payload(self) -> None:
        payload = _synthetic_payload()
        validation = rt.validate_v3_m18_device_side_grouped_contract_payload(payload)
        self.assertEqual(2, validation["partner_count"])
        self.assertTrue(validation["signature_match"])
        self.assertTrue(validation["measured_window_no_hidden_copy_ready"])

    def test_validator_rejects_hot_window_materialization(self) -> None:
        payload = _synthetic_payload()
        rows = [dict(row) for row in payload["partner_rows"]]
        rows[0]["per_group_results_downloaded_to_host_in_hot_window"] = True
        payload["partner_rows"] = tuple(rows)
        with self.assertRaisesRegex(GraphValidationError, "hot window"):
            rt.validate_v3_m18_device_side_grouped_contract_payload(payload)

    def test_validator_rejects_public_speedup_claim(self) -> None:
        payload = _synthetic_payload()
        payload["claim_boundary"] = dict(payload["claim_boundary"])
        payload["claim_boundary"]["public_speedup_claim_authorized"] = True
        with self.assertRaisesRegex(GraphValidationError, "public_speedup"):
            rt.validate_v3_m18_device_side_grouped_contract_payload(payload)

    def test_report_and_pod_artifact_capture_m18_boundaries(self) -> None:
        payload = json.loads(EVIDENCE_JSON.read_text(encoding="utf-8"))
        validation = rt.validate_v3_m18_device_side_grouped_contract_payload(payload)
        self.assertTrue(validation["signature_match"])
        self.assertEqual(2, validation["partner_count"])
        rows = {row["partner"]: row for row in payload["partner_rows"]}
        self.assertEqual({"cupy", "numba"}, set(rows))
        self.assertEqual(rows["cupy"]["validation_signature"], rows["numba"]["validation_signature"])
        for row in rows.values():
            self.assertEqual("per_prepared_ray_ordinal", row["group_mapping_contract"])
            self.assertTrue(row["grouped_input_columns_partner_owned"])
            self.assertFalse(row["per_group_results_downloaded_to_host_in_hot_window"])
            self.assertTrue(row["result_materialization_after_measured_window"])
            self.assertTrue(row["measured_window_no_hidden_copy_ready"])
        report = REPORT.read_text(encoding="utf-8")
        self.assertIn("measured-window no-hidden-copy", report)
        self.assertIn("public speedup claim", report)
        self.assertIn("automatic partner/backend selection claim", report)
        self.assertIn("LD_PRELOAD shim", report)


def _classification(window: str) -> dict[str, object]:
    return rt.classify_no_hidden_copy_transfer_snapshot(
        {
            "counter_version": "rtdl.cuda_transfer_counter.v3_m11",
            "total_calls": 1,
            "total_bytes": 88,
            "host_to_device_calls": 1,
            "host_to_device_bytes": 88,
            "device_to_host_calls": 0,
            "device_to_host_bytes": 0,
            "device_to_device_calls": 0,
            "device_to_device_bytes": 0,
            "unknown_calls": 0,
            "unknown_bytes": 0,
        },
        min_named_column_bytes=8192,
        measured_window=window,
        readiness_source="synthetic_m18_test",
    )


def _row(partner: str) -> dict[str, object]:
    prepare = _classification("partner_device_ray_and_grouped_input_prepare_before_grouped_hot_path")
    hot = _classification(
        "prepared_device_ray_and_device_grouped_inputs_to_device_grouped_argmin_before_result_materialization"
    )
    return {
        "partner": partner,
        "backend": "optix",
        "ray_count": 8192,
        "group_count": 128,
        "validation_signature": (128, 128, 1408, 128000000, 11, 11),
        "metadata": {
            "device_execution_metadata": {
                "transfer_metadata": {
                    "group_mapping_contract": "per_prepared_ray_ordinal",
                    "grouped_input_columns_partner_owned": True,
                    "per_group_results_downloaded_to_host": False,
                },
            }
        },
        "prepare_transfer_counter_classification": prepare,
        "transfer_counter_classification": hot,
        "prepared_ray_batch_used": True,
        "ray_columns_partner_owned": True,
        "grouped_input_columns_partner_owned": True,
        "group_mapping_contract": "per_prepared_ray_ordinal",
        "grouped_inputs_created_from": "partner_device_columns",
        "group_ids_uploaded_each_run": False,
        "candidate_values_uploaded_each_run": False,
        "candidate_indices_uploaded_each_run": False,
        "per_group_results_downloaded_to_host_in_hot_window": False,
        "result_materialization_after_measured_window": True,
        "prepare_transfer_counter_observed": True,
        "hot_transfer_counter_observed": True,
        "prepare_no_hidden_column_copy_ready": True,
        "hot_no_hidden_column_copy_ready": True,
        "measured_window_no_hidden_copy_ready": True,
        "public_claim_authorized": False,
    }


def _synthetic_payload() -> dict[str, object]:
    return {
        "version": rt.V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_VERSION,
        "status": rt.V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_STATUS,
        "graph_id": rt.V3_M18_GRAPH_ID,
        "contract_key": rt.V3_M18_CONTRACT_KEY,
        "partner_rows": (_row("cupy"), _row("numba")),
        "comparison": {
            "signature_match": True,
            "prepare_no_hidden_column_copy_ready": True,
            "hot_no_hidden_column_copy_ready": True,
            "measured_window_no_hidden_copy_ready": True,
            "result_materialization_after_measured_window": True,
            "group_mapping_contract": "per_prepared_ray_ordinal",
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "author_code_parity_claim_authorized": False,
        },
    }


if __name__ == "__main__":
    unittest.main()
