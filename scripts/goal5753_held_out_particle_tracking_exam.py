#!/usr/bin/env python3
"""Run the frozen-core Goal5753 held-out particle-tracking exam.

This program never invokes a GPU runtime.  The selected application reaches
the frozen Callback IR and ABI, then must fail closed at the independently
checked physical geometry/runtime boundary.  The failure is the registered
Goal5753 outcome; it is not repaired in place.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


SELECTED_ID = "Wang2022AnGP::particle_tracking"
AUTHOR_COMMIT = "5cfe63fed227c238905a8f24082b59b5d3160966"
FROZEN_SOURCE_SHA256 = "96dd2398f3e438b43320ca076ffaf3b74647bcb6095260877278741920741a33"
FROZEN_NATIVE_SHA256 = "d790104ee042967d5e5dc73c4ddcf4f1af312170e7f701ff3a779bbb092e1154"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def require_tokens(path: Path, tokens: tuple[str, ...]) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    missing = [token for token in tokens if token not in text]
    if missing:
        raise RuntimeError(f"source audit failed for {path}: {missing}")
    return {
        "sha256": sha256_file(path),
        "required_token_count": len(tokens),
        "missing_tokens": missing,
    }


def audit_author_source(author: Path) -> dict[str, Any]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=author, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=author, check=True,
        capture_output=True, text=True,
    ).stdout.strip()
    if commit != AUTHOR_COMMIT or dirty:
        raise RuntimeError(f"author source identity mismatch: commit={commit}, dirty={dirty!r}")

    files = {
        "optix/optixQueryKernel.cu": (
            "OPTIX_CLOSEST_HIT_PROGRAM(sharedFacesCH)",
            "optixGetPrimitiveIndex()",
            "OPTIX_HIT_KIND_TRIANGLE_FRONT_FACE",
            "self.tetForFace[faceID].front",
            "self.tetForFace[faceID].back",
            "OPTIX_RAYGEN_PROGRAM(queryKernel)",
            "vec3f(1.f, 1e-10f, 1e-10f)",
            "OPTIX_RAY_FLAG_DISABLE_ANYHIT",
            "OPTIX_RAYGEN_PROGRAM(queryKernelBD)",
            "OPTIX_RAY_FLAG_CULL_FRONT_FACING_TRIANGLES",
        ),
        "optix/internalTypes.h": (
            "struct FaceInfo { int front=-1, back=-1; }",
            "float                  maxEdgeLength;",
            "int     *out_tetIDs;",
        ),
        "optix/OptixTriQuery.cpp": (
            "faceVertices.push_back",
            "faceIndices.push_back",
            "faceInfos.push_back",
            "maxEdgeLength = std::max",
        ),
        "query/ConvexQuery.cu": (
            "for(int i=0;i<50;++i)",
            "d_faceinfos[faceID].front",
            "d_faceinfos[faceID].back",
            "reflectInTet",
        ),
        "README.md": ("cudaParticleAdvection.exe", "--input_mesh", "--input_tet_velocity_field"),
    }
    return {
        "repository": "https://github.com/BinWang0213/RTXAdvect",
        "commit": commit,
        "working_tree_clean": True,
        "files": {
            relative: require_tokens(author / relative, tokens)
            for relative, tokens in files.items()
        },
        "source_derived_algorithm": {
            "geometry": "built_in_triangle_gas_over_shared_tetrahedral_faces",
            "cell_locator": "closest_triangle_hit_plus_front_back_face_adjacency",
            "point_ray": "origin_particle__direction_1_1e-10_1e-10__tmax_max_edge_length",
            "boundary_ray": "displacement_direction__front_face_culling__face_output",
            "cuda_partner": "bounded_neighbor_walk_and_wall_reflection",
        },
    }


def audit_frozen_runtime(workspace: Path) -> dict[str, Any]:
    api = workspace / "src/native/optix/rtdl_optix_api.cpp"
    native = workspace / "src/native/optix/rtdl_optix_v4_callback_poc.cpp"
    wrapper = workspace / "src/rtdsl/v4_callback_optix_wrapper_codegen.py"
    return {
        "api": require_tokens(api, (
            "rtdl_optix_v4_prepare_formal_callback_v1",
            "const V4CallbackSphere* spheres",
            "rtdl_optix_v4_execute_prepared_formal_callback_device_v1",
            "uint64_t query_x_device_ptr",
            "uint64_t query_y_device_ptr",
            "uint64_t query_z_device_ptr",
            "uint64_t query_tmax_device_ptr",
            "uint64_t output_ids_device_ptr",
            "uint64_t output_distance_device_ptr",
        )),
        "native": require_tokens(native, (
            "struct V4CallbackSphere",
            "float cx, cy, cz, radius;",
            "std::vector<OptixAabb> v4_formal_sphere_aabbs",
            "build_custom_accel(ctx, aabbs)",
            "parameters.spheres",
            "parameters.query_x",
            "parameters.output_ids",
            "parameters.output_distance",
        )),
        "wrapper": require_tokens(wrapper, (
            'geometry.contract_name != "tested_analytic_sphere_v1"',
            '_fail("physical_template", "requires tested_analytic_sphere_v1")',
            'physical_template="tested_analytic_sphere_nearest_search_v1"',
        )),
        "admitted_geometry": "custom_analytic_sphere_aabb_gas",
        "triangle_vertices_indices_adjacency_or_hit_orientation_admitted": False,
    }


def run_oracle(oracle) -> dict[str, Any]:
    vertices, cells = oracle.two_tetra_fixture()
    cases = (
        ("cell_0_interior", oracle.point(Fraction(1, 10), Fraction(1, 10), Fraction(1, 10)), 0),
        ("cell_1_interior", oracle.point(Fraction(1, 2), Fraction(1, 2), Fraction(1, 2)), 1),
    )
    rows = []
    for name, query, expected in cases:
        actual = oracle.locate_cell(query, vertices, cells)
        if actual != expected:
            raise RuntimeError(f"oracle mismatch: {name}: {actual} != {expected}")
        rows.append({"case": name, "expected": expected, "actual": actual, "exact": True})

    rejected = []
    for name, query, expected_matches in (
        ("shared_face_ambiguous", oracle.point(Fraction(1, 3), Fraction(1, 3), Fraction(1, 3)), (0, 1)),
        ("outside_mesh", oracle.point(2, 2, 2), ()),
    ):
        actual_matches = oracle.containing_cells(query, vertices, cells)
        if actual_matches != expected_matches:
            raise RuntimeError(f"oracle adversarial mismatch: {name}")
        try:
            oracle.locate_cell(query, vertices, cells)
        except ValueError:
            rejected.append({"case": name, "matches": actual_matches, "failed_closed": True})
        else:
            raise RuntimeError(f"oracle failed to reject: {name}")
    return {"positive_cases": rows, "fail_closed_cases": rejected, "all_passed": True}


def run_exam(workspace: Path, author: Path) -> dict[str, Any]:
    app = workspace / "Paper-reproduction-apps/goal5753-held-out-particle-tracking"
    attempt = load_module("goal5753_attempt", app / "callback_attempt.py")
    contract = load_module("goal5753_contract", app / "physical_contract.py")
    oracle = load_module("goal5753_oracle", app / "independent_oracle.py")

    selection_path = workspace / "history/internal_docs/goal5753_held_out_selection_20260811.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    selected = selection["selection"]["selected_candidate"]["candidate_id"]
    if selected != SELECTED_ID or selection["selection"]["replacement_allowed"]:
        raise RuntimeError("held-out selection identity changed or replacement enabled")

    core_seal_path = workspace / "history/internal_docs/goal5753_frozen_core_seal_audit_final_20260811.json"
    core_seal = json.loads(core_seal_path.read_text(encoding="utf-8"))
    if (core_seal["execution_source_archive_sha256"] != FROZEN_SOURCE_SHA256 or
            core_seal["native_sha256"] != FROZEN_NATIVE_SHA256 or
            core_seal["held_out_exam_core_diff_count"] != 0):
        raise RuntimeError("frozen core/native seal failed")

    from rtdsl.v4_callback_abi import compile_callback_abi
    from rtdsl.v4_callback_frontend import compile_callback_source
    from rtdsl.v4_callback_optix_wrapper_codegen import (
        CallbackWrapperCodegenError,
        generate_trusted_optix_wrapper_v1,
    )

    verified = compile_callback_source(attempt.CALLBACK_SOURCE, attempt.manifest())
    abi = compile_callback_abi(verified)

    wrapper_failure = None
    try:
        generate_trusted_optix_wrapper_v1(
            verified, abi, any_hit_proof_authority=None
        )
    except CallbackWrapperCodegenError as exc:
        wrapper_failure = {"code": exc.code, "message": str(exc)}
    if wrapper_failure is None or wrapper_failure["code"] != "physical_template":
        raise RuntimeError(f"unexpected wrapper disposition: {wrapper_failure}")

    physical_failure = None
    try:
        contract.admit_required_physical_capabilities(attempt.REQUIRED_PHYSICAL_CAPABILITIES)
    except contract.PhysicalAdmissionError as exc:
        physical_failure = {"code": exc.code, "missing": exc.missing}
    if physical_failure is None or physical_failure["code"] != contract.FAILURE_CODE:
        raise RuntimeError(f"unexpected physical admission: {physical_failure}")

    return {
        "schema": "rtdl.v4.goal5753.held_out_particle_tracking_exam_result.v1",
        "status": "honest_held_out_exam_failure__physical_host_abi_not_generalized",
        "selected_application": {
            "candidate_id": SELECTED_ID,
            "paper": "Wang et al., CPC 271 (2022) 108221",
            "doi": "10.1016/j.cpc.2021.108221",
            "selection_sha256": sha256_file(selection_path),
            "replacement_used": False,
        },
        "frozen_identity": {
            "core_seal_sha256": sha256_file(core_seal_path),
            "execution_source_archive_sha256": FROZEN_SOURCE_SHA256,
            "native_sha256": FROZEN_NATIVE_SHA256,
            "core_or_native_diff_count": 0,
        },
        "author_source_audit": audit_author_source(author),
        "application_callback": {
            "callback_source_sha256": sha256_bytes(attempt.CALLBACK_SOURCE.encode("utf-8")),
            "callback_ir_sha256": verified.ir_sha256,
            "effect_digest": verified.effect_digest,
            "abi_sha256": abi.abi_sha256,
            "restricted_frontend_and_abi_passed": True,
            "wrapper_codegen_passed": False,
            "wrapper_failure": wrapper_failure,
            "any_hit_disabled_to_match_author_route": True,
        },
        "independent_exact_oracle": run_oracle(oracle),
        "frozen_runtime_source_audit": audit_frozen_runtime(workspace),
        "physical_admission": {
            "passed": False,
            "failure": physical_failure,
            "older_v3_triangle_primitive_substituted": False,
            "author_optix_binary_substituted": False,
        },
        "behavioral_execution": {
            "gpu_runtime_imported_or_called_by_exam": False,
            "optix_launch_count": 0,
            "raygen_invocation_count": 0,
            "behavioral_true_optix_passed": False,
            "reason": "frozen physical-schema admission failed before wrapper/native launch",
        },
        "exam_grade": {
            "expressibility_frontend_only": "partial_pass",
            "physical_runtime_generalization": "fail",
            "exact_end_to_end_output": "not_executed_due_to_fail_closed_admission",
            "goal5753_completion": "honest_failure_completed",
            "current_v4_generalization_claim": "refuted_by_selected_held_out_application",
        },
        "claim_boundary": {
            "correctness_of_oracle_claimed": True,
            "selected_application_v4_correctness_claimed": False,
            "selected_application_behavioral_true_optix_claimed": False,
            "performance_claimed": False,
            "pod_used_or_authorized": False,
            "production_or_submission_claimed": False,
            "post_selection_core_extension_allowed_to_rescue_exam": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--author-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run_exam(args.workspace.resolve(), args.author_source.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
