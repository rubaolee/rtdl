#!/usr/bin/env python3
"""Build Goal5796's three source-backed responsibility tables."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
OWL_COMMIT = "df7390b16bce5244b7352ca6d3e320f838297072"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_head(path: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"],
        check=True, text=True, capture_output=True).stdout.strip()


def evidence(path: Path, pattern: str, *, root: Path) -> dict[str, object]:
    lines = path.read_text(encoding="utf-8", errors="strict").splitlines()
    matches = [index + 1 for index, line in enumerate(lines) if pattern in line]
    if not matches:
        raise RuntimeError(f"missing source evidence {pattern!r} in {path}")
    return {
        "path": path.relative_to(root).as_posix()
        if path.is_relative_to(root) else str(path),
        "sha256": sha(path), "literal": pattern, "line_numbers": matches,
    }


def cell(owner: str, statement: str, *sources: dict[str, object]) -> dict[str, object]:
    return {"owner": owner, "statement": statement, "sources": list(sources)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--pyoptix", type=Path, required=True)
    parser.add_argument("--owl", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve()
    pyoptix = args.pyoptix.resolve()
    owl = args.owl.resolve()
    if git_head(pyoptix) != PYOPTIX_COMMIT:
        raise RuntimeError("PyOptiX source pin drift")
    if git_head(owl) != OWL_COMMIT:
        raise RuntimeError("OWL source pin drift")

    direct = root / "experiments/goal5796_matched/direct_optix.cpp"
    py_arm = root / "experiments/goal5796_matched/pyoptix_baseline.py"
    device = root / "experiments/goal5796_matched/matched_device.cu"
    public = root / "src/rtdsl/v4_callback_lifecycle.py"
    v4 = root / "src/rtdsl/v4.py"
    py_sphere = pyoptix / "examples/sphere.py"
    py_triangle = pyoptix / "examples/triangle.py"
    owl_impl = owl / "owl/impl.cpp"
    owl_mixed_host = owl / "samples/cmdline/s06-rtow-mixedGeometries/hostCode.cpp"
    owl_mixed_device = owl / "samples/cmdline/s06-rtow-mixedGeometries/deviceCode.cu"

    d_accel = evidence(direct, "optixAccelBuild(", root=root)
    d_pipeline = evidence(direct, "optixPipelineCreate(", root=root)
    d_sbt = evidence(direct, "optixSbtRecordPackHeader", root=root)
    d_launch = evidence(direct, "optixLaunch(", root=root)
    p_accel = evidence(py_sphere, "ctx.accelBuild(", root=root)
    p_pipeline = evidence(py_sphere, "ctx.pipelineCreate(", root=root)
    p_sbt = evidence(py_sphere, "optix.sbtRecordPackHeader", root=root)
    p_launch = evidence(py_sphere, "optix.launch(", root=root)
    o_accel = evidence(owl_impl, "OWL_API void owlGroupBuildAccel", root=root)
    o_pipeline = evidence(owl_impl, "OWL_API void owlBuildPipeline", root=root)
    o_sbt = evidence(owl_impl, "OWL_API void owlBuildSBT", root=root)
    o_launch = evidence(owl_impl, "OWL_API void owlLaunch2D", root=root)
    r_prepare = evidence(public, "def prepare(", root=root)
    r_execute = evidence(public, "def execute(", root=root)
    r_close = evidence(public, "def close(self) -> None:", root=root)

    composition = []
    for responsibility, sources in (
        ("acceleration_structure", (d_accel, p_accel, o_accel, r_prepare)),
        ("program_and_pipeline", (d_pipeline, p_pipeline, o_pipeline, r_prepare)),
        ("shader_binding_table", (d_sbt, p_sbt, o_sbt, r_prepare)),
        ("launch_and_sync", (d_launch, p_launch, o_launch, r_execute)),
    ):
        composition.append({
            "responsibility": responsibility,
            "A_direct": cell("application", "manual CUDA/OptiX host construction", sources[0]),
            "B_pyoptix": cell("application_via_binding", "application calls bound OptiX objects", sources[1]),
            "C_owl": cell("owl_library", "OWL exposes one high-level ownership operation", sources[2]),
            "D_rtdl": cell("rtdl_runtime", "public lifecycle materializes/prepares/executes admitted family", sources[3]),
            "novelty_score_allowed": False,
        })
    composition.append({
        "responsibility": "deterministic_close",
        "A_direct": cell("application_raii", "standalone owner destroys resources", evidence(direct, "~Pipeline()", root=root)),
        "B_pyoptix": cell("application_python_lifetime", "matched Python arm retains all owners through launch", evidence(py_arm, "keepalive", root=root)),
        "C_owl": cell("owl_library_plus_application", "OWL owns objects; application releases context", evidence(owl_mixed_host, "owlContextDestroy", root=root)),
        "D_rtdl": cell("rtdl_public_contract", "public close is idempotent and use-after-close rejects", r_close),
        "novelty_score_allowed": False,
    })

    protocol_sources = {
        "effect": evidence(public, "PL034_PHYSICAL_PLAN_MISMATCH", root=root),
        "abi": evidence(public, "callback_ir_sha256", root=root),
        "physical": evidence(public, "physical_schema_sha256", root=root),
        "status": evidence(public, "PL029_DEVICE_STATUS_INVALID", root=root),
        "identity": evidence(public, "PL028_EXECUTION_IDENTITY_MISMATCH", root=root),
        "cpu": evidence(public, "def interpret(self", root=root),
    }
    manual_payload = evidence(device, "optixGetPayload_0", root=root)
    owl_payload = evidence(owl_mixed_device, "owl::getPRD<PerRayData>", root=root)
    owl_vars = evidence(owl_mixed_host, "OWLVarDecl", root=root)
    protocol = []
    descriptions = {
        "role_effect_closure": "declared producers/consumers and continuation effects close across roles",
        "payload_attribute_semantic_ownership": "slot width, meaning, owner, producer and consumer agree",
        "physical_geometry_binding": "callback assumptions match physical geometry and wrapper projection",
        "device_status_before_consume": "failed/incomplete device status prevents application result exposure",
        "checked_program_executable_identity": "launched executable is the checked program projection",
    }
    for name, statement in descriptions.items():
        r_source = protocol_sources[
            {"role_effect_closure": "effect",
             "payload_attribute_semantic_ownership": "abi",
             "physical_geometry_binding": "physical",
             "device_status_before_consume": "status",
             "checked_program_executable_identity": "identity"}[name]]
        protocol.append({
            "responsibility": name,
            "statement": statement,
            "A_direct": cell("application_convention", "no baseline static protocol checker", manual_payload),
            "B_pyoptix": cell("application_convention", "binding exposes mechanisms; matched arm declares no cross-role checker", manual_payload, evidence(py_arm, "build_pipeline", root=root)),
            "C_owl": cell("application_convention_after_composition", "OWL variables/composition do not by themselves establish this residual semantic contract", owl_vars, owl_payload),
            "D_rtdl": cell("compiler_or_public_runtime", "checked for the admitted public family", r_source),
            "owl_execution_attack_still_required": True,
        })
    protocol.append({
        "responsibility": "cpu_reference_from_same_public_program",
        "statement": "CPU and GPU routes accept the same RTDL program identity; correctness still uses an independent oracle",
        "A_direct": cell("matched_experiment", "separate independent oracle maintained outside device source", evidence(root / "experiments/goal5796_matched/independent_oracle.py", "imports none of the A/B/C/D", root=root)),
        "B_pyoptix": cell("matched_experiment", "separate independent oracle; PyOptiX supplies no task oracle", evidence(py_triangle, "import optix", root=root)),
        "C_owl": cell("matched_experiment", "analysed-only arm has no task CPU interpreter", evidence(owl_mixed_host, "owlBuildPrograms", root=root)),
        "D_rtdl": cell("rtdl_public_program_plus_independent_oracle", "public verified program supplies CPU interpretation and the experiment retains a route-independent oracle", protocol_sources["cpu"], evidence(v4, "VerifiedProtocolProgram", root=root)),
        "static_theorem_claimed": False,
    })

    device_language = [
        {
            "task": "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1",
            "A_direct": "CUDA_CPP_NVRTC",
            "B_pyoptix": "PYTHON_HOST_PLUS_CUDA_CPP_NVRTC_CUSTOM_INTERSECTION",
            "C_owl": "CPP_HOST_PLUS_CUDA_CPP_DEVICE__ANALYSED_NOT_IMPLEMENTED",
            "D_rtdl": "RESTRICTED_CALLBACK_SOURCE_TO_GENERATED_PTX",
        },
        {
            "task": "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1",
            "A_direct": "CUDA_CPP_NVRTC",
            "B_pyoptix": "PYTHON_HOST_PLUS_CUDA_CPP_NVRTC",
            "C_owl": "CPP_HOST_PLUS_CUDA_CPP_DEVICE__ANALYSED_NOT_IMPLEMENTED",
            "D_rtdl": "RESTRICTED_CALLBACK_SOURCE_TO_GENERATED_PTX",
        },
    ]

    validation_policy = {
        "public_input_classes": [
            {"class": "protocol_plan_proof", "consequence": "semantic_and_admission", "policy": "fail_closed"},
            {"class": "target_toolchain_native", "consequence": "executable_identity", "policy": "fail_closed"},
            {"class": "static_geometry_and_resource_capacity", "consequence": "execution_and_output", "policy": "fail_closed"},
            {"class": "dynamic_queries_weights_expected_output", "consequence": "execution_and_result", "policy": "fail_closed"},
            {"class": "primitive_or_query_metadata", "consequence": "declared_task_semantics", "policy": "fail_closed"},
            {"class": "lifecycle_and_traversal_diagnostics", "consequence": "output_observation_only", "policy": "output_only_not_an_input_degradation_channel"},
        ],
        "optional_public_input_metadata_channel_exists": False,
        "graceful_degradation_implemented_for_v4_input": False,
        "reason": "no actual optional public V4 input exists; adding one would manufacture favorable evidence",
        "x3_harvester_is_separate": True,
    }

    remains_application_owned = [
        "problem_to_ray_and_geometry_mapping", "algorithm", "semantic_oracle",
        "input_data", "precision_choice", "tie_and_duplicate_policy",
        "resource_budget", "trusted_physical_partner_declarations",
    ]
    historical_audit_path = root / (
        "history/internal_docs/"
        "goal5792_source_backed_responsibility_audit_result_v3_20260820.json")
    historical_audit = json.loads(historical_audit_path.read_bytes())
    if historical_audit.get("summary", {}).get("application_count") != 9:
        raise RuntimeError("Goal5792 nine-application audit denominator drift")
    application_table = []
    for row in historical_audit["rows"]:
        application_table.append({
            "application": row["app"],
            "paper_algorithm": row["paper_algorithm"],
            "application_owned": row["application_owned_responsibilities"],
            "system_owned": row["system_owned_responsibilities"],
            "trusted_partner_boundary": row["trusted_partner_boundary"],
            "historical_v4_source": row["v4_application_site"],
            "historical_native_loader_behind_registered_interface": row[
                "native_runtime_loading_behind_registered_v4_interface"],
            "historical_native_loader_exception": row[
                "native_runtime_loading_exception"],
            "historical_evidence_only_not_matched_generalization": True,
            "developer_task_or_productivity_measurement": False,
        })
    exceptions = [
        row["application"] for row in application_table
        if row["historical_native_loader_exception"] is not None
    ]
    if exceptions != ["raydb"]:
        raise RuntimeError(f"historical private-loader exceptions drifted: {exceptions!r}")
    result = {
        "schema": "rtdl.goal5796.source_backed_responsibility.v1",
        "status": "PASS",
        "source_pins": {
            "pyoptix_commit": PYOPTIX_COMMIT, "owl_commit": OWL_COMMIT,
            "pyoptix_tree": subprocess.run(
                ["git", "-C", str(pyoptix), "rev-parse", "HEAD^{tree}"],
                check=True, text=True, capture_output=True).stdout.strip(),
            "owl_tree": subprocess.run(
                ["git", "-C", str(owl), "rev-parse", "HEAD^{tree}"],
                check=True, text=True, capture_output=True).stdout.strip(),
        },
        "composition_ownership": composition,
        "protocol_contract_ownership": protocol,
        "device_language_path": device_language,
        "validation_policy": validation_policy,
        "remains_application_owned": remains_application_owned,
        "historical_application_table": application_table,
        "historical_application_table_authority": {
            "path": historical_audit_path.relative_to(root).as_posix(),
            "sha256": sha(historical_audit_path),
            "application_count": 9,
            "native_loader_encapsulation_count": 8,
            "raydb_private_loader_exception_visible_in_row": True,
            "matched_task_or_generalization_evidence": False,
        },
        "owl_arm_status": "ANALYSED_NOT_IMPLEMENTED",
        "owl_performance_claim_allowed": False,
        "usability_or_productivity_inference_allowed": False,
        "registered_performance_timing_count": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
