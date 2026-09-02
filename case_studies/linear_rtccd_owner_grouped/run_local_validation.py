"""Build the deterministic local-only successor validation receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import tarfile

REPO_ROOT = Path(__file__).resolve().parents[2]
for import_root in (REPO_ROOT / "src", REPO_ROOT):
    if str(import_root) not in sys.path:
        sys.path.insert(0, str(import_root))

from rtdsl.v4_callback_ir import CallbackRole
from rtdsl.v4_curve_owner_grouped_any_hit_optix_compiler import (
    generate_curve_owner_grouped_any_hit_numba_leaf,
)
from rtdsl.v4_curve_owner_grouped_any_hit_optix_wrapper_codegen import (
    generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1,
)
from rtdsl.v4_curve_owner_grouped_any_hit_standard_library import (
    build_curve_owner_grouped_any_hit_authority,
)
from rtdsl.v4_curve_physical_schema import CurveTargetProfile
from rtdsl.v4_owner_grouped_any_hit import compile_owner_grouped_any_hit_abi

from case_studies.linear_rtccd_owner_grouped.fixtures import (
    REGISTERED_SURFACE_GAP_FLOOR,
    REGISTERED_SURFACE_GAP_FLOOR_EXPONENT2,
    deterministic_scale_case,
    registered_local_cases,
)
from case_studies.linear_rtccd_owner_grouped.independent_oracle import (
    evaluate_owner_grouped_collision_reference,
)


STORED_RECEIPT = REPO_ROOT / (
    "history/internal_docs/"
    "successor_owner_grouped_any_hit_local_validation_20260901.json"
)
AUTHOR_ARCHIVE = REPO_ROOT / (
    "history/internal_docs/goal5836_a0_source_acquisition_20260901/"
    "AUTHOR_SELECTED_SOURCE.tar.gz"
)
AUTHOR_COMMIT = "bacbf77a612bba3e6e8f7a464fa0fa2c67298ac7"
AUTHOR_PREFIX = f"RTCollisionDetection-{AUTHOR_COMMIT}/"
SYNTHETIC_LOCAL_NATIVE_SHA256 = hashlib.sha256(
    b"RTDL successor local source-generation target; not native bytes"
).hexdigest()


CODE_SOURCES = (
    "src/rtdsl/__init__.py",
    "src/rtdsl/v4_owner_grouped_any_hit.py",
    "src/rtdsl/v4_curve_owner_grouped_any_hit.py",
    "src/rtdsl/v4_curve_owner_grouped_any_hit_standard_library.py",
    "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_wrapper_codegen.py",
    "src/rtdsl/v4_curve_owner_grouped_any_hit_optix_compiler.py",
    "src/rtdsl/v4_curve_owner_grouped_any_hit_prepared_runtime.py",
    "src/rtdsl/v4_curve_owner_grouped_any_hit_public.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_api.cpp",
    "case_studies/linear_rtccd_owner_grouped/__init__.py",
    "case_studies/linear_rtccd_owner_grouped/linear_rtccd_owner_grouped.py",
    "case_studies/linear_rtccd_owner_grouped/independent_oracle.py",
    "case_studies/linear_rtccd_owner_grouped/fixtures.py",
    "case_studies/linear_rtccd_owner_grouped/run_local_validation.py",
    "case_studies/linear_rtccd_owner_grouped/README.md",
    "scripts/build_v4_optix_native_snapshot.py",
    "scripts/successor_owner_grouped_pod_preflight.py",
    "scripts/successor_linear_rtccd_owner_grouped_pod_runner.py",
    "tests/successor_owner_grouped_any_hit_contract_test.py",
    "tests/successor_linear_rtccd_owner_grouped_app_test.py",
    "tests/successor_owner_grouped_gpu_tooling_test.py",
)


AUTHOR_SOURCE_REQUIREMENTS = {
    "RTCD/CollisionDetector/CCCuda.cu": (
        "optixGetPrimitiveIndex()",
        "primIdxToPoseIdx[primID]",
        "atomicAdd",
        "optixIgnoreIntersection()",
    ),
    "RTCD/CollisionDetector/CollisionDetector.h": (
        "params.mesh.primIdxToPoseIdx",
        "getMapIndex(i)",
    ),
    "RTCD/Meshes/mesh.h": (
        "loopEdgeIndices",
        "ordered_edges",
        "doesLoop",
    ),
}


def _sha_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _canonical_bytes(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")


def _source_inventory() -> list[dict[str, object]]:
    rows = []
    for relative in CODE_SOURCES:
        path = REPO_ROOT / relative
        content = path.read_bytes()
        rows.append({
            "path": relative,
            "bytes": len(content),
            "sha256": _sha_bytes(content),
        })
    return rows


def _author_source_evidence() -> list[dict[str, object]]:
    rows = []
    with tarfile.open(AUTHOR_ARCHIVE, "r:gz") as archive:
        for relative, markers in AUTHOR_SOURCE_REQUIREMENTS.items():
            member_name = AUTHOR_PREFIX + relative
            member = archive.getmember(member_name)
            stream = archive.extractfile(member)
            if stream is None or not member.isfile():
                raise RuntimeError(f"author member is not a regular file: {relative}")
            content = stream.read()
            text = content.decode("utf-8", errors="strict")
            missing = tuple(marker for marker in markers if marker not in text)
            if missing:
                raise RuntimeError(
                    f"author evidence markers missing in {relative}: {missing}")
            rows.append({
                "path": relative,
                "archive_member": member_name,
                "bytes": len(content),
                "sha256": _sha_bytes(content),
                "required_markers": list(markers),
                "all_required_markers_present": True,
            })
    return rows


def build_local_validation_receipt() -> dict[str, object]:
    target = CurveTargetProfile(
        "optix", "8.0.0", "8.9", SYNTHETIC_LOCAL_NATIVE_SHA256)
    authority, proof = build_curve_owner_grouped_any_hit_authority(target)
    abi = compile_owner_grouped_any_hit_abi(authority.behavior)
    wrapper = generate_trusted_optix_curve_owner_grouped_any_hit_wrapper_v1(
        authority, abi)
    roles = (
        CallbackRole.MAKE_RAY,
        CallbackRole.ANY_HIT,
        CallbackRole.MISS,
        CallbackRole.FINALIZE,
    )
    leaves = tuple(generate_curve_owner_grouped_any_hit_numba_leaf(
        authority, abi, role) for role in roles)
    def validate_cases(cases):
        rows = []
        for case in cases:
            observed = evaluate_owner_grouped_collision_reference(case.problem)
            static, batch = case.problem.public_inputs()
            if observed.per_trajectory_collision != case.expected_bits:
                raise RuntimeError(f"local oracle mismatch: {case.case_id}")
            if observed.minimum_surface_gap < REGISTERED_SURFACE_GAP_FLOOR:
                raise RuntimeError(
                    f"local case enters numeric boundary band: {case.case_id}")
            projection = case.problem.identity_projection()
            admission = case.problem.surface_crossing_domain_admission()
            rows.append({
                "case_id": case.case_id,
                "purpose": case.purpose,
                "expected_owner_bits": list(case.expected_bits),
                "observed_owner_bits": list(observed.per_trajectory_collision),
                "match": True,
                "owner_count": static.owner_count,
                "primitive_count": len(static.segment_indices),
                "query_count": len(batch.queries),
                "intersecting_directed_pair_count": observed.intersecting_pair_count,
                "minimum_surface_gap": observed.minimum_surface_gap,
                "surface_crossing_domain_admission": admission,
                "identity_projection_sha256": projection["projection_sha256"],
            })
        return rows

    semantic_cases = registered_local_cases()
    scale_cases = tuple(deterministic_scale_case(*dimensions[:2],
        hit_stride=dimensions[2], duplicate_query_factor=dimensions[3])
        for dimensions in (
            (8, 2, 2, 1),
            (32, 4, 3, 2),
            (64, 8, 5, 1),
        ))
    semantic_rows = validate_cases(semantic_cases)
    scale_rows = validate_cases(scale_cases)
    payload = {
        "schema": "rtdl.successor_owner_grouped_any_hit.local_validation.v3",
        "date": "2026-09-02",
        "status": "LOCAL_RECEIPT_PASS__GPU_FUNCTIONAL_EVIDENCE_IS_SEPARATE",
        "scope": (
            "bounded paper-derived linear RT-CCD owner-grouped Boolean subset"
        ),
        "generic_contract": {
            "template": authority.behavior.schema.semantic_dict()["template_id"],
            "callback_ir_sha256": authority.callback.ir_sha256,
            "callback_effect_digest": authority.callback.effect_digest,
            "behavior_schema_sha256": authority.behavior.schema.schema_sha256,
            "behavior_authority_sha256": authority.behavior.authority_sha256,
            "physical_schema_sha256": authority.schema.schema_sha256,
            "physical_plan_sha256": authority.canonical_plan.plan_sha256,
            "any_hit_proof_sha256": proof.proof_sha256,
            "callback_abi_sha256": abi.abi_sha256,
            "generated_wrapper_sha256": wrapper.source_sha256,
            "numba_leaf_source_sha256": {
                leaf.role.value: leaf.generated_source_sha256 for leaf in leaves
            },
            "role_topology": [role.value for role in roles],
            "closed_reduction": "owner_hit_bits[owner_ids[primitive_id]] |= 1",
            "event_order_semantic": False,
            "duplicate_delivery_semantic": False,
        },
        "synthetic_local_target": {
            "optix_sdk": target.optix_sdk,
            "compute_capability": target.compute_capability,
            "native_sha256": target.native_sha256,
            "warning": (
                "source-generation identity only; no native library was loaded"
            ),
        },
        "author_source": {
            "commit": AUTHOR_COMMIT,
            "archive_path": str(AUTHOR_ARCHIVE.relative_to(REPO_ROOT)),
            "archive_sha256": _sha_bytes(AUTHOR_ARCHIVE.read_bytes()),
            "evidence": _author_source_evidence(),
            "bounded_interpretation": (
                "author source evidences primitive-to-pose grouped any-hit "
                "accumulation and continued traversal; this successor uses "
                "Boolean OR rather than reproducing author hit counts"
            ),
        },
        "registered_semantic_cases": semantic_rows,
        "registered_scale_cases": scale_rows,
        "registered_surface_gap_floor_exponent2":
            REGISTERED_SURFACE_GAP_FLOOR_EXPONENT2,
        "registered_semantic_case_count": len(semantic_rows),
        "registered_scale_case_count": len(scale_rows),
        "registered_local_case_count": len(semantic_rows) + len(scale_rows),
        "matching_local_case_count": sum(
            row["match"] for row in semantic_rows + scale_rows),
        "code_sources": _source_inventory(),
        "pod_toolchain_preflight_ready": True,
        "fresh_native_builder_ready": True,
        "public_app_gpu_runner_ready": True,
        "frozen_goal5835_goal5836_files_modified": False,
        "author_code_executed": False,
        "native_library_built": False,
        "numba_ptx_compiled": False,
        "optix_launch_count": 0,
        "gpu_correctness_evidence_count": 0,
        "external_pod_evidence_embedded": False,
        "performance_timing_count": 0,
        "full_paper_reproduction_claimed": False,
        "benchmark_app_claimed": False,
        "external_review_count": 0,
        "next_separate_gates": [
            "owner-deferred external review before promotion wording",
            "preregistered Embree/timing study before performance wording",
            "R570-or-newer execution only for optional OptiX 9 coverage",
        ],
    }
    return {**payload, "receipt_sha256": _sha_bytes(_canonical_bytes(payload))}


def _write(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--verify-stored", action="store_true")
    args = parser.parse_args()
    if args.output is not None and args.verify_stored:
        raise SystemExit("choose --output or --verify-stored")
    observed = build_local_validation_receipt()
    if args.verify_stored:
        expected = json.loads(STORED_RECEIPT.read_text(
            encoding="utf-8", errors="strict"))
        if observed != expected:
            raise SystemExit("stored successor local receipt differs")
    elif args.output is not None:
        _write(args.output, observed)
    print(json.dumps({
        "status": observed["status"],
        "case_count": observed["registered_local_case_count"],
        "matching_case_count": observed["matching_local_case_count"],
        "gpu_correctness_evidence_count":
            observed["gpu_correctness_evidence_count"],
        "receipt_sha256": observed["receipt_sha256"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
