"""Independent verifier for Goal5797; deliberately imports no RTDL module."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[1]
PREACTION = ROOT / "history/internal_docs/goal5797_s0_five_mechanism_ablation_preaction_20260823.json"
GPU_ROOT = ROOT / "history/internal_docs/goal5797_gpu_evidence_20260823"
GPU = GPU_ROOT / "GOAL5797_PYOPTIX_CONTROLS.json"
RESULT = ROOT / "history/internal_docs/goal5797_five_mechanism_liveness_and_necessity_result_20260823.json"
OWL = ROOT / "history/internal_docs/goal5797_owl_source_responsibility_and_goal5794_tree_correction_20260823.json"
BASE_SOURCE = ROOT / "experiments/goal5796_matched/matched_device.cu"
PTX_RECOUNT = GPU_ROOT / "GOAL5797_INDEPENDENT_PTX_RECOMPILE.json"
OUTPUT = ROOT / "history/internal_docs/goal5797_independent_verification_20260823.json"


REASONS = {
    "role_effect_closure": "CP001_ROLE_EFFECT_MISMATCH",
    "payload_attribute_abi_ownership": "CP002_ATTRIBUTE_ABI_OWNERSHIP_MISMATCH",
    "physical_geometry_binding": "CP003_PHYSICAL_BINDING_MISMATCH",
    "device_status_continuation": "CP004_CONTINUATION_STATUS_MISMATCH",
    "checked_program_executable_identity": "CP005_EXECUTABLE_IDENTITY_MISMATCH",
}


def canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode()


def sha(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def load(path: Path):
    return json.loads(path.read_bytes())


def verify_seal(value, field):
    body = dict(value)
    observed = body.pop(field)
    if sha(canonical(body)) != observed:
        raise RuntimeError(f"seal mismatch: {field}")


def independent_variants(base: bytes) -> dict[str, bytes]:
    text = base.decode()
    variants = {"valid_a": text}
    old = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixIgnoreIntersection();\n}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}")
    new = (
        "    set_payload_u64(before + 1ull);\n"
        "    optixTerminateRay();\n}\n\n"
        "extern \"C\" __global__ void __miss__goal5796_triangle() {}")
    if text.count(old) != 1:
        raise RuntimeError("effects anchor")
    variants["role_effect_closure"] = text.replace(old, new, 1)
    old = "optixReportIntersection(0.0f, 0u, item.item_id);"
    if text.count(old) != 1:
        raise RuntimeError("ABI anchor")
    variants["payload_attribute_abi_ownership"] = text.replace(
        old, "optixReportIntersection(0.0f, 0u, primitive_index);", 1)
    anchor = "extern \"C\" __global__ void __raygen__goal5796_relation() {"
    helper = r'''static __forceinline__ __device__ Box goal5797_swap_xy(Box value) {
    const float lower_x = value.lower_x;
    const float upper_x = value.upper_x;
    value.lower_x = value.lower_y;
    value.lower_y = lower_x;
    value.upper_x = value.upper_y;
    value.upper_y = upper_x;
    return value;
}

extern "C" __global__ void __raygen__goal5796_relation() {'''
    physical = text.replace(anchor, helper, 1)
    query = "const Box query = params.queries[query_index];"
    if physical.count(query) != 2:
        raise RuntimeError("physical anchors")
    variants["physical_geometry_binding"] = physical.replace(
        query, "const Box query = goal5797_swap_xy(params.queries[query_index]);")
    old = "set_payload_u64(before + 1ull);"
    if text.count(old) != 1:
        raise RuntimeError("identity anchor")
    variants["checked_program_executable_identity"] = text.replace(
        old, "set_payload_u64(before + 2ull);", 1)
    return {key: value.encode() for key, value in variants.items()}


def mismatches(contract, projection):
    checks = [
        ("physical_geometry_binding",
         (contract["family"], contract["task_semantics_sha256"], contract["physical_bindings"]),
         (projection["family"], projection["task_semantics_sha256"], projection["physical_bindings"])),
        ("role_effect_closure", contract["role_effects"], projection["role_effects"]),
        ("payload_attribute_abi_ownership", contract["attribute_abi_ownership"], projection["attribute_abi_ownership"]),
        ("device_status_continuation", contract["continuation_policy"], projection["continuation_policy"]),
        ("checked_program_executable_identity", contract["checked_executable_sha256"], projection["actual_executable_sha256"]),
    ]
    return [name for name, left, right in checks if canonical(left) != canonical(right)]


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--owl-root", type=Path)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError(args.output)
    preaction_bytes = PREACTION.read_bytes()
    gpu_bytes = GPU.read_bytes()
    result_bytes = RESULT.read_bytes()
    preaction, gpu, result, owl = map(load, (PREACTION, GPU, RESULT, OWL))
    verify_seal(result, "result_sha256")
    if result["preaction"]["sha256"] != sha(preaction_bytes) \
            or result["gpu_evidence"]["sha256"] != sha(gpu_bytes):
        raise RuntimeError("root identity mismatch")
    if gpu["baseline_runtime"]["optix_validation"] != "PASS" \
            or gpu["baseline_runtime"]["cuda_last_error"] != "SUCCESS":
        raise RuntimeError("GPU diagnostics not clean")

    generated = independent_variants(BASE_SOURCE.read_bytes())
    source_rows = []
    for name, payload in sorted(generated.items()):
        path = GPU_ROOT / "gpu_evidence/device_sources" / f"{name}.cu"
        actual = path.read_bytes()
        expected_sha = gpu["identities"][name]["device_source_sha256"]
        if payload != actual or sha(actual) != expected_sha:
            raise RuntimeError(f"variant mismatch: {name}")
        source_rows.append({
            "name": name, "bytes": len(actual), "sha256": sha(actual),
            "independently_regenerated_byte_identical": True,
        })

    matrix_rows = []
    for row in result["rows"]:
        mechanism = row["mechanism"]
        if row["expected_reason"] != REASONS[mechanism]:
            raise RuntimeError(f"reason mismatch: {mechanism}")
        liveness_contract = row["liveness"]["mutated_contract"]
        behavior_contract = row["semantic_necessity"]["invalid_contract"]
        behavior_projection = row["semantic_necessity"]["actual_projection"]
        verify_seal(liveness_contract, "contract_sha256")
        verify_seal(behavior_contract, "contract_sha256")
        verify_seal(behavior_projection, "projection_sha256")
        # Independently reconstruct the nearby-valid projection.  Its five
        # semantic fields are exactly the valid declaration; source hashes do
        # not participate in the comparison, while actual executable identity
        # equals the declaration's checked identity.
        valid_projection = {
            "family": behavior_contract["family"],
            "task_semantics_sha256": behavior_contract["task_semantics_sha256"],
            "role_effects": behavior_contract["role_effects"],
            "attribute_abi_ownership": behavior_contract["attribute_abi_ownership"],
            "physical_bindings": behavior_contract["physical_bindings"],
            "continuation_policy": behavior_contract["continuation_policy"],
            "actual_executable_sha256": (
                behavior_contract["checked_executable_sha256"]
                if mechanism == "checked_program_executable_identity"
                else liveness_contract["checked_executable_sha256"]
            ),
        }
        if mismatches(liveness_contract, valid_projection) != [mechanism]:
            raise RuntimeError(f"liveness mismatch set: {mechanism}")
        if mismatches(behavior_contract, behavior_projection) != [mechanism]:
            raise RuntimeError(f"behavior mismatch set: {mechanism}")
        verify_seal(row["liveness"]["decision"], "decision_sha256")
        verify_seal(
            row["semantic_necessity"]["full_decision"], "decision_sha256")
        finding = row["semantic_necessity"]["full_decision"]["findings"]
        if len(finding) != 1 or finding[0]["mechanism"] != mechanism \
                or finding[0]["reason_id"] != REASONS[mechanism]:
            raise RuntimeError(f"stored finding mismatch: {mechanism}")
        if row["liveness"]["decision"]["verdict"] != "REJECT" \
                or row["semantic_necessity"]["full_decision"]["verdict"] != "REJECT" \
                or row["liveness"]["only_this_mechanism_ablated_verdict"] != "ACCEPT" \
                or row["semantic_necessity"]["only_this_mechanism_ablated_verdict"] != "ACCEPT":
            raise RuntimeError(f"verdict mismatch: {mechanism}")
        matrix_rows.append({"mechanism": mechanism, "passed": True})

    prereg = {row["id"]: row for row in preaction["mechanisms"]}
    controls = gpu["behavioral_controls"]
    observed = {
        "role_effect_closure": controls["role_effect_closure"]["output"],
        "payload_attribute_abi_ownership": controls["payload_attribute_abi_ownership"]["output"],
        "physical_geometry_binding": controls["physical_geometry_binding"]["output"],
        "checked_program_executable_identity": controls["checked_program_executable_identity"]["output"],
    }
    for name, value in observed.items():
        expected = prereg[name].get("expected_invalid_output")
        if value != expected:
            raise RuntimeError(f"preregistered output mismatch: {name}")
    status = controls["device_status_continuation"]
    expected_status = prereg["device_status_continuation"]["expected_invalid_invariant"]
    for key, expected in expected_status.items():
        if status.get(key) != expected:
            raise RuntimeError(f"status invariant mismatch: {key}")

    owl_rehashed = None
    if args.owl_root:
        head = subprocess.run(
            ["git", "-C", str(args.owl_root), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip()
        tree = subprocess.run(
            ["git", "-C", str(args.owl_root), "rev-parse", "HEAD^{tree}"],
            check=True, capture_output=True, text=True).stdout.strip()
        if head != owl["repository_commit"] or tree != owl["repository_tree"]:
            raise RuntimeError("OWL git identity mismatch")
        for item in owl["selected_source_files"]:
            payload = (args.owl_root / item["path"]).read_bytes()
            if len(payload) != item["bytes"] or sha(payload) != item["sha256"]:
                raise RuntimeError(f"OWL file mismatch: {item['path']}")
        owl_rehashed = len(owl["selected_source_files"])

    ptx = load(PTX_RECOUNT)
    if ptx["status"] != "PASS" or ptx["byte_identical_ptx_count"] != 5:
        raise RuntimeError("independent PTX recount missing")
    out = {
        "schema": "rtdl.goal5797.independent_verification.v1",
        "status": "PASS",
        "imports_rtdl": False,
        "preaction_sha256": sha(preaction_bytes),
        "gpu_result_sha256": sha(gpu_bytes),
        "result_file_sha256": sha(result_bytes),
        "variant_source_rows": source_rows,
        "variant_source_byte_identical_count": len(source_rows),
        "ptx_independent_recompile_sha256": sha(PTX_RECOUNT.read_bytes()),
        "ptx_byte_identical_count": 5,
        "matrix_rows": matrix_rows,
        "liveness_pass_count": 5,
        "semantic_necessity_pass_count": 5,
        "owl_selected_files_rehashed": owl_rehashed,
        "registered_performance_timing_count": 0,
    }
    args.output.write_bytes(json.dumps(out, indent=2, sort_keys=True).encode() + b"\n")
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
