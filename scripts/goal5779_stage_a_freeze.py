#!/usr/bin/env python3
"""Freeze the Goal5779 controlled code-quality experiment before timing.

Stage A compiles but never times three controlled pairs.  Each pair uses the
same trusted wrapper and the same generated leaves except for one role, where
the control side substitutes a closed hand-written CUDA implementation of the
same ABI and semantics.  The output binds exact PTX, native, target, fixture,
schedule and statistics identities.  Stage B must consume this exact JSON and
is forbidden until its digest has been published.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
from pathlib import Path
import platform
import sys

import numpy as np

from rtdsl.v4_bounded_relation import (
    BoundedRelationEmissionSchema,
    RelationDuplicatePolicy,
    compile_bounded_relation_contract,
    verify_bounded_relation_schema,
)
from rtdsl.v4_bounded_relation_optix_compiler import (
    compile_verified_bounded_relation_executable,
)
from rtdsl.v4_box_relation_callback import (
    compile_callback as compile_box_callback,
    physical_schema as box_physical_schema,
)
from rtdsl.v4_callback_abi import AnyHitProofAuthority, compile_callback_abi
from rtdsl.v4_callback_ir import AnyHitDeliveryContract, CallbackRole
from rtdsl.v4_callback_ptx_composer import compose_callback_ptx
from rtdsl.v4_multiround_spatial import (
    MultiRoundSpatialSchema,
    verify_multiround_spatial_schema,
)
from rtdsl.v4_multiround_spatial_optix_compiler import (
    compile_verified_multiround_spatial_executable,
)
from rtdsl.v4_spatial_candidate_callback import (
    compile_callback as compile_spatial_callback,
    physical_schema as spatial_physical_schema,
)
from rtdsl.v4_triangle_reduction import (
    compile_triangle_reduction_abi,
    compile_triangle_reduction_contract,
    verify_triangle_reduction_schema,
)
from rtdsl.v4_triangle_reduction_optix_compiler import (
    compile_verified_triangle_reduction_executable,
)
from rtdsl.v4_triangle_standard_library import (
    all_hit_count_schema,
    compile_count_callback,
)
from rtdsl.v4_typed_physical_schema import (
    ReferenceTargetProfile,
    verify_typed_physical_schema,
)
from scripts.goal5779_handwritten_leaf_controls import (
    box_closed_overlap_intersection_control,
    compile_handwritten_control,
    spatial_sphere_intersection_control,
    triangle_count_any_hit_control,
)


SCHEMA = "rtdl.goal5779.generated_vs_handwritten.stage_a.v1"
ROW_ORDER = (
    "TRIANGLE_ANY_HIT_U64_COUNT",
    "CUSTOM_AABB_CLOSED_BOX_INTERSECTION",
    "CUSTOM_AABB_ANALYTIC_SPHERE_INTERSECTION",
)
ROOT = Path(__file__).resolve().parents[1]
PRODUCT_SOURCE_PATHS = (
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_triangle_standard_library.py",
    "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_spatial_candidate_callback.py",
    "src/rtdsl/v4_multiround_spatial_optix_compiler.py",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_workloads.cpp",
)


def _sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha_path(path: Path) -> str:
    return _sha_bytes(path.read_bytes())


def _digest(value: object) -> str:
    return _sha_bytes(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8"))


def _proof(callback) -> AnyHitProofAuthority:
    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "schema": "rtdl.goal5779.control_order_proof.v1",
            "callback": callback.ir_sha256,
            "effect": callback.effect_digest,
            "claim": "commutative/order-independent control fixture effects",
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _triangle(target, args):
    callback = compile_count_callback()
    authority = verify_triangle_reduction_schema(
        callback, all_hit_count_schema(callback), target=target)
    proof = _proof(callback)
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=proof)
    contract = compile_triangle_reduction_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, _ = compile_verified_triangle_reduction_executable(
        authority, contract, abi,
        any_hit_proof_authority=proof,
        compute_capability=args.compute_capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=args.python_version,
        expected_numba_version=args.numba_version,
        expected_numpy_version=args.numpy_version,
    )
    role = next(item for item in abi.roles if item.role is CallbackRole.ANY_HIT)
    control = triangle_count_any_hit_control(role)
    return callback, abi, executable, role, control


def _box(target, args):
    callback = compile_box_callback()
    physical = verify_typed_physical_schema(
        callback, box_physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, 1 << 20,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
    )
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, _ = compile_verified_bounded_relation_executable(
        authority, contract, abi,
        any_hit_proof_authority=proof,
        compute_capability=args.compute_capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=args.python_version,
        expected_numba_version=args.numba_version,
        expected_numpy_version=args.numpy_version,
    )
    role = next(item for item in abi.roles if item.role is CallbackRole.INTERSECTION)
    control = box_closed_overlap_intersection_control(role)
    return callback, abi, executable, role, control


def _spatial(target, args):
    callback = compile_spatial_callback()
    physical = verify_typed_physical_schema(
        callback, spatial_physical_schema(callback), target=target)
    relation_schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, 1 << 20,
        minimum_overlap_f32=0.0,
        duplicate_policy=RelationDuplicatePolicy.KEYED_IDENTICAL_DEDUP,
    )
    relation = verify_bounded_relation_schema(physical, relation_schema)
    proof = _proof(callback)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    relation_contract = compile_bounded_relation_contract(
        relation, abi_sha256=abi.abi_sha256)
    schema = MultiRoundSpatialSchema(
        relation_schema_sha256=relation.schema.schema_sha256,
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        physical_schema_sha256=physical.schema.schema_sha256,
        maximum_rounds=8,
        maximum_event_capacity=1 << 20,
    )
    authority = verify_multiround_spatial_schema(
        relation, relation_contract, abi, schema,
        any_hit_proof_authority=proof)
    executable, _ = compile_verified_multiround_spatial_executable(
        authority,
        any_hit_proof_authority=proof,
        compute_capability=args.compute_capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        expected_python_version=args.python_version,
        expected_numba_version=args.numba_version,
        expected_numpy_version=args.numpy_version,
    )
    role = next(item for item in abi.roles if item.role is CallbackRole.INTERSECTION)
    control = spatial_sphere_intersection_control(role)
    return callback, abi, executable, role, control


def _replace_leaf(executable, role, replacement):
    leaves = tuple(
        replacement if item.role == role.role.value else item
        for item in executable.compiled_leaves
    )
    if sum(item is replacement for item in leaves) != 1:
        raise RuntimeError(f"role replacement cardinality: {role.role.value}")
    symbols = {item.role: item.abi_name for item in leaves}
    composed = compose_callback_ptx(
        executable.wrapper_ptx, leaves,
        exact_symbols_by_role=symbols)
    return composed, leaves


def fixture_arrays() -> dict[str, dict[str, object]]:
    rng = np.random.default_rng(57790001)
    # These arrays are deterministic and moderate; they are large enough to
    # make callback work observable without turning Stage B into an app run.
    vertices = rng.uniform(-1.0, 1.0, size=(12288, 3)).astype(np.float32)
    triangles = np.arange(12288, dtype=np.uint32).reshape(-1, 3)
    origins = rng.uniform(-1.0, 1.0, size=(65536, 3)).astype(np.float32)
    directions = np.zeros((65536, 3), dtype=np.float32)
    directions[:, 2] = 1.0
    tmax = np.full(65536, 4.0, dtype=np.float32)

    grid = np.arange(4096, dtype=np.float32)
    x = (grid % 64) * np.float32(2.0)
    y = (grid // 64) * np.float32(2.0)
    indexed = np.column_stack((x, y, x + 1.0, y + 1.0)).astype(np.float32)
    source = np.column_stack((x + 0.25, y + 0.25, x + 0.75, y + 0.75)).astype(np.float32)
    ids = np.arange(4096, dtype=np.uint32)

    points = rng.uniform(-32.0, 32.0, size=(8192, 3)).astype(np.float32)
    queries = points[:4096].copy()
    query_ids = np.arange(4096, dtype=np.uint32)
    return {
        ROW_ORDER[0]: {
            "vertices": vertices, "triangles": triangles,
            "origins": origins, "directions": directions, "tmax": tmax,
        },
        ROW_ORDER[1]: {"indexed": indexed, "source": source, "ids": ids},
        ROW_ORDER[2]: {
            "points": points, "queries": queries, "query_ids": query_ids,
            "initial_radius_f32": np.float32(0.5),
            "physical_radius_f32": np.float32(0.5),
        },
    }


def _fixtures() -> dict[str, object]:
    arrays = fixture_arrays()
    triangle = arrays[ROW_ORDER[0]]
    box = arrays[ROW_ORDER[1]]
    spatial = arrays[ROW_ORDER[2]]
    return {
        ROW_ORDER[0]: _digest({
            key: _sha_bytes(triangle[key].tobytes())
            for key in ("vertices", "triangles", "origins", "directions", "tmax")
        }),
        ROW_ORDER[1]: _digest({
            key: _sha_bytes(box[key].tobytes())
            for key in ("indexed", "source", "ids")
        }),
        ROW_ORDER[2]: _digest({
            "points": _sha_bytes(spatial["points"].tobytes()),
            "queries": _sha_bytes(spatial["queries"].tobytes()),
            "query_ids": _sha_bytes(spatial["query_ids"].tobytes()),
            "initial_radius_f32": float(spatial["initial_radius_f32"]),
            "physical_radius_f32": float(spatial["physical_radius_f32"]),
        }),
    }


def build(args) -> dict[str, object]:
    native = Path(args.native).resolve()
    if not native.is_file():
        raise FileNotFoundError(native)
    native_sha = _sha_path(native)
    target = ReferenceTargetProfile(
        provider="optix",
        optix_sdk=args.optix_sdk,
        compute_capability=f"{args.compute_capability[0]}.{args.compute_capability[1]}",
        native_sha256=native_sha,
        supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    builders = (_triangle, _box, _spatial)
    fixtures = _fixtures()
    rows = []
    for row_index, builder in enumerate(builders):
        callback, abi, executable, role, control = builder(target, args)
        handwritten, log = compile_handwritten_control(
            control, role,
            compiler_options=executable.compiler_options,
            compute_capability=args.compute_capability,
            callback_ir_sha256=callback.ir_sha256,
        )
        control_composed, control_leaves = _replace_leaf(
            executable, role, handwritten)
        family = ROW_ORDER[row_index]
        if family != control.family_id:
            raise RuntimeError("frozen row order drift")
        generated_role = next(
            item for item in executable.compiled_leaves
            if item.role == role.role.value)
        rows.append({
            "row_index": row_index,
            "family_id": family,
            "role": role.role.value,
            "semantic_contract": control.semantic_contract,
            "source_provenance": control.source_provenance,
            "callback_ir_sha256": callback.ir_sha256,
            "callback_effect_digest": callback.effect_digest,
            "callback_abi_sha256": abi.abi_sha256,
            "role_symbol": role.symbol,
            "wrapper_source_sha256": executable.wrapper.source_sha256,
            "wrapper_ptx_sha256": executable.wrapper_ptx_sha256,
            "unchanged_generated_leaf_ptx_sha256": [
                item.ptx_sha256 for item in executable.compiled_leaves
                if item.role != role.role.value
            ],
            "generated_role_source_sha256": generated_role.generated_source_sha256,
            "generated_role_ptx_sha256": generated_role.ptx_sha256,
            "generated_composed_ptx_sha256": executable.composed.ptx_sha256,
            "handwritten_source_sha256": control.source_sha256,
            "handwritten_ptx_sha256": handwritten.ptx_sha256,
            "handwritten_composed_ptx_sha256": control_composed.ptx_sha256,
            "handwritten_nvrtc_log_sha256": _sha_bytes(log.encode("utf-8")),
            "fixture_sha256": fixtures[family],
            "same_wrapper": control_composed.wrapper_ptx_sha256 == executable.composed.wrapper_ptx_sha256,
            "same_non_replaced_leaves": all(
                candidate == original
                for candidate, original in zip(
                    control_leaves, executable.compiled_leaves)
                if original.role != role.role.value
            ),
            "same_semantics_and_physical_algorithm_claim": True,
            "comparator_class": "handwritten_direct_optix_control",
            "comparator_is_exact_prior_v2_source_bytes": False,
            "comparison_is_codegen_isolation_not_app_endpoint_v2_v4": True,
            "functional_device_execution_completed": False,
            "device_timing_observed": False,
        })
    payload = {
        "schema": SCHEMA,
        "status": "STAGE_A_FROZEN__DEVICE_TIMING_FORBIDDEN_UNTIL_THIS_ARTIFACT_IS_HASHED",
        "goal": 5779,
        "target": {
            "hostname": platform.node(),
            "provider": target.provider,
            "optix_sdk": target.optix_sdk,
            "compute_capability": target.compute_capability,
            "native_path": str(native),
            "native_sha256": native_sha,
            "python_executable": str(Path(sys.executable).resolve()),
            "python_version": args.python_version,
            "numba_version": args.numba_version,
            "numpy_version": args.numpy_version,
        },
        "design_identity": {
            "amendment_a1_path": "history/internal_docs/v4_cgo_next_stage_plan_amendment_a1_preregistrations_20260814.json",
            "amendment_a1_sha256": "343015ce6963b68d26665cd482d250458ef57fe6d78b8cb12226d59b78a99fca",
            "external_review_sha256": "92eec43b0c55a646ea8754133c0403c633a9968ae71ce3244ba3b6138e99ef17",
        },
        "implementation_identity": {
            "stage_a_script": {
                "path": "scripts/goal5779_stage_a_freeze.py",
                "sha256": _sha_path(Path(__file__).resolve()),
            },
            "handwritten_control_script": {
                "path": "scripts/goal5779_handwritten_leaf_controls.py",
                "sha256": _sha_path(
                    ROOT / "scripts/goal5779_handwritten_leaf_controls.py"),
            },
            "product_sources": [
                {"path": path, "sha256": _sha_path(ROOT / path)}
                for path in PRODUCT_SOURCE_PATHS
            ],
        },
        "row_order": list(ROW_ORDER),
        "rows": rows,
        "schedule": {
            "pair_count_per_row": 16,
            "order": "ABBA by pair; even pairs handwritten/generated, odd pairs generated/handwritten",
            "warmup_launches_per_variant": 2,
            "fresh_prepared_owner_per_variant": True,
            "retry_resume_replacement_allowed": False,
        },
        "timing_api": {
            "scope": "prepared physical callback execution on the legacy default CUDA stream",
            "clock": "CUDA events recorded immediately before and after the exact prepared execute ABI",
            "included": "GPU work and device copies enqueued by the exact prepared execute ABI",
            "excluded": "PTX compilation, OptiX module/pipeline/GAS preparation, Python output validation and owner teardown",
            "same_fixture_wrapper_gas_ray_layout_output_contract": True,
        },
        "statistics": {
            "ratio": "handwritten_seconds/generated_v4_seconds",
            "draws": 10000,
            "sampler": "python_random_Random_choices",
            "statistic": "statistics_median",
            "ci_indices": [249, 9749],
            "seed": "57790000 + frozen_row_index",
            "competitive_rule": "95% bootstrap lower bound >= 0.95",
        },
        "stage_b_gate": {
            "minimum_rows": 3,
            "all_rows_have_distinct_semantic_family": len({r["family_id"] for r in rows}) == 3,
            "all_rows_same_wrapper": all(r["same_wrapper"] for r in rows),
            "all_rows_same_non_replaced_leaves": all(
                r["same_non_replaced_leaves"] for r in rows),
            "all_rows_device_timing_unobserved": all(not r["device_timing_observed"] for r in rows),
            "stage_a_sha256_must_be_supplied_to_stage_b": True,
        },
        "claim_boundary": {
            "device_performance_claimed": False,
            "v4_competitive_claimed": False,
            "device_timing_observed": False,
            "product_source_changed": False,
            "pod_used_or_authorized": False,
        },
    }
    if not all(payload["stage_b_gate"].values()):
        raise RuntimeError("Stage-A gate failed closed")
    return payload


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", required=True)
    parser.add_argument("--optix-include", required=True)
    parser.add_argument("--cuda-include", required=True)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--compute-capability", default="6,1")
    parser.add_argument("--python-version", default="3.12.3")
    parser.add_argument("--numba-version", default="0.65.1")
    parser.add_argument("--numpy-version", default="2.2.6")
    parser.add_argument("--output", required=True)
    args = parser.parse_args(argv)
    args.compute_capability = tuple(map(int, args.compute_capability.split(",")))
    return args


def main(argv=None) -> int:
    args = parse_args(argv)
    payload = build(args)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    output.write_text(data, encoding="utf-8")
    print(json.dumps({
        "status": "PASS",
        "output": str(output.resolve()),
        "sha256": _sha_bytes(data.encode("utf-8")),
        "rows": len(payload["rows"]),
        "device_timing_observed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
