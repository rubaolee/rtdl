from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .neutral_buffer_seam import V2_5_NEUTRAL_BUFFER_SEAM_VERSION
from .neutral_buffer_seam import create_neutral_buffer_lease
from .neutral_buffer_seam import neutral_buffer_descriptor_from_object


V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION = "rtdl.v2_6.neutral_partner_handoff.v1"
V2_6_NEUTRAL_PARTNER_HANDOFF_SUPPORTED_PARTNERS = ("cupy", "numba")
V2_6_NEUTRAL_PARTNER_HANDOFF_CLAIM_BOUNDARY = (
    "The v2.6 neutral partner handoff records runtime-observed device "
    "descriptors and neutral-seam lease transitions for explicit user-selected "
    "partners. It does not execute arbitrary partner kernels, authorize release, "
    "authorize true-zero-copy wording, authorize speedup wording, or allow torch "
    "carrier/coercion on the CuPy/Numba data path."
)


def plan_v2_6_neutral_partner_handoff(
    columns: Mapping[str, Any],
    *,
    partner: str,
    producer: str = "python_user",
    consumer: str | None = None,
    access_modes: Mapping[str, str] | None = None,
    require_device_resident: bool = True,
) -> dict[str, Any]:
    """Plan a v2.6 neutral handoff for explicit CuPy/Numba partner columns.

    This is the N-0 bridge from descriptor-only v2.5 planning to v2.6
    first-class partner work. It observes buffer protocols at runtime and runs
    the neutral-seam lease state machine, while deliberately not executing the
    partner continuation or authorizing zero-copy/speedup claims.
    """

    normalized_partner = _normalize_v2_6_partner(partner)
    resolved_consumer = (
        f"{normalized_partner}_partner_continuation"
        if consumer is None
        else str(consumer)
    )
    access_by_name = {} if access_modes is None else dict(access_modes)
    errors: list[str] = []
    records: list[dict[str, Any]] = []
    lease_records: list[dict[str, Any]] = []

    if normalized_partner not in V2_6_NEUTRAL_PARTNER_HANDOFF_SUPPORTED_PARTNERS:
        errors.append("v2.6 neutral partner handoff supports only CuPy and Numba")
    if not isinstance(columns, Mapping) or not columns:
        errors.append("neutral partner handoff requires at least one named column")

    for raw_name, obj in columns.items():
        name = str(raw_name)
        if not name:
            errors.append("neutral partner handoff column names must be non-empty")
            continue
        access_mode = str(access_by_name.get(name, "read"))
        try:
            descriptor = neutral_buffer_descriptor_from_object(
                name,
                obj,
                producer=producer,
                consumer=resolved_consumer,
                access_mode=access_mode,
                lifetime_state="caller_retained",
            )
        except Exception as exc:
            errors.append(f"{name}: cannot build neutral descriptor: {exc}")
            continue

        metadata = descriptor.to_metadata()
        source_protocol = str(metadata["buffer"]["source_protocol"])
        if source_protocol == "torch":
            errors.append(f"{name}: torch source protocol is forbidden on the v2.6 CuPy/Numba neutral path")
        if require_device_resident and not bool(metadata["device_resident"]):
            errors.append(f"{name}: device-resident CUDA column is required")
        if str(metadata["transfer_status"]) == "host_stage":
            errors.append(f"{name}: host-stage transfer is forbidden on the neutral partner path")

        lease = create_neutral_buffer_lease(descriptor)
        completed = lease.begin_partner_borrow().complete_partner_borrow()
        lease_metadata = completed.to_metadata()
        lease_records.append(lease_metadata)
        records.append(
            {
                "name": name,
                "access_mode": access_mode,
                "source_protocol": source_protocol,
                "device_resident": bool(metadata["device_resident"]),
                "direct_device_pointer_observed": bool(metadata["direct_device_pointer_observed"]),
                "transfer_status": metadata["transfer_status"],
                "copy_status": metadata["copy_status"],
                "torch_source_protocol": source_protocol == "torch",
                "torch_conversion_used": False,
                "torch_carrier_used": False,
                "neutral_descriptor": metadata,
                "lease": lease_metadata,
            }
        )

    torch_source_count = sum(1 for record in records if record["torch_source_protocol"])
    device_resident_count = sum(1 for record in records if record["device_resident"])
    all_leases_completed = bool(lease_records) and all(
        tuple(record["event_log"]) == ("handoff_begin", "continuation_complete")
        for record in lease_records
    )
    status = "accept" if not errors else "reject"
    return {
        "contract_version": V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION,
        "neutral_buffer_seam_contract_version": V2_5_NEUTRAL_BUFFER_SEAM_VERSION,
        "status": status,
        "requested_partner": str(partner),
        "selected_partner": normalized_partner,
        "producer": str(producer),
        "consumer": resolved_consumer,
        "column_count": len(records),
        "device_resident_column_count": device_resident_count,
        "torch_source_column_count": torch_source_count,
        "require_device_resident": bool(require_device_resident),
        "runtime_observed_descriptor_count": len(records),
        "copy_or_borrow_status_runtime_observed": bool(records),
        "all_columns_device_resident": bool(records) and device_resident_count == len(records),
        "all_leases_completed": all_leases_completed,
        "torch_conversion_used": False,
        "torch_carrier_used": False,
        "silent_cross_partner_torch_coercion_allowed": False,
        "partner_choice_user_owned": True,
        "engine_boundary": "generic_app_agnostic_native_primitives_only",
        "column_records": tuple(records),
        "lease_records": tuple(lease_records),
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
        "whole_app_speedup_claim_authorized": False,
        "true_zero_copy_claim_authorized": False,
        "errors": tuple(errors),
        "claim_boundary": V2_6_NEUTRAL_PARTNER_HANDOFF_CLAIM_BOUNDARY,
    }


def prepare_v2_6_neutral_partner_handoff(
    columns: Mapping[str, Any],
    *,
    partner: str,
    producer: str = "python_user",
    consumer: str | None = None,
    access_modes: Mapping[str, str] | None = None,
    require_device_resident: bool = True,
) -> dict[str, Any]:
    """Return an accepted v2.6 neutral handoff packet or fail closed."""

    packet = plan_v2_6_neutral_partner_handoff(
        columns,
        partner=partner,
        producer=producer,
        consumer=consumer,
        access_modes=access_modes,
        require_device_resident=require_device_resident,
    )
    if packet["status"] != "accept":
        raise ValueError("; ".join(str(error) for error in packet["errors"]))
    return packet


def validate_v2_6_neutral_partner_handoff(packet: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if packet.get("contract_version") != V2_6_NEUTRAL_PARTNER_HANDOFF_VERSION:
        errors.append("unexpected v2.6 neutral partner handoff version")
    if packet.get("selected_partner") not in V2_6_NEUTRAL_PARTNER_HANDOFF_SUPPORTED_PARTNERS:
        errors.append("selected partner must be cupy or numba")
    if packet.get("partner_choice_user_owned") is not True:
        errors.append("partner choice must remain user-owned")
    if "app_agnostic" not in str(packet.get("engine_boundary", "")):
        errors.append("native engine boundary must remain app-agnostic")
    if packet.get("torch_conversion_used") is not False:
        errors.append("torch conversion must not be used on the v2.6 neutral path")
    if packet.get("torch_carrier_used") is not False:
        errors.append("torch carrier must not be used on the v2.6 neutral path")
    if packet.get("silent_cross_partner_torch_coercion_allowed") is not False:
        errors.append("silent cross-partner torch coercion must remain forbidden")
    if packet.get("all_leases_completed") is not True:
        errors.append("all neutral handoff leases must complete")
    if packet.get("copy_or_borrow_status_runtime_observed") is not True:
        errors.append("copy/borrow status must be runtime-observed")
    if packet.get("all_columns_device_resident") is not True:
        errors.append("v2.6 neutral handoff requires device-resident columns")
    if int(packet.get("torch_source_column_count", -1)) != 0:
        errors.append("torch source columns are not allowed for CuPy/Numba neutral handoff")
    if int(packet.get("runtime_observed_descriptor_count", 0)) <= 0:
        errors.append("at least one runtime-observed descriptor is required")
    for record in packet.get("column_records", ()):
        if record.get("torch_conversion_used") is not False:
            errors.append(f"{record.get('name')}: torch conversion was used")
        if record.get("torch_carrier_used") is not False:
            errors.append(f"{record.get('name')}: torch carrier was used")
        if record.get("transfer_status") not in {
            "borrowed_device_pointer_unmeasured",
            "zero_copy_measured",
        }:
            errors.append(f"{record.get('name')}: expected a device-pointer transfer status")
    for field in (
        "release_authorized",
        "public_speedup_claim_authorized",
        "rt_core_speedup_claim_authorized",
        "whole_app_speedup_claim_authorized",
        "true_zero_copy_claim_authorized",
    ):
        if packet.get(field) is not False:
            errors.append(f"{field} must remain false")
    if packet.get("status") == "reject":
        errors.extend(str(error) for error in packet.get("errors", ()))
    return {
        "status": "accept" if not errors else "reject",
        "contract_version": packet.get("contract_version"),
        "selected_partner": packet.get("selected_partner"),
        "runtime_observed_descriptor_count": packet.get("runtime_observed_descriptor_count"),
        "errors": tuple(errors),
    }


def _normalize_v2_6_partner(partner: str) -> str:
    normalized = str(partner).strip().lower().replace("-", "_")
    aliases = {
        "cupy_conformance": "cupy",
        "cupy_descriptor": "cupy",
        "cuda_cupy": "cupy",
    }
    return aliases.get(normalized, normalized)
