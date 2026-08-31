"""Build Goal5797-A1 exhaustive populated-leaf liveness evidence."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re

from rtdsl.v4_protocol_contract import (
    CompilerProtocolProjection,
    ProtocolContractDeclaration,
    verify_protocol_contract,
)


ROOT = Path(__file__).resolve().parents[1]
PREACTION = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_preaction_20260823.json")
GPU = ROOT / (
    "history/internal_docs/goal5797_gpu_evidence_20260823/"
    "GOAL5797_PYOPTIX_CONTROLS.json")
OUTPUT = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def file_sha(path: Path) -> str:
    return digest(path.read_bytes())


def declaration(
    *, family: str, task_sha: str, effects: dict[str, tuple[str, ...]],
    attribute: dict[str, str], physical: dict[str, str], continuation: str,
    executable: str,
) -> ProtocolContractDeclaration:
    return ProtocolContractDeclaration(
        family=family,
        task_semantics_sha256=task_sha,
        role_effects=tuple(sorted(
            (key, tuple(sorted(values))) for key, values in effects.items())),
        attribute_abi_ownership=tuple(sorted(attribute.items())),
        physical_bindings=tuple(sorted(physical.items())),
        continuation_policy=continuation,
        checked_executable_sha256=executable,
    )


def projection(
    contract: ProtocolContractDeclaration, *, device_sha: str, host_sha: str,
) -> CompilerProtocolProjection:
    return CompilerProtocolProjection(
        family=contract.family,
        task_semantics_sha256=contract.task_semantics_sha256,
        role_effects=contract.role_effects,
        attribute_abi_ownership=contract.attribute_abi_ownership,
        physical_bindings=contract.physical_bindings,
        continuation_policy=contract.continuation_policy,
        actual_executable_sha256=contract.checked_executable_sha256,
        generated_device_source_sha256=device_sha,
        generated_host_source_sha256=host_sha,
    )


def baselines(gpu: dict[str, object]):
    task_sha = str(gpu["semantic_spec_sha256"])
    host_sha = str(gpu["host_control_source_sha256"])
    valid = gpu["identities"]["valid_a"]
    executable = str(valid["loaded_ptx_sha256"])
    device = str(valid["device_source_sha256"])
    complete = "REQUIRE_COMPLETE_BEFORE_CONSUME"
    triangle = declaration(
        family="builtin_triangle_reduction_v1", task_sha=task_sha,
        effects={
            "any_hit": ("accept_continue", "payload_write"),
            "finalize": ("checked_u64_reduce", "require_status_ok"),
        },
        attribute={},
        physical={
            "gas": "builtin_triangle_vertices_f32x3",
            "ray.direction": "host.query.direction_f32x3",
            "ray.origin": "host.query.origin_f32x3",
        },
        continuation=complete, executable=executable,
    )
    relation = declaration(
        family="custom_aabb_bounded_relation_v1", task_sha=task_sha,
        effects={
            "any_hit": ("accept_continue", "emit_relation_row"),
            "intersection": ("report_application_item_id",),
        },
        attribute={"attr0": "application_item_id_u32"},
        physical={
            "query.lower.x": "host.query.lower.x",
            "query.lower.y": "host.query.lower.y",
            "query.upper.x": "host.query.upper.x",
            "query.upper.y": "host.query.upper.y",
        },
        continuation=complete, executable=executable,
    )
    return {
        triangle.family: (triangle, projection(
            triangle, device_sha=device, host_sha=host_sha)),
        relation.family: (relation, projection(
            relation, device_sha=device, host_sha=host_sha)),
    }


def populated_paths(mapping: dict[str, object]) -> set[str]:
    result = {"continuation_policy", "checked_executable_sha256"}
    for root in ("attribute_abi_ownership", "physical_bindings"):
        result.update(f"{root}.{key}" for key in mapping[root])
    for role, values in mapping["role_effects"].items():
        result.update(
            f"role_effects.{role}[{index}]"
            for index in range(len(values)))
    return result


_LIST_PATH = re.compile(r"^(role_effects)\.([^\[]+)\[(\d+)\]$")


def replace_leaf(
    mapping: dict[str, object], *, path: str, expected: object,
    replacement: object,
) -> tuple[object, object]:
    list_match = _LIST_PATH.fullmatch(path)
    if list_match:
        root, key, raw_index = list_match.groups()
        index = int(raw_index)
        values = mapping[root][key]
        observed = values[index]
        if observed != expected:
            raise RuntimeError(
                f"old value mismatch at {path}: {observed!r} != {expected!r}")
        values[index] = replacement
        return observed, values[index]
    if "." in path:
        root, key = path.split(".", 1)
        observed = mapping[root][key]
        if observed != expected:
            raise RuntimeError(
                f"old value mismatch at {path}: {observed!r} != {expected!r}")
        mapping[root][key] = replacement
        return observed, mapping[root][key]
    observed = mapping[path]
    if observed != expected:
        raise RuntimeError(
            f"old value mismatch at {path}: {observed!r} != {expected!r}")
    mapping[path] = replacement
    return observed, mapping[path]


def from_mapping(mapping: dict[str, object]) -> ProtocolContractDeclaration:
    return ProtocolContractDeclaration(
        family=mapping["family"],
        task_semantics_sha256=mapping["task_semantics_sha256"],
        role_effects=tuple(
            (key, tuple(values))
            for key, values in sorted(mapping["role_effects"].items())),
        attribute_abi_ownership=tuple(sorted(
            mapping["attribute_abi_ownership"].items())),
        physical_bindings=tuple(sorted(mapping["physical_bindings"].items())),
        continuation_policy=mapping["continuation_policy"],
        checked_executable_sha256=mapping["checked_executable_sha256"],
    )


def build() -> dict[str, object]:
    preaction_bytes = PREACTION.read_bytes()
    gpu_bytes = GPU.read_bytes()
    preaction = json.loads(preaction_bytes)
    gpu = json.loads(gpu_bytes)
    if preaction["status"] != "FROZEN_BEFORE_FIRST_EXHAUSTIVE_LEAF_SWEEP":
        raise RuntimeError("preaction is not frozen")
    if preaction["authorization"] != {
        "formal_performance_timing": False,
        "goal5798_execution": False,
        "gpu_execution": False,
        "in_process_leaf_sweep_only": True,
    }:
        raise RuntimeError("preaction authorization changed")
    by_family = baselines(gpu)
    declared_rows = {
        (row["contract"], row["path"]) for row in preaction["mutations"]
    }
    discovered_rows = {
        (family, path)
        for family, (contract, _) in by_family.items()
        for path in populated_paths(contract.to_mapping())
    }
    if declared_rows != discovered_rows:
        raise RuntimeError(
            f"preaction leaf universe mismatch: missing="
            f"{sorted(discovered_rows - declared_rows)!r}, extra="
            f"{sorted(declared_rows - discovered_rows)!r}")

    rows = []
    for item in preaction["mutations"]:
        contract, fixed_projection = by_family[item["contract"]]
        baseline = verify_protocol_contract(contract, fixed_projection)
        if baseline.verdict != "ACCEPT" or baseline.findings:
            raise RuntimeError(f"baseline rejected: {item['contract']}")
        projection_before = canonical(fixed_projection.to_mapping())
        mapping = deepcopy(contract.to_mapping())
        mapping.pop("contract_sha256")
        if item["path"] == "checked_executable_sha256":
            expected = mapping[item["path"]]
            replacement = digest(
                item["mutation_sha256_of_utf8"].encode("utf-8"))
        else:
            expected = item["expected_old"]
            replacement = item["mutation"]
        old, new = replace_leaf(
            mapping, path=item["path"], expected=expected,
            replacement=replacement)
        mutated = from_mapping(mapping)
        decision = verify_protocol_contract(mutated, fixed_projection)
        projection_after = canonical(fixed_projection.to_mapping())
        decision_bearing = decision.verdict == "REJECT"
        reason_ids = [finding.reason_id for finding in decision.findings]
        if not decision_bearing \
                or reason_ids != [item["expected_reason"]] \
                or projection_before != projection_after:
            raise RuntimeError(
                f"leaf liveness failed: {item['contract']} {item['path']} "
                f"verdict={decision.verdict} reasons={reason_ids!r}")
        rows.append({
            "contract": item["contract"],
            "path": item["path"],
            "old_value": old,
            "mutated_value": new,
            "baseline_verdict": "ACCEPT",
            "mutated_verdict": decision.verdict,
            "verdict_delta": "ACCEPT_TO_REJECT",
            "decision_bearing": True,
            "classification": "DECISION_BEARING",
            "expected_reason": item["expected_reason"],
            "finding_count": len(decision.findings),
            "reason_ids": reason_ids,
            "projection_bytes_unchanged": True,
            "projection_sha256": digest(projection_before),
            "mutated_contract": mutated.to_mapping(),
            "decision": decision.to_mapping(),
        })

    result = {
        "schema": "rtdl.goal5797.a1.exhaustive_populated_leaf_liveness.v1",
        "status": "PASS",
        "date": "2026-08-23",
        "preaction": {
            "path": PREACTION.relative_to(ROOT).as_posix(),
            "bytes": len(preaction_bytes),
            "sha256": digest(preaction_bytes),
            "frozen_before_sweep": True,
        },
        "baseline_gpu_result": {
            "path": GPU.relative_to(ROOT).as_posix(),
            "bytes": len(gpu_bytes),
            "sha256": digest(gpu_bytes),
            "executed_again": False,
        },
        "contracts": sorted(by_family),
        "populated_leaf_count": len(discovered_rows),
        "pre_registered_leaf_count": len(declared_rows),
        "leaf_universe_set_identical": True,
        "decision_bearing_count": sum(row["decision_bearing"] for row in rows),
        "non_decision_bearing_count": sum(
            not row["decision_bearing"] for row in rows),
        "projection_bytes_unchanged_count": sum(
            row["projection_bytes_unchanged"] for row in rows),
        "single_expected_finding_count": sum(
            row["finding_count"] == 1
            and row["reason_ids"] == [row["expected_reason"]]
            for row in rows),
        "require_status_ok": next(
            row for row in rows
            if row["contract"] == "builtin_triangle_reduction_v1"
            and row["path"] == "role_effects.finalize[1]"),
        "rows": rows,
        "claim": {
            "every_populated_nonidentity_semantic_leaf_decision_bearing": True,
            "family_task_and_seal_identity_fields_excluded": True,
            "semantic_necessity_inferred_for_new_leaves": False,
            "gpu_or_performance_inferred": False,
        },
        "authorization": {
            "goal5797_p1_1_closeable": True,
            "goal5798_execution": False,
            "formal_performance_timing": False,
        },
        "registered_performance_timing_count": 0,
    }
    result["result_sha256"] = digest(canonical(result))
    return result


def main() -> int:
    if OUTPUT.exists():
        raise FileExistsError(f"create-only output exists: {OUTPUT}")
    value = build()
    OUTPUT.write_bytes(json.dumps(
        value, indent=2, sort_keys=True, allow_nan=False,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": value["status"],
        "leaves": value["populated_leaf_count"],
        "decision_bearing": value["decision_bearing_count"],
        "result_sha256": value["result_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
