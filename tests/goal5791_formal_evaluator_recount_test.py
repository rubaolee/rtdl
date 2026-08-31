from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import tempfile
import unittest

from scripts import goal5791_formal_evaluate as primary
from scripts import goal5791_formal_independent_recount as independent
from scripts import goal5791_formal_controller as controller
from scripts.goal5791_formal_contract import (
    ALLOWED_DELTA_ID,
    AUTHORITY_ROLES,
    CACHE_POLICY,
    COLD,
    DATA_AUTHORITY_DATASETS,
    DATA_AUTHORITY_FILE_SHA256,
    DATA_AUTHORITY_SHA256,
    FUSION_OFF,
    FUSION_OFF_OPERATION_IDS,
    FUSION_ON,
    FUSION_ON_OPERATION_IDS,
    FORMAL_AUTHORIZATION,
    FORMAL_EXECUTION_POLICY,
    FORMAL_WORKER_ENVIRONMENT_CONTRACT,
    GOAL,
    MECHANISM_ID,
    OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA,
    OWNER_FORMAL_EXECUTION_STATUS,
    PAPER_OUTCOME_CONSEQUENCE_CONTRACT,
    POSTPREPARE_STATUS,
    PREEXECUTION_AUTHORITY_SCHEMA,
    PREPARED,
    SEMANTIC_REQUEST_SHA256,
    PHYSICAL_ENCODING_SHA256,
    SEGMENT_PLAN_INPUT_CONTRACT,
    SOURCE_ADMISSION_POLICY,
    TARGET_BINDING_SCHEMA,
    TARGET_BINDING_STATUS,
    TARGET_HASH_SLOTS,
    contract_document,
    contract_sha256,
    digest,
    lifecycle_contract,
    lifecycle_contract_sha256,
    oracle_contract_sha256,
    output_contract_sha256,
    pod_endpoint_identity_record,
    provider_program_bundle_digest_record,
    schedule,
    schedule_document,
    schedule_sha256,
    statistical_rows,
    timer_contract,
    timer_contract_sha256,
    validate_target_materialization_binding,
)
from rtdsl.v4_fusion_ablation import (
    FusionVariant,
    SHARED_CONTRACT_FREEZE_SHA256,
    TARGET_MATERIALIZATION_AUTHORITY_SCHEMA,
    build_checked_u64_product_sum_ablation_plan,
    load_verified_shared_contract_freeze,
    verify_target_materialization_authority,
)
from rtdsl.v4_checked_u64_device_reduction import (
    checked_u64_downstream_operation_identity,
)


ROOT = Path(__file__).resolve().parents[1]
DATA_AUTHORITY = (
    ROOT / "history" / "internal_docs"
    / "goal5791_frozen_triangle_data_and_oracle_authority_20260817.json"
)
SHARED_FREEZE = (
    ROOT / "history" / "internal_docs" / "goal5789_contract_evidence_20260816"
    / "GOAL5789_GOAL5790_SHARED_CONTRACT_FREEZE.json"
)


def _write(path: Path, value: object) -> None:
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n",
    )


def _file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _identity(label: str) -> str:
    return digest({"goal5791_test_identity": label})


def _no_gpu_process_state(phase: str) -> dict[str, object]:
    names = sorted({
        "__main__", "hashlib", "json", "scripts.goal5791_formal_contract",
    })
    lines = [
        "00400000-00452000 r-xp 00000000 08:01 1 /usr/bin/python3.13",
        "7f000000-7f001000 r--p 00000000 08:01 2 /usr/lib/libc.so.6",
    ]
    maps_bytes = ("\n".join(lines) + "\n").encode("utf-8")
    contract = primary.NO_GPU_PRODUCT_PROCESS_STATE_OBSERVATION_CONTRACT
    return {
        "schema": contract["schema"],
        "phase": phase,
        "forbidden_module_prefixes": list(
            contract["forbidden_module_prefixes"]
        ),
        "forbidden_dso_map_markers": list(
            contract["forbidden_dso_map_markers"]
        ),
        "loaded_module_names": names,
        "proc_self_maps_lines": lines,
        "proc_self_maps_sha256": hashlib.sha256(maps_bytes).hexdigest(),
        "forbidden_module_matches": [],
        "forbidden_dso_map_matches": [],
    }


def _seal(value: dict[str, object], field: str) -> dict[str, object]:
    result = dict(value)
    result[field] = digest(value)
    return result


def _target_authority() -> object:
    target_sha = _identity("target-identity")
    cupy_version = "14.0.1"
    on_recipe = checked_u64_downstream_operation_identity(
        FUSION_ON, target_identity_sha256=target_sha,
        cupy_version=cupy_version,
    )
    off_recipe = checked_u64_downstream_operation_identity(
        FUSION_OFF, target_identity_sha256=target_sha,
        cupy_version=cupy_version,
    )
    body = {
        "schema": TARGET_MATERIALIZATION_AUTHORITY_SCHEMA,
        "shared_contract_freeze_sha256": SHARED_CONTRACT_FREEZE_SHA256,
        "execution_source_archive_sha256": _identity("source-archive"),
        "execution_source_tree_sha256": _identity("source-tree"),
        "callback_ir_sha256": _identity("callback-ir"),
        "callback_authority_nonce": "a" * 64,
        "contract_sha256": _identity("callback-contract"),
        "abi_sha256": _identity("callback-abi"),
        "provider_identity": "optix",
        "program_bundle_identity": primary.PROGRAM_BUNDLE,
        "composed_program_sha256": _identity("composed-program"),
        "cupy_version": cupy_version,
        "fusion_on_downstream_operation_recipe": on_recipe,
        "fusion_off_downstream_operation_recipe": off_recipe,
        "fusion_on_downstream_operation_recipe_sha256": digest(on_recipe),
        "fusion_off_downstream_operation_recipe_sha256": digest(off_recipe),
        "native_library_sha256": _identity("native"),
        "native_payload_sha256": _identity("native"),
        "target_identity_sha256": target_sha,
        "materializer_source_sha256": _identity("materializer"),
        "source_manifest_sha256": _identity("source-manifest"),
        "evidence_archive_sha256": _identity("target-evidence"),
        "materialization_nonce": "b" * 64,
        "actual_native_rehashed_from_preserved_payload": True,
        "actual_source_tree_recounted_from_preserved_archive": True,
        "cross_target_native_byte_reproducibility_claimed": False,
    }
    body["receipt_sha256"] = digest(body)
    return verify_target_materialization_authority(body)


def _shared_freeze():
    return load_verified_shared_contract_freeze(SHARED_FREEZE.read_bytes())


def _program_bundle_id() -> int:
    value = 1469598103934665603
    for byte in primary.PROGRAM_BUNDLE.encode("utf-8"):
        value ^= byte
        value = (value * 1099511628211) & ((1 << 64) - 1)
    return value


def _behavioral_receipt(
    worker_index: int, segment_index: int, output_sha: str,
    native_sha: str, query_count: int, semantic_binding: dict[str, object],
) -> dict[str, object]:
    nonce_hi = 700_000 + worker_index
    nonce_lo = 900_000 + segment_index
    bundle_id = _program_bundle_id()
    body = {
        "schema": "rtdl.physical_execution.traversal_receipt.v1",
        "provider_library": "librtdl_optix",
        "provider_library_path": "/goal5791/librtdl_optix.so",
        "provider_library_sha256": native_sha,
        "route_identity": (
            "v4_builtin_triangle_callback_ir:partner_resident_checked_count_v1"
        ),
        "semantic_digest": digest(semantic_binding),
        "physical_executor_classification": "optix_traversal_observed",
        "output_digest": output_sha,
        "nonce": {"hi": nonce_hi, "lo": nonce_lo},
        "expected_program_bundles": [primary.PROGRAM_BUNDLE],
        "expected_program_bundle_ids": [bundle_id],
        "expected_program_observed_at_receipt_edge": True,
        "native_snapshot": {
            "nonce_hi": nonce_hi, "nonce_lo": nonce_lo,
            "attempted_launch_count": 2, "successful_launch_count": 2,
            "complete_context_launch_count": 2, "failed_launch_count": 0,
            "incomplete_context_launch_count": 0, "context_bind_count": 2,
            "raygen_invocation_count": query_count,
            "program_bundle_mix": bundle_id, "traversable_mix": 11,
            "pipeline_mix": 12, "sbt_mix": 13, "stream_mix": 14,
            "params_mix": 15, "callsite_mix": 16,
            "first_program_bundle_id": bundle_id,
            "last_program_bundle_id": bundle_id,
            "pending_context_at_finish": 0, "session_error": 0,
            "first_traversable": 17 + segment_index,
            "last_traversable": 17 + segment_index,
            "incomplete_callsite_record_count": 0,
            "incomplete_callsite_lines": [0] * 32,
        },
        "claim_rules": primary.TRAVERSAL_CLAIM_RULES,
    }
    return {**body, "receipt_sha256": digest(body)}


def _operation_receipt(
    *, worker_index: int, segment_index: int, variant: str,
    plan: dict[str, object], output_sha: str,
    behavioral: dict[str, object],
) -> dict[str, object]:
    plan_sha = str(plan["plan_sha256"])
    value_count = int(plan["value_count"])
    requirements = plan["operation_requirements"]
    contract_body = {
        "schema": primary.OPERATION_CONTRACT_SCHEMA,
        "plan_sha256": plan_sha, "mechanism_id": MECHANISM_ID,
        "variant": variant, "declared_value_count": value_count,
        "requirements": requirements,
        "tcb_statement": primary.OPERATION_EVIDENCE_TCB,
        "timing_or_duration_recorded": False,
        "hardware_introspection_claimed": False,
    }
    contract_sha = digest(contract_body)
    previous = contract_sha
    events = []
    for index, requirement in enumerate(requirements):
        units = (
            requirement["units_per_value"] * value_count
            + requirement["fixed_units"]
        )
        event = {
            "schema": primary.OPERATION_EVENT_SCHEMA,
            "sequence": index, "operation_id": requirement["operation_id"],
            "kind": requirement["kind"], "accounted_units": units,
            "accounted_bytes": (
                requirement["bytes_per_unit"] * units
                + requirement["fixed_bytes"]
            ),
            "previous_event_sha256": previous,
            "recorded_after_callable_success": True,
        }
        event["event_sha256"] = digest(event)
        previous = event["event_sha256"]
        events.append(event)
    body = {
        "schema": primary.OPERATION_RECEIPT_SCHEMA,
        "contract_sha256": contract_sha, "plan_sha256": plan_sha,
        "mechanism_id": MECHANISM_ID, "variant": variant,
        "execution_nonce": (
            f"goal5791-worker-{worker_index:04d}-segment-{segment_index:06d}"
        ),
        "value_count": value_count, "output_sha256": output_sha,
        "traversal_receipt_sha256": behavioral["receipt_sha256"],
        "events": events, "event_chain_sha256": previous,
        "successful_event_count": len(events),
        "event_evidence_tcb": primary.OPERATION_EVIDENCE_TCB,
        "hardware_introspection_claimed": False,
        "opaque_partner_kernel_count_claimed": False,
        "timing_or_duration_recorded": False,
    }
    return {**body, "receipt_sha256": digest(body)}


def _checked_reduction(
    variant: str, *, query_count: int, primitive_count: int, scalar_sum: int,
) -> dict[str, object]:
    on = variant == FUSION_ON
    return {
        "schema": "rtdl.v4.checked_u64_weighted_reduction.receipt.v1",
        "maximum_value": primitive_count, "maximum_weight": 1,
        "weight_sum": query_count, "value_count": query_count,
        "value_upper_bound": primitive_count,
        "device_kernel_launch_count": 1 if on else 0,
        "host_synchronization_count": 1 if on else 3,
        "logical_reduction_count": 0 if on else 3,
        "device_materialization_count": 0 if on else 1,
        "operation_counts_event_derived": True,
        "maximum_value_is_device_observed": on,
        "maximum_value_provenance": (
            "device_observed" if on
            else "optix_producer_declared_primitive_bound"
        ),
        "provisional_sum_trusted_only_after_bounds": True,
    }


def _target_binding(target: dict[str, object], target_file_sha: str) -> dict[str, object]:
    hashes = {name: _identity("target:" + name) for name in TARGET_HASH_SLOTS}
    hashes.update({
        "execution_source_archive_sha256": target["execution_source_archive_sha256"],
        "execution_source_tree_sha256": target["execution_source_tree_sha256"],
        "execution_source_manifest_sha256": target["source_manifest_sha256"],
        "native_library_sha256": target["native_library_sha256"],
        "native_payload_sha256": target["native_payload_sha256"],
        "provider_library_sha256": target["native_library_sha256"],
        "target_identity_sha256": target["target_identity_sha256"],
        "semantic_request_sha256": SEMANTIC_REQUEST_SHA256,
        "physical_encoding_sha256": PHYSICAL_ENCODING_SHA256,
        "callback_ir_sha256": target["callback_ir_sha256"],
        "contract_sha256": target["contract_sha256"],
        "abi_sha256": target["abi_sha256"],
        "composed_program_sha256": target["composed_program_sha256"],
        "composed_ptx_sha256": target["composed_program_sha256"],
        "fusion_off_recipe_sha256": target["fusion_off_downstream_operation_recipe_sha256"],
        "fusion_on_recipe_sha256": target["fusion_on_downstream_operation_recipe_sha256"],
        "materializer_sha256": target["materializer_source_sha256"],
        "target_source_manifest_sha256": target["source_manifest_sha256"],
        "target_evidence_contract_sha256": _identity("target-evidence-contract"),
        "target_materialization_authority_sha256": target_file_sha,
    })
    formal_identity_preimage = {
        "schema": "rtdl.goal5791.formal_identity.v1",
        "prepared_identity_sha256": hashes["prepared_identity_sha256"],
        "runtime_identity_sha256": hashes["runtime_identity_sha256"],
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "formal_sources": {
            name: _identity("formal-source:" + name)
            for name in primary.FORMAL_SOURCE_PATHS
        },
        "formal_worker_count": 96,
        "independent_row_count": 6,
    }
    hashes["formal_identity_sha256"] = digest(formal_identity_preimage)
    nonces = {
        "callback_authority_nonce": target["callback_authority_nonce"],
        "target_evidence_nonce": _identity("independent-target-evidence-nonce"),
    }
    versions = {
        "gpu_uuid": "GPU-goal5791-test",
        "compute_capability": "8.9",
        "driver_version": "test-driver",
        "cuda_runtime_version": "test-cuda",
        "optix_sdk_version": "9.0.0",
        "python_version": "3.13.0",
        "cupy_version": target["cupy_version"],
    }
    recipes = {}
    for variant, prefix, events in (
        (FUSION_OFF, "fusion_off", FUSION_OFF_OPERATION_IDS),
        (FUSION_ON, "fusion_on", FUSION_ON_OPERATION_IDS),
    ):
        actual = target[prefix + "_downstream_operation_recipe"]
        wrapper = {
            "variant": variant,
            "mechanism_id": MECHANISM_ID,
            "allowed_delta_id": ALLOWED_DELTA_ID,
            "operation_ids": list(events),
        }
        recipes[variant] = {
            "actual_recipe": actual,
            "actual_recipe_sha256": digest(actual),
            "claim_wrapper": wrapper,
            "claim_wrapper_sha256": digest(wrapper),
        }
    program = provider_program_bundle_digest_record(hashes, nonces)
    hashes["provider_program_bundle_sha256"] = program["sha256"]
    payload = {
        "schema": TARGET_BINDING_SCHEMA,
        "goal": GOAL,
        "status": TARGET_BINDING_STATUS,
        "hashes": hashes,
        "nonces": nonces,
        "versions": versions,
        "recipes": recipes,
        "derived_digests": {"provider_program_bundle": program},
        "cache_policy": CACHE_POLICY,
    }
    binding = _seal(payload, "binding_sha256")
    validate_target_materialization_binding(binding)
    return binding


def _formal_identity_record(binding: dict[str, object]) -> dict[str, object]:
    hashes = binding["hashes"]
    body = {
        "schema": "rtdl.goal5791.formal_identity.v1",
        "prepared_identity_sha256": hashes["prepared_identity_sha256"],
        "runtime_identity_sha256": hashes["runtime_identity_sha256"],
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "formal_sources": {
            name: _identity("formal-source:" + name)
            for name in primary.FORMAL_SOURCE_PATHS
        },
        "formal_worker_count": 96,
        "independent_row_count": 6,
    }
    return {**body, "formal_identity_sha256": digest(body)}


def _segment_evidence(
    spec: dict[str, object], *, target_object: object,
    target: dict[str, object], expected_output: int,
) -> list[dict[str, object]]:
    target_dict = target_object.to_dict()
    values = [expected_output // 3, expected_output // 3]
    values.append(expected_output - sum(values))
    result = []
    for segment_id, scalar in enumerate(values):
        query_count = 1_000_000
        primitive_count = 1_000_000
        descriptor = {
            "schema": "rtdl.goal5791.rt2a1_segment_descriptor.v1",
            "segment_id": segment_id,
            "partition": {
                "source_begin": segment_id * 10,
                "source_end": segment_id * 10 + 10,
                "oversized_source_part": 0,
                "global_segment_id": segment_id,
            },
            "relation_count": query_count,
            "primitive_count": primitive_count,
            "query_count": query_count,
            "host_geometry_bytes": 76 * primitive_count + 68 * query_count,
            "maximum_weight": 1,
            "weight_sum": query_count,
            "paper_algorithm": "RT-2A1",
            "gpu_touched": False,
        }
        descriptor_sha = digest(descriptor)
        plan_input_binding = {
            "schema": SEGMENT_PLAN_INPUT_CONTRACT["schema"],
            "source_input_sha256": DATA_AUTHORITY_DATASETS[
                str(spec["dataset_id"])
            ]["sha256"],
            "segment_descriptor_sha256": descriptor_sha,
            "formal_input": True,
        }
        variant = str(spec["variant"])
        plan = build_checked_u64_product_sum_ablation_plan(
            _shared_freeze(),
            variant=FusionVariant(variant),
            target_materialization=target_object,
            input_sha256=digest(plan_input_binding),
            output_contract_sha256=output_contract_sha256(),
            oracle_sha256=DATA_AUTHORITY_DATASETS[
                str(spec["dataset_id"])
            ]["oracle_authority_sha256"],
            timer_contract_sha256=timer_contract_sha256(str(spec["lifecycle"])),
            lifecycle_contract_sha256=lifecycle_contract_sha256(str(spec["lifecycle"])),
            value_count=query_count,
        ).to_dict()
        output_sha = digest(scalar)
        semantic = {
            "authority": target_dict["callback_authority_nonce"],
            "contract": target_dict["contract_sha256"],
            "abi": target_dict["abi_sha256"],
            "composed_ptx": target_dict["composed_program_sha256"],
            "native": target_dict["native_library_sha256"],
            "device_column_count": True,
        }
        traversal = _behavioral_receipt(
            int(spec["worker_index"]), segment_id, output_sha,
            str(target_dict["native_library_sha256"]), query_count, semantic,
        )
        operation = _operation_receipt(
            worker_index=int(spec["worker_index"]), segment_index=segment_id,
            variant=variant,
            plan=plan, output_sha=output_sha, behavioral=traversal,
        )
        reduction = _checked_reduction(
            variant, query_count=query_count,
            primitive_count=primitive_count, scalar_sum=scalar,
        )
        result.append({
            "segment_id": segment_id,
            "descriptor": descriptor,
            "segment_descriptor_sha256": descriptor_sha,
            "partition": descriptor["partition"],
            "relation_count": query_count,
            "primitive_count": primitive_count,
            "query_count": query_count,
            "host_geometry_bytes": descriptor["host_geometry_bytes"],
            "scalar_sum": scalar,
            "output_sha256": output_sha,
            "plan_input_binding": plan_input_binding,
            "fusion_ablation_plan": plan,
            "token_admission": {
                "pre_admitted_in_preparation": True,
                "admitted_during_phase": "preparation",
                "creator_pid": 100_000 + int(spec["worker_index"]),
                "segment_ordinal": segment_id,
                "descriptor_sha256": descriptor_sha,
                "plan_sha256": plan["plan_sha256"],
                "plan_input_sha256": plan["input_sha256"],
                "operation_execution_nonce": operation["execution_nonce"],
                "state_before_execute": "fresh",
                "state_after_execute": "consumed",
                "single_use": True,
            },
            "operation_evidence_receipt": operation,
            "checked_u64_weighted_reduction": reduction,
            "traversal_receipt": traversal,
            "traversal_semantic_binding": semantic,
            "device_phase_terminal_state": "device_complete_unsealed",
            "evidence_phase_terminal_state": "sealed",
            "evidence_sealed_after_device_phase": True,
        })
    return result


def _phase_evidence(lifecycle: str, execute: float):
    requested = {
        "loading": 0.1,
        "preparation": 0.2,
        "prewarm": 0.0 if lifecycle == COLD else 0.3,
        "execute": execute,
        "close": 0.1,
    }
    phase_seconds = {
        phase: round(value * 1_000_000_000) / 1_000_000_000.0
        for phase, value in requested.items()
    }
    sequence = []
    cursor = 1_000_000_000
    phases = ("loading", "preparation", "prewarm", "execute", "close")
    interphase_gap_ns = 10_000_000
    for index, phase in enumerate(phases):
        duration = round(phase_seconds[phase] * 1_000_000_000)
        sequence.append({
            "phase": phase, "started_ns": cursor,
            "ended_ns": cursor + duration, "seconds": phase_seconds[phase],
        })
        cursor += duration
        if index + 1 < len(phases):
            cursor += interphase_gap_ns
    registered = (
        (
            sequence[-1]["ended_ns"] - sequence[0]["started_ns"]
        ) / 1_000_000_000.0
        if lifecycle == COLD else phase_seconds["execute"]
    )
    return phase_seconds, sequence, registered


def _worker(
    spec: dict[str, object], *, context: dict[str, object], favor: bool,
    narrow_favor: bool = False,
    favor_difference_seconds: float | None = None,
) -> dict[str, object]:
    dataset = str(spec["dataset_id"])
    expected = DATA_AUTHORITY_DATASETS[dataset]["expected_triangle_count"]
    variant = str(spec["variant"])
    pair_index = int(spec["pair_index"])
    if favor_difference_seconds is not None:
        execute = (
            1.0 + favor_difference_seconds
            if variant == FUSION_OFF else 1.0
        )
    elif narrow_favor:
        execute = (1.00001 if variant == FUSION_OFF else 1.0)
    else:
        execute = (
            (2.0 if variant == FUSION_OFF else 1.0)
            if favor else (1.0 if variant == FUSION_OFF else 2.0)
        )
    execute += pair_index * 0.001
    phase_seconds, phase_sequence, registered = _phase_evidence(
        str(spec["lifecycle"]), execute,
    )
    segments = _segment_evidence(
        spec, target_object=context["target_object"],
        target=context["target_binding"], expected_output=expected,
    )
    cache_payload = {
        "schema": "rtdl.goal5791.worker_cache_receipt.v2",
        "worker_index": spec["worker_index"],
        "cupy_cache_dir_identity": digest({
            "worker_index": spec["worker_index"],
            "directory_name": f"worker_{int(spec['worker_index']):04d}",
        }),
        "cupy_cache_dir_name": f"worker_{int(spec['worker_index']):04d}",
        "cupy_cache_relative_path": "cupy",
        "numba_cache_relative_path": "numba",
        "numba_cache_dir_identity": digest({
            "worker_index": spec["worker_index"],
            "directory_name": f"worker_{int(spec['worker_index']):04d}",
            "relative_path": "numba",
        }),
        "initially_empty_before_product_import": True,
        "cold_empty_immediately_before_execute": spec["lifecycle"] == COLD,
        "cold_empty_before_execute_applicable": spec["lifecycle"] == COLD,
        "shared_between_workers_or_measured_arms": CACHE_POLICY[
            "shared_cache_between_workers_or_measured_arms"
        ],
        "unique_per_worker": True,
        "prepared_same_worker_cache_contains_both_variant_recipes": (
            spec["lifecycle"] == PREPARED
        ),
        "selected_recipe_first_compile_inside_execute": spec["lifecycle"] == COLD,
        "measurement_started_after_both_prewarms": spec["lifecycle"] == PREPARED,
        "cold_definition": CACHE_POLICY["cold_definition"],
        "cold_claim_excludes": list(CACHE_POLICY["cold_claim_excludes"]),
        "operating_system_page_cache_controlled_or_dropped": CACHE_POLICY[
            "operating_system_page_cache_controlled_or_dropped"
        ],
        "cuda_driver_jit_cache_controlled_or_isolated": CACHE_POLICY[
            "cuda_driver_jit_cache_controlled_or_isolated"
        ],
        "optix_disk_cache_controlled_or_isolated": CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"
        ],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
            ]
        ),
    }
    if spec["lifecycle"] == COLD:
        prewarm_payload = {
            "schema": "rtdl.goal5791.worker_prewarm_receipt.v1",
            "performed": False, "order": [], "input_sha256": None,
            "rows": [], "reported_seconds": 0.0,
        }
    else:
        prewarm_payload = {
            "schema": "rtdl.goal5791.worker_prewarm_receipt.v1",
            "performed": True, "order": [FUSION_OFF, FUSION_ON],
            "input_sha256": context["runtime"]["neutral_prewarm"]["input_sha256"],
            "rows": [{
                "variant": item,
                "token_pre_admitted_in_preparation": True,
                "token_consumed_once": True, "launch_completed": True,
                "synchronized": True, "device_pool_freed": True,
                "output_exact": True, "formal_evidence_created": False,
            } for item in (FUSION_OFF, FUSION_ON)],
            "reported_seconds": phase_seconds["prewarm"],
        }
    admission = context["data_admission"]["datasets"][dataset]
    input_payload = {
        "schema": "rtdl.goal5791.worker_input_file_receipt.v1",
        "dataset_id": dataset,
        **{name: admission[name] for name in (
            "resolved_path", "bytes", "st_dev", "st_ino", "st_mtime_ns", "st_mode", "read_only",
        )},
        "observed_before_loader_read": True,
        "pre_and_post_loader_fstat_equal": True,
        "proc_self_fd_used": True,
    }
    source_admission = context["source_admission"]
    source_rehash_payload = {
        "schema": "rtdl.goal5791.worker_source_rehash_receipt.v1",
        "worker_index": spec["worker_index"],
        "source_admission_sha256": source_admission["admission_sha256"],
        **{
            name: source_admission[name] for name in (
                "execution_source_root",
                "execution_source_manifest_file_sha256",
                "execution_source_tree_sha256", "manifest_payload_count",
                "manifest_payload_bytes", "full_manifest_rehash_complete",
                "all_manifest_payloads_read_only", "manifest_file_read_only",
                "exact_regular_file_set_verified",
                "exact_implied_directory_set_verified",
                "unmanifested_path_count", "missing_manifest_payload_count",
                "symlink_or_special_path_count",
                "all_source_paths_without_write_bits", "regular_file_count",
                "source_directory_count_including_root", "source_path_count",
            )
        },
        "observed_before_product_import": True,
        "same_host_root_race_excluded": False,
        "tcb_boundary": primary.SOURCE_TCB_BOUNDARY,
    }
    payload = {
        "schema": primary.WORKER_SCHEMA, "goal": GOAL, "status": "COMPLETE",
        "formal_worker": True,
        **{name: spec[name] for name in (
            "worker_index", "row_index", "row_id", "dataset_id", "lifecycle",
            "pair_index", "order_ordinal", "variant", "paper_algorithm", "mechanism_id",
        )},
        "parent_pid": 100_000 + int(spec["worker_index"]),
        "registered_complete_endpoint_seconds": registered,
        "phase_seconds": phase_seconds, "phase_sequence": phase_sequence,
        "timer_contract_sha256": timer_contract_sha256(str(spec["lifecycle"])),
        "timer_contract": timer_contract(str(spec["lifecycle"])),
        "lifecycle_contract_sha256": lifecycle_contract_sha256(str(spec["lifecycle"])),
        "lifecycle_contract": lifecycle_contract(str(spec["lifecycle"])),
        "input_sha256": DATA_AUTHORITY_DATASETS[dataset]["sha256"],
        "output_scalar_u64": expected, "output_sha256": digest(expected),
        "oracle_output_scalar_u64": expected,
        "oracle_output_sha256": digest(expected),
        "output_contract_sha256": output_contract_sha256(),
        "oracle_contract_sha256": oracle_contract_sha256(),
        "dataset_oracle_authority_sha256": DATA_AUTHORITY_DATASETS[dataset]["oracle_authority_sha256"],
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "runtime_sha256": context["runtime"]["runtime_sha256"],
        "runtime_file_sha256": context["runtime_file_sha"],
        "preexecution_authority_file_sha256": context["pre_file_sha"],
        "preexecution_authority_sha256": context["pre"]["authority_sha256"],
        "target_materialization_binding_sha256": context["target_binding"]["binding_sha256"],
        "target_materialization_authority_file_sha256": context["target_file_sha"],
        "formal_authority_file_sha256": context["formal_file_sha"],
        "formal_authority_sha256": context["formal"]["authority_sha256"],
        "formal_identity_sha256": context["target_binding"]["hashes"]["formal_identity_sha256"],
        "runtime_budget_authority_sha256": context["pre"]["authority_records"]["runtime_budget_authority"]["sha256"],
        "data_admission_sha256": context["data_admission"]["admission_sha256"],
        "data_authority_file_sha256": DATA_AUTHORITY_FILE_SHA256,
        "source_admission_sha256": source_admission["admission_sha256"],
        "llvmlite_version": context["runtime"]["llvmlite_version"],
        "source_rehash_receipt": _seal(
            source_rehash_payload, "receipt_sha256"
        ),
        "input_file_receipt": _seal(input_payload, "receipt_sha256"),
        "target_materialization_binding": context["target_binding"],
        "cache_receipt": _seal(cache_payload, "receipt_sha256"),
        "prewarm_receipt": _seal(prewarm_payload, "receipt_sha256"),
        "segment_count": len(segments), "segment_evidence": segments,
        "two_phase_execution_evidence_seal_enforced": True,
        "evidence_hashing_or_serialization_inside_registered_timer": False,
        "comparator_inside_registered_timer": False,
        "receipt_serialization_inside_registered_timer": False,
        "execute_timer_continuous_without_pause": True,
        "deep_verification_inside_execute": False,
        "constant_time_pre_admitted_token_binding_only_inside_execute": True,
        "evidence_seal_started_after_registered_endpoint": True,
        "registered_endpoint_is_one_continuous_interval": True,
        "cold_registered_endpoint_includes_interphase_dispatch_and_cache_check": (
            spec["lifecycle"] == COLD
        ),
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    return _seal(payload, "worker_sha256")


def _raw(
    root: Path, *, favor: bool = True, narrow_favor: bool = False,
    favor_difference_seconds: float | None = None,
) -> Path:
    root.mkdir()
    (root / "workers").mkdir()
    (root / "AUTHORITIES").mkdir()
    cache_root = root / "worker_caches"
    cache_root.mkdir()
    for index in range(len(schedule())):
        (cache_root / f"worker_{index:04d}").mkdir()
    _write(root / "FORMAL_CONTRACT.json", contract_document())
    _write(root / "SCHEDULE.json", schedule_document())
    (root / "DATA_AUTHORITY.json").write_bytes(DATA_AUTHORITY.read_bytes())
    if _file_sha(root / "DATA_AUTHORITY.json") != DATA_AUTHORITY_FILE_SHA256:
        raise AssertionError("frozen data authority fixture drifted")

    target_object = _target_authority()
    target_dict = target_object.to_dict()
    _write(root / "TARGET_MATERIALIZATION_AUTHORITY.json", target_dict)
    target_file_sha = _file_sha(root / "TARGET_MATERIALIZATION_AUTHORITY.json")
    target_binding = _target_binding(target_dict, target_file_sha)
    _write(root / "TARGET_BINDING.json", target_binding)

    authority_sources = {
        "source_authority": ROOT / "history/internal_docs/goal5791_successor_source_authority_v2_20260817.json",
        "data_authority": DATA_AUTHORITY,
        "runtime_budget_authority": ROOT / "history/internal_docs/goal5791_pre_pod_conservative_runtime_budget_20260817.json",
        "expected_value_authority": ROOT / "history/internal_docs/goal5790_preregistered_expected_value_and_fallback_20260816.json",
        "citation_authority": ROOT / "history/internal_docs/goal5791_pre_worker_zero_related_work_and_claim_freeze_20260817.json",
    }
    authority_records = {}
    authority_manifest_rows = {}
    for role in AUTHORITY_ROLES:
        source = authority_sources[role]
        relative = source.relative_to(ROOT).as_posix()
        copied = root / "AUTHORITIES" / f"{role}.json"
        copied.write_bytes(source.read_bytes())
        authority_records[role] = {
            "path": relative, "sha256": _file_sha(source),
            "bytes": source.stat().st_size,
        }
        authority_manifest_rows[role] = {
            "path": f"AUTHORITIES/{role}.json",
            "file_sha256": _file_sha(copied), "bytes": copied.stat().st_size,
        }
    runtime_budget_authority = json.loads(
        authority_sources["runtime_budget_authority"].read_text(
            encoding="utf-8"
        )
    )
    pre_payload = {
        "schema": PREEXECUTION_AUTHORITY_SCHEMA,
        "goal": GOAL, "status": POSTPREPARE_STATUS,
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "authority_records": authority_records,
        "dataset_input_sha256": {
            dataset: DATA_AUTHORITY_DATASETS[dataset]["sha256"]
            for dataset in DATA_AUTHORITY_DATASETS
        },
        "oracle_authority_sha256": {
            dataset: DATA_AUTHORITY_DATASETS[dataset]["oracle_authority_sha256"]
            for dataset in DATA_AUTHORITY_DATASETS
        },
        "target_materialization_binding": target_binding,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "authorization": {
            "authorizes_pod": False, "authorizes_target_prepare": False,
            "authorizes_formal_workers": False,
            "authorizes_registered_timing": False,
        },
    }
    pre = _seal(pre_payload, "authority_sha256")
    _write(root / "PREEXECUTION_AUTHORITY.json", pre)
    pre_file_sha = _file_sha(root / "PREEXECUTION_AUTHORITY.json")
    authority_manifest = _seal({
        "schema": "rtdl.goal5791.raw_authority_manifest.v1",
        "goal": GOAL,
        "preexecution_authority_file_sha256": pre_file_sha,
        "authorities": authority_manifest_rows,
    }, "manifest_sha256")
    _write(root / "AUTHORITY_MANIFEST.json", authority_manifest)

    endpoint = pod_endpoint_identity_record(
        ssh_user="root", host="goal5791.test", port=22000,
    )
    target_materialization_root = "/tmp/goal5791_formal_test"
    formal_output_root = "/tmp/goal5791_formal_output"
    controller_staging_root = (
        "/tmp/.goal5791_formal_output.goal5791_incomplete"
    )
    formal_payload = {
        "schema": OWNER_FORMAL_EXECUTION_AUTHORITY_SCHEMA,
        "goal": GOAL, "status": OWNER_FORMAL_EXECUTION_STATUS,
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "preexecution_authority_file_sha256": pre_file_sha,
        "target_materialization_binding_sha256": target_binding["binding_sha256"],
        "formal_identity_sha256": target_binding["hashes"]["formal_identity_sha256"],
        "runtime_budget_authority_sha256": authority_records["runtime_budget_authority"]["sha256"],
        "owner_authorization_nonce": "c" * 64,
        "independent_row_count": 6, "formal_worker_count": 96,
        "execution_target": {
            "target_materialization_root": target_materialization_root,
            "create_only_formal_output_root": formal_output_root,
            "controller_incomplete_staging_root": controller_staging_root,
            "pod_endpoint": endpoint,
            "target_materialization_root_observed_existing_and_bound_at_authority_creation": True,
            "formal_output_root_observed_absent_at_authority_creation": True,
            "controller_incomplete_staging_root_observed_absent_at_authority_creation": True,
            "preexisting_or_shared_formal_output_root_allowed": False,
        },
        "execution_policy": FORMAL_EXECUTION_POLICY,
        "authorization": FORMAL_AUTHORIZATION,
    }

    datasets = {}
    admission_rows = {}
    for index, (dataset, frozen) in enumerate(DATA_AUTHORITY_DATASETS.items()):
        path = f"/tmp/goal5791_formal_test/data/{dataset}.edge"
        datasets[dataset] = {
            "edge_path": path, "input_sha256": frozen["sha256"],
            "size_bytes": frozen["bytes"],
            "expected_triangle_count": frozen["expected_triangle_count"],
            "oracle_authority_sha256": frozen["oracle_authority_sha256"],
        }
        admission_rows[dataset] = {
            "resolved_path": path, "sha256": frozen["sha256"],
            "bytes": frozen["bytes"], "st_dev": 11,
            "st_ino": 1000 + index, "st_mtime_ns": 2000,
            "st_mode": 0o100444, "read_only": True,
            "full_rehash_complete": True,
        }
    runtime_payload = {
        "schema": "rtdl.goal5791.formal_runtime.v1", "goal": GOAL,
        "status": "TARGET_PREPARED__FORMAL_AUTHORITY_STILL_REQUIRED",
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "preexecution_authority_file_sha256": pre_file_sha,
        "target_materialization_binding_sha256": target_binding["binding_sha256"],
        "formal_identity_sha256": target_binding["hashes"]["formal_identity_sha256"],
        "runtime_budget_authority_sha256": authority_records["runtime_budget_authority"]["sha256"],
        "execution_source_root": "/tmp/goal5791_formal_test/source",
        "execution_source_manifest_path": (
            "/tmp/goal5791_formal_test/source/history/internal_docs/"
            "goal5791_portable_source_manifest_v1_20260817.json"
        ),
        "execution_source_manifest_file_sha256": target_binding["hashes"][
            "execution_source_manifest_sha256"
        ],
        "formal_identity_record": _formal_identity_record(target_binding),
        "python_executable": "/usr/bin/python3",
        "python_executable_sha256": _identity("python"),
        "python_version": target_binding["versions"]["python_version"],
        "numba_version": "test-numba", "llvmlite_version": "0.47.0",
        "numpy_version": "test-numpy",
        "cupy_version": target_binding["versions"]["cupy_version"],
        "native_library_path": "/tmp/goal5791_formal_test/librtdl_optix.so",
        "native_library_sha256": target_dict["native_library_sha256"],
        "optix_include": "/tmp/goal5791_formal_test/optix/include",
        "cuda_include": "/tmp/goal5791_formal_test/cuda/include",
        "compute_capability": "8.9", "optix_sdk_version": "9.0.0",
        "shared_contract_freeze_path": "/tmp/goal5791_formal_test/freeze.json",
        "shared_contract_freeze_file_sha256": primary.FROZEN_PLAN_IDENTITIES["shared_contract_file_sha256"],
        "target_materialization_authority_path": "/tmp/goal5791_formal_test/target.json",
        "target_materialization_authority_file_sha256": target_file_sha,
        "max_relation_rows": 1_000_000,
        "datasets": datasets,
        "neutral_prewarm": {
            "edge_path": "/tmp/goal5791_formal_test/prewarm.edge",
            "input_sha256": _identity("neutral-prewarm"), "size_bytes": 80,
            "expected_triangle_count": 1,
            "purpose": "recipe_jit_cache_neutralization_only",
            "formal_input": False, "variant_order": [FUSION_OFF, FUSION_ON],
        },
        "formal_worker_environment": {
            "PYTHONPATH": "/tmp/goal5791_formal_test/source",
            "PATH": "/usr/bin:/bin",
            "PYTHONHASHSEED": "0",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONNOUSERSITE": "1",
            "CUDA_HOME": "/usr/local/cuda",
            "CUDA_PATH": "/usr/local/cuda",
            "LD_LIBRARY_PATH": "/usr/local/cuda/lib64",
            "LD_PRELOAD": FORMAL_WORKER_ENVIRONMENT_CONTRACT["ld_preload"],
            "RTDL_OPTIX_LIB": "/tmp/goal5791_formal_test/librtdl_optix.so",
            "RTDL_OPTIX_LIBRARY": "/tmp/goal5791_formal_test/librtdl_optix.so",
            "RTDL_V4_CUDA_PREFIX": "/usr/local/cuda",
            "RTDL_V4_OPTIX_PREFIX": "/tmp/goal5791_formal_test/optix",
            "LC_ALL": FORMAL_WORKER_ENVIRONMENT_CONTRACT["lc_all"],
        },
        "worker_timeout_seconds": FORMAL_EXECUTION_POLICY[
            "per_worker_timeout_seconds"
        ],
        "formal_conservative_budget_seconds": runtime_budget_authority[
            "frozen_budget"
        ]["formal_conservative_budget_seconds"],
    }
    runtime = _seal(runtime_payload, "runtime_sha256")
    _write(root / "RUNTIME.json", runtime)
    runtime_file_sha = _file_sha(root / "RUNTIME.json")
    formal_payload.update({
        "runtime_file_sha256": runtime_file_sha,
        "runtime_sha256": runtime["runtime_sha256"],
        "resource_confirmation": {
            "owner_confirmed_uninterrupted_window_hours": 7.0,
            "confirmed_free_disk_bytes": 20_000_000_000,
            "confirmed_before_formal_worker_zero": True,
            "formal_output_parent_resolved_path": "/tmp",
            "formal_output_parent_free_bytes_observed_at_authority_creation": (
                30_000_000_000
            ),
            "minimum_required_free_disk_bytes": 20_000_000_000,
        },
    })
    formal = _seal(formal_payload, "authority_sha256")
    _write(root / "OWNER_FORMAL_AUTHORITY.json", formal)
    formal_file_sha = _file_sha(root / "OWNER_FORMAL_AUTHORITY.json")
    control_file_observations = {
        role: {
            "resolved_path": path,
            "file_sha256": file_sha,
            "bytes": size,
            "st_dev": 41,
            "st_ino": 50_000 + index,
            "st_mtime_ns": 60_000 + index,
            "st_mode": 0o100444,
            "regular_nonlink": True,
            "read_only": True,
        }
        for index, (role, path, file_sha, size) in enumerate((
            (
                "runtime", "/tmp/goal5791_controls/RUNTIME.json",
                runtime_file_sha, (root / "RUNTIME.json").stat().st_size,
            ),
            (
                "preexecution_authority",
                "/tmp/goal5791_controls/PREEXECUTION_AUTHORITY.json",
                pre_file_sha,
                (root / "PREEXECUTION_AUTHORITY.json").stat().st_size,
            ),
            (
                "formal_authority",
                "/tmp/goal5791_controls/OWNER_FORMAL_AUTHORITY.json",
                formal_file_sha,
                (root / "OWNER_FORMAL_AUTHORITY.json").stat().st_size,
            ),
        ))
    }
    source_admission_payload = {
        "schema": "rtdl.goal5791.source_admission.v1", "goal": GOAL,
        "status": "PASS__FULL_EXECUTION_SOURCE_REHASHED_BEFORE_WORKER_ZERO",
        "runtime_file_sha256": runtime_file_sha,
        "runtime_sha256": runtime["runtime_sha256"],
        "execution_source_root": runtime["execution_source_root"],
        "execution_source_manifest_file_sha256": runtime[
            "execution_source_manifest_file_sha256"
        ],
        "execution_source_tree_sha256": target_binding["hashes"][
            "execution_source_tree_sha256"
        ],
        "manifest_payload_count": 6, "manifest_payload_bytes": 600,
        "full_manifest_rehash_complete": True,
        "all_manifest_payloads_read_only": True,
        "manifest_file_read_only": True,
        "exact_regular_file_set_verified": True,
        "exact_implied_directory_set_verified": True,
        "unmanifested_path_count": 0,
        "missing_manifest_payload_count": 0,
        "symlink_or_special_path_count": 0,
        "all_source_paths_without_write_bits": True,
        "regular_file_count": 7,
        "source_directory_count_including_root": 3,
        "source_path_count": 10, "created_before_worker_zero": True,
        "controller_bootstrap_observation": {
            "schema": primary.CONTROLLER_BOOTSTRAP_OBSERVATION_SCHEMA,
            "controller_environment_sha256": digest(
                runtime["formal_worker_environment"]
            ),
            "controller_environment_exact_frozen_14_keys_verified": True,
            "controller_environment_key_count": 14,
            "controller_cupy_cache_dir_absent": True,
            "preimport_stdlib_bootstrap_verified": True,
            "loaded_harness_sources": {
                name: {
                    "resolved_path": (
                        PurePosixPath(runtime["execution_source_root"])
                        / PurePosixPath(name)
                    ).as_posix(),
                    "file_sha256": runtime["formal_identity_record"][
                        "formal_sources"
                    ][name],
                }
                for name in primary.CONTROLLER_BOOTSTRAP_SOURCE_PATHS
            },
            "loaded_harness_paths_and_hashes_match_formal_identity_record": True,
            "immutable_control_file_observations": (
                control_file_observations
            ),
            "no_gpu_product_process_state_observation": (
                _no_gpu_process_state(
                    "after_shared_import_before_target_probe"
                )
            ),
            "cuda_context_or_product_import_used": False,
            "completed_after_transaction_marker_before_worker_zero": True,
        },
        "same_host_root_race_excluded": False,
        "tcb_boundary": primary.SOURCE_TCB_BOUNDARY,
    }
    source_admission = _seal(
        source_admission_payload, "admission_sha256"
    )
    _write(root / "SOURCE_ADMISSION.json", source_admission)
    resource_admission = _seal({
        "schema": primary.RESOURCE_ADMISSION_SCHEMA,
        "goal": GOAL,
        "status": primary.RESOURCE_ADMISSION_STATUS,
        "formal_authority_file_sha256": formal_file_sha,
        "formal_authority_sha256": formal["authority_sha256"],
        "target_materialization_root": target_materialization_root,
        "create_only_formal_output_root": formal_output_root,
        "controller_incomplete_staging_root": controller_staging_root,
        "formal_output_parent_resolved_path": "/tmp",
        "authority_confirmed_free_disk_bytes": 20_000_000_000,
        "authority_observed_free_disk_bytes_at_authority_creation": (
            30_000_000_000
        ),
        "controller_observed_free_disk_bytes_before_worker_zero": (
            25_000_000_000
        ),
        "minimum_required_free_disk_bytes": 20_000_000_000,
        "same_parent_sibling_roots_verified": True,
        "controller_observation_meets_authority_confirmed_threshold": True,
        "controller_observation_meets_minimum_required_threshold": True,
        "created_before_worker_zero": True,
    }, "admission_sha256")
    _write(root / "RESOURCE_ADMISSION.json", resource_admission)
    target_runtime_admission = _seal({
        "schema": primary.TARGET_RUNTIME_ADMISSION_SCHEMA,
        "goal": GOAL,
        "status": primary.TARGET_RUNTIME_ADMISSION_STATUS,
        "formal_authority_file_sha256": formal_file_sha,
        "formal_authority_sha256": formal["authority_sha256"],
        "target_materialization_binding_sha256": target_binding[
            "binding_sha256"
        ],
        "pod_endpoint": endpoint,
        "nvidia_smi_executable": "/usr/bin/nvidia-smi",
        "nvidia_smi_query": primary.NVIDIA_SMI_QUERY,
        "visible_gpu_row_count": 1,
        "observed_gpu_uuid": target_binding["versions"]["gpu_uuid"],
        "observed_driver_version": target_binding["versions"][
            "driver_version"
        ],
        "observed_compute_capability": target_binding["versions"][
            "compute_capability"
        ],
        "controlled_environment_sha256": digest(
            runtime["formal_worker_environment"]
        ),
        "controlled_environment_exact_14_keys_verified": True,
        "cupy_cache_dir_absent": True,
        "no_gpu_product_process_state_before_nvidia_smi": (
            _no_gpu_process_state("before_nvidia_smi")
        ),
        "no_gpu_product_process_state_after_nvidia_smi": (
            _no_gpu_process_state("after_nvidia_smi")
        ),
        "cuda_context_or_product_import_used": False,
        "created_before_worker_zero": True,
    }, "admission_sha256")
    _write(
        root / "TARGET_RUNTIME_ADMISSION.json", target_runtime_admission
    )

    admission_payload = {
        "schema": "rtdl.goal5791.data_admission.v1", "goal": GOAL,
        "status": "PASS__ALL_SCHEDULED_EDGE_BYTES_REHASHED_BEFORE_WORKER_ZERO",
        "data_authority_file_sha256": DATA_AUTHORITY_FILE_SHA256,
        "data_authority_sha256": DATA_AUTHORITY_SHA256,
        "datasets": admission_rows, "created_before_worker_zero": True,
        "full_rehash_complete": True,
        "unscheduled_bundle_members_opened": False,
        "drop_caches_or_page_cache_control_used": False,
    }
    data_admission = _seal(admission_payload, "admission_sha256")
    _write(root / "DATA_ADMISSION.json", data_admission)

    context = {
        "target_object": target_object, "target_binding": target_binding,
        "target_file_sha": target_file_sha, "pre": pre,
        "pre_file_sha": pre_file_sha, "formal": formal,
        "formal_file_sha": formal_file_sha, "runtime": runtime,
        "runtime_file_sha": runtime_file_sha,
        "data_admission": data_admission,
        "source_admission": source_admission,
    }
    for spec in schedule():
        value = _worker(
            dict(spec), context=context, favor=favor,
            narrow_favor=narrow_favor,
            favor_difference_seconds=favor_difference_seconds,
        )
        _write(
            root / "workers" / f"worker_{int(spec['worker_index']):04d}.json",
            value,
        )
    return root


def _publish_raw(root: Path) -> tuple[dict[str, object], dict[str, object]]:
    """Materialize the controller's sealed final-published topology."""

    runtime = json.loads((root / "RUNTIME.json").read_text())
    preexecution = json.loads(
        (root / "PREEXECUTION_AUTHORITY.json").read_text()
    )
    data_admission = json.loads((root / "DATA_ADMISSION.json").read_text())
    source_admission = json.loads(
        (root / "SOURCE_ADMISSION.json").read_text()
    )
    resource_admission = json.loads(
        (root / "RESOURCE_ADMISSION.json").read_text()
    )
    target_runtime_admission = json.loads(
        (root / "TARGET_RUNTIME_ADMISSION.json").read_text()
    )
    authority_manifest = json.loads(
        (root / "AUTHORITY_MANIFEST.json").read_text()
    )
    primary_evaluation = json.loads(
        (root / "EVALUATION.json").read_text()
    )
    prior_recount = json.loads(
        (root / "INDEPENDENT_RECOUNT.json").read_text()
    )
    if primary_evaluation["rows"] != prior_recount["rows"]:
        raise AssertionError("fixture primary/recount row drift")
    workers = [
        json.loads(
            (root / "workers" / f"worker_{index:04d}.json").read_text()
        )
        for index in range(len(schedule()))
    ]
    worker_rows = [
        {
            "worker_index": index,
            "parent_pid": worker["parent_pid"],
            "worker_sha256": worker["worker_sha256"],
            "file_sha256": _file_sha(
                root / "workers" / f"worker_{index:04d}.json"
            ),
            "cache_dir_name": f"worker_{index:04d}",
            "launch_attempt_count": 1,
        }
        for index, worker in enumerate(workers)
    ]
    publication_policy = {
        "same_host_root_race_excluded": SOURCE_ADMISSION_POLICY[
            "same_host_malicious_root_race_excluded"
        ],
        "cold_process_warm_system_definition": CACHE_POLICY["cold_definition"],
        "cold_process_warm_system_excludes": list(
            CACHE_POLICY["cold_claim_excludes"]),
        "operating_system_page_cache_controlled_or_dropped": CACHE_POLICY[
            "operating_system_page_cache_controlled_or_dropped"
        ],
        "operating_system_page_cache_scope": CACHE_POLICY[
            "operating_system_page_cache_scope"
        ],
        "cuda_driver_jit_cache_controlled_or_isolated": CACHE_POLICY[
            "cuda_driver_jit_cache_controlled_or_isolated"
        ],
        "optix_disk_cache_controlled_or_isolated": CACHE_POLICY[
            "optix_disk_cache_controlled_or_isolated"
        ],
        "round_major_abba_is_uncontrolled_cache_mitigation_not_control": (
            CACHE_POLICY[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
            ]
        ),
        "worker_cache_payloads_preserved": False,
        "worker_cache_payloads_removed_after_validation": CACHE_POLICY[
            "successful_cohort_cache_payloads_removed_after_validation_before_publication"
        ],
        "cache_receipts_preserved": CACHE_POLICY["cache_receipts_preserved"],
        "cache_payloads_are_authoritative_evidence": CACHE_POLICY[
            "cache_payloads_are_authoritative_evidence"
        ],
        "successful_cohort_cache_payloads_removed_after_validation_before_publication": (
            CACHE_POLICY[
                "successful_cohort_cache_payloads_removed_after_validation_before_publication"
            ]
        ),
        "failed_terminal_staging_may_preserve_cache_payloads": CACHE_POLICY[
            "failed_terminal_staging_may_preserve_cache_payloads"
        ],
        "worker_cache_empty_directory_shells_preserved": True,
        "worker_cache_empty_directory_shell_count": len(schedule()),
        "worker_cache_empty_directory_shells_are_authoritative_evidence": False,
        "worker_cache_empty_directory_shells_all_empty": True,
    }
    manifest_payload = {
        "schema": "rtdl.goal5791.formal_cohort_manifest.v1",
        "goal": GOAL,
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "preexecution_authority_file_sha256": _file_sha(
            root / "PREEXECUTION_AUTHORITY.json"
        ),
        "target_materialization_binding_sha256": preexecution[
            "target_materialization_binding"
        ]["binding_sha256"],
        "target_materialization_authority_file_sha256": _file_sha(
            root / "TARGET_MATERIALIZATION_AUTHORITY.json"
        ),
        "formal_authority_file_sha256": _file_sha(
            root / "OWNER_FORMAL_AUTHORITY.json"
        ),
        "runtime_sha256": runtime["runtime_sha256"],
        "runtime_file_sha256": _file_sha(root / "RUNTIME.json"),
        "data_admission_sha256": data_admission["admission_sha256"],
        "source_admission_sha256": source_admission["admission_sha256"],
        "resource_admission_sha256": resource_admission[
            "admission_sha256"
        ],
        "resource_admission_file_sha256": _file_sha(
            root / "RESOURCE_ADMISSION.json"
        ),
        "target_runtime_admission_sha256": target_runtime_admission[
            "admission_sha256"
        ],
        "target_runtime_admission_file_sha256": _file_sha(
            root / "TARGET_RUNTIME_ADMISSION.json"
        ),
        "raw_authority_manifest_sha256": authority_manifest[
            "manifest_sha256"
        ],
        "authorities": authority_manifest["authorities"],
        "worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "workers": worker_rows,
        "evaluation_file_sha256": _file_sha(root / "EVALUATION.json"),
        "independent_recount_file_sha256": _file_sha(
            root / "INDEPENDENT_RECOUNT.json"
        ),
        "fresh_parent_pid_count": len(schedule()),
        "launch_attempt_count": len(schedule()),
        **publication_policy,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    manifest = _seal(manifest_payload, "manifest_sha256")
    _write(root / "COHORT_MANIFEST.json", manifest)
    result_payload = {
        "schema": "rtdl.goal5791.formal_controller_result.v1",
        "goal": GOAL,
        "status": "COMPLETE__96_OF_96_EXACTLY_ONCE",
        "formal_worker_count": len(schedule()),
        "independent_row_count": len(statistical_rows()),
        "fresh_parent_pid_count": len(schedule()),
        "launch_attempt_count": len(schedule()),
        "formal_contract_sha256": contract_sha256(),
        "schedule_sha256": schedule_sha256(),
        "runtime_file_sha256": _file_sha(root / "RUNTIME.json"),
        "runtime_sha256": runtime["runtime_sha256"],
        "cohort_manifest_sha256": manifest["manifest_sha256"],
        "evaluation_file_sha256": manifest["evaluation_file_sha256"],
        "independent_recount_file_sha256": manifest[
            "independent_recount_file_sha256"
        ],
        "primary_and_independent_rows_exactly_equal": True,
        "rows": primary_evaluation["rows"],
        "result_lifecycle_labels": primary_evaluation[
            "result_lifecycle_labels"
        ],
        "trace_cost_diagnostic_authority": primary_evaluation[
            "trace_cost_diagnostic_authority"
        ],
        "independent_recount_external_review_status": primary_evaluation[
            "independent_recount_external_review_status"
        ],
        "every_figure_caption_must_state_includes_evidence_overhead": True,
        **{
            field: deepcopy(primary_evaluation[field])
            for field in PAPER_OUTCOME_CONSEQUENCE_CONTRACT[
                "published_paper_outcome_fields"
            ]
        },
        "data_admission_sha256": data_admission["admission_sha256"],
        "source_admission_sha256": source_admission["admission_sha256"],
        "resource_admission_sha256": resource_admission[
            "admission_sha256"
        ],
        "resource_admission_file_sha256": _file_sha(
            root / "RESOURCE_ADMISSION.json"
        ),
        "target_runtime_admission_sha256": target_runtime_admission[
            "admission_sha256"
        ],
        "target_runtime_admission_file_sha256": _file_sha(
            root / "TARGET_RUNTIME_ADMISSION.json"
        ),
        "raw_authority_manifest_sha256": authority_manifest[
            "manifest_sha256"
        ],
        "controller_elapsed_seconds": 100.0,
        "formal_conservative_budget_seconds": runtime[
            "formal_conservative_budget_seconds"
        ],
        "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control": (
            CACHE_POLICY[
                "same_cohort_abba_symmetry_is_page_cache_mitigation_not_control"
            ]
        ),
        **publication_policy,
        "retry_resume_replacement_row_drop_relabel_used": False,
    }
    result = _seal(result_payload, "result_sha256")
    _write(root / "RESULT.json", result)
    return manifest, result


def _final_published_raw(root: Path, *, favor: bool = True) -> Path:
    raw = _raw(root, favor=favor)
    primary.evaluate(raw, raw / "EVALUATION.json")
    independent.recount(raw, raw / "INDEPENDENT_RECOUNT.json")
    _publish_raw(raw)
    return raw


def _resign(value: dict[str, object], field: str) -> None:
    value.pop(field, None)
    value[field] = digest(value)


def _resign_operation_events(receipt: dict[str, object]) -> None:
    previous = str(receipt["contract_sha256"])
    for index, event in enumerate(receipt["events"]):
        event["sequence"] = index
        event["previous_event_sha256"] = previous
        _resign(event, "event_sha256")
        previous = str(event["event_sha256"])
    receipt["event_chain_sha256"] = previous
    _resign(receipt, "receipt_sha256")


def _resign_plan(plan: dict[str, object]) -> None:
    unsigned = dict(plan)
    unsigned.pop("shared_identity_sha256", None)
    unsigned.pop("plan_sha256", None)
    common = dict(unsigned)
    for name in primary.VARIANT_PLAN_FIELDS | {"only_allowlisted_difference"}:
        common.pop(name, None)
    plan["shared_identity_sha256"] = digest(common)
    plan["plan_sha256"] = digest(unsigned)


class Goal5791FormalEvaluatorRecountTest(unittest.TestCase):
    def test_real_shaped_96_worker_primary_and_recount_exactly_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "raw")
            target = json.loads(
                (raw / "TARGET_MATERIALIZATION_AUTHORITY.json").read_text()
            )
            preexecution = json.loads(
                (raw / "PREEXECUTION_AUTHORITY.json").read_text()
            )
            self.assertNotEqual(
                target["materialization_nonce"],
                preexecution["target_materialization_binding"]["nonces"][
                    "target_evidence_nonce"
                ],
            )
            first_worker = json.loads(
                (raw / "workers" / "worker_0000.json").read_text()
            )
            first_plan = first_worker["segment_evidence"][0][
                "fusion_ablation_plan"
            ]
            self.assertEqual(
                first_plan["oracle_sha256"],
                first_worker["dataset_oracle_authority_sha256"],
            )
            self.assertNotEqual(
                first_plan["oracle_sha256"],
                first_worker["oracle_contract_sha256"],
            )
            primary_result = primary.build_evaluation(raw)
            _write(raw / "EVALUATION.json", primary_result)
            recount_result = independent.build_recount(raw)
        self.assertEqual(primary_result["rows"], recount_result["rows"])
        self.assertEqual(primary_result["worker_count"], 96)
        self.assertEqual(primary_result["unique_parent_pid_count"], 96)
        self.assertEqual(primary_result["unique_worker_cache_count"], 96)
        self.assertEqual(primary_result["unique_execution_token_count"], 288)
        self.assertEqual(primary_result["source_rehash_receipt_worker_count"], 96)
        self.assertTrue(primary_result["source_exact_path_set_verified"])
        self.assertTrue(primary_result["source_admission_policy_verified"])
        self.assertTrue(primary_result["cache_receipts_preserved"])
        self.assertTrue(primary_result["cache_payloads_non_authoritative"])
        self.assertTrue(
            primary_result[
                "cache_payloads_must_be_removed_before_final_cohort_publication"
            ]
        )
        self.assertTrue(primary_result[
            "failed_terminal_staging_may_preserve_cache_payloads"
        ])
        self.assertEqual(primary_result["exact_output_worker_count"], 96)
        self.assertEqual(primary_result["behavioral_true_optix_worker_count"], 96)
        self.assertEqual(len(primary_result["rows"]), 6)
        self.assertTrue(all(row["demonstrated_clear_win"] for row in primary_result["rows"]))
        self.assertEqual(primary_result["paper_clear_winning_row_count"], 6)
        self.assertEqual(
            primary_result["paper_clear_winning_row_ids"],
            [row["row_id"] for row in primary_result["rows"]],
        )
        self.assertEqual(
            primary_result["ci_clear_win_trace_cost_inconclusive_count"], 0)
        self.assertEqual(
            primary_result["ci_clear_win_trace_cost_inconclusive_row_ids"], [])
        all_six_selection = primary_result[
            "paper_outcome_consequence_selection"
        ]
        self.assertEqual(
            all_six_selection["paper_outcome_consequence_branch"],
            "all_six_clear_winning_rows",
        )
        self.assertEqual(
            all_six_selection["paper_outcome_consequence"],
            PAPER_OUTCOME_CONSEQUENCE_CONTRACT["all_six_clear_winning_rows"],
        )
        unsigned_selection = dict(all_six_selection)
        selection_seal = unsigned_selection.pop("selection_sha256")
        self.assertEqual(selection_seal, digest(unsigned_selection))
        for field in PAPER_OUTCOME_CONSEQUENCE_CONTRACT[
            "published_paper_outcome_fields"
        ]:
            self.assertEqual(primary_result[field], recount_result[field])
        self.assertEqual(
            primary_result["result_lifecycle_labels"]["cold"],
            "cold_process_warm_system",
        )
        self.assertEqual(
            primary_result["independent_recount_external_review_status"],
            "INDEPENDENT_RECOUNT_NOT_ITSELF_EXTERNALLY_REVIEWED",
        )
        self.assertTrue(
            primary_result[
                "every_figure_caption_must_state_includes_evidence_overhead"
            ]
        )
        for row in primary_result["rows"]:
            self.assertIn(
                row["lifecycle"],
                {
                    "cold_process_warm_system",
                    "prepared",
                },
            )
            self.assertIn(row["lifecycle_internal_schedule_id"], {"cold", "prepared"})
            self.assertEqual(
                row["row_id_internal_schedule_id"],
                f"{row['dataset_id']}__{row['lifecycle_internal_schedule_id']}",
            )
            self.assertEqual(
                row["row_id"], f"{row['dataset_id']}__{row['lifecycle']}")
            self.assertEqual(row["per_event_record_cost_bound_ns"], 12_202)
            self.assertEqual(
                row["five_extra_event_differential_bound_per_segment_ns"],
                61_010,
            )
            self.assertEqual(
                row["row_total_trace_differential_bound_ns"],
                61_010 * row["exact_row_segment_count"],
            )
            self.assertTrue(
                row["trace_cost_bound_small_relative_to_observed_difference"]
            )
            self.assertTrue(row["mechanism_performance_statement_eligible"])
            self.assertTrue(row["estimand_includes_evidence_overhead"])
            self.assertFalse(row["pure_device_kernel_timing_claimed"])
            self.assertTrue(
                row["statistical_classification_unchanged_by_trace_diagnostic"]
            )
        self.assertFalse(
            primary_result["operating_system_page_cache_controlled_or_dropped"]
        )
        self.assertEqual(
            primary_result["operating_system_page_cache_scope"],
            CACHE_POLICY["operating_system_page_cache_scope"],
        )
        self.assertNotIn("os_page_cache_controlled_or_dropped", primary_result)
        self.assertNotIn("os_page_cache_scope", primary_result)
        self.assertNotIn("os_page_cache_controlled_or_dropped", recount_result)
        self.assertNotIn("os_page_cache_scope", recount_result)
        self.assertEqual(
            primary_result["cold_process_warm_system_excludes"],
            [
                "operating_system_page_cache",
                "cuda_driver_jit_cache",
                "optix_disk_cache",
            ],
        )
        self.assertFalse(
            primary_result["cuda_driver_jit_cache_controlled_or_isolated"]
        )
        self.assertFalse(
            primary_result["optix_disk_cache_controlled_or_isolated"]
        )
        self.assertTrue(
            primary_result[
                "round_major_abba_is_uncontrolled_cache_mitigation_not_control"
            ]
        )

    def test_unfavorable_rows_are_retained_without_compensation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "raw", favor=False)
            first = primary.build_evaluation(raw)
            _write(raw / "EVALUATION.json", first)
            second = independent.build_recount(raw)
        self.assertEqual(first["rows"], second["rows"])
        self.assertEqual(first["ci_clear_loss_count"], 6)
        self.assertEqual(first["ci_clear_win_count"], 0)
        self.assertEqual(first["paper_clear_winning_row_count"], 0)
        self.assertEqual(first["paper_clear_winning_row_ids"], [])
        self.assertEqual(
            first["paper_outcome_consequence_selection"]
            ["paper_outcome_consequence_branch"],
            "zero_clear_winning_rows",
        )
        self.assertTrue(first["all_six_rows_retained"])
        self.assertFalse(first["cross_dataset_lifecycle_or_row_compensation_used"])

        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "narrow", narrow_favor=True)
            narrow = primary.build_evaluation(raw)
        self.assertEqual(narrow["ci_clear_win_count"], 6)
        self.assertEqual(narrow["paper_clear_winning_row_count"], 0)
        self.assertEqual(narrow["paper_clear_winning_row_ids"], [])
        self.assertEqual(
            narrow["ci_clear_win_trace_cost_inconclusive_count"], 6)
        self.assertEqual(
            narrow["ci_clear_win_trace_cost_inconclusive_row_ids"],
            [row["row_id"] for row in narrow["rows"]],
        )
        self.assertEqual(
            narrow["paper_outcome_consequence_selection"]
            ["paper_outcome_consequence_branch"],
            "zero_clear_winning_rows",
        )
        self.assertEqual(
            narrow["paper_outcome_consequence_selection"]
            ["ci_clear_win_count"],
            narrow["paper_clear_winning_row_count"]
            + narrow["ci_clear_win_trace_cost_inconclusive_count"],
        )
        self.assertTrue(all(
            not row["demonstrated_clear_win"] for row in narrow["rows"]
        ))
        self.assertTrue(all(
            not row["trace_cost_bound_small_relative_to_observed_difference"]
            for row in narrow["rows"]
        ))
        self.assertTrue(all(
            not row["mechanism_performance_statement_eligible"]
            for row in narrow["rows"]
        ))
        self.assertTrue(all(
            row["mechanism_performance_statement_classification"]
            == "trace_cost_inconclusive"
            for row in narrow["rows"]
        ))
        self.assertTrue(all(
            row["statistical_classification_unchanged_by_trace_diagnostic"]
            for row in narrow["rows"]
        ))

    def test_paper_outcome_branch_is_independently_rebuilt_for_zero_mixed_all(self) -> None:
        row_ids = [str(row["row_id"]) for row in statistical_rows()]
        for eligible_count, branch in (
            (0, "zero_clear_winning_rows"),
            (3, "mixed_one_through_five_clear_winning_rows"),
            (6, "all_six_clear_winning_rows"),
        ):
            rows = [
                {
                    "row_id": row_id,
                    "classification": "ci_clear_win",
                    "mechanism_performance_statement_eligible": (
                        index < eligible_count
                    ),
                }
                for index, row_id in enumerate(row_ids)
            ]
            summaries = (
                primary._paper_outcome_summary(deepcopy(rows)),
                independent._paper_outcome_summary(deepcopy(rows)),
                controller._paper_outcome_summary(deepcopy(rows)),
            )
            self.assertEqual(summaries[0], summaries[1])
            self.assertEqual(summaries[0], summaries[2])
            summary = summaries[0]
            self.assertEqual(
                summary["paper_clear_winning_row_count"], eligible_count)
            self.assertEqual(
                summary["paper_clear_winning_row_ids"],
                row_ids[:eligible_count],
            )
            self.assertEqual(
                summary["ci_clear_win_trace_cost_inconclusive_count"],
                6 - eligible_count,
            )
            selection = summary["paper_outcome_consequence_selection"]
            self.assertEqual(
                selection["paper_outcome_consequence_branch"], branch)
            self.assertEqual(
                selection["paper_outcome_consequence"],
                PAPER_OUTCOME_CONSEQUENCE_CONTRACT[branch],
            )
            unsigned = dict(selection)
            claimed = unsigned.pop("selection_sha256")
            self.assertEqual(claimed, digest(unsigned))

    def test_trace_small_relative_exact_boundary_passes_and_above_fails(self) -> None:
        cases = (
            (0.018303, True, 6, "all_six_clear_winning_rows"),
            (0.018302, False, 0, "zero_clear_winning_rows"),
        )
        for difference, expected_small, expected_count, expected_branch in cases:
            with self.subTest(difference=difference):
                with tempfile.TemporaryDirectory() as temp:
                    raw = _raw(
                        Path(temp) / "raw",
                        favor_difference_seconds=difference,
                    )
                    first = primary.build_evaluation(raw)
                    _write(raw / "EVALUATION.json", first)
                    second = independent.build_recount(raw)
                self.assertEqual(first["rows"], second["rows"])
                self.assertTrue(all(
                    row["classification"] == "ci_clear_win"
                    for row in first["rows"]
                ))
                self.assertTrue(all(
                    row[
                        "trace_cost_bound_small_relative_to_observed_difference"
                    ] is expected_small
                    for row in first["rows"]
                ))
                self.assertEqual(
                    first["paper_clear_winning_row_count"], expected_count)
                self.assertEqual(
                    first["paper_outcome_consequence_selection"]
                    ["paper_outcome_consequence_branch"],
                    expected_branch,
                )
                if expected_small:
                    self.assertTrue(all(
                        row[
                            "trace_differential_fraction_of_absolute_median_seconds_difference"
                        ] <= 0.01
                        for row in first["rows"]
                    ))
                else:
                    self.assertTrue(all(
                        row[
                            "trace_differential_fraction_of_absolute_median_seconds_difference"
                        ] > 0.01
                        for row in first["rows"]
                    ))

    def test_jointly_resigned_wrong_paper_outcome_branch_is_rejected(self) -> None:
        def forge_zero_branch(
            value: dict[str, object], seal_field: str,
        ) -> None:
            row_ids = [str(row["row_id"]) for row in value["rows"]]
            value["paper_clear_winning_row_count"] = 0
            value["paper_clear_winning_row_ids"] = []
            value["ci_clear_win_trace_cost_inconclusive_count"] = 6
            value["ci_clear_win_trace_cost_inconclusive_row_ids"] = row_ids
            selection_payload = {
                "schema": (
                    "rtdl.goal5791.paper_outcome_consequence_selection.v1"
                ),
                "paper_clear_winning_row_count": 0,
                "paper_clear_winning_row_ids": [],
                "ci_clear_win_count": 6,
                "ci_clear_win_trace_cost_inconclusive_count": 6,
                "ci_clear_win_trace_cost_inconclusive_row_ids": row_ids,
                "paper_outcome_consequence_contract_sha256": digest(
                    PAPER_OUTCOME_CONSEQUENCE_CONTRACT
                ),
                "paper_outcome_consequence_branch": "zero_clear_winning_rows",
                "paper_outcome_consequence": deepcopy(
                    PAPER_OUTCOME_CONSEQUENCE_CONTRACT[
                        "zero_clear_winning_rows"
                    ]
                ),
            }
            value["paper_outcome_consequence_selection"] = {
                **selection_payload,
                "selection_sha256": digest(selection_payload),
            }
            _resign(value, seal_field)

        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "analysis_stage")
            evaluation = primary.build_evaluation(raw)
            forge_zero_branch(evaluation, "evaluation_sha256")
            _write(raw / "EVALUATION.json", evaluation)
            with self.assertRaises(RuntimeError):
                independent.build_recount(raw)

        with tempfile.TemporaryDirectory() as temp:
            published = _final_published_raw(Path(temp) / "final_published")
            evaluation_path = published / "EVALUATION.json"
            evaluation = json.loads(evaluation_path.read_text())
            forge_zero_branch(evaluation, "evaluation_sha256")
            _write(evaluation_path, evaluation)

            recount_path = published / "INDEPENDENT_RECOUNT.json"
            recount = json.loads(recount_path.read_text())
            forge_zero_branch(recount, "recount_sha256")
            recount["primary_evaluation_file_sha256"] = _file_sha(
                evaluation_path
            )
            recount["primary_evaluation_sha256"] = evaluation[
                "evaluation_sha256"
            ]
            _resign(recount, "recount_sha256")
            _write(recount_path, recount)

            cohort_path = published / "COHORT_MANIFEST.json"
            cohort = json.loads(cohort_path.read_text())
            cohort["evaluation_file_sha256"] = _file_sha(evaluation_path)
            cohort["independent_recount_file_sha256"] = _file_sha(recount_path)
            _resign(cohort, "manifest_sha256")
            _write(cohort_path, cohort)

            result_path = published / "RESULT.json"
            result = json.loads(result_path.read_text())
            forge_zero_branch(result, "result_sha256")
            result["evaluation_file_sha256"] = _file_sha(evaluation_path)
            result["independent_recount_file_sha256"] = _file_sha(recount_path)
            result["cohort_manifest_sha256"] = cohort["manifest_sha256"]
            _resign(result, "result_sha256")
            _write(result_path, result)
            with self.assertRaises(RuntimeError):
                independent.build_recount(published)

    def _both_reject(self, mutate) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            primary_raw = _raw(root / "primary_raw")
            mutate(primary_raw)
            with self.assertRaises(RuntimeError):
                primary.build_evaluation(primary_raw)

            recount_raw = _raw(root / "recount_raw")
            evaluation = primary.build_evaluation(recount_raw)
            _write(recount_raw / "EVALUATION.json", evaluation)
            mutate(recount_raw)
            with self.assertRaises(RuntimeError):
                independent.build_recount(recount_raw)

    def test_worker_output_timing_pause_deepverify_cache_and_prewarm_attacks(self) -> None:
        def attack(name, change):
            def mutate(raw):
                path = raw / "workers" / "worker_0000.json"
                value = json.loads(path.read_text())
                change(value)
                _resign(value, "worker_sha256")
                _write(path, value)
            with self.subTest(name=name):
                self._both_reject(mutate)
        def cache_attack(worker):
            receipt = worker["cache_receipt"]
            receipt["unique_per_worker"] = False
            _resign(receipt, "receipt_sha256")

        def prewarm_attack(worker):
            receipt = worker["prewarm_receipt"]
            receipt["performed"] = True
            _resign(receipt, "receipt_sha256")

        def cold_boundary_attack(worker):
            receipt = worker["cache_receipt"]
            receipt["cuda_driver_jit_cache_controlled_or_isolated"] = True
            _resign(receipt, "receipt_sha256")

        def excluded_interphase_gap_attack(worker):
            worker["registered_complete_endpoint_seconds"] = sum(
                worker["phase_seconds"][name]
                for name in ("loading", "preparation", "execute", "close")
            )

        attacks = {
            "output": lambda w: w.__setitem__("oracle_output_scalar_u64", w["oracle_output_scalar_u64"] + 1),
            "timing": lambda w: w.__setitem__("registered_complete_endpoint_seconds", w["registered_complete_endpoint_seconds"] + 1.0),
            "cold_interphase_gap_excluded": excluded_interphase_gap_attack,
            "continuous_endpoint_flag": lambda w: w.__setitem__(
                "registered_endpoint_is_one_continuous_interval", False
            ),
            "pause": lambda w: w.__setitem__("execute_timer_continuous_without_pause", False),
            "deepverify": lambda w: w.__setitem__("deep_verification_inside_execute", True),
            "cache": cache_attack,
            "cold_cache_claim_boundary": cold_boundary_attack,
            "prewarm": prewarm_attack,
        }
        for name, change in attacks.items():
            attack(name, change)

        def prepared_cache_missing_both_recipes(raw):
            prepared_index = next(
                int(spec["worker_index"])
                for spec in schedule()
                if spec["lifecycle"] == PREPARED
            )
            path = raw / "workers" / f"worker_{prepared_index:04d}.json"
            value = json.loads(path.read_text())
            receipt = value["cache_receipt"]
            receipt[
                "prepared_same_worker_cache_contains_both_variant_recipes"
            ] = False
            _resign(receipt, "receipt_sha256")
            _resign(value, "worker_sha256")
            _write(path, value)
        with self.subTest(name="prepared_cache_contains_both_recipes"):
            self._both_reject(prepared_cache_missing_both_recipes)

    def test_token_descriptor_count_events_receipt_target_and_plan_delta_attacks(self) -> None:
        def worker_attack(name, change, nested_seals=()):
            def mutate(raw):
                path = raw / "workers" / "worker_0000.json"
                value = json.loads(path.read_text())
                change(value)
                for obj, field in nested_seals:
                    _resign(obj(value), field)
                _resign(value, "worker_sha256")
                _write(path, value)
            with self.subTest(name=name):
                self._both_reject(mutate)
        worker_attack("token", lambda w: w["segment_evidence"][0]["token_admission"].__setitem__("state_after_execute", "fresh"))

        def descriptor_attack(worker):
            segment = worker["segment_evidence"][0]
            segment["descriptor"]["gpu_touched"] = True
            descriptor_sha = digest(segment["descriptor"])
            segment["segment_descriptor_sha256"] = descriptor_sha
            segment["token_admission"]["descriptor_sha256"] = descriptor_sha

        worker_attack("descriptor", descriptor_attack)

        def same_descriptor_different_input_attack(worker):
            segment = worker["segment_evidence"][0]
            binding = segment["plan_input_binding"]
            binding["source_input_sha256"] = _identity(
                "different-source-with-same-segment-descriptor"
            )
            plan = segment["fusion_ablation_plan"]
            plan["input_sha256"] = digest(binding)
            _resign_plan(plan)
            token = segment["token_admission"]
            token["plan_sha256"] = plan["plan_sha256"]
            token["plan_input_sha256"] = plan["input_sha256"]
            operation = _operation_receipt(
                worker_index=int(worker["worker_index"]),
                segment_index=int(segment["segment_id"]),
                variant=str(worker["variant"]),
                plan=plan,
                output_sha=str(segment["output_sha256"]),
                behavioral=segment["traversal_receipt"],
            )
            segment["operation_evidence_receipt"] = operation
            token["operation_execution_nonce"] = operation["execution_nonce"]

        worker_attack(
            "same_descriptor_different_input_fully_resigned",
            same_descriptor_different_input_attack,
        )

        def primitive_bound_attack(worker):
            segment = worker["segment_evidence"][0]
            descriptor = segment["descriptor"]
            descriptor["primitive_count"] = 1_000_001
            descriptor["host_geometry_bytes"] = (
                76 * descriptor["primitive_count"] + 68 * descriptor["query_count"]
            )
            segment["primitive_count"] = descriptor["primitive_count"]
            segment["host_geometry_bytes"] = descriptor["host_geometry_bytes"]
            descriptor_sha = digest(descriptor)
            segment["segment_descriptor_sha256"] = descriptor_sha
            segment["token_admission"]["descriptor_sha256"] = descriptor_sha

        worker_attack("primitive_bound", primitive_bound_attack)

        def inconsistent_device_maximum(worker):
            worker["segment_evidence"][0][
                "checked_u64_weighted_reduction"
            ]["maximum_value"] = 0

        def mutate_inconsistent_device_maximum(raw):
            path = raw / "workers" / "worker_0001.json"
            value = json.loads(path.read_text())
            inconsistent_device_maximum(value)
            _resign(value, "worker_sha256")
            _write(path, value)
        with self.subTest(name="device_maximum_cannot_bound_exact_sum"):
            self._both_reject(mutate_inconsistent_device_maximum)

        worker_attack("count", lambda w: w.__setitem__("segment_count", w["segment_count"] + 1))

        def event_attack(worker):
            receipt = worker["segment_evidence"][0]["operation_evidence_receipt"]
            receipt["events"][0]["operation_id"] = "forged_operation"
            _resign_operation_events(receipt)

        worker_attack("events", event_attack)

        def traversal_attack(worker):
            segment = worker["segment_evidence"][0]
            traversal = segment["traversal_receipt"]
            traversal["native_snapshot"]["failed_launch_count"] = 1
            _resign(traversal, "receipt_sha256")
            operation = segment["operation_evidence_receipt"]
            operation["traversal_receipt_sha256"] = traversal["receipt_sha256"]
            _resign(operation, "receipt_sha256")

        worker_attack("traversal", traversal_attack)

        def target_attack(raw):
            path = raw / "TARGET_BINDING.json"
            value = json.loads(path.read_text())
            value["hashes"]["formal_identity_sha256"] = _identity("forged")
            _resign(value, "binding_sha256")
            _write(path, value)
        self._both_reject(target_attack)

        def plan_delta(raw):
            path = raw / "workers" / "worker_0001.json"
            value = json.loads(path.read_text())
            segment = value["segment_evidence"][0]
            plan = segment["fusion_ablation_plan"]
            plan["same_optix_producer_required"] = False
            _resign_plan(plan)
            segment["token_admission"]["plan_sha256"] = plan["plan_sha256"]
            _resign(value, "worker_sha256")
            _write(path, value)
        self._both_reject(plan_delta)

    def test_pid_schedule_row_drop_bootstrap_and_authority_attacks(self) -> None:
        def pid(raw):
            path = raw / "workers" / "worker_0001.json"
            value = json.loads(path.read_text())
            value["parent_pid"] = 100000
            for segment in value["segment_evidence"]:
                segment["token_admission"]["creator_pid"] = 100000
            _resign(value, "worker_sha256")
            _write(path, value)
        self._both_reject(pid)

        self._both_reject(lambda raw: (raw / "workers" / "worker_0095.json").unlink())
        self._both_reject(
            lambda raw: (raw / "workers" / "unexpected.txt").write_text(
                "not a formal worker", encoding="utf-8"
            )
        )

        def worker_name_case_drift(raw):
            source = raw / "workers" / "worker_0000.json"
            temporary = raw / "workers" / "case_rename.tmp"
            source.rename(temporary)
            temporary.rename(raw / "workers" / "WORKER_0000.json")
        self._both_reject(worker_name_case_drift)
        self._both_reject(
            lambda raw: (raw / "UNMANIFESTED.json").write_text(
                "{}\n", encoding="utf-8"
            )
        )
        self._both_reject(lambda raw: (raw / "unexpected_directory").mkdir())
        self._both_reject(
            lambda raw: (raw / "worker_caches" / "worker_0095").rmdir()
        )
        self._both_reject(
            lambda raw: (
                raw / "worker_caches" / "worker_0096"
            ).mkdir()
        )

        def schedule_attack(raw):
            path = raw / "SCHEDULE.json"
            value = json.loads(path.read_text())
            value["workers"][0]["pair_index"] = 7
            _write(path, value)
        self._both_reject(schedule_attack)

        def bootstrap_attack(raw):
            path = raw / "FORMAL_CONTRACT.json"
            value = json.loads(path.read_text())
            value["statistics"]["bootstrap_draws"] = 9999
            _write(path, value)
        self._both_reject(bootstrap_attack)

        def authority_attack(raw):
            path = raw / "OWNER_FORMAL_AUTHORITY.json"
            value = json.loads(path.read_text())
            value["authorization"]["authorizes_any_other_goal_matrix_target_or_worker"] = True
            _resign(value, "authority_sha256")
            _write(path, value)
        self._both_reject(authority_attack)

    def test_data_admission_input_file_and_page_cache_claim_attacks(self) -> None:
        def admission(raw):
            path = raw / "DATA_ADMISSION.json"
            value = json.loads(path.read_text())
            value["drop_caches_or_page_cache_control_used"] = True
            _resign(value, "admission_sha256")
            _write(path, value)
        self._both_reject(admission)

        def input_stat(raw):
            path = raw / "workers" / "worker_0000.json"
            value = json.loads(path.read_text())
            receipt = value["input_file_receipt"]
            receipt["st_ino"] += 1
            _resign(receipt, "receipt_sha256")
            _resign(value, "worker_sha256")
            _write(path, value)
        self._both_reject(input_stat)

    def test_environment_and_raw_authority_manifest_attacks(self) -> None:
        def environment_extra(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["formal_worker_environment"]["CUPY_CACHE_DIR"] = "/tmp/shared"
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(environment_extra)

        def environment_missing_locale(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            del value["formal_worker_environment"]["LC_ALL"]
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(environment_missing_locale)

        def environment_injected_locale(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["formal_worker_environment"]["LC_CTYPE"] = "C.UTF-8"
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(environment_injected_locale)

        def environment_preload(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["formal_worker_environment"]["LD_PRELOAD"] = "/tmp/inject.so"
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(environment_preload)

        def manifest_path(raw):
            path = raw / "AUTHORITY_MANIFEST.json"
            value = json.loads(path.read_text())
            value["authorities"]["source_authority"]["path"] = (
                "AUTHORITIES/../AUTHORITIES/source_authority.json"
            )
            _resign(value, "manifest_sha256")
            _write(path, value)
        self._both_reject(manifest_path)

        def manifest_hash(raw):
            path = raw / "AUTHORITY_MANIFEST.json"
            value = json.loads(path.read_text())
            value["authorities"]["citation_authority"]["file_sha256"] = _identity("forged-authority")
            _resign(value, "manifest_sha256")
            _write(path, value)
        self._both_reject(manifest_hash)

        def extra_authority_file(raw):
            _write(
                raw / "AUTHORITIES" / "unmanifested_authority.json",
                {"schema": "rtdl.goal5791.unmanifested_authority.v1"},
            )
        self._both_reject(extra_authority_file)

        def authority_name_case_drift(raw):
            source = raw / "AUTHORITIES" / "source_authority.json"
            temporary = raw / "AUTHORITIES" / "case_rename.tmp"
            source.rename(temporary)
            temporary.rename(raw / "AUTHORITIES" / "SOURCE_AUTHORITY.json")
        self._both_reject(authority_name_case_drift)

        def copied_authority_resigned(raw):
            authority_path = raw / "AUTHORITIES" / "data_authority.json"
            authority = json.loads(authority_path.read_text())
            authority["authorization"]["authorizes_formal_execution"] = True
            _resign(authority, "authority_sha256")
            _write(authority_path, authority)
            manifest_path = raw / "AUTHORITY_MANIFEST.json"
            manifest = json.loads(manifest_path.read_text())
            row = manifest["authorities"]["data_authority"]
            row["file_sha256"] = _file_sha(authority_path)
            row["bytes"] = authority_path.stat().st_size
            _resign(manifest, "manifest_sha256")
            _write(manifest_path, manifest)
        self._both_reject(copied_authority_resigned)

    def test_formal_root_resource_and_target_runtime_admission_attacks(
        self,
    ) -> None:
        def fully_resign_formal_chain(raw, mutate_formal) -> None:
            formal_path = raw / "OWNER_FORMAL_AUTHORITY.json"
            formal = json.loads(formal_path.read_text())
            mutate_formal(formal)
            _resign(formal, "authority_sha256")
            _write(formal_path, formal)
            formal_file_sha = _file_sha(formal_path)
            for filename in (
                "RESOURCE_ADMISSION.json", "TARGET_RUNTIME_ADMISSION.json",
            ):
                path = raw / filename
                admission = json.loads(path.read_text())
                admission["formal_authority_file_sha256"] = formal_file_sha
                admission["formal_authority_sha256"] = formal[
                    "authority_sha256"
                ]
                if filename == "RESOURCE_ADMISSION.json":
                    target = formal["execution_target"]
                    resources = formal["resource_confirmation"]
                    for name in (
                        "target_materialization_root",
                        "create_only_formal_output_root",
                        "controller_incomplete_staging_root",
                    ):
                        admission[name] = target[name]
                    admission["formal_output_parent_resolved_path"] = (
                        resources["formal_output_parent_resolved_path"]
                    )
                    admission[
                        "authority_confirmed_free_disk_bytes"
                    ] = resources["confirmed_free_disk_bytes"]
                    admission[
                        "authority_observed_free_disk_bytes_at_authority_creation"
                    ] = resources[
                        "formal_output_parent_free_bytes_observed_at_authority_creation"
                    ]
                    admission["minimum_required_free_disk_bytes"] = (
                        resources["minimum_required_free_disk_bytes"]
                    )
                _resign(admission, "admission_sha256")
                _write(path, admission)

        def swap_roots(raw):
            def mutate(formal):
                target = formal["execution_target"]
                target["target_materialization_root"], target[
                    "create_only_formal_output_root"
                ] = (
                    target["create_only_formal_output_root"],
                    target["target_materialization_root"],
                )
                output = PurePosixPath(target["create_only_formal_output_root"])
                target["controller_incomplete_staging_root"] = (
                    output.with_name(
                        f".{output.name}.goal5791_incomplete"
                    ).as_posix()
                )
            fully_resign_formal_chain(raw, mutate)
        self._both_reject(swap_roots)

        def overlap_roots(raw):
            def mutate(formal):
                target = formal["execution_target"]
                target["create_only_formal_output_root"] = target[
                    "target_materialization_root"
                ]
                output = PurePosixPath(target["create_only_formal_output_root"])
                target["controller_incomplete_staging_root"] = (
                    output.with_name(
                        f".{output.name}.goal5791_incomplete"
                    ).as_posix()
                )
            fully_resign_formal_chain(raw, mutate)
        self._both_reject(overlap_roots)

        def backslash_root(raw):
            def mutate(formal):
                target = formal["execution_target"]
                target["create_only_formal_output_root"] = (
                    "/tmp/goal5791\\formal_output"
                )
                output = PurePosixPath(target["create_only_formal_output_root"])
                target["controller_incomplete_staging_root"] = (
                    output.with_name(
                        f".{output.name}.goal5791_incomplete"
                    ).as_posix()
                )
            fully_resign_formal_chain(raw, mutate)
        self._both_reject(backslash_root)

        def authority_observation(raw):
            def mutate(formal):
                formal["resource_confirmation"][
                    "formal_output_parent_free_bytes_observed_at_authority_creation"
                ] = 19_999_999_999
            fully_resign_formal_chain(raw, mutate)
        self._both_reject(authority_observation)

        def admission_attack(name, value):
            def mutate(raw):
                path = raw / "RESOURCE_ADMISSION.json"
                admission = json.loads(path.read_text())
                admission[name] = value(admission) if callable(value) else value
                _resign(admission, "admission_sha256")
                _write(path, admission)
            return mutate

        self._both_reject(admission_attack(
            "minimum_required_free_disk_bytes", 19_999_999_999,
        ))
        self._both_reject(admission_attack(
            "controller_observed_free_disk_bytes_before_worker_zero",
            lambda value: value["authority_confirmed_free_disk_bytes"] - 1,
        ))
        self._both_reject(admission_attack(
            "target_materialization_root",
            "/tmp/goal5791_formal_output",
        ))

        def target_attack(name, value):
            def mutate(raw):
                path = raw / "TARGET_RUNTIME_ADMISSION.json"
                admission = json.loads(path.read_text())
                admission[name] = value
                _resign(admission, "admission_sha256")
                _write(path, admission)
            return mutate

        for name, value in (
            ("observed_gpu_uuid", "GPU-forged"),
            ("observed_driver_version", "forged-driver"),
            ("observed_compute_capability", "9.9"),
            ("nvidia_smi_query", "uuid"),
            ("controlled_environment_sha256", _identity("forged-env")),
            ("visible_gpu_row_count", True),
        ):
            with self.subTest(name=name):
                self._both_reject(target_attack(name, value))

        def controller_bootstrap_attack(name, value):
            def mutate(raw):
                path = raw / "SOURCE_ADMISSION.json"
                admission = json.loads(path.read_text())
                observation = admission["controller_bootstrap_observation"]
                observation[name] = value
                _resign(admission, "admission_sha256")
                _write(path, admission)
            return mutate

        for name, value in (
            ("controller_environment_sha256", _identity("polluted-env")),
            ("controller_environment_key_count", 15),
            ("controller_cupy_cache_dir_absent", False),
        ):
            with self.subTest(name=name):
                self._both_reject(controller_bootstrap_attack(name, value))

        def controller_source_attack(field, value):
            def mutate(raw):
                path = raw / "SOURCE_ADMISSION.json"
                admission = json.loads(path.read_text())
                observation = admission["controller_bootstrap_observation"]
                observation["loaded_harness_sources"][
                    "scripts/goal5791_formal_controller.py"
                ][field] = value
                _resign(admission, "admission_sha256")
                _write(path, admission)
            return mutate

        self._both_reject(controller_source_attack(
            "resolved_path", "/tmp/goal5791_formal_test/source/forged.py",
        ))
        self._both_reject(controller_source_attack(
            "file_sha256", _identity("forged-controller-source"),
        ))

    def test_control_file_and_no_gpu_process_state_attacks(self) -> None:
        def mutate_source_process_state(raw, mutate) -> None:
            path = raw / "SOURCE_ADMISSION.json"
            admission = json.loads(path.read_text())
            observation = admission["controller_bootstrap_observation"][
                "no_gpu_product_process_state_observation"
            ]
            mutate(observation)
            _resign(admission, "admission_sha256")
            _write(path, admission)

        def malicious_bootstrap_maps(raw) -> None:
            def mutate(observation) -> None:
                malicious = (
                    "7f100000-7f101000 r-xp 00000000 08:01 3 "
                    "/usr/lib/libcuda.so.1"
                )
                observation["proc_self_maps_lines"].append(malicious)
                payload = (
                    "\n".join(observation["proc_self_maps_lines"]) + "\n"
                ).encode("utf-8")
                observation["proc_self_maps_sha256"] = hashlib.sha256(
                    payload
                ).hexdigest()
                observation["forbidden_dso_map_matches"] = [malicious]
            mutate_source_process_state(raw, mutate)
        self._both_reject(malicious_bootstrap_maps)

        def deleted_marker(raw) -> None:
            def mutate(observation) -> None:
                observation["forbidden_dso_map_markers"].remove(
                    "/libcuda.so"
                )
            mutate_source_process_state(raw, mutate)
        self._both_reject(deleted_marker)

        def forbidden_module(raw) -> None:
            def mutate(observation) -> None:
                observation["loaded_module_names"].append("rtdsl")
                observation["loaded_module_names"].sort()
                observation["forbidden_module_matches"] = ["rtdsl"]
            mutate_source_process_state(raw, mutate)
        self._both_reject(forbidden_module)

        def writable_control_file(raw) -> None:
            path = raw / "SOURCE_ADMISSION.json"
            admission = json.loads(path.read_text())
            row = admission["controller_bootstrap_observation"][
                "immutable_control_file_observations"
            ]["formal_authority"]
            row["st_mode"] = 0o100644
            _resign(admission, "admission_sha256")
            _write(path, admission)
        self._both_reject(writable_control_file)

        def changed_control_file(raw) -> None:
            path = raw / "SOURCE_ADMISSION.json"
            admission = json.loads(path.read_text())
            row = admission["controller_bootstrap_observation"][
                "immutable_control_file_observations"
            ]["runtime"]
            row["file_sha256"] = _identity("swapped-runtime-control-file")
            row["bytes"] += 1
            _resign(admission, "admission_sha256")
            _write(path, admission)
        self._both_reject(changed_control_file)

        def swap_control_roles(raw) -> None:
            path = raw / "SOURCE_ADMISSION.json"
            admission = json.loads(path.read_text())
            rows = admission["controller_bootstrap_observation"][
                "immutable_control_file_observations"
            ]
            rows["runtime"], rows["formal_authority"] = (
                rows["formal_authority"], rows["runtime"]
            )
            _resign(admission, "admission_sha256")
            _write(path, admission)
        self._both_reject(swap_control_roles)

        def mutate_target_process_state(raw, field, malicious) -> None:
            path = raw / "TARGET_RUNTIME_ADMISSION.json"
            admission = json.loads(path.read_text())
            observation = admission[field]
            observation["proc_self_maps_lines"].append(malicious)
            payload = (
                "\n".join(observation["proc_self_maps_lines"]) + "\n"
            ).encode("utf-8")
            observation["proc_self_maps_sha256"] = hashlib.sha256(
                payload
            ).hexdigest()
            observation["forbidden_dso_map_matches"] = [malicious]
            _resign(admission, "admission_sha256")
            _write(path, admission)

        self._both_reject(lambda raw: mutate_target_process_state(
            raw,
            "no_gpu_product_process_state_before_nvidia_smi",
            (
                "7f200000-7f201000 r-xp 00000000 08:01 4 "
                "/usr/lib/libnvoptix.so.1"
            ),
        ))
        self._both_reject(lambda raw: mutate_target_process_state(
            raw,
            "no_gpu_product_process_state_after_nvidia_smi",
            (
                "7f300000-7f301000 r-xp 00000000 08:01 5 "
                "/tmp/librtdl_optix.so"
            ),
        ))

    def test_resigned_source_runtime_manifest_map_and_receipt_attacks(self) -> None:
        def worker_timeout_policy(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["worker_timeout_seconds"] += 1.0
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(worker_timeout_policy)

        def formal_budget_authority_binding(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["formal_conservative_budget_seconds"] += 1.0
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(formal_budget_authority_binding)

        def runtime_crosslink(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["numba_version"] = "different-but-well-formed"
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(runtime_crosslink)

        def llvmlite_identity(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["llvmlite_version"] = "0.47.1"
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(llvmlite_identity)

        def source_tree(raw):
            path = raw / "SOURCE_ADMISSION.json"
            value = json.loads(path.read_text())
            value["execution_source_tree_sha256"] = _identity("changed-source")
            _resign(value, "admission_sha256")
            _write(path, value)
        self._both_reject(source_tree)

        def extra_source_path_fully_resigned(raw):
            admission_path = raw / "SOURCE_ADMISSION.json"
            admission = json.loads(admission_path.read_text())
            admission["unmanifested_path_count"] = 1
            admission["regular_file_count"] += 1
            admission["source_path_count"] += 1
            _resign(admission, "admission_sha256")
            _write(admission_path, admission)
            mirrored = (
                "unmanifested_path_count", "regular_file_count",
                "source_path_count",
            )
            for worker_path in sorted((raw / "workers").iterdir()):
                worker = json.loads(worker_path.read_text())
                worker["source_admission_sha256"] = admission[
                    "admission_sha256"
                ]
                receipt = worker["source_rehash_receipt"]
                receipt["source_admission_sha256"] = admission[
                    "admission_sha256"
                ]
                for name in mirrored:
                    receipt[name] = admission[name]
                _resign(receipt, "receipt_sha256")
                _resign(worker, "worker_sha256")
                _write(worker_path, worker)
        self._both_reject(extra_source_path_fully_resigned)

        def manifest_binding(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            value["execution_source_manifest_file_sha256"] = _identity(
                "changed-manifest"
            )
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(manifest_binding)

        def formal_source_map(raw):
            path = raw / "RUNTIME.json"
            value = json.loads(path.read_text())
            identity = value["formal_identity_record"]
            identity["formal_sources"][primary.FORMAL_SOURCE_PATHS[0]] = (
                _identity("changed-formal-source")
            )
            identity.pop("formal_identity_sha256")
            identity["formal_identity_sha256"] = digest(identity)
            value["formal_identity_sha256"] = identity[
                "formal_identity_sha256"
            ]
            _resign(value, "runtime_sha256")
            _write(path, value)
        self._both_reject(formal_source_map)

        def read_only_claim(raw):
            path = raw / "SOURCE_ADMISSION.json"
            value = json.loads(path.read_text())
            value["all_manifest_payloads_read_only"] = False
            _resign(value, "admission_sha256")
            _write(path, value)
        self._both_reject(read_only_claim)

        def receipt_swap(raw):
            first_path = raw / "workers" / "worker_0000.json"
            second_path = raw / "workers" / "worker_0001.json"
            first = json.loads(first_path.read_text())
            second = json.loads(second_path.read_text())
            second["source_rehash_receipt"] = deepcopy(
                first["source_rehash_receipt"]
            )
            _resign(second, "worker_sha256")
            _write(second_path, second)
        self._both_reject(receipt_swap)

        def receipt_stat(raw):
            path = raw / "workers" / "worker_0000.json"
            value = json.loads(path.read_text())
            receipt = value["source_rehash_receipt"]
            receipt["manifest_payload_bytes"] += 1
            _resign(receipt, "receipt_sha256")
            _resign(value, "worker_sha256")
            _write(path, value)
        self._both_reject(receipt_stat)

    def test_result_seals_and_create_only_writers(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            raw = _raw(root / "raw")
            first = primary.evaluate(raw, raw / "EVALUATION.json")
            second = independent.recount(
                raw, raw / "INDEPENDENT_RECOUNT.json"
            )
            primary_value = json.loads(first.read_text())
            recount_value = json.loads(second.read_text())
            primary_seal = primary_value.pop("evaluation_sha256")
            recount_seal = recount_value.pop("recount_sha256")
            self.assertEqual(primary_seal, digest(primary_value))
            self.assertEqual(recount_seal, digest(recount_value))
            with self.assertRaises(FileExistsError):
                primary.evaluate(raw, first)
            with self.assertRaises(FileExistsError):
                independent.recount(raw, second)

    def test_final_published_clean_copy_offline_recount_and_attacks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            published = _final_published_raw(root / "published")
            clean_copy = root / "clean_copy"
            shutil.copytree(published, clean_copy)
            offline_path = root / "offline_recount.json"
            independent.recount(clean_copy, offline_path)
            stored = json.loads(
                (clean_copy / "INDEPENDENT_RECOUNT.json").read_text()
            )
            offline = json.loads(offline_path.read_text())
            self.assertEqual(offline["raw_root_mode"], "final_published")
            self.assertEqual(offline["rows"], stored["rows"])
            self.assertEqual(offline["worker_count"], 96)
            self.assertTrue(all(
                not any(path.iterdir())
                for path in (clean_copy / "worker_caches").iterdir()
            ))
            with self.assertRaises(RuntimeError):
                independent.recount(
                    clean_copy, clean_copy / "OFFLINE_RECOUNT.json"
                )
            self.assertFalse((clean_copy / "OFFLINE_RECOUNT.json").exists())

        with tempfile.TemporaryDirectory() as temp:
            published = _final_published_raw(Path(temp) / "cache_payload")
            (published / "worker_caches" / "worker_0000" / "payload.bin").write_bytes(
                b"non-authoritative-cache-payload"
            )
            with self.assertRaises(RuntimeError):
                independent.build_recount(published)

        with tempfile.TemporaryDirectory() as temp:
            published = _final_published_raw(Path(temp) / "mixed_stage")
            (published / "RESULT.json").unlink()
            with self.assertRaises(RuntimeError):
                independent.build_recount(published)

        with tempfile.TemporaryDirectory() as temp:
            published = _final_published_raw(Path(temp) / "resigned_chain")
            recount_path = published / "INDEPENDENT_RECOUNT.json"
            stored = json.loads(recount_path.read_text())
            stored["runtime_sha256"] = _identity(
                "forged-published-recount-runtime"
            )
            _resign(stored, "recount_sha256")
            _write(recount_path, stored)

            cohort_path = published / "COHORT_MANIFEST.json"
            cohort = json.loads(cohort_path.read_text())
            cohort["independent_recount_file_sha256"] = _file_sha(
                recount_path
            )
            _resign(cohort, "manifest_sha256")
            _write(cohort_path, cohort)

            result_path = published / "RESULT.json"
            result = json.loads(result_path.read_text())
            result["independent_recount_file_sha256"] = _file_sha(
                recount_path
            )
            result["cohort_manifest_sha256"] = cohort["manifest_sha256"]
            _resign(result, "result_sha256")
            _write(result_path, result)
            with self.assertRaises(RuntimeError):
                independent.build_recount(published)

        with tempfile.TemporaryDirectory() as temp:
            published = _final_published_raw(
                Path(temp) / "cohort_worker_file_pin"
            )
            cohort_path = published / "COHORT_MANIFEST.json"
            cohort = json.loads(cohort_path.read_text())
            cohort["workers"][0]["file_sha256"] = _identity(
                "forged-worker-file-pin"
            )
            _resign(cohort, "manifest_sha256")
            _write(cohort_path, cohort)
            result_path = published / "RESULT.json"
            result = json.loads(result_path.read_text())
            result["cohort_manifest_sha256"] = cohort["manifest_sha256"]
            _resign(result, "result_sha256")
            _write(result_path, result)
            with self.assertRaises(RuntimeError):
                independent.build_recount(published)

        with tempfile.TemporaryDirectory() as temp:
            published = _final_published_raw(
                Path(temp) / "result_analysis_file_pin"
            )
            result_path = published / "RESULT.json"
            result = json.loads(result_path.read_text())
            result["evaluation_file_sha256"] = _identity(
                "forged-evaluation-file-pin"
            )
            _resign(result, "result_sha256")
            _write(result_path, result)
            with self.assertRaises(RuntimeError):
                independent.build_recount(published)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            baseline = _final_published_raw(root / "baseline_long_names")
            attacks = (
                ("EVALUATION.json", "evaluation_sha256",
                 "os_page_cache_controlled_or_dropped"),
                ("INDEPENDENT_RECOUNT.json", "recount_sha256",
                 "os_page_cache_scope"),
                ("COHORT_MANIFEST.json", "manifest_sha256",
                 "os_page_cache_controlled_or_dropped"),
                ("RESULT.json", "result_sha256", "os_page_cache_scope"),
            )
            for ordinal, (filename, seal, short_name) in enumerate(attacks):
                attacked = root / f"resigned_short_name_{ordinal}"
                shutil.copytree(baseline, attacked)
                path = attacked / filename
                value = json.loads(path.read_text())
                value[short_name] = False
                _resign(value, seal)
                _write(path, value)
                with self.assertRaises(RuntimeError):
                    independent.build_recount(attacked)

    def test_primary_and_recount_stage_exact_sets_and_evaluation_pin_attacks(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "missing_evaluation")
            with self.assertRaises(RuntimeError):
                independent.build_recount(raw)

        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "preexisting_evaluation")
            evaluation = primary.build_evaluation(raw)
            _write(raw / "EVALUATION.json", evaluation)
            with self.assertRaises(RuntimeError):
                primary.build_evaluation(raw)

        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "bad_evaluation_seal")
            evaluation = primary.build_evaluation(raw)
            evaluation["worker_count"] = 95
            _write(raw / "EVALUATION.json", evaluation)
            with self.assertRaises(RuntimeError):
                independent.build_recount(raw)

        with tempfile.TemporaryDirectory() as temp:
            raw = _raw(Path(temp) / "resigned_evaluation_pin")
            evaluation = primary.build_evaluation(raw)
            evaluation["runtime_sha256"] = _identity(
                "forged-primary-runtime-pin"
            )
            _resign(evaluation, "evaluation_sha256")
            _write(raw / "EVALUATION.json", evaluation)
            with self.assertRaises(RuntimeError):
                independent.build_recount(raw)

    def test_independent_recount_import_boundary(self) -> None:
        source = Path(independent.__file__).read_text(encoding="utf-8")
        self.assertNotIn("validate_phase_accounting", source)
        tree = ast.parse(source)
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
        joined = "\n".join(sorted(imports)).lower()
        for forbidden in (
            "goal5791_formal_evaluate", "goal5791_formal_controller",
            "goal5791_formal_worker", "paper-reproduction-apps", "rtdsl",
        ):
            self.assertNotIn(forbidden, joined)


if __name__ == "__main__":
    unittest.main()
