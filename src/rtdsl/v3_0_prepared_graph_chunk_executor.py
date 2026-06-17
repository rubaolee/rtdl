from __future__ import annotations

from collections.abc import Mapping

from .v3_0_execution_graph import GraphValidationError
from .v3_0_execution_graph import validate_v3_public_name


V3_PREPARED_GRAPH_CHUNK_EXECUTOR_VERSION = (
    "rtdl.v3_0.prepared_graph_chunk_executor.m113.v1"
)
V3_PREPARED_GRAPH_CHUNK_EXECUTOR_STATUS = (
    "app_agnostic_prepared_graph_chunk_executor_contract"
)
V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_VERSION = (
    "rtdl.v3_0.prepared_graph_chunk_executor_adoption_gate.m120.v1"
)
V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_STATUS = (
    "app_agnostic_prepared_graph_chunk_executor_adoption_gate"
)
V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_VERSION = (
    "rtdl.v3_0.chunk_local_prepared_handle_gate.m123.v1"
)
V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_STATUS = (
    "app_agnostic_chunk_local_prepared_handle_readiness_gate"
)
V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_VERSION = (
    "rtdl.v3_0.chunked_unique_count_continuation_gate.m125.v1"
)
V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_STATUS = (
    "app_agnostic_chunked_unique_count_continuation_gate"
)


def plan_v3_prepared_graph_chunk_executor(
    *,
    graph_id: str,
    contract_key: str,
    operation: str,
    item_count: int,
    max_item_count: int,
    axis_name: str = "query",
    requires_partner_continuation: bool = True,
    continuation_kind: str = "same_stream_partner_device_reduction",
) -> dict[str, object]:
    """Plan app-agnostic prepared-graph chunks without executing them.

    This is the generic form of the M19 RTNN chunk shape: a prepared scene is
    retained across chunks, while each chunk prepares its own query/item handle,
    CUDA graph, and explicit partner continuation. It is a contract and
    validation surface only; callers still execute backend and partner work
    explicitly.
    """

    validate_v3_public_name(graph_id, label="prepared graph chunk graph_id")
    validate_v3_public_name(contract_key, label="prepared graph chunk contract_key")
    validate_v3_public_name(operation, label="prepared graph chunk operation")
    validate_v3_public_name(axis_name, label="prepared graph chunk axis_name")
    validate_v3_public_name(continuation_kind, label="prepared graph chunk continuation_kind")
    normalized_item_count = int(item_count)
    normalized_max_item_count = int(max_item_count)
    if normalized_item_count <= 0:
        raise GraphValidationError("item_count must be positive")
    if normalized_max_item_count <= 0:
        raise GraphValidationError("max_item_count must be positive")
    if not bool(requires_partner_continuation):
        raise GraphValidationError(
            "prepared graph chunk executor is only for explicit partner continuation"
        )

    chunks = []
    item_offset = 0
    while item_offset < normalized_item_count:
        chunk_item_count = min(normalized_max_item_count, normalized_item_count - item_offset)
        chunks.append(
            {
                "chunk_index": len(chunks),
                "item_offset": item_offset,
                "item_start_inclusive": item_offset,
                "item_end_exclusive": item_offset + chunk_item_count,
                "item_count": chunk_item_count,
                "prepared_scene_reused": True,
                "prepared_item_handle_per_chunk": True,
                "prepared_graph_per_chunk": True,
                "partner_continuation_per_chunk": True,
                "continuation_kind": str(continuation_kind),
                "host_materialization_before_partner": False,
            }
        )
        item_offset += chunk_item_count

    single_graph_cap_exceeded = normalized_item_count > normalized_max_item_count
    return {
        "version": V3_PREPARED_GRAPH_CHUNK_EXECUTOR_VERSION,
        "status": V3_PREPARED_GRAPH_CHUNK_EXECUTOR_STATUS,
        "graph_id": str(graph_id),
        "contract_key": str(contract_key),
        "operation": str(operation),
        "axis_name": str(axis_name),
        "item_count": normalized_item_count,
        "max_item_count": normalized_max_item_count,
        "chunk_count": len(chunks),
        "chunks": tuple(chunks),
        "single_graph_cap_exceeded": single_graph_cap_exceeded,
        "plan_status": (
            "chunked_partner_continuation_required"
            if single_graph_cap_exceeded
            else "single_graph_partner_continuation"
        ),
        "requires_partner_continuation": True,
        "prepared_scene_reuse_required": True,
        "prepared_item_handle_per_chunk_required": True,
        "prepared_graph_per_chunk_required": True,
        "partner_continuation_per_chunk_required": True,
        "continuation_kind": str(continuation_kind),
        "aggregate_only_substitute_allowed": False,
        "hidden_auto_dispatch_allowed": False,
        "automatic_partner_selection_authorized": False,
        "public_speedup_claim_authorized": False,
        "runtime_executed": False,
    }


def validate_v3_prepared_graph_chunk_executor_plan(
    plan: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(plan, Mapping):
        raise GraphValidationError("prepared graph chunk executor plan must be a mapping")
    if plan.get("version") != V3_PREPARED_GRAPH_CHUNK_EXECUTOR_VERSION:
        raise GraphValidationError("unexpected prepared graph chunk executor plan version")
    if plan.get("status") != V3_PREPARED_GRAPH_CHUNK_EXECUTOR_STATUS:
        raise GraphValidationError("unexpected prepared graph chunk executor plan status")
    item_count = int(plan.get("item_count", 0) or 0)
    max_item_count = int(plan.get("max_item_count", 0) or 0)
    chunks = tuple(plan.get("chunks", ()))
    if item_count <= 0:
        raise GraphValidationError("prepared graph chunk executor item_count must be positive")
    if max_item_count <= 0:
        raise GraphValidationError("prepared graph chunk executor max_item_count must be positive")
    if int(plan.get("chunk_count", -1)) != len(chunks):
        raise GraphValidationError("prepared graph chunk executor chunk_count mismatch")
    for key in (
        "requires_partner_continuation",
        "prepared_scene_reuse_required",
        "prepared_item_handle_per_chunk_required",
        "prepared_graph_per_chunk_required",
        "partner_continuation_per_chunk_required",
    ):
        if plan.get(key) is not True:
            raise GraphValidationError(f"prepared graph chunk executor must prove {key}=true")
    for key in (
        "aggregate_only_substitute_allowed",
        "hidden_auto_dispatch_allowed",
        "automatic_partner_selection_authorized",
        "public_speedup_claim_authorized",
    ):
        if bool(plan.get(key)):
            raise GraphValidationError(f"prepared graph chunk executor must not authorize {key}")

    expected_offset = 0
    for index, chunk in enumerate(chunks):
        if not isinstance(chunk, Mapping):
            raise GraphValidationError("prepared graph chunk executor chunk must be a mapping")
        chunk_count = int(chunk.get("item_count", 0) or 0)
        start = int(chunk.get("item_start_inclusive", -1))
        end = int(chunk.get("item_end_exclusive", -1))
        if int(chunk.get("chunk_index", -1)) != index:
            raise GraphValidationError("prepared graph chunk executor chunk_index mismatch")
        if start != expected_offset or int(chunk.get("item_offset", -1)) != expected_offset:
            raise GraphValidationError("prepared graph chunk executor item offsets are not contiguous")
        if chunk_count <= 0 or chunk_count > max_item_count:
            raise GraphValidationError("prepared graph chunk executor chunk item_count is invalid")
        if end - start != chunk_count:
            raise GraphValidationError("prepared graph chunk executor chunk end/start mismatch")
        for key in (
            "prepared_scene_reused",
            "prepared_item_handle_per_chunk",
            "prepared_graph_per_chunk",
            "partner_continuation_per_chunk",
        ):
            if chunk.get(key) is not True:
                raise GraphValidationError(f"prepared graph chunk executor chunk must prove {key}=true")
        if chunk.get("host_materialization_before_partner") is not False:
            raise GraphValidationError(
                "prepared graph chunk executor must block host materialization before partner"
            )
        expected_offset = end
    if expected_offset != item_count:
        raise GraphValidationError("prepared graph chunk executor chunks do not cover item_count")
    return {
        "status": "accept",
        "version": plan.get("version"),
        "item_count": item_count,
        "chunk_count": len(chunks),
        "single_graph_cap_exceeded": bool(plan.get("single_graph_cap_exceeded")),
        "runtime_executed": bool(plan.get("runtime_executed")),
        "public_claim_authorized": False,
    }


def assess_v3_prepared_graph_chunk_executor_adoption(
    *,
    app_id: str,
    graph_id: str,
    contract_key: str,
    operation: str,
    item_count: int,
    max_item_count: int,
    prepared_scene_reuse_available: bool,
    prepared_item_handle_per_chunk_available: bool,
    prepared_graph_capture_validated: bool,
    partner_continuation_explicit: bool,
    partner_continuation_associative: bool,
    host_materialization_before_partner: bool,
    axis_name: str = "query",
    continuation_kind: str = "same_stream_partner_device_reduction",
    aggregate_only_substitute_requested: bool = False,
    hidden_auto_dispatch_requested: bool = False,
    automatic_partner_selection_requested: bool = False,
    app_specific_native_engine_logic_requested: bool = False,
) -> dict[str, object]:
    """Assess whether a workload may use the M113 chunk executor plan.

    This is an adoption gate, not a dispatcher. It encodes the requirements a
    caller must satisfy before using the prepared graph chunk executor:
    prepared scene reuse, chunk-local prepared item handles, validated graph
    capture, explicit same-stream partner continuation, no host materialization
    before the partner, and no hidden automatic route/partner choice.
    """

    normalized_app_id = str(app_id).strip()
    if not normalized_app_id:
        raise GraphValidationError("prepared graph chunk adoption app_id must be non-empty")
    validate_v3_public_name(graph_id, label="prepared graph chunk adoption graph_id")
    validate_v3_public_name(contract_key, label="prepared graph chunk adoption contract_key")
    validate_v3_public_name(operation, label="prepared graph chunk adoption operation")
    validate_v3_public_name(axis_name, label="prepared graph chunk adoption axis_name")
    validate_v3_public_name(
        continuation_kind,
        label="prepared graph chunk adoption continuation_kind",
    )

    blockers = []
    if not bool(partner_continuation_explicit):
        blockers.append("missing_explicit_partner_continuation")
    if not bool(prepared_scene_reuse_available):
        blockers.append("missing_prepared_scene_reuse")
    if not bool(prepared_item_handle_per_chunk_available):
        blockers.append("missing_prepared_item_handle_per_chunk")
    if not bool(prepared_graph_capture_validated):
        blockers.append("prepared_graph_capture_not_validated")
    if not bool(partner_continuation_associative):
        blockers.append("partner_continuation_not_associative")
    if bool(host_materialization_before_partner):
        blockers.append("host_materialization_before_partner")
    if bool(aggregate_only_substitute_requested):
        blockers.append("aggregate_only_substitute_requested")
    if bool(hidden_auto_dispatch_requested):
        blockers.append("hidden_auto_dispatch_requested")
    if bool(automatic_partner_selection_requested):
        blockers.append("automatic_partner_selection_requested")
    if bool(app_specific_native_engine_logic_requested):
        blockers.append("app_specific_native_engine_logic_requested")

    plan = None
    if not blockers:
        plan = plan_v3_prepared_graph_chunk_executor(
            graph_id=graph_id,
            contract_key=contract_key,
            operation=operation,
            item_count=item_count,
            max_item_count=max_item_count,
            axis_name=axis_name,
            requires_partner_continuation=True,
            continuation_kind=continuation_kind,
        )
    return {
        "version": V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_VERSION,
        "status": V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_STATUS,
        "app_id": normalized_app_id,
        "graph_id": str(graph_id),
        "contract_key": str(contract_key),
        "operation": str(operation),
        "axis_name": str(axis_name),
        "item_count": int(item_count),
        "max_item_count": int(max_item_count),
        "ready_for_m113_plan": not blockers,
        "adoption_status": "ready_for_m113_plan" if not blockers else "blocked_for_m113_plan",
        "blockers": tuple(blockers),
        "plan": plan,
        "requires_partner_continuation": True,
        "prepared_scene_reuse_available": bool(prepared_scene_reuse_available),
        "prepared_item_handle_per_chunk_available": bool(
            prepared_item_handle_per_chunk_available
        ),
        "prepared_graph_capture_validated": bool(prepared_graph_capture_validated),
        "partner_continuation_explicit": bool(partner_continuation_explicit),
        "partner_continuation_associative": bool(partner_continuation_associative),
        "host_materialization_before_partner": bool(host_materialization_before_partner),
        "aggregate_only_substitute_requested": bool(aggregate_only_substitute_requested),
        "hidden_auto_dispatch_requested": bool(hidden_auto_dispatch_requested),
        "automatic_partner_selection_requested": bool(automatic_partner_selection_requested),
        "app_specific_native_engine_logic_requested": bool(
            app_specific_native_engine_logic_requested
        ),
        "automatic_partner_selection_authorized": False,
        "public_speedup_claim_authorized": False,
        "runtime_executed": False,
    }


def validate_v3_prepared_graph_chunk_executor_adoption(
    adoption: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(adoption, Mapping):
        raise GraphValidationError("prepared graph chunk adoption must be a mapping")
    if adoption.get("version") != V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_VERSION:
        raise GraphValidationError("unexpected prepared graph chunk adoption version")
    if adoption.get("status") != V3_PREPARED_GRAPH_CHUNK_ADOPTION_GATE_STATUS:
        raise GraphValidationError("unexpected prepared graph chunk adoption status")
    blockers = tuple(str(blocker) for blocker in adoption.get("blockers", ()))
    ready = bool(adoption.get("ready_for_m113_plan"))
    if ready and blockers:
        raise GraphValidationError("ready prepared graph chunk adoption cannot have blockers")
    if not ready and not blockers:
        raise GraphValidationError("blocked prepared graph chunk adoption must list blockers")
    if bool(adoption.get("automatic_partner_selection_authorized")):
        raise GraphValidationError("prepared graph chunk adoption cannot authorize automatic partner selection")
    if bool(adoption.get("public_speedup_claim_authorized")):
        raise GraphValidationError("prepared graph chunk adoption cannot authorize public speedup claims")
    if bool(adoption.get("runtime_executed")):
        raise GraphValidationError("prepared graph chunk adoption gate must not claim runtime execution")
    plan = adoption.get("plan")
    if ready:
        if not isinstance(plan, Mapping):
            raise GraphValidationError("ready prepared graph chunk adoption must include a plan")
        plan_validation = validate_v3_prepared_graph_chunk_executor_plan(plan)
        plan_status = plan.get("plan_status")
        chunk_count = plan_validation["chunk_count"]
    else:
        if plan is not None:
            raise GraphValidationError("blocked prepared graph chunk adoption must not include a plan")
        plan_status = "blocked_for_m113_plan"
        chunk_count = 0
    return {
        "status": "accept",
        "version": adoption.get("version"),
        "app_id": adoption.get("app_id"),
        "ready_for_m113_plan": ready,
        "adoption_status": adoption.get("adoption_status"),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "plan_status": plan_status,
        "chunk_count": chunk_count,
        "runtime_executed": False,
        "public_claim_authorized": False,
    }


def assess_v3_chunk_local_prepared_handle_readiness(
    *,
    app_id: str,
    contract_key: str,
    operation: str,
    item_count: int,
    max_item_count: int,
    whole_dataset_prepared_handle_available: bool,
    caller_owned_item_columns_available: bool,
    chunk_slice_prepare_api_available: bool,
    live_chunk_handle_smoke_validated: bool,
    prepared_graph_capture_validated: bool,
    partner_continuation_explicit: bool,
    partner_continuation_associative: bool,
    host_materialization_before_partner: bool,
    axis_name: str = "query",
) -> dict[str, object]:
    """Assess whether a workload has the chunk-local prepared handle layer.

    This gate is narrower than the M120 adoption gate. It separates API-shape
    readiness from runtime validation: a workload may have a whole-dataset
    prepared handle and caller-owned item columns, but still be blocked until a
    live chunk-handle smoke and graph capture are validated.
    """

    normalized_app_id = str(app_id).strip()
    if not normalized_app_id:
        raise GraphValidationError("chunk-local prepared handle app_id must be non-empty")
    validate_v3_public_name(contract_key, label="chunk-local prepared handle contract_key")
    validate_v3_public_name(operation, label="chunk-local prepared handle operation")
    validate_v3_public_name(axis_name, label="chunk-local prepared handle axis_name")
    normalized_item_count = int(item_count)
    normalized_max_item_count = int(max_item_count)
    if normalized_item_count <= 0:
        raise GraphValidationError("chunk-local prepared handle item_count must be positive")
    if normalized_max_item_count <= 0:
        raise GraphValidationError("chunk-local prepared handle max_item_count must be positive")

    api_shape_ready = (
        bool(whole_dataset_prepared_handle_available)
        and bool(caller_owned_item_columns_available)
        and bool(chunk_slice_prepare_api_available)
    )
    blockers = []
    if not bool(whole_dataset_prepared_handle_available):
        blockers.append("missing_whole_dataset_prepared_handle")
    if not bool(caller_owned_item_columns_available):
        blockers.append("missing_caller_owned_item_columns")
    if not bool(chunk_slice_prepare_api_available):
        blockers.append("missing_chunk_slice_prepare_api")
    if not bool(live_chunk_handle_smoke_validated):
        blockers.append("live_chunk_handle_smoke_not_validated")
    if not bool(prepared_graph_capture_validated):
        blockers.append("prepared_graph_capture_not_validated")
    if not bool(partner_continuation_explicit):
        blockers.append("missing_explicit_partner_continuation")
    if not bool(partner_continuation_associative):
        blockers.append("partner_continuation_not_associative")
    if bool(host_materialization_before_partner):
        blockers.append("host_materialization_before_partner")

    plan = None
    if not blockers:
        plan = plan_v3_prepared_graph_chunk_executor(
            graph_id=f"{contract_key}_chunk_local_handle",
            contract_key=contract_key,
            operation=operation,
            item_count=normalized_item_count,
            max_item_count=normalized_max_item_count,
            axis_name=axis_name,
            requires_partner_continuation=True,
            continuation_kind="chunk_local_prepared_handle_partner_continuation",
        )

    return {
        "version": V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_VERSION,
        "status": V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_STATUS,
        "app_id": normalized_app_id,
        "contract_key": str(contract_key),
        "operation": str(operation),
        "axis_name": str(axis_name),
        "item_count": normalized_item_count,
        "max_item_count": normalized_max_item_count,
        "api_shape_ready": api_shape_ready,
        "ready_for_m113_plan": not blockers,
        "readiness_status": (
            "ready_for_m113_plan" if not blockers else "blocked_for_m113_plan"
        ),
        "blockers": tuple(blockers),
        "plan": plan,
        "whole_dataset_prepared_handle_available": bool(
            whole_dataset_prepared_handle_available
        ),
        "caller_owned_item_columns_available": bool(caller_owned_item_columns_available),
        "chunk_slice_prepare_api_available": bool(chunk_slice_prepare_api_available),
        "live_chunk_handle_smoke_validated": bool(live_chunk_handle_smoke_validated),
        "prepared_graph_capture_validated": bool(prepared_graph_capture_validated),
        "partner_continuation_explicit": bool(partner_continuation_explicit),
        "partner_continuation_associative": bool(partner_continuation_associative),
        "host_materialization_before_partner": bool(host_materialization_before_partner),
        "runtime_executed": False,
        "automatic_partner_selection_authorized": False,
        "public_speedup_claim_authorized": False,
    }


def validate_v3_chunk_local_prepared_handle_readiness(
    readiness: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(readiness, Mapping):
        raise GraphValidationError("chunk-local prepared handle readiness must be a mapping")
    if readiness.get("version") != V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_VERSION:
        raise GraphValidationError("unexpected chunk-local prepared handle readiness version")
    if readiness.get("status") != V3_CHUNK_LOCAL_PREPARED_HANDLE_GATE_STATUS:
        raise GraphValidationError("unexpected chunk-local prepared handle readiness status")
    blockers = tuple(str(blocker) for blocker in readiness.get("blockers", ()))
    ready = bool(readiness.get("ready_for_m113_plan"))
    if ready and blockers:
        raise GraphValidationError("ready chunk-local prepared handle cannot have blockers")
    if not ready and not blockers:
        raise GraphValidationError("blocked chunk-local prepared handle must list blockers")
    if bool(readiness.get("runtime_executed")):
        raise GraphValidationError("chunk-local prepared handle gate must not claim runtime execution")
    if bool(readiness.get("automatic_partner_selection_authorized")):
        raise GraphValidationError("chunk-local prepared handle gate cannot authorize automatic partner selection")
    if bool(readiness.get("public_speedup_claim_authorized")):
        raise GraphValidationError("chunk-local prepared handle gate cannot authorize public speedup")

    plan = readiness.get("plan")
    if ready:
        if not isinstance(plan, Mapping):
            raise GraphValidationError("ready chunk-local prepared handle must include a plan")
        plan_validation = validate_v3_prepared_graph_chunk_executor_plan(plan)
        plan_status = plan.get("plan_status")
        chunk_count = plan_validation["chunk_count"]
    else:
        if plan is not None:
            raise GraphValidationError("blocked chunk-local prepared handle must not include a plan")
        plan_status = "blocked_for_m113_plan"
        chunk_count = 0
    return {
        "status": "accept",
        "version": readiness.get("version"),
        "app_id": readiness.get("app_id"),
        "api_shape_ready": bool(readiness.get("api_shape_ready")),
        "ready_for_m113_plan": ready,
        "readiness_status": readiness.get("readiness_status"),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "plan_status": plan_status,
        "chunk_count": chunk_count,
        "runtime_executed": False,
        "public_claim_authorized": False,
    }


def combine_v3_chunked_unique_count_key_payloads(
    chunk_payloads: tuple[Mapping[str, object], ...],
) -> dict[str, object]:
    """Merge per-chunk unique-key/count payloads as an associative continuation."""

    if not chunk_payloads:
        raise GraphValidationError("unique-count continuation requires at least one chunk")
    merged_counts: dict[tuple[object, ...], int] = {}
    chunk_summaries = []
    for chunk_index, payload in enumerate(chunk_payloads):
        if not isinstance(payload, Mapping):
            raise GraphValidationError("unique-count chunk payload must be a mapping")
        keys = tuple(payload.get("keys", ()))
        counts = tuple(payload.get("counts", (1 for _ in keys)))
        if len(keys) != len(counts):
            raise GraphValidationError("unique-count chunk keys/counts length mismatch")
        normalized_keys = []
        for key, count in zip(keys, counts):
            if isinstance(key, tuple):
                normalized_key = key
            else:
                try:
                    normalized_key = tuple(key)  # type: ignore[arg-type]
                except TypeError:
                    normalized_key = (key,)
            normalized_count = int(count)
            if normalized_count <= 0:
                raise GraphValidationError("unique-count chunk counts must be positive")
            merged_counts[normalized_key] = merged_counts.get(normalized_key, 0) + normalized_count
            normalized_keys.append(normalized_key)
        chunk_summaries.append(
            {
                "chunk_index": chunk_index,
                "key_count": len(normalized_keys),
                "weight_sum": sum(int(value) for value in counts),
            }
        )

    sorted_items = tuple(sorted(merged_counts.items()))
    return {
        "version": V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_VERSION,
        "status": "associative_unique_count_key_payload_merge",
        "chunk_count": len(chunk_payloads),
        "chunk_summaries": tuple(chunk_summaries),
        "unique_keys": tuple(key for key, _count in sorted_items),
        "counts": tuple(count for _key, count in sorted_items),
        "unique_key_count": len(sorted_items),
        "total_weight": sum(count for _key, count in sorted_items),
        "scalar_chunk_sum": sum(summary["key_count"] for summary in chunk_summaries),
        "cross_chunk_duplicate_delta": (
            sum(summary["key_count"] for summary in chunk_summaries) - len(sorted_items)
        ),
        "runtime_executed": False,
        "public_speedup_claim_authorized": False,
    }


def assess_v3_chunked_unique_count_continuation_readiness(
    *,
    app_id: str,
    contract_key: str,
    operation: str,
    item_count: int,
    max_item_count: int,
    prepared_scene_reuse_available: bool,
    prepared_item_handle_per_chunk_available: bool,
    prepared_graph_capture_validated: bool,
    per_chunk_unique_payload_available: bool,
    key_payload_carries_counts: bool,
    duplicate_keys_can_cross_chunk_boundaries: bool,
    chunk_key_ranges_disjoint: bool,
    final_key_payload_merge_validated: bool,
    host_materialization_before_partner: bool,
    axis_name: str = "query",
) -> dict[str, object]:
    """Gate chunked unique/count continuations before adopting M113."""

    normalized_app_id = str(app_id).strip()
    if not normalized_app_id:
        raise GraphValidationError("chunked unique-count app_id must be non-empty")
    validate_v3_public_name(contract_key, label="chunked unique-count contract_key")
    validate_v3_public_name(operation, label="chunked unique-count operation")
    validate_v3_public_name(axis_name, label="chunked unique-count axis_name")
    normalized_item_count = int(item_count)
    normalized_max_item_count = int(max_item_count)
    if normalized_item_count <= 0:
        raise GraphValidationError("chunked unique-count item_count must be positive")
    if normalized_max_item_count <= 0:
        raise GraphValidationError("chunked unique-count max_item_count must be positive")

    associative_duplicate_policy_available = (
        not bool(duplicate_keys_can_cross_chunk_boundaries)
        or bool(chunk_key_ranges_disjoint)
        or (
            bool(per_chunk_unique_payload_available)
            and bool(key_payload_carries_counts)
            and bool(final_key_payload_merge_validated)
        )
    )

    blockers = []
    if not bool(prepared_scene_reuse_available):
        blockers.append("missing_prepared_scene_reuse")
    if not bool(prepared_item_handle_per_chunk_available):
        blockers.append("missing_prepared_item_handle_per_chunk")
    if not bool(prepared_graph_capture_validated):
        blockers.append("prepared_graph_capture_not_validated")
    if not bool(per_chunk_unique_payload_available):
        blockers.append("missing_per_chunk_unique_payload")
    if bool(duplicate_keys_can_cross_chunk_boundaries):
        if not bool(key_payload_carries_counts):
            blockers.append("missing_key_count_payload")
        if not associative_duplicate_policy_available:
            blockers.append("chunk_boundary_duplicate_handling_not_associative")
    if bool(key_payload_carries_counts) and not bool(final_key_payload_merge_validated):
        blockers.append("final_key_payload_merge_not_validated")
    if bool(host_materialization_before_partner):
        blockers.append("host_materialization_before_partner")

    plan = None
    if not blockers:
        continuation_kind = (
            "chunked_unique_count_disjoint_scalar_sum"
            if bool(chunk_key_ranges_disjoint)
            else "chunked_unique_count_key_payload_merge"
        )
        plan = plan_v3_prepared_graph_chunk_executor(
            graph_id=f"{contract_key}_unique_count_chunks",
            contract_key=contract_key,
            operation=operation,
            item_count=normalized_item_count,
            max_item_count=normalized_max_item_count,
            axis_name=axis_name,
            requires_partner_continuation=True,
            continuation_kind=continuation_kind,
        )

    return {
        "version": V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_VERSION,
        "status": V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_STATUS,
        "app_id": normalized_app_id,
        "contract_key": str(contract_key),
        "operation": str(operation),
        "axis_name": str(axis_name),
        "item_count": normalized_item_count,
        "max_item_count": normalized_max_item_count,
        "ready_for_m113_plan": not blockers,
        "readiness_status": (
            "ready_for_m113_plan" if not blockers else "blocked_for_m113_plan"
        ),
        "blockers": tuple(blockers),
        "plan": plan,
        "prepared_scene_reuse_available": bool(prepared_scene_reuse_available),
        "prepared_item_handle_per_chunk_available": bool(
            prepared_item_handle_per_chunk_available
        ),
        "prepared_graph_capture_validated": bool(prepared_graph_capture_validated),
        "per_chunk_unique_payload_available": bool(per_chunk_unique_payload_available),
        "key_payload_carries_counts": bool(key_payload_carries_counts),
        "duplicate_keys_can_cross_chunk_boundaries": bool(
            duplicate_keys_can_cross_chunk_boundaries
        ),
        "chunk_key_ranges_disjoint": bool(chunk_key_ranges_disjoint),
        "final_key_payload_merge_validated": bool(final_key_payload_merge_validated),
        "associative_duplicate_policy_available": associative_duplicate_policy_available,
        "host_materialization_before_partner": bool(host_materialization_before_partner),
        "runtime_executed": False,
        "automatic_partner_selection_authorized": False,
        "public_speedup_claim_authorized": False,
    }


def validate_v3_chunked_unique_count_continuation_readiness(
    readiness: Mapping[str, object],
) -> dict[str, object]:
    if not isinstance(readiness, Mapping):
        raise GraphValidationError("chunked unique-count readiness must be a mapping")
    if readiness.get("version") != V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_VERSION:
        raise GraphValidationError("unexpected chunked unique-count readiness version")
    if readiness.get("status") != V3_CHUNKED_UNIQUE_COUNT_CONTINUATION_GATE_STATUS:
        raise GraphValidationError("unexpected chunked unique-count readiness status")
    blockers = tuple(str(blocker) for blocker in readiness.get("blockers", ()))
    ready = bool(readiness.get("ready_for_m113_plan"))
    if ready and blockers:
        raise GraphValidationError("ready chunked unique-count continuation cannot have blockers")
    if not ready and not blockers:
        raise GraphValidationError("blocked chunked unique-count continuation must list blockers")
    if bool(readiness.get("runtime_executed")):
        raise GraphValidationError("chunked unique-count gate must not claim runtime execution")
    if bool(readiness.get("automatic_partner_selection_authorized")):
        raise GraphValidationError("chunked unique-count gate cannot authorize automatic partner selection")
    if bool(readiness.get("public_speedup_claim_authorized")):
        raise GraphValidationError("chunked unique-count gate cannot authorize public speedup")

    plan = readiness.get("plan")
    if ready:
        if not isinstance(plan, Mapping):
            raise GraphValidationError("ready chunked unique-count continuation must include a plan")
        plan_validation = validate_v3_prepared_graph_chunk_executor_plan(plan)
        plan_status = plan.get("plan_status")
        chunk_count = plan_validation["chunk_count"]
    else:
        if plan is not None:
            raise GraphValidationError("blocked chunked unique-count continuation must not include a plan")
        plan_status = "blocked_for_m113_plan"
        chunk_count = 0

    return {
        "status": "accept",
        "version": readiness.get("version"),
        "app_id": readiness.get("app_id"),
        "ready_for_m113_plan": ready,
        "readiness_status": readiness.get("readiness_status"),
        "blocker_count": len(blockers),
        "blockers": blockers,
        "associative_duplicate_policy_available": bool(
            readiness.get("associative_duplicate_policy_available")
        ),
        "plan_status": plan_status,
        "chunk_count": chunk_count,
        "runtime_executed": False,
        "public_claim_authorized": False,
    }


def combine_v3_prepared_graph_chunk_signatures(
    chunk_signatures: tuple[tuple[tuple[int, ...], ...], ...],
) -> tuple[tuple[int, ...], ...]:
    if not chunk_signatures:
        raise GraphValidationError("prepared graph chunk signature requires at least one chunk")
    request_count = len(chunk_signatures[0])
    width = len(chunk_signatures[0][0]) if request_count else 0
    if request_count <= 0 or width <= 0:
        raise GraphValidationError("prepared graph chunk signature rows must be non-empty")
    totals = [[0 for _ in range(width)] for _ in range(request_count)]
    for signature in chunk_signatures:
        if len(signature) != request_count:
            raise GraphValidationError("prepared graph chunk signatures have inconsistent row counts")
        for request_index, row in enumerate(signature):
            if len(row) != width:
                raise GraphValidationError("prepared graph chunk signature rows have inconsistent width")
            for value_index, value in enumerate(row):
                totals[request_index][value_index] += int(value)
    return tuple(tuple(row) for row in totals)
