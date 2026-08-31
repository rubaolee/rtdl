"""Build the sealed Goal5797 liveness/necessity matrix from frozen GPU bytes."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
from pathlib import Path

from rtdsl.v4_protocol_contract import (
    CompilerProtocolProjection,
    ProtocolContractDeclaration,
    ProtocolMechanism,
    verify_protocol_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PREACTION = ROOT / "history/internal_docs/goal5797_s0_five_mechanism_ablation_preaction_20260823.json"
GPU_ROOT = ROOT / "history/internal_docs/goal5797_gpu_evidence_20260823"
GPU_RESULT = GPU_ROOT / "GOAL5797_PYOPTIX_CONTROLS.json"
OWL = ROOT / "history/internal_docs/goal5797_owl_source_responsibility_and_goal5794_tree_correction_20260823.json"
SPEC = ROOT / "experiments/goal5796_matched/semantic_spec.json"
CONTROL_SOURCE = ROOT / "experiments/goal5797_ablation/pyoptix_controls.py"
OUTPUT = ROOT / "history/internal_docs/goal5797_five_mechanism_liveness_and_necessity_result_20260823.json"


def _bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _pretty(value: object) -> bytes:
    return json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False,
    ).encode("utf-8") + b"\n"


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha_file(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"object required: {path}")
    return value


def _decision(declaration, projection) -> dict[str, object]:
    return verify_protocol_contract(declaration, projection).to_mapping()


def _common(
    *, family: str, task_sha: str, role_effects, attribute, physical,
    continuation: str, executable: str,
) -> ProtocolContractDeclaration:
    return ProtocolContractDeclaration(
        family=family,
        task_semantics_sha256=task_sha,
        role_effects=tuple(sorted(
            (key, tuple(sorted(value))) for key, value in role_effects.items())),
        attribute_abi_ownership=tuple(sorted(attribute.items())),
        physical_bindings=tuple(sorted(physical.items())),
        continuation_policy=continuation,
        checked_executable_sha256=executable,
    )


def _projection(
    declaration: ProtocolContractDeclaration,
    *, device_source_sha: str, host_source_sha: str, executable: str,
    role_effects=None, attribute=None, physical=None, continuation=None,
) -> CompilerProtocolProjection:
    return CompilerProtocolProjection(
        family=declaration.family,
        task_semantics_sha256=declaration.task_semantics_sha256,
        role_effects=(declaration.role_effects if role_effects is None else tuple(
            sorted((key, tuple(sorted(value))) for key, value in role_effects.items()))),
        attribute_abi_ownership=(
            declaration.attribute_abi_ownership if attribute is None
            else tuple(sorted(attribute.items()))),
        physical_bindings=(
            declaration.physical_bindings if physical is None
            else tuple(sorted(physical.items()))),
        continuation_policy=(
            declaration.continuation_policy if continuation is None
            else continuation),
        actual_executable_sha256=executable,
        generated_device_source_sha256=device_source_sha,
        generated_host_source_sha256=host_source_sha,
    )


def _assert_single(decision, mechanism, reason) -> None:
    if decision.verdict != "REJECT" or len(decision.findings) != 1:
        raise RuntimeError(
            f"{mechanism.value}: expected one finding, got {decision!r}")
    finding = decision.findings[0]
    if finding.mechanism is not mechanism or finding.reason_id != reason:
        raise RuntimeError(
            f"{mechanism.value}: unexpected finding {finding!r}")
    if decision.verdict_with_mechanism_ablated(mechanism) != "ACCEPT":
        raise RuntimeError(f"{mechanism.value}: single ablation did not accept")


def build() -> dict[str, object]:
    preaction_bytes = PREACTION.read_bytes()
    gpu_bytes = GPU_RESULT.read_bytes()
    owl_bytes = OWL.read_bytes()
    preaction = json.loads(preaction_bytes)
    gpu = json.loads(gpu_bytes)
    owl = json.loads(owl_bytes)
    if preaction.get("status") != "FROZEN_BEFORE_FIRST_GOAL5797_ATTACK_OR_GPU_CONTROL":
        raise RuntimeError("preaction not frozen")
    if gpu.get("status") != "PASS" or gpu.get("registered_performance_timing_count") != 0:
        raise RuntimeError("GPU functional controls did not pass exactly")
    if gpu.get("baseline_runtime") != {
        "cuda_last_error": "SUCCESS", "cuda_last_error_code": 0,
        "optix_validation": "PASS",
        "optix_validation_error_message_count": 0, "process_exit_code": 0,
    }:
        raise RuntimeError("baseline runtime diagnostics are not exact PASS")
    if owl.get("status") != "PASS_AT_FROZEN_ANALYSED_NOT_IMPLEMENTED_SCOPE":
        raise RuntimeError("OWL source responsibility did not pass")
    if _sha_file(SPEC) != gpu["semantic_spec_sha256"]:
        raise RuntimeError("semantic spec identity mismatch")
    if _sha_file(CONTROL_SOURCE) != gpu["host_control_source_sha256"]:
        raise RuntimeError("executed host control identity mismatch")

    identities = gpu["identities"]
    for name, identity in identities.items():
        source = GPU_ROOT / "gpu_evidence/device_sources" / f"{name}.cu"
        ptx = GPU_ROOT / "gpu_evidence/ptx" / f"{name}.ptx"
        if _sha_file(source) != identity["device_source_sha256"] \
                or _sha_file(ptx) != identity["loaded_ptx_sha256"]:
            raise RuntimeError(f"GPU identity mismatch: {name}")

    task_sha = str(gpu["semantic_spec_sha256"])
    host_sha = str(gpu["host_control_source_sha256"])
    valid_identity = identities["valid_a"]
    valid_ptx = str(valid_identity["loaded_ptx_sha256"])
    relation_effects = {
        "intersection": ("report_application_item_id",),
        "any_hit": ("emit_relation_row", "accept_continue"),
    }
    triangle_effects = {
        "any_hit": ("payload_write", "accept_continue"),
        "finalize": ("checked_u64_reduce", "require_status_ok"),
    }
    relation_attribute = {"attr0": "application_item_id_u32"}
    triangle_attribute = {}
    relation_physical = {
        "query.lower.x": "host.query.lower.x",
        "query.lower.y": "host.query.lower.y",
        "query.upper.x": "host.query.upper.x",
        "query.upper.y": "host.query.upper.y",
    }
    triangle_physical = {
        "ray.origin": "host.query.origin_f32x3",
        "ray.direction": "host.query.direction_f32x3",
        "gas": "builtin_triangle_vertices_f32x3",
    }
    complete = "REQUIRE_COMPLETE_BEFORE_CONSUME"
    relation = _common(
        family="custom_aabb_bounded_relation_v1", task_sha=task_sha,
        role_effects=relation_effects, attribute=relation_attribute,
        physical=relation_physical, continuation=complete,
        executable=valid_ptx)
    triangle = _common(
        family="builtin_triangle_reduction_v1", task_sha=task_sha,
        role_effects=triangle_effects, attribute=triangle_attribute,
        physical=triangle_physical, continuation=complete,
        executable=valid_ptx)
    relation_projection = _projection(
        relation, device_source_sha=str(valid_identity["device_source_sha256"]),
        host_source_sha=host_sha, executable=valid_ptx)
    triangle_projection = _projection(
        triangle, device_source_sha=str(valid_identity["device_source_sha256"]),
        host_source_sha=host_sha, executable=valid_ptx)
    if verify_protocol_contract(relation, relation_projection).verdict != "ACCEPT" \
            or verify_protocol_contract(triangle, triangle_projection).verdict != "ACCEPT":
        raise RuntimeError("nearby valid full contracts did not accept")

    prereg = {row["id"]: row for row in preaction["mechanisms"]}
    observed = gpu["behavioral_controls"]
    rows = []
    definitions = [
        (
            ProtocolMechanism.ROLE_EFFECT_CLOSURE, triangle,
            triangle_projection,
            replace(triangle, role_effects=(("any_hit", ()),
                                             ("finalize", ("checked_u64_reduce", "require_status_ok")))),
            _projection(
                replace(triangle, checked_executable_sha256=str(
                    identities["role_effect_closure"]["loaded_ptx_sha256"])),
                device_source_sha=str(identities["role_effect_closure"]["device_source_sha256"]),
                host_source_sha=host_sha,
                executable=str(identities["role_effect_closure"]["loaded_ptx_sha256"]),
                role_effects={
                    "any_hit": ("payload_write", "terminate"),
                    "finalize": ("checked_u64_reduce", "require_status_ok"),
                }),
            ["role_effects.any_hit"],
        ),
        (
            ProtocolMechanism.PAYLOAD_ATTRIBUTE_ABI_OWNERSHIP, relation,
            relation_projection,
            replace(relation, attribute_abi_ownership=(("attr0", "primitive_index_u32"),)),
            _projection(
                replace(relation, checked_executable_sha256=str(
                    identities["payload_attribute_abi_ownership"]["loaded_ptx_sha256"])),
                device_source_sha=str(identities["payload_attribute_abi_ownership"]["device_source_sha256"]),
                host_source_sha=host_sha,
                executable=str(identities["payload_attribute_abi_ownership"]["loaded_ptx_sha256"]),
                attribute={"attr0": "primitive_index_u32"}),
            ["attribute_abi_ownership.attr0"],
        ),
        (
            ProtocolMechanism.PHYSICAL_GEOMETRY_BINDING, relation,
            relation_projection,
            replace(relation, physical_bindings=tuple(sorted({
                **relation_physical,
                "query.lower.x": "host.query.lower.y",
                "query.lower.y": "host.query.lower.x",
                "query.upper.x": "host.query.upper.y",
                "query.upper.y": "host.query.upper.x",
            }.items()))),
            _projection(
                replace(relation, checked_executable_sha256=str(
                    identities["physical_geometry_binding"]["loaded_ptx_sha256"])),
                device_source_sha=str(identities["physical_geometry_binding"]["device_source_sha256"]),
                host_source_sha=host_sha,
                executable=str(identities["physical_geometry_binding"]["loaded_ptx_sha256"]),
                physical={
                    "query.lower.x": "host.query.lower.y",
                    "query.lower.y": "host.query.lower.x",
                    "query.upper.x": "host.query.upper.y",
                    "query.upper.y": "host.query.upper.x",
                }),
            ["physical_bindings.query.lower.x", "physical_bindings.query.lower.y",
             "physical_bindings.query.upper.x", "physical_bindings.query.upper.y"],
        ),
        (
            ProtocolMechanism.DEVICE_STATUS_CONTINUATION, relation,
            relation_projection,
            replace(relation, continuation_policy="ALLOW_PARTIAL"),
            _projection(
                relation, device_source_sha=str(valid_identity["device_source_sha256"]),
                host_source_sha=host_sha, executable=valid_ptx,
                continuation="ALLOW_PARTIAL"),
            ["continuation_policy"],
        ),
        (
            ProtocolMechanism.CHECKED_PROGRAM_EXECUTABLE_IDENTITY, triangle,
            triangle_projection,
            replace(triangle, checked_executable_sha256=str(
                identities["checked_program_executable_identity"]["loaded_ptx_sha256"])),
            _projection(
                triangle,
                device_source_sha=str(identities["checked_program_executable_identity"]["device_source_sha256"]),
                host_source_sha=host_sha,
                executable=str(identities["checked_program_executable_identity"]["loaded_ptx_sha256"])),
            ["checked_executable_sha256"],
        ),
    ]
    for mechanism, baseline_contract, baseline_projection, liveness_mutated, behavior_projection, mutation_paths in definitions:
        mechanism_id = mechanism.value
        expected_reason = prereg[mechanism_id]["expected_full_reason"]
        liveness = verify_protocol_contract(liveness_mutated, baseline_projection)
        _assert_single(liveness, mechanism, expected_reason)

        behavior_contract = baseline_contract
        if mechanism is not ProtocolMechanism.CHECKED_PROGRAM_EXECUTABLE_IDENTITY:
            behavior_contract = replace(
                baseline_contract,
                checked_executable_sha256=behavior_projection.actual_executable_sha256)
        behavior = verify_protocol_contract(behavior_contract, behavior_projection)
        _assert_single(behavior, mechanism, expected_reason)
        gpu_row = observed[mechanism_id]
        if gpu_row.get("exception") is not None:
            raise RuntimeError(f"baseline exception for {mechanism_id}")
        rows.append({
            "mechanism": mechanism_id,
            "expected_reason": expected_reason,
            "liveness": {
                "baseline_full_verdict": "ACCEPT",
                "mutation_paths": mutation_paths,
                "mutated_contract": liveness_mutated.to_mapping(),
                "projection_bytes_unchanged": True,
                "decision": liveness.to_mapping(),
                "verdict_delta": "ACCEPT_TO_REJECT",
                "only_this_mechanism_ablated_verdict": "ACCEPT",
            },
            "semantic_necessity": {
                "invalid_contract": behavior_contract.to_mapping(),
                "actual_projection": behavior_projection.to_mapping(),
                "full_decision": behavior.to_mapping(),
                "only_this_mechanism_ablated_verdict": "ACCEPT",
                "other_mechanism_finding_count": 0,
                "pyoptix_gpu_control": gpu_row,
                "optix_validation": "PASS",
                "cuda_last_error": "SUCCESS",
                "process_exit_code": 0,
            },
        })

    # Identity's B/B nearby control is essential: the gate must not merely
    # reject every alternate executable.
    identity_b = identities["checked_program_executable_identity"]
    b_contract = replace(
        triangle, checked_executable_sha256=str(identity_b["loaded_ptx_sha256"]))
    b_projection = _projection(
        b_contract,
        device_source_sha=str(identity_b["device_source_sha256"]),
        host_source_sha=host_sha,
        executable=str(identity_b["loaded_ptx_sha256"]),
        role_effects=triangle_effects)
    if verify_protocol_contract(b_contract, b_projection).verdict != "ACCEPT":
        raise RuntimeError("identity B/B reject-all guard failed")

    result = {
        "schema": "rtdl.goal5797.five_mechanism_liveness_and_necessity.v1",
        "status": "PASS",
        "date": "2026-08-23",
        "preaction": {
            "path": PREACTION.relative_to(ROOT).as_posix(),
            "bytes": len(preaction_bytes), "sha256": _sha_bytes(preaction_bytes),
            "frozen_before_gpu_controls": True,
        },
        "gpu_evidence": {
            "path": GPU_RESULT.relative_to(ROOT).as_posix(),
            "bytes": len(gpu_bytes), "sha256": _sha_bytes(gpu_bytes),
            "arm": gpu["arm"], "runtime": gpu["baseline_runtime"],
        },
        "nearby_valid_controls": {
            "relation_full_verdict": "ACCEPT",
            "relation_output": gpu["nearby_valid"]["relation"],
            "triangle_a_full_verdict": "ACCEPT",
            "triangle_a_output": gpu["nearby_valid"]["triangle"],
            "triangle_b_full_verdict": "ACCEPT",
            "triangle_b_output": observed["checked_program_executable_identity"]["output"],
        },
        "mechanism_count": 5,
        "liveness_pass_count": len(rows),
        "semantic_necessity_pass_count": len(rows),
        "rows": rows,
        "owl": {
            "path": OWL.relative_to(ROOT).as_posix(),
            "bytes": len(owl_bytes), "sha256": _sha_bytes(owl_bytes),
            "status": owl["status"],
            "execution_claimed": False,
            "performance_claimed": False,
        },
        "failed_predecessor_harness": {
            "v1_source_sha256": _sha_file(GPU_ROOT / "pyoptix_controls_v1_failed.py"),
            "v2_source_sha256": _sha_file(GPU_ROOT / "pyoptix_controls_v2_executed.py"),
            "failure_stage": "after all preregistered output assertions, before result serialization",
            "failure": "CuPy 14 public runtime facade has no getLastError attribute",
            "scientific_source_or_expected_output_changed": False,
            "v1_result_file_emitted": False,
            "v2_create_only_successor_used": True,
        },
        "claim_boundary": {
            "two_designed_matched_tasks_only": True,
            "new_application_generalization_inferred": False,
            "usability_or_productivity_inferred": False,
            "performance_inferred": False,
            "stock_pyoptix_9_1_executed": False,
            "pyoptix_current_source_optix90_compatibility_executed": True,
            "owl_accepted_invalid_execution_claimed": False,
            "loaded_executable_identity_ceiling": "exact PTX module input; opaque driver JIT machine code is not claimed readable",
        },
        "authorization": {
            "goal5797_complete_at_declared_scope": True,
            "goal5798_entry": False,
            "formal_performance_timing": False,
        },
        "registered_performance_timing_count": 0,
    }
    result["result_sha256"] = _sha_bytes(_bytes(result))
    return result


def main() -> int:
    if OUTPUT.exists():
        raise RuntimeError(f"create-only output exists: {OUTPUT}")
    value = build()
    OUTPUT.write_bytes(_pretty(value))
    print(json.dumps({
        "status": value["status"],
        "liveness": value["liveness_pass_count"],
        "necessity": value["semantic_necessity_pass_count"],
        "result_sha256": value["result_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
