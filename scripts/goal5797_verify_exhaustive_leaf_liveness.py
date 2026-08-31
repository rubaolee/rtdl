"""Independent, no-RTDL verifier for Goal5797-A1 leaf liveness."""

from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREACTION = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_preaction_20260823.json")
GPU = ROOT / (
    "history/internal_docs/goal5797_gpu_evidence_20260823/"
    "GOAL5797_PYOPTIX_CONTROLS.json")
RESULT = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_result_20260823.json")
DEFAULT_OUTPUT = ROOT / (
    "history/internal_docs/"
    "goal5797_a1_exhaustive_populated_leaf_liveness_independent_verification_20260823.json")


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def seal(mapping: dict[str, object], field: str) -> None:
    body = dict(mapping)
    observed = body.pop(field)
    if sha(canonical(body)) != observed:
        raise RuntimeError(f"seal mismatch: {field}")


def contract(
    *, family: str, task_sha: str, effects, attribute, physical,
    continuation: str, executable: str,
) -> dict[str, object]:
    body = {
        "schema": "rtdl.v4.callback_protocol_contract.v1",
        "family": family,
        "task_semantics_sha256": task_sha,
        "role_effects": effects,
        "attribute_abi_ownership": attribute,
        "physical_bindings": physical,
        "continuation_policy": continuation,
        "checked_executable_sha256": executable,
    }
    return {**body, "contract_sha256": sha(canonical(body))}


def projection(base: dict[str, object], *, device_sha: str, host_sha: str):
    body = {
        "schema": "rtdl.v4.compiler_protocol_projection.v1",
        "family": base["family"],
        "task_semantics_sha256": base["task_semantics_sha256"],
        "role_effects": deepcopy(base["role_effects"]),
        "attribute_abi_ownership": deepcopy(base["attribute_abi_ownership"]),
        "physical_bindings": deepcopy(base["physical_bindings"]),
        "continuation_policy": base["continuation_policy"],
        "actual_executable_sha256": base["checked_executable_sha256"],
        "generated_device_source_sha256": device_sha,
        "generated_host_source_sha256": host_sha,
    }
    return {**body, "projection_sha256": sha(canonical(body))}


def baselines(gpu: dict[str, object]):
    task_sha = gpu["semantic_spec_sha256"]
    host_sha = gpu["host_control_source_sha256"]
    valid = gpu["identities"]["valid_a"]
    executable = valid["loaded_ptx_sha256"]
    device = valid["device_source_sha256"]
    triangle = contract(
        family="builtin_triangle_reduction_v1", task_sha=task_sha,
        effects={
            "any_hit": ["accept_continue", "payload_write"],
            "finalize": ["checked_u64_reduce", "require_status_ok"],
        }, attribute={}, physical={
            "gas": "builtin_triangle_vertices_f32x3",
            "ray.direction": "host.query.direction_f32x3",
            "ray.origin": "host.query.origin_f32x3",
        }, continuation="REQUIRE_COMPLETE_BEFORE_CONSUME",
        executable=executable)
    relation = contract(
        family="custom_aabb_bounded_relation_v1", task_sha=task_sha,
        effects={
            "any_hit": ["accept_continue", "emit_relation_row"],
            "intersection": ["report_application_item_id"],
        }, attribute={"attr0": "application_item_id_u32"}, physical={
            "query.lower.x": "host.query.lower.x",
            "query.lower.y": "host.query.lower.y",
            "query.upper.x": "host.query.upper.x",
            "query.upper.y": "host.query.upper.y",
        }, continuation="REQUIRE_COMPLETE_BEFORE_CONSUME",
        executable=executable)
    return {
        triangle["family"]: (triangle, projection(
            triangle, device_sha=device, host_sha=host_sha)),
        relation["family"]: (relation, projection(
            relation, device_sha=device, host_sha=host_sha)),
    }


def semantic_differences(left: dict[str, object], right: dict[str, object]):
    differences = []
    for key in (
        "family", "task_semantics_sha256", "role_effects",
        "attribute_abi_ownership", "physical_bindings",
        "continuation_policy", "checked_executable_sha256",
    ):
        if left[key] != right[key]:
            differences.append(key)
    return differences


def expected_reason(differences: list[str]) -> str:
    if differences == ["role_effects"]:
        return "CP001_ROLE_EFFECT_MISMATCH"
    if differences == ["attribute_abi_ownership"]:
        return "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH"
    if differences in (["physical_bindings"], ["family"],
                       ["task_semantics_sha256"]):
        return "CP003_PHYSICAL_BINDING_MISMATCH"
    if differences == ["continuation_policy"]:
        return "CP004_CONTINUATION_STATUS_MISMATCH"
    if differences == ["checked_executable_sha256"]:
        return "CP005_EXECUTABLE_IDENTITY_MISMATCH"
    raise RuntimeError(f"unexpected semantic difference set: {differences!r}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    preaction_bytes = PREACTION.read_bytes()
    gpu_bytes = GPU.read_bytes()
    result_bytes = RESULT.read_bytes()
    preaction = json.loads(preaction_bytes)
    gpu = json.loads(gpu_bytes)
    result = json.loads(result_bytes)
    if result["preaction"]["sha256"] != sha(preaction_bytes) \
            or result["baseline_gpu_result"]["sha256"] != sha(gpu_bytes):
        raise RuntimeError("input identity mismatch")
    result_body = dict(result)
    result_digest = result_body.pop("result_sha256")
    if sha(canonical(result_body)) != result_digest:
        raise RuntimeError("result digest mismatch")
    baseline = baselines(gpu)
    preaction_set = {
        (row["contract"], row["path"]) for row in preaction["mutations"]
    }
    result_set = {(row["contract"], row["path"]) for row in result["rows"]}
    if preaction_set != result_set or len(result_set) != 19:
        raise RuntimeError("leaf universe mismatch")

    rows = []
    for row in result["rows"]:
        base_contract, base_projection = baseline[row["contract"]]
        mutated = row["mutated_contract"]
        decision = row["decision"]
        seal(mutated, "contract_sha256")
        seal(decision, "decision_sha256")
        seal(base_projection, "projection_sha256")
        if row["projection_sha256"] != sha(canonical(base_projection)):
            raise RuntimeError(f"projection changed: {row['path']}")
        differences = semantic_differences(mutated, base_contract)
        reason = expected_reason(differences)
        findings = decision["findings"]
        if decision["verdict"] != "REJECT" or len(findings) != 1 \
                or findings[0]["reason_id"] != reason \
                or row["expected_reason"] != reason \
                or row["verdict_delta"] != "ACCEPT_TO_REJECT" \
                or row["classification"] != "DECISION_BEARING":
            raise RuntimeError(f"decision mismatch: {row['path']}")
        rows.append({
            "contract": row["contract"],
            "path": row["path"],
            "reason": reason,
            "passed": True,
        })

    status = next(
        row for row in rows
        if row["contract"] == "builtin_triangle_reduction_v1"
        and row["path"] == "role_effects.finalize[1]")
    output = {
        "schema": (
            "rtdl.goal5797.a1.exhaustive_populated_leaf_liveness_"
            "independent_verification.v1"),
        "status": "PASS",
        "imports_rtdl": False,
        "preaction_sha256": sha(preaction_bytes),
        "gpu_result_sha256": sha(gpu_bytes),
        "result_file_sha256": sha(result_bytes),
        "leaf_universe_count": len(rows),
        "decision_bearing_count": sum(row["passed"] for row in rows),
        "non_decision_bearing_count": 0,
        "single_expected_finding_count": sum(row["passed"] for row in rows),
        "projection_bytes_unchanged_count": sum(row["passed"] for row in rows),
        "require_status_ok_decision_bearing": status["passed"],
        "rows": rows,
        "registered_performance_timing_count": 0,
    }
    args.output.write_bytes(json.dumps(
        output, indent=2, sort_keys=True, allow_nan=False,
    ).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": output["status"],
        "leaves": output["leaf_universe_count"],
        "require_status_ok": output["require_status_ok_decision_bearing"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
