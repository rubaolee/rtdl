from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import statistics
import time

from .optix_runtime import prepare_optix_static_triangle_scene_3d
from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name
from .v3_0_m13_hit_stream_no_hidden_copy_evidence import make_v3_m13_two_plane_triangles
from .v3_0_m16_partner_device_ray_hit_stream_no_hidden_copy_evidence import make_v3_m16_cupy_ray_columns
from .v3_0_no_hidden_copy_contract import CudaTransferCounter
from .v3_0_no_hidden_copy_contract import V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
from .v3_0_no_hidden_copy_contract import classify_no_hidden_copy_transfer_snapshot
from .v3_0_no_hidden_copy_contract import summarize_no_hidden_copy_classifications


V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_VERSION = "rtdl.v3_0.device_side_grouped_contract.m18"
V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_STATUS = (
    "m18_device_side_grouped_argmin_contract_internal_claims_gated"
)
V3_M18_GRAPH_ID = "device_side_prepared_ray_grouped_argmin_contract_pilot"
V3_M18_CONTRACT_KEY = "device_side_prepared_ray_grouped_argmin_contract_v1"
V3_M18_PARTNERS = ("cupy", "numba")
V3_M18_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES = (
    V3_NO_HIDDEN_COPY_DEFAULT_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES
)


def run_v3_m18_device_side_grouped_contract_evidence_case(
    *,
    transfer_counter_library: str | Path,
    ray_count: int = 8192,
    group_count: int = 128,
    warmups: int = 2,
    repeats: int = 5,
    hardware: str = "pod_rtx_4000_ada",
) -> dict[str, object]:
    validate_v3_public_name(V3_M18_GRAPH_ID, label="M18 graph id")
    ray_count = int(ray_count)
    group_count = int(group_count)
    warmups = int(warmups)
    repeats = int(repeats)
    if ray_count <= 0:
        raise GraphValidationError("ray_count must be positive")
    if group_count <= 0:
        raise GraphValidationError("group_count must be positive")
    if group_count > ray_count:
        raise GraphValidationError("group_count must not exceed ray_count for the M18 evidence fixture")
    if warmups < 0 or repeats <= 0:
        raise GraphValidationError("warmups/repeats are invalid")

    transfer_counter = CudaTransferCounter(transfer_counter_library)
    triangles = make_v3_m13_two_plane_triangles()
    rows = []
    with prepare_optix_static_triangle_scene_3d(triangles) as scene:
        for partner in V3_M18_PARTNERS:
            ray_columns = _make_partner_ray_columns(partner, ray_count)
            grouped_columns = _make_partner_grouped_columns(partner, ray_count, group_count)
            for _ in range(warmups):
                ray_batch = scene.prepare_ray_batch_device_columns(ray_columns)
                grouped_inputs = scene.prepare_closest_hit_device_per_ray_grouped_argmin_inputs(
                    per_ray_group_ids=grouped_columns["per_ray_group_ids"],
                    candidate_values=grouped_columns["candidate_values"],
                    candidate_indices=grouped_columns["candidate_indices"],
                    group_count=group_count,
                )
                try:
                    scene.ray_closest_hit_prepared_grouped_argmin_device(ray_batch, grouped_inputs)
                    grouped_inputs.materialize_grouped_results()
                finally:
                    grouped_inputs.close()
                    ray_batch.close()
            rows.append(
                _run_partner_row(
                    scene=scene,
                    partner=partner,
                    ray_columns=ray_columns,
                    grouped_columns=grouped_columns,
                    transfer_counter=transfer_counter,
                    ray_count=ray_count,
                    group_count=group_count,
                    repeats=repeats,
                )
            )

    signatures = {tuple(row["validation_signature"]) for row in rows}
    payload = {
        "version": V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_VERSION,
        "status": V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_STATUS,
        "graph_id": V3_M18_GRAPH_ID,
        "contract_key": V3_M18_CONTRACT_KEY,
        "parameters": {
            "ray_count": ray_count,
            "group_count": group_count,
            "triangle_count": len(triangles),
            "warmups": warmups,
            "repeats": repeats,
            "allowed_non_column_host_to_device_bytes": V3_M18_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            "transfer_counter_library": str(transfer_counter_library),
            "hardware": hardware,
        },
        "partner_rows": tuple(rows),
        "comparison": {
            "signature_match": len(signatures) == 1,
            "partners": V3_M18_PARTNERS,
            "prepare_no_hidden_column_copy_ready": all(
                bool(row["prepare_no_hidden_column_copy_ready"]) for row in rows
            ),
            "hot_no_hidden_column_copy_ready": all(bool(row["hot_no_hidden_column_copy_ready"]) for row in rows),
            "measured_window_no_hidden_copy_ready": all(
                bool(row["measured_window_no_hidden_copy_ready"]) for row in rows
            ),
            "result_materialization_after_measured_window": all(
                bool(row["result_materialization_after_measured_window"]) for row in rows
            ),
            "group_mapping_contract": "per_prepared_ray_ordinal",
            "public_claim_authorized": False,
        },
        "claim_boundary": {
            "public_speedup_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_public_claim_authorized": False,
            "automatic_partner_selection_authorized": False,
            "author_code_parity_claim_authorized": False,
            "reason": (
                "M18 validates an app-agnostic device-side grouped input contract for "
                "prepared device-column ray batches. It does not authorize public performance, "
                "whole-app speedup, automatic partner selection, or end-to-end zero-copy wording."
            ),
        },
        "measurement_methodology_limits": {
            "transfer_counter_scope": (
                "LD_PRELOAD CUDA transfer counter intercepts public CUDA runtime/driver copy calls "
                "in the measured process; it does not prove absence of transfers through unobserved "
                "internal library mechanisms, child processes, or non-CUDA DMA paths."
            ),
            "materialization_scope": (
                "Per-group result arrays are downloaded only after the hot measured window closes."
            ),
        },
    }
    validate_v3_m18_device_side_grouped_contract_payload(payload)
    return payload


def _run_partner_row(
    *,
    scene,
    partner: str,
    ray_columns: Mapping[str, object],
    grouped_columns: Mapping[str, object],
    transfer_counter: CudaTransferCounter,
    ray_count: int,
    group_count: int,
    repeats: int,
) -> dict[str, object]:
    prepare_samples = []
    hot_samples = []
    materialize_samples = []
    prepare_snapshots = []
    hot_snapshots = []
    prepare_classifications = []
    hot_classifications = []
    signatures = []
    device_metadata = []
    materialize_metadata = []
    min_prepare_named_bytes = _m18_named_column_bytes(ray_count)
    min_hot_named_bytes = max(ray_count * 4, 1)
    for _ in range(repeats):
        transfer_counter.reset()
        transfer_counter.enable()
        prepare_start = time.perf_counter()
        ray_batch = scene.prepare_ray_batch_device_columns(ray_columns)
        grouped_inputs = scene.prepare_closest_hit_device_per_ray_grouped_argmin_inputs(
            per_ray_group_ids=grouped_columns["per_ray_group_ids"],
            candidate_values=grouped_columns["candidate_values"],
            candidate_indices=grouped_columns["candidate_indices"],
            group_count=group_count,
        )
        prepare_samples.append(time.perf_counter() - prepare_start)
        prepare_snapshot = transfer_counter.disable_and_snapshot()
        prepare_classification = classify_no_hidden_copy_transfer_snapshot(
            prepare_snapshot,
            min_named_column_bytes=min_prepare_named_bytes,
            allowed_non_column_host_to_device_bytes=V3_M18_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
            measured_window="partner_device_ray_and_grouped_input_prepare_before_grouped_hot_path",
            readiness_source="v3_m18_prepare_transfer_counter_classification",
        )
        try:
            transfer_counter.reset()
            transfer_counter.enable()
            hot_start = time.perf_counter()
            device_result = scene.ray_closest_hit_prepared_grouped_argmin_device(ray_batch, grouped_inputs)
            hot_samples.append(time.perf_counter() - hot_start)
            hot_snapshot = transfer_counter.disable_and_snapshot()
            hot_classification = classify_no_hidden_copy_transfer_snapshot(
                hot_snapshot,
                min_named_column_bytes=min_hot_named_bytes,
                allowed_non_column_host_to_device_bytes=V3_M18_ALLOWED_NON_COLUMN_HOST_TO_DEVICE_BYTES,
                measured_window=(
                    "prepared_device_ray_and_device_grouped_inputs_to_device_grouped_argmin_"
                    "before_result_materialization"
                ),
                readiness_source="v3_m18_hot_transfer_counter_classification",
            )
            materialize_start = time.perf_counter()
            materialized = grouped_inputs.materialize_grouped_results()
            materialize_samples.append(time.perf_counter() - materialize_start)
        finally:
            grouped_inputs.close()
            ray_batch.close()
        prepare_snapshots.append(prepare_snapshot)
        hot_snapshots.append(hot_snapshot)
        prepare_classifications.append(prepare_classification)
        hot_classifications.append(hot_classification)
        signatures.append(_grouped_argmin_signature(materialized))
        device_metadata.append(dict(device_result["metadata"]))
        materialize_metadata.append(dict(materialized["metadata"]))

    if not signatures:
        raise GraphValidationError("M18 partner run produced no signatures")
    if any(signature != signatures[-1] for signature in signatures):
        raise GraphValidationError(f"M18 {partner} signatures changed across repeats")
    prepare_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in prepare_classifications)
    hot_ready = all(bool(item["no_hidden_column_copy_ready"]) for item in hot_classifications)
    measured_ready = prepare_ready and hot_ready
    final_metadata = device_metadata[-1]
    final_transfer = dict(final_metadata.get("transfer_metadata") or {})
    return {
        "partner": partner,
        "backend": "optix",
        "ray_count": ray_count,
        "group_count": group_count,
        "validation_signature": signatures[-1],
        "prepare_samples_seconds": tuple(prepare_samples),
        "hot_device_run_samples_seconds": tuple(hot_samples),
        "materialize_samples_seconds": tuple(materialize_samples),
        "prepare_seconds_median": statistics.median(prepare_samples),
        "hot_device_run_seconds_median": statistics.median(hot_samples),
        "materialize_seconds_median": statistics.median(materialize_samples),
        "metadata": {
            "device_execution_metadata": final_metadata,
            "materialization_metadata": materialize_metadata[-1],
            "transfer_metadata": final_transfer,
        },
        "prepare_transfer_counter_samples": tuple(prepare_snapshots),
        "prepare_transfer_counter_classifications": tuple(prepare_classifications),
        "prepare_transfer_counter_classification": prepare_classifications[-1],
        "prepare_transfer_counter_summary": summarize_no_hidden_copy_classifications(tuple(prepare_classifications)),
        "transfer_counter_samples": tuple(hot_snapshots),
        "transfer_counter_classifications": tuple(hot_classifications),
        "transfer_counter_classification": hot_classifications[-1],
        "transfer_counter_summary": summarize_no_hidden_copy_classifications(tuple(hot_classifications)),
        "prepared_ray_batch_used": True,
        "ray_columns_partner_owned": True,
        "grouped_input_columns_partner_owned": bool(final_transfer.get("grouped_input_columns_partner_owned")),
        "group_mapping_contract": final_transfer.get("group_mapping_contract"),
        "grouped_inputs_created_from": final_transfer.get("grouped_inputs_created_from"),
        "group_ids_uploaded_each_run": bool(final_transfer.get("group_ids_uploaded_each_run")),
        "candidate_values_uploaded_each_run": bool(final_transfer.get("candidate_values_uploaded_each_run")),
        "candidate_indices_uploaded_each_run": bool(final_transfer.get("candidate_indices_uploaded_each_run")),
        "per_group_results_downloaded_to_host_in_hot_window": bool(
            final_transfer.get("per_group_results_downloaded_to_host")
        ),
        "result_materialization_after_measured_window": True,
        "prepare_transfer_counter_observed": True,
        "hot_transfer_counter_observed": True,
        "prepare_no_hidden_column_copy_ready": prepare_ready,
        "hot_no_hidden_column_copy_ready": hot_ready,
        "measured_window_no_hidden_copy_ready": measured_ready,
        "public_claim_authorized": False,
        "claim_readiness": {
            "prepared_ray_batch_used": True,
            "ray_columns_partner_owned": True,
            "grouped_input_columns_partner_owned": bool(final_transfer.get("grouped_input_columns_partner_owned")),
            "group_mapping_contract": final_transfer.get("group_mapping_contract"),
            "prepare_transfer_counter_observed": True,
            "hot_transfer_counter_observed": True,
            "no_hidden_column_copy_ready": measured_ready,
            "true_zero_copy_ready": measured_ready,
            "measured_window_scope_only": True,
            "public_claim_authorized": False,
        },
    }


def _make_partner_ray_columns(partner: str, ray_count: int) -> dict[str, object]:
    if partner == "cupy":
        return make_v3_m16_cupy_ray_columns(ray_count)
    if partner == "numba":
        try:
            import numpy as np
            from numba import cuda
        except Exception as exc:
            raise RuntimeError("M18 Numba evidence requires numba.cuda and numpy") from exc
        count = int(ray_count)
        ids = np.arange(count, dtype=np.uint32)
        ids_f64 = ids.astype(np.float64)
        return {
            "ids": cuda.to_device(ids),
            "ox": cuda.to_device(0.25 + np.mod(ids_f64, 7.0) * 0.01),
            "oy": cuda.to_device(0.25 + np.mod(np.floor(ids_f64 / 7.0), 7.0) * 0.01),
            "oz": cuda.to_device(np.full(count, -1.0, dtype=np.float64)),
            "dx": cuda.to_device(np.zeros(count, dtype=np.float64)),
            "dy": cuda.to_device(np.zeros(count, dtype=np.float64)),
            "dz": cuda.to_device(np.ones(count, dtype=np.float64)),
            "tmax": cuda.to_device(np.full(count, 4.0, dtype=np.float64)),
        }
    raise GraphValidationError(f"unsupported M18 partner: {partner}")


def _make_partner_grouped_columns(partner: str, ray_count: int, group_count: int) -> dict[str, object]:
    if partner == "cupy":
        try:
            import cupy as cp
        except Exception as exc:
            raise RuntimeError("M18 CuPy evidence requires cupy") from exc
        ids = cp.arange(int(ray_count), dtype=cp.uint32)
        return {
            "per_ray_group_ids": cp.mod(ids, cp.uint32(int(group_count))).astype(cp.uint32),
            "candidate_values": cp.asarray([1.0, 2.0], dtype=cp.float64),
            "candidate_indices": cp.asarray([11, 22], dtype=cp.uint32),
        }
    if partner == "numba":
        try:
            import numpy as np
            from numba import cuda
        except Exception as exc:
            raise RuntimeError("M18 Numba evidence requires numba.cuda and numpy") from exc
        per_ray = (np.arange(int(ray_count), dtype=np.uint32) % np.uint32(int(group_count))).astype(np.uint32)
        return {
            "per_ray_group_ids": cuda.to_device(per_ray),
            "candidate_values": cuda.to_device(np.asarray([1.0, 2.0], dtype=np.float64)),
            "candidate_indices": cuda.to_device(np.asarray([11, 22], dtype=np.uint32)),
        }
    raise GraphValidationError(f"unsupported M18 partner: {partner}")


def _grouped_argmin_signature(materialized: Mapping[str, object]) -> tuple[int, ...]:
    try:
        import numpy as np
    except Exception as exc:
        raise RuntimeError("M18 grouped signature requires numpy") from exc
    has_value = np.asarray(materialized["has_value"], dtype=np.uint8)
    index = np.asarray(materialized["index"], dtype=np.uint32)
    value = np.asarray(materialized["value"], dtype=np.float64)
    mask = has_value != 0
    populated = int(mask.sum())
    if populated == 0:
        return (int(has_value.shape[0]), 0, 0, 0, -1, -1)
    return (
        int(has_value.shape[0]),
        populated,
        int(index[mask].sum()),
        int(round(float(value[mask].sum()) * 1_000_000.0)),
        int(index[mask].min()),
        int(index[mask].max()),
    )


def _m18_named_column_bytes(ray_count: int) -> int:
    ray_column_bytes = int(ray_count) * (4 + 7 * 8)
    grouped_column_bytes = int(ray_count) * 4 + 2 * (8 + 4)
    return max(ray_column_bytes + grouped_column_bytes, 1)


def validate_v3_m18_device_side_grouped_contract_payload(payload: Mapping[str, object]) -> dict[str, object]:
    if not isinstance(payload, Mapping):
        raise GraphValidationError("M18 payload must be a mapping")
    if payload.get("version") != V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_VERSION:
        raise GraphValidationError("unexpected M18 payload version")
    if payload.get("status") != V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_STATUS:
        raise GraphValidationError("unexpected M18 payload status")
    rows = tuple(payload.get("partner_rows", ()))
    if {str(row.get("partner")) for row in rows if isinstance(row, Mapping)} != set(V3_M18_PARTNERS):
        raise GraphValidationError("M18 payload requires CuPy and Numba partner rows")
    signatures = {tuple(row.get("validation_signature", ())) for row in rows if isinstance(row, Mapping)}
    if len(signatures) != 1:
        raise GraphValidationError("M18 partner signatures must match")
    for row in rows:
        if not isinstance(row, Mapping):
            raise GraphValidationError("M18 partner row must be a mapping")
        partner = str(row.get("partner"))
        if row.get("prepared_ray_batch_used") is not True:
            raise GraphValidationError(f"{partner} row must use prepared ray batch")
        if row.get("ray_columns_partner_owned") is not True:
            raise GraphValidationError(f"{partner} row must use partner-owned ray columns")
        if row.get("grouped_input_columns_partner_owned") is not True:
            raise GraphValidationError(f"{partner} row must use partner-owned grouped input columns")
        if row.get("group_mapping_contract") != "per_prepared_ray_ordinal":
            raise GraphValidationError(f"{partner} row must use per-prepared-ray grouped contract")
        if row.get("group_ids_uploaded_each_run") is not False:
            raise GraphValidationError(f"{partner} row must not upload group ids each run")
        if row.get("candidate_values_uploaded_each_run") is not False:
            raise GraphValidationError(f"{partner} row must not upload candidate values each run")
        if row.get("candidate_indices_uploaded_each_run") is not False:
            raise GraphValidationError(f"{partner} row must not upload candidate indices each run")
        if row.get("per_group_results_downloaded_to_host_in_hot_window") is not False:
            raise GraphValidationError(f"{partner} hot window must not download per-group results")
        if row.get("result_materialization_after_measured_window") is not True:
            raise GraphValidationError(f"{partner} row must materialize only after measured window")
        if row.get("prepare_no_hidden_column_copy_ready") is not True:
            raise GraphValidationError(f"{partner} prepare window must pass no-hidden-copy")
        if row.get("hot_no_hidden_column_copy_ready") is not True:
            raise GraphValidationError(f"{partner} hot window must pass no-hidden-copy")
        if row.get("measured_window_no_hidden_copy_ready") is not True:
            raise GraphValidationError(f"{partner} measured windows must pass no-hidden-copy")
        if bool(row.get("public_claim_authorized")):
            raise GraphValidationError(f"{partner} row must not authorize public claims")
        for key in ("prepare_transfer_counter_classification", "transfer_counter_classification"):
            classification = row.get(key, {})
            if not isinstance(classification, Mapping):
                raise GraphValidationError(f"{partner} row requires {key}")
            if classification.get("hidden_copy_observed") is not False:
                raise GraphValidationError(f"{partner} {key} observed hidden copy")
            if classification.get("no_hidden_column_copy_ready") is not True:
                raise GraphValidationError(f"{partner} {key} is not ready")
    comparison = payload.get("comparison", {})
    if not isinstance(comparison, Mapping):
        raise GraphValidationError("M18 payload requires comparison")
    for key in (
        "signature_match",
        "prepare_no_hidden_column_copy_ready",
        "hot_no_hidden_column_copy_ready",
        "measured_window_no_hidden_copy_ready",
        "result_materialization_after_measured_window",
    ):
        if comparison.get(key) is not True:
            raise GraphValidationError(f"M18 comparison must prove {key}=true")
    boundary = payload.get("claim_boundary", {})
    if not isinstance(boundary, Mapping):
        raise GraphValidationError("M18 payload requires claim boundary")
    for key in (
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "true_zero_copy_public_claim_authorized",
        "automatic_partner_selection_authorized",
        "author_code_parity_claim_authorized",
    ):
        if bool(boundary.get(key)):
            raise GraphValidationError(f"M18 must not authorize {key}")
    return {
        "status": V3_M18_DEVICE_SIDE_GROUPED_CONTRACT_STATUS,
        "partner_count": len(rows),
        "signature_match": True,
        "measured_window_no_hidden_copy_ready": True,
        "public_claim_authorized": False,
    }
