#!/usr/bin/env python3
"""One fresh-process Home arm for a Goal5790-A1 rejected encoding.

GPU/compiler imports are deliberately lazy.  The product rejection arm loads
only the app-neutral semantic/physical admission module; execution arms load
the family compiler and runtime only after their arm identity is fixed.

The diagnostic routes are test-only and non-registrable.  A behavioral OptiX
receipt proves the traversal named in that record, not that the rejected
semantic association is correct.  Correctness is decided separately by the
route-free oracle frozen in ``goal5790_a1_rejected_encoding_cases.py``.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
from dataclasses import replace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import struct
import subprocess
import sys
from types import ModuleType
from types import SimpleNamespace

from scripts.goal5790_a1_rejected_encoding_cases import (
    CASE_IDS,
    canonical_sha256,
    evaluate_case,
    expected_rejection_reasons,
    parse_suite_json,
)


SCHEMA = "rtdl.goal5790_a1.home_worker.v1"
HOME_HOSTNAME = "lx1"
HOME_GPU = "NVIDIA GeForce GTX 1070"
HOME_DRIVER = "580.126.09"
HOME_UUID = "GPU-8e04454e-c177-6e5b-3f43-e676980ecdfa"
HOME_CC = "6.1"
HOME_AUTHORITY_FILE_SHA256 = (
    "bcfd6a99766621d474dc45aa1b8c896df725575fd1131b64471b5d3d75316314")
HOME_AUTHORITY_RECEIPT_SHA256 = (
    "73fc385cabf2ea5b6cff70eb6d0fc31750cda206377015805c2935f02de6bb40")
PARTICLE_GATE_AUTHORITY_PATH = (
    "history/internal_docs/"
    "goal5790_a1_amendment_a1_particle_earliest_product_gate_20260816.md")
PARTICLE_GATE_AUTHORITY_SHA256 = (
    "84872fdb24f5d398644ec421b55a8a53c7f6cc19af4860ac4ad10f440d958625")
HOME_TOOLCHAIN_FIELDS = (
    "cuda_toolkit_resolved_path", "cuda_nvrtc_resolved_path",
    "cuda_nvrtc_sha256", "cuda_nvrtc_builtins_resolved_path",
    "cuda_nvrtc_builtins_sha256", "cuda_nvrtc_runtime_version",
    "cuda_nvvm_resolved_path", "cuda_nvvm_sha256",
    "cuda_libdevice_resolved_path", "cuda_libdevice_sha256",
    "cuda_nvcc_version", "cuda_host_compiler_path",
    "cuda_host_compiler_version",
)
ARMS = {
    "product_admission_reject",
    "accepted_control",
    "diagnostic_counterfactual",
}
ROOT = Path(__file__).resolve().parents[1]
NO_ORIENTATION_CONTRACT_SHA256 = hashlib.sha256(
    b"rtdl.v4.orientation_contract.not_applicable.v1").hexdigest()

_UNCHECKED_U64_CONTINUATION_SOURCE = r'''
extern "C" __global__ void goal5790_a1_unchecked_weighted_sum(
    const unsigned long long* values,
    const unsigned long long* weights,
    unsigned long long count,
    unsigned long long* output) {
  if (blockIdx.x == 0 && threadIdx.x == 0) {
    unsigned long long total = 0ull;
    for (unsigned long long index = 0; index < count; ++index) {
      total += values[index] * weights[index];
    }
    output[0] = total;
  }
}
'''

# Test-only trusted-classifier catalog.  These descriptors are deliberately
# independent of the CPU witness suite.  The pre-run execution spec freezes
# this file, the exact live family tuple and the issued registry snapshots
# before any executable is compiled or any arm is launched.
_TRUSTED_POLICY_BY_CASE = {
    CASE_IDS[0]: ({
        "exactness": "exact_for_registered_interior_cell_encoding_domain",
        "multiplicity": "one_output_per_semantic_request",
        "numeric_precision": "integer_rank_geometry_with_binary32_interior_coordinates",
        "order_policy": "semantic_request_order",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "leftmost_minimum_index",
    }, {
        "exactness": "not_exact_when_query_coordinates_lie_on_cell_boundaries",
        "multiplicity": "one_output_per_semantic_request",
        "numeric_precision": "integer_rank_geometry_with_binary32_interior_coordinates",
        "order_policy": "semantic_request_order",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "leftmost_minimum_index",
    }),
    CASE_IDS[1]: ({
        "exactness": "exact_for_registered_interior_cell_encoding_domain",
        "multiplicity": "one_output_per_semantic_request",
        "numeric_precision": "integer_rank_geometry_with_binary32_interior_coordinates",
        "order_policy": "semantic_request_order",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "leftmost_minimum_index",
    }, {
        "exactness": "exact_for_registered_interior_cell_encoding_domain",
        "multiplicity": "one_output_per_semantic_request",
        "numeric_precision": "integer_rank_geometry_with_binary32_interior_coordinates",
        "order_policy": "semantic_request_order",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "rightmost_minimum_index",
    }),
    CASE_IDS[2]: ({
        "exactness": "exact_checked_integer_reduction",
        "multiplicity": "paper_owned_weighted_hit_multiplicity",
        "numeric_precision": "u32_inputs_checked_u64_accumulator",
        "order_policy": "commutative_checked_reduction",
        "overflow_policy": "fail_closed_before_u64_wraparound",
        "tie_policy": "not_applicable_scalar",
    }, {
        "exactness": "exact_checked_integer_reduction",
        "multiplicity": "paper_owned_weighted_hit_multiplicity",
        "numeric_precision": "u32_inputs_checked_u64_accumulator",
        "order_policy": "commutative_checked_reduction",
        "overflow_policy": "unchecked_modulo_u64",
        "tie_policy": "not_applicable_scalar",
    }),
    CASE_IDS[3]: ({
        "exactness": "exact_checked_integer_reduction",
        "multiplicity": "paper_owned_weighted_hit_multiplicity",
        "numeric_precision": "u32_inputs_checked_u64_accumulator",
        "order_policy": "commutative_checked_reduction",
        "overflow_policy": "fail_closed_before_u64_wraparound",
        "tie_policy": "not_applicable_scalar",
    }, {
        "exactness": "exact_checked_integer_reduction",
        "multiplicity": "unweighted_hit_multiplicity",
        "numeric_precision": "u32_inputs_checked_u64_accumulator",
        "order_policy": "commutative_checked_reduction",
        "overflow_policy": "fail_closed_before_u64_wraparound",
        "tie_policy": "not_applicable_scalar",
    }),
    CASE_IDS[4]: ({
        "exactness": "exact_for_declared_mesh_and_ray_domain",
        "multiplicity": "one_hit_or_miss_per_query",
        "numeric_precision": "binary32_triangle_with_pinned_orientation",
        "order_policy": "query_index_ascending",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "nearest_t_then_min_u32_primitive",
    }, {
        "exactness": "exact_for_declared_mesh_and_ray_domain",
        "multiplicity": "one_hit_or_miss_per_query",
        "numeric_precision": "binary32_triangle_with_pinned_orientation",
        "order_policy": "query_index_ascending",
        "overflow_policy": "fail_closed_before_integer_wraparound",
        "tie_policy": "nearest_t_then_min_u32_primitive",
    }),
    CASE_IDS[5]: ({
        "exactness": "inclusive_overlap_exact_for_declared_binary32_domain",
        "multiplicity": "deduplicated_set",
        "numeric_precision": "binary32_geometry_with_exact_u32_identity",
        "order_policy": "lexicographic_u32_pair",
        "overflow_policy": "fail_closed_capacity_or_counter_overflow",
        "tie_policy": "ascending_u32_pair",
    }, {
        "exactness": "strict_positive_width_overlap_only",
        "multiplicity": "deduplicated_set",
        "numeric_precision": "binary32_geometry_with_exact_u32_identity",
        "order_policy": "lexicographic_u32_pair",
        "overflow_policy": "fail_closed_capacity_or_counter_overflow",
        "tie_policy": "ascending_u32_pair",
    }),
}
_TRUSTED_STAGE_SOURCES_BY_CASE = {
    CASE_IDS[0]: ({
        "encode": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
        "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_optix_runtime.py",
        "continuation": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }, {
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_optix_runtime.py",
        "continuation": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }),
    CASE_IDS[1]: ({
        "encode": "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
        "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_optix_runtime.py",
        "continuation": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }, {
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_optix_runtime.py",
        "continuation": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }),
    CASE_IDS[2]: ({
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_reduction_optix_runtime.py",
        "continuation": "src/rtdsl/v4_triangle_reduction.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }, {
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_triangle_standard_library.py",
        "trace": "scripts/goal5790_a1_home_worker.py",
        "continuation": "scripts/goal5790_a1_home_worker.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }),
    CASE_IDS[3]: ({
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_reduction_optix_runtime.py",
        "continuation": "src/rtdsl/v4_triangle_reduction.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }, {
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_reduction_optix_runtime.py",
        "continuation": "src/rtdsl/v4_triangle_reduction.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }),
    CASE_IDS[4]: ({
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_optix_runtime.py",
        "continuation": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }, {
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "trace": "src/rtdsl/v4_triangle_optix_runtime.py",
        "continuation": "src/rtdsl/v4_builtin_triangle_standard_library.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }),
    CASE_IDS[5]: ({
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "src/rtdsl/v4_box_relation_callback.py",
        "trace": "src/rtdsl/v4_bounded_relation_optix_runtime.py",
        "continuation": "src/rtdsl/v4_box_relation_callback.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }, {
        "encode": "scripts/goal5790_a1_home_worker.py",
        "ray": "scripts/goal5790_a1_home_worker.py",
        "trace": "src/rtdsl/v4_bounded_relation_optix_runtime.py",
        "continuation": "scripts/goal5790_a1_home_worker.py",
        "decode": "scripts/goal5790_a1_home_worker.py",
    }),
}


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _jsonable(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    if hasattr(value, "item") and callable(value.item):
        return _jsonable(value.item())
    return value


def _digest(value: object) -> str:
    return canonical_sha256(_jsonable(value))


def _load_module(relative: str, name: str) -> ModuleType:
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _process_audit_snapshot() -> dict[str, object]:
    module_rows = []
    for name, module in sorted(sys.modules.items()):
        path_value = getattr(module, "__file__", None)
        if not isinstance(path_value, str):
            continue
        path = Path(path_value)
        row = {"module": name, "source_path": path.as_posix()}
        if path.is_file():
            row["source_sha256"] = _sha_file(path)
        module_rows.append(row)
    maps_path = Path("/proc/self/maps")
    maps = maps_path.read_text(encoding="utf-8", errors="replace").splitlines() \
        if maps_path.is_file() else []
    relevant = sorted(line for line in maps if any(
        token in line.lower() for token in (
            "cuda", "nvrtc", "nvvm", "libdevice", "optix", "cupy", "numba")))
    return {
        "modules": module_rows,
        "modules_sha256": _digest(module_rows),
        "relevant_memory_maps": relevant,
        "relevant_memory_maps_sha256": _digest(relevant),
    }


def _target(args):
    from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile

    return ReferenceTargetProfile(
        provider="optix", optix_sdk=args.optix_sdk,
        compute_capability=f"{args.cc[0]}.{args.cc[1]}",
        native_sha256=_sha_file(args.native),
        supports_custom_aabb=True, supports_builtin_triangle=True,
    )


def _query_exact_home_machine(
    expected_machine_sha256: str,
    authority_file: Path,
    expected_authority_file_sha256: str,
) -> dict[str, object]:
    """Fail before admission or execution unless this is the frozen Home GPU."""

    authority_file = authority_file.resolve()
    actual_file_sha256 = _sha_file(authority_file)
    if expected_authority_file_sha256 != HOME_AUTHORITY_FILE_SHA256 \
            or actual_file_sha256 != HOME_AUTHORITY_FILE_SHA256:
        raise RuntimeError("Goal5790-A1 frozen Home-authority bytes drifted")
    authority = json.loads(authority_file.read_text(encoding="utf-8"))
    body = dict(authority)
    claimed_receipt = body.pop("receipt_sha256", None)
    if claimed_receipt != HOME_AUTHORITY_RECEIPT_SHA256 \
            or canonical_sha256(body) != HOME_AUTHORITY_RECEIPT_SHA256:
        raise RuntimeError("Goal5790-A1 frozen Home-authority receipt drifted")
    line = subprocess.run(
        [
            "nvidia-smi",
            "--query-gpu=name,driver_version,uuid,compute_cap",
            "--format=csv,noheader",
        ],
        check=True,
        text=True,
        capture_output=True,
    ).stdout.strip()
    fields = tuple(item.strip() for item in line.split(","))
    expected = (
        authority.get("gpu_name"), authority.get("driver_version"),
        authority.get("gpu_uuid"), authority.get("compute_capability"))
    if expected != (HOME_GPU, HOME_DRIVER, HOME_UUID, HOME_CC):
        raise RuntimeError("Goal5790-A1 frozen Home identity fields drifted")
    if platform.node() != HOME_HOSTNAME or fields != expected:
        raise RuntimeError(
            "Goal5790-A1 worker requires exact Home lx1 authority: "
            f"host={platform.node()!r}, gpu_line={line!r}")
    result: dict[str, object] = {
        "hostname": HOME_HOSTNAME,
        "gpu": HOME_GPU,
        "driver": HOME_DRIVER,
        "uuid": HOME_UUID,
        "compute_capability": HOME_CC,
        "classification": "exact_home_lx1__not_pod",
        "frozen_home_authority_file_sha256": actual_file_sha256,
        "frozen_home_authority_receipt_sha256": claimed_receipt,
        "home_toolchain_identity_sha256": canonical_sha256({
            field: authority[field] for field in HOME_TOOLCHAIN_FIELDS}),
    }
    result["home_machine_authority_sha256"] = canonical_sha256(result)
    if result["home_machine_authority_sha256"] != expected_machine_sha256:
        raise RuntimeError("Goal5790-A1 Home-machine authority digest drift")
    return result


def _binary_column(kind: str, values: Sequence[int | float]) -> dict[str, object]:
    formats = {"f32": "f", "u32": "I", "u64": "Q"}
    if kind not in formats:
        raise AssertionError(kind)
    normalized = tuple(
        float(value) if kind == "f32" else int(value) for value in values)
    raw = b"".join(struct.pack("<" + formats[kind], value)
                   for value in normalized)
    return {
        "scalar_type": kind,
        "endianness": "little",
        "count": len(normalized),
        "bytes_hex": raw.hex(),
        "bytes_sha256": hashlib.sha256(raw).hexdigest(),
    }


def _triangle_exact_input(
    *, family: str, vertices, triangles, queries,
    front_values=(), back_values=(), weights=(), event_capacity=None,
) -> dict[str, object]:
    columns = {
        "vertices_xyz": _binary_column(
            "f32", tuple(value for row in vertices for value in row)),
        "triangle_indices": _binary_column(
            "u32", tuple(value for row in triangles for value in row)),
        "query_origin_direction_tmax": _binary_column(
            "f32", tuple(
                value for origin, direction, tmax in queries
                for value in (*origin, *direction, tmax))),
        "primitive_front_values": _binary_column("u32", front_values),
        "primitive_back_values": _binary_column("u32", back_values),
        "query_weights": _binary_column("u64", weights),
    }
    return {
        "schema": "rtdl.goal5790_a1.exact_executed_input.v1",
        "family": family,
        "columns": columns,
        "event_capacity": event_capacity,
    }


def _relation_exact_input(*, indexed_boxes, source_boxes, capacity: int):
    return {
        "schema": "rtdl.goal5790_a1.exact_executed_input.v1",
        "family": "custom_aabb.bounded_relation",
        "columns": {
            "indexed_bounds_xyxy": _binary_column(
                "f32", tuple(value for row in indexed_boxes
                             for value in row[:4])),
            "indexed_ids": _binary_column(
                "u32", tuple(row[4] for row in indexed_boxes)),
            "source_bounds_xyxy": _binary_column(
                "f32", tuple(value for row in source_boxes
                             for value in row[:4])),
            "source_ids": _binary_column(
                "u32", tuple(row[4] for row in source_boxes)),
        },
        "capacity": int(capacity),
        "minimum_overlap_f32": _binary_column("f32", (0.0,)),
    }


def _executed_input(value: Mapping[str, object]) -> dict[str, object]:
    """Freeze exact little-endian device-input bytes, never decimal aliases."""

    payload = _jsonable(value)
    assert isinstance(payload, dict)
    return {
        "executed_input": payload,
        "executed_input_sha256": _digest(payload),
    }


def _require_isolated_non_authority_caches() -> dict[str, object]:
    forbidden = sorted(
        key for key in os.environ if key.startswith("RTDL_V4_FORMAL_LEAF_CACHE"))
    if forbidden:
        raise RuntimeError(
            f"Goal5790-A1 forbids ambient formal-leaf cache authority: {forbidden!r}")
    paths = {}
    for variable in ("CUPY_CACHE_DIR", "NUMBA_CACHE_DIR"):
        raw = os.environ.get(variable)
        if not raw:
            raise RuntimeError(f"Goal5790-A1 requires isolated {variable}")
        path = Path(raw)
        if not path.is_absolute() or not path.is_dir() or any(path.iterdir()):
            raise RuntimeError(
                f"Goal5790-A1 {variable} must name a fresh empty directory")
        paths[variable] = path.resolve().as_posix()
    if paths["CUPY_CACHE_DIR"] == paths["NUMBA_CACHE_DIR"]:
        raise RuntimeError("Goal5790-A1 CuPy and Numba caches must be distinct")
    return {
        "formal_leaf_cache_environment_cleared": True,
        "cupy_cache_dir": paths["CUPY_CACHE_DIR"],
        "numba_cache_dir": paths["NUMBA_CACHE_DIR"],
        "initially_empty": True,
        "per_arm_isolated": True,
        "cache_is_execution_authority": False,
        "cache_contents_used_as_evidence": False,
    }


def _receipt_is_complete(receipt: Mapping[str, object]) -> bool:
    if receipt.get("physical_executor_classification") \
            != "optix_traversal_observed":
        return False
    snapshot = receipt.get("native_snapshot")
    if not isinstance(snapshot, Mapping):
        return False
    successful = snapshot.get("successful_launch_count")
    complete = snapshot.get("complete_context_launch_count")
    raygen = snapshot.get("raygen_invocation_count")
    zero_fields = (
        "failed_launch_count",
        "incomplete_context_launch_count",
        "pending_context_at_finish",
        "session_error",
    )
    return type(successful) is int and successful > 0 \
        and type(complete) is int and complete > 0 \
        and complete == successful \
        and all(type(snapshot.get(field)) is int
                and snapshot[field] == 0 for field in zero_fields) \
        and type(raygen) is int and raygen > 0 \
        and receipt.get("expected_program_observed_at_receipt_edge") is True


def _case_from_suite(path: Path, case_id: str) -> tuple[dict, dict]:
    suite = parse_suite_json(path.read_text(encoding="utf-8"))
    case = next((row for row in suite["cases"] if row["case_id"] == case_id), None)
    if case is None:
        raise ValueError(f"case is absent from exact suite: {case_id}")
    return suite, case


def _execution_spec_case(
    path: Path, expected_sha256: str, *, suite_sha256: str,
    case: Mapping[str, object],
) -> tuple[dict[str, object], dict[str, object]]:
    value = json.loads(path.resolve().read_text(encoding="utf-8"))
    body = dict(value)
    claimed = body.pop("execution_spec_sha256", None)
    if claimed != expected_sha256 or canonical_sha256(body) != claimed \
            or value.get("schema") \
                != "rtdl.goal5790_a1.home_execution_spec.v2" \
            or value.get("upstream_suite_sha256") != suite_sha256:
        raise RuntimeError("Goal5790-A1 worker execution-spec authority drift")
    _verify_execution_spec_source_members(value)
    rows = value.get("cases")
    row = next((item for item in rows
                if item.get("case_id") == case["case_id"]), None) \
        if isinstance(rows, list) else None
    if not isinstance(row, dict) \
            or row.get("upstream_case_sha256") != case["case_sha256"]:
        raise RuntimeError("Goal5790-A1 worker case-spec identity drift")
    case_body = dict(row)
    case_claimed = case_body.pop("case_execution_spec_sha256", None)
    if case_claimed != canonical_sha256(case_body):
        raise RuntimeError("Goal5790-A1 worker case-spec seal drift")
    return value, row


def _verify_execution_spec_source_members(
    value: Mapping[str, object],
) -> tuple[dict[str, object], ...]:
    """Rehash every source byte frozen by the independent pre-run spec."""

    raw_rows = value.get("pre_run_source_members")
    if not isinstance(raw_rows, list) or not raw_rows:
        raise RuntimeError("Goal5790-A1 execution spec lacks source members")
    rows: list[dict[str, object]] = []
    seen: set[str] = set()
    for index, raw in enumerate(raw_rows):
        if not isinstance(raw, Mapping):
            raise RuntimeError(
                f"Goal5790-A1 source member {index} is not an object")
        logical = raw.get("logical_path")
        expected = raw.get("sha256")
        roles = raw.get("roles")
        if not isinstance(logical, str) or not logical \
                or not isinstance(expected, str) or len(expected) != 64 \
                or not isinstance(roles, list) or not roles \
                or not all(isinstance(role, str) and role for role in roles):
            raise RuntimeError(
                f"Goal5790-A1 source member {index} is malformed")
        relative = Path(logical)
        if relative.is_absolute() or ".." in relative.parts \
                or logical in seen:
            raise RuntimeError(
                f"Goal5790-A1 source member path is unsafe/duplicate: {logical}")
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT.resolve())
        except ValueError as exc:
            raise RuntimeError(
                f"Goal5790-A1 source member escapes repository: {logical}") from exc
        if not path.is_file() or _sha_file(path) != expected:
            raise RuntimeError(
                f"Goal5790-A1 frozen source bytes drifted: {logical}")
        seen.add(logical)
        rows.append(dict(raw))
    return tuple(rows)


def _policy_for_bridge(case: Mapping[str, object], *, semantic: bool) -> dict[str, str]:
    canonical, diagnostic = _TRUSTED_POLICY_BY_CASE[str(case["case_id"])]
    if dict(case["semantic_authority"]["policy"]) != canonical \
            or dict(case["physical_authority"]["guarantees"]) != diagnostic:
        raise RuntimeError("CPU suite and trusted classifier catalog diverged")
    policy = dict(canonical if semantic else diagnostic)
    contract_id = str(case["semantic_authority"]["contract_id"])
    policy["input_type"] = "frozen_minimal_witness:" + contract_id
    policy["output_type"] = "declared_semantic_output:" + contract_id
    # Orientation is a binding property rather than one of the six CPU policy
    # fields.  Reflect the counterfactual in the product calculus' output
    # contract instead of pretending the declarations are compatible.
    if not semantic and case["case_id"] == CASE_IDS[4]:
        policy["output_type"] = "swapped_front_back_adjacency_output"
    return policy


def _install_test_only_rtdsl_namespace() -> None:
    """Avoid executing the broad package initializer in a reject-only PID."""

    if "rtdsl" in sys.modules:
        raise RuntimeError(
            "product rejection must begin before the rtdsl package is imported")
    import importlib.machinery

    package_root = ROOT / "src/rtdsl"
    package = ModuleType("rtdsl")
    package.__path__ = [str(package_root)]
    package.__package__ = "rtdsl"
    package.__spec__ = importlib.machinery.ModuleSpec(
        "rtdsl", loader=None, is_package=True)
    package.__spec__.submodule_search_locations = [str(package_root)]
    sys.modules["rtdsl"] = package


def _forbidden_reject_imports(names: Sequence[str]) -> tuple[str, ...]:
    return tuple(sorted(name for name in names if name == "cupy"
                        or name.startswith("cupy.") or name == "numba"
                        or name.startswith("numba.")
                        or "optix_runtime" in name
                        or "optix_compiler" in name))


def _admit_live_family(issued, live) -> object:
    """Call the exact public product facade, never the inert evaluator."""

    from rtdsl.v4_semantically_admitted_compiler import (
        admit_bounded_relation_compilation,
        admit_builtin_triangle_compilation,
        admit_triangle_reduction_compilation,
    )

    if live.family == "builtin_triangle":
        return admit_builtin_triangle_compilation(
            issued.semantic_authority,
            issued.diagnostic_physical_authority,
            authority=live.authority, plan=live.plan, abi=live.abi)
    if live.family == "triangle_reduction":
        return admit_triangle_reduction_compilation(
            issued.semantic_authority,
            issued.diagnostic_physical_authority,
            authority=live.authority, contract=live.contract, abi=live.abi)
    if live.family == "bounded_relation":
        return admit_bounded_relation_compilation(
            issued.semantic_authority,
            issued.diagnostic_physical_authority,
            authority=live.authority, contract=live.contract, abi=live.abi)
    raise AssertionError(live.family)


def _product_reject(case: Mapping[str, object], args) -> dict[str, object]:
    """Reject one actual live family tuple before low-level compilation."""

    before_names = set(sys.modules)
    process_before = _process_audit_snapshot()
    _install_test_only_rtdsl_namespace()
    target = _target(args)
    issued = _issue_case_authorities(case, target)
    facade_path = ROOT / "src/rtdsl/v4_semantically_admitted_compiler.py"
    calculus_path = ROOT / "src/rtdsl/v4_semantic_physical_admission.py"
    worker_path = Path(__file__).resolve()
    finding: dict[str, object]
    diagnostic_live = None
    diagnostic_attempt = None
    production_facade_called = False

    if case["case_id"] == CASE_IDS[4]:
        from rtdsl.v4_typed_physical_schema import PhysicalSchemaError
        attempt = _build_builtin_orientation_attempt(
            case, target, diagnostic=True)
        diagnostic_attempt = _builtin_orientation_attempt_snapshot(attempt)
        try:
            from rtdsl.v4_typed_physical_schema import verify_typed_physical_schema
            verify_typed_physical_schema(
                attempt.callback, attempt.schema, target=target,
                orientation_authorities={
                    attempt.orientation.authority_sha256: attempt.orientation})
        except PhysicalSchemaError as error:
            if error.code != "triangle_orientation_mapping":
                raise RuntimeError(
                    f"Particle rejected at the wrong product gate: {error}") from error
            finding = {
                "rule_id": error.code,
                "path": error.path,
                "detail": error.message,
                "gate": "verify_typed_physical_schema",
            }
        else:  # pragma: no cover - hard safety assertion
            raise RuntimeError("swapped Particle orientation escaped product schema")
    else:
        from rtdsl.v4_semantic_physical_admission import (
            SemanticPhysicalAdmissionError,
        )
        diagnostic_live = issued.diagnostic
        if diagnostic_live is None \
                or issued.diagnostic_physical_authority is None:
            raise RuntimeError("diagnostic registry authority was not issued")
        production_facade_called = True
        try:
            _admit_live_family(issued, diagnostic_live)
        except SemanticPhysicalAdmissionError as error:
            finding = {
                "rule_id": error.code,
                "path": error.path,
                "detail": error.message,
                "gate": "v4_semantically_admitted_compiler.admit_*",
            }
        else:  # pragma: no cover - hard safety assertion
            raise RuntimeError("counterfactual received executable authority")

    process_after = _process_audit_snapshot()
    imported = sorted(set(sys.modules) - before_names)
    forbidden = _forbidden_reject_imports(imported)
    if forbidden:
        raise RuntimeError(
            f"rejection imported a GPU/low-level compiler route: {forbidden!r}")
    driver_maps = tuple(
        line for line in process_after["relevant_memory_maps"]
        if "libcuda" in line.lower() or "libcudart" in line.lower())
    if driver_maps:
        raise RuntimeError(
            "product rejection mapped a CUDA driver/runtime library")
    reasons = expected_rejection_reasons(case)
    if reasons != (case["expected_rule_id"],):
        raise RuntimeError("CPU and product rejection identities diverged")
    decision = {
        "verdict": "INCOMPATIBLE",
        "finding": finding,
        "semantic_authority_sha256": issued.semantic_authority.authority_sha256,
        "physical_authority_sha256": (
            None if issued.diagnostic_physical_authority is None
            else issued.diagnostic_physical_authority.authority_sha256),
        "canonical_live_family": _family_live_snapshot(issued.canonical),
        "diagnostic_live_family": (
            None if diagnostic_live is None
            else _family_live_snapshot(diagnostic_live)),
        "diagnostic_family_attempt": diagnostic_attempt,
    }
    return {
        "engine": "production_semantically_admitted_compiler_facade_v1",
        "verdict": "INCOMPATIBLE",
        "product_rule_ids": [finding["rule_id"]],
        "named_case_rule_id": case["expected_rule_id"],
        "product_rejection_gate": finding["gate"],
        "production_facade_called": production_facade_called,
        "decision": decision,
        "decision_sha256": _digest(decision),
        "product_facade_path": facade_path.relative_to(ROOT).as_posix(),
        "product_facade_sha256": _sha_file(facade_path),
        "semantic_physical_calculus_path": (
            calculus_path.relative_to(ROOT).as_posix()),
        "semantic_physical_calculus_sha256": _sha_file(calculus_path),
        "trusted_test_classifier_path": worker_path.relative_to(ROOT).as_posix(),
        "trusted_test_classifier_sha256": _sha_file(worker_path),
        "semantic_authority": issued.semantic_authority.to_dict(),
        "physical_registry": issued.registry.to_dict(),
        "canonical_physical_authority": (
            issued.canonical_physical_authority.to_dict()),
        "diagnostic_physical_authority": (
            None if issued.diagnostic_physical_authority is None
            else issued.diagnostic_physical_authority.to_dict()),
        "canonical_live_family": _family_live_snapshot(issued.canonical),
        "diagnostic_live_family": (
            None if diagnostic_live is None
            else _family_live_snapshot(diagnostic_live)),
        "diagnostic_family_attempt": diagnostic_attempt,
        "target_sha256": target.target_sha256,
        "native_library_sha256": target.native_sha256,
        "process_audit_before": process_before,
        "process_audit_after": process_after,
        "new_module_names": imported,
        "forbidden_gpu_or_compiler_imports": list(forbidden),
        "compiler_call_count": 0,
        "low_level_compiler_call_count": 0,
        "native_prepare_call_count": 0,
        "native_execute_call_count": 0,
        "traversal_launch_count": 0,
        "cuda_or_gpu_library_map_observed": bool(
            process_after["relevant_memory_maps"]),
        "cuda_driver_initialization_observed": bool(driver_maps),
        "cuda_driver_initialization_proven_absent": False,
        "cuda_initialization_evidence_kind": (
            "negative_module_and_proc_maps_observation__not_a_formal_absence_proof"),
        "execution_authorized": False,
        "executable_issued": False,
        "claim_boundary": {
            "public_facade_rejects_raw_caller_self_proof": True,
            "compiler_internal_classifier_is_trusted_tcb": True,
            "malicious_same_process_reflection_resisted": False,
            "python_semantics_automatically_inferred": False,
            "concrete_runtime_input_certified_by_compile_admission": False,
        },
    }


def _compiler_kwargs(args) -> dict[str, object]:
    return {
        "compute_capability": (int(args.cc[0]), int(args.cc[1])),
        "optix_include": args.optix_include,
        "cuda_include": args.cuda_include,
        "expected_python_version": args.expected_python,
        "expected_numba_version": args.expected_numba,
        "expected_numpy_version": args.expected_numpy,
    }


def _accepted_declarations(
    case: Mapping[str, object], *, callback, schema_sha256: str,
    geometry_family: str, orientation_contract_sha256: str,
    diagnostic: bool = False,
) -> tuple[dict[str, object], dict[str, object]]:
    """Bind accepted semantics to exact live callback/schema identities."""

    policy = _policy_for_bridge(case, semantic=True)
    physical_policy = _policy_for_bridge(case, semantic=not diagnostic)
    stage_sources = _TRUSTED_STAGE_SOURCES_BY_CASE[str(case["case_id"])][
        1 if diagnostic else 0]
    # The physical manifest contains implementation bytes only, and every
    # member is consumed by at least one explicit stage edge.  Independent
    # semantic oracles remain on the semantic-authority side of the calculus.
    manifest = {
        path: _sha_file(ROOT / path)
        for path in sorted(set(stage_sources.values()))
    }
    graph = {
        "encode": (["semantic_input"], ["geometry", "query_state"]),
        "ray": (["query_state"], ["ray"]),
        "trace": (["geometry", "ray"], ["hit_stream"]),
        "continuation": (["hit_stream"], ["candidate_output"]),
        "decode": (["candidate_output"], ["semantic_output"]),
    }
    semantic = {
        "contract_id": str(case["semantic_authority"]["contract_id"]),
        "algorithm_identity": "goal5790_a1." + str(case["case_id"]),
        "declared_domain_sha256": _digest(case["minimal_witness"]),
        "policy": policy,
        "required_hit_semantics": ["bound_hit_stream"],
        "orientation_contract_sha256": orientation_contract_sha256,
        "specification_source_sha256": str(
            case["semantic_authority"]["oracle_source_sha256"]),
    }
    physical = {
        "encoding_id": (
            "diagnostic." if diagnostic else "accepted.")
            + str(case["case_id"]),
        "supported_algorithm_identity": semantic["algorithm_identity"],
        "supported_domain_sha256": semantic["declared_domain_sha256"],
        "orientation_contract_sha256": orientation_contract_sha256,
        "geometry_family": geometry_family,
        "schema_sha256": schema_sha256,
        "callback_ir_sha256": callback.ir_sha256,
        "effect_digest": callback.effect_digest,
        "guarantees": physical_policy,
        "maps": [
            {
                "kind": kind,
                "source_id": stage_sources[kind],
                "source_sha256": manifest[stage_sources[kind]],
                "consumes": consumes,
                "produces": produces,
            }
            for kind, (consumes, produces) in graph.items()
        ],
        "hit_semantics": ["bound_hit_stream"],
        "gas_graph_depth": 1,
        "gas_sbt_record_stride": 1,
        "gas_update_policy": "static",
        "buffer_contract_sha256": _digest({
            "case": case["case_sha256"],
            "callback": callback.ir_sha256,
            "schema": schema_sha256,
        }),
        "required_target_capabilities": [
            "bound_program_bundle", "optix",
            "optix_builtin_triangle" if geometry_family == "builtin_triangle"
            else "optix_custom_aabb",
        ],
        "source_manifest": manifest,
    }
    return semantic, physical


def _build_builtin_orientation_attempt(case, target, *, diagnostic: bool):
    from rtdsl.v4_builtin_triangle_standard_library import (
        adjacency_schema,
        compile_adjacency_callback,
        make_orientation_authority,
    )
    from rtdsl.v4_typed_physical_schema import (
        AdjacencySide,
        triangle_author_semantics_sha256,
    )

    callback = compile_adjacency_callback()
    family = (
        "particle_orientation" if case["case_id"] == CASE_IDS[4]
        else "rtxrmq")
    source_semantics = _digest({
        "case_source_authority": case["source_authority"]["authority_sha256"],
        "family": family,
    })
    if family == "rtxrmq":
        # Classifier construction binds the frozen oracle source identity; it
        # must not import the application execution module in a reject PID.
        independent_oracle = case["semantic_authority"]["oracle_source_sha256"]
    else:
        independent_oracle = case["semantic_authority"]["oracle_source_sha256"]
    orientation = make_orientation_authority(
        callback, source_semantics_sha256=source_semantics,
        independent_oracle_sha256=independent_oracle)
    if diagnostic and family == "particle_orientation":
        # Exercise the real earliest product gate.  No fake SP039 mapping is
        # manufactured: the typed physical verifier itself must reject the
        # swapped author rule as ``triangle_orientation_mapping``.
        orientation = replace(
            orientation,
            front_hit_selects=AdjacencySide.BACK,
            back_hit_selects=AdjacencySide.FRONT,
            author_semantics_sha256=triangle_author_semantics_sha256(
                front_hit_kind=orientation.front_hit_kind,
                back_hit_kind=orientation.back_hit_kind,
                front_hit_selects=AdjacencySide.BACK,
                back_hit_selects=AdjacencySide.FRONT,
            ),
        )
    schema = adjacency_schema(
        callback, orientation_authority_sha256=orientation.authority_sha256)
    return SimpleNamespace(
        family="builtin_triangle", callback=callback, schema=schema,
        target=target, orientation=orientation,
        schema_sha256=schema.schema_sha256,
        geometry_family=schema.geometry_family.value,
        orientation_contract_sha256=orientation.authority_sha256,
    )


def _builtin_orientation_attempt_snapshot(value) -> dict[str, object]:
    orientation = value.orientation
    return {
        "family": value.family,
        "callback_ir_sha256": value.callback.ir_sha256,
        "effect_digest": value.callback.effect_digest,
        "schema_sha256": value.schema_sha256,
        "target_sha256": value.target.target_sha256,
        "orientation_authority_sha256": orientation.authority_sha256,
        "orientation_author_source_sha256": orientation.author_source_sha256,
        "orientation_independent_oracle_sha256": (
            orientation.independent_cpu_oracle_sha256),
        "front_hit_kind": int(orientation.front_hit_kind),
        "back_hit_kind": int(orientation.back_hit_kind),
        "front_hit_selects": orientation.front_hit_selects.value,
        "back_hit_selects": orientation.back_hit_selects.value,
        "verified_family_authority_issued": False,
        "plan_issued": False,
        "abi_issued": False,
    }


def _build_builtin_family_inputs(case, target, *, diagnostic: bool):
    from rtdsl.v4_callback_abi import compile_callback_abi
    from rtdsl.v4_typed_physical_schema import (
        default_reference_templates,
        lower_canonical_reference_plan,
        verify_typed_physical_schema,
    )

    attempt = _build_builtin_orientation_attempt(
        case, target, diagnostic=diagnostic)
    authority = verify_typed_physical_schema(
        attempt.callback, attempt.schema,
        target=target,
        orientation_authorities={
            attempt.orientation.authority_sha256: attempt.orientation},
    )
    plan = lower_canonical_reference_plan(
        authority, default_reference_templates())
    abi = compile_callback_abi(
        attempt.callback, physical_schema_authority=authority)
    return SimpleNamespace(
        family="builtin_triangle", callback=attempt.callback, authority=authority,
        artifact=plan, plan=plan, abi=abi, proof=None,
        schema_sha256=authority.schema.schema_sha256,
        geometry_family=authority.schema.geometry_family.value,
        orientation_contract_sha256=(
            attempt.orientation.authority_sha256),
        canonical_template_id=plan.template_id.value,
    )


def _build_relation_family_inputs(case, target, *, diagnostic: bool):
    from rtdsl.v4_bounded_relation import (
        BoundedRelationEmissionSchema,
        compile_bounded_relation_contract,
        verify_bounded_relation_schema,
    )
    from rtdsl.v4_box_relation_callback import (
        compile_callback, manifest, physical_schema,
    )
    from rtdsl.v4_callback_abi import compile_callback_abi
    from rtdsl.v4_callback_frontend import compile_callback_source
    from rtdsl.v4_typed_physical_schema import verify_typed_physical_schema

    callback = (
        compile_callback_source(_strict_box_source(), manifest())
        if diagnostic else compile_callback())
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity=4, minimum_overlap_f32=0.0)
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _relation_proof(callback, case)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    return SimpleNamespace(
        family="bounded_relation", callback=callback, authority=authority,
        artifact=contract, contract=contract, abi=abi, proof=proof,
        schema_sha256=authority.schema.schema_sha256,
        geometry_family=authority.physical.schema.geometry_family.value,
        orientation_contract_sha256=NO_ORIENTATION_CONTRACT_SHA256,
        canonical_template_id=contract.template_id,
    )


def _build_triangle_family_inputs(case, target, *, diagnostic: bool):
    from rtdsl.v4_triangle_reduction import (
        compile_triangle_reduction_abi,
        compile_triangle_reduction_contract,
        verify_triangle_reduction_schema,
    )
    from rtdsl.v4_triangle_standard_library import (
        all_hit_count_schema,
        compile_count_callback,
        weighted_hit_count_schema,
    )

    callback = compile_count_callback()
    overflow = case["case_id"] == CASE_IDS[2]
    weighted = overflow or not diagnostic
    schema = (
        weighted_hit_count_schema(callback)
        if weighted else all_hit_count_schema(callback))
    authority = verify_triangle_reduction_schema(
        callback, schema, target=target)
    proof = _triangle_proof(callback, case)
    abi = compile_triangle_reduction_abi(
        authority, any_hit_proof_authority=proof)
    contract = compile_triangle_reduction_contract(
        authority, abi_sha256=abi.abi_sha256)
    return SimpleNamespace(
        family="triangle_reduction", callback=callback, authority=authority,
        artifact=contract, contract=contract, abi=abi, proof=proof,
        schema_sha256=authority.schema.schema_sha256,
        geometry_family="builtin_triangle",
        orientation_contract_sha256=NO_ORIENTATION_CONTRACT_SHA256,
        canonical_template_id=contract.template_id,
    )


def _build_family_inputs(case, target, *, diagnostic: bool):
    if case["case_id"] in CASE_IDS[:2] or case["case_id"] == CASE_IDS[4]:
        return _build_builtin_family_inputs(case, target, diagnostic=diagnostic)
    if case["case_id"] in CASE_IDS[2:4]:
        return _build_triangle_family_inputs(case, target, diagnostic=diagnostic)
    if case["case_id"] == CASE_IDS[5]:
        return _build_relation_family_inputs(case, target, diagnostic=diagnostic)
    raise AssertionError(case["case_id"])


def _family_live_snapshot(value) -> dict[str, object]:
    artifact = value.artifact
    authority = value.authority
    return {
        "family": value.family,
        "callback_ir_sha256": value.callback.ir_sha256,
        "effect_digest": value.callback.effect_digest,
        "schema_sha256": value.schema_sha256,
        "target_sha256": value.authority.target.target_sha256
        if value.family == "triangle_reduction" else (
            value.authority.physical.target.target_sha256
            if value.family == "bounded_relation"
            else value.authority.target.target_sha256),
        "artifact_kind": "plan" if hasattr(value, "plan") else "contract",
        "artifact_sha256": (
            artifact.plan_sha256 if hasattr(artifact, "plan_sha256")
            else artifact.contract_sha256),
        "abi_sha256": value.abi.abi_sha256,
        "orientation_contract_sha256": value.orientation_contract_sha256,
        "canonical_template_id": value.canonical_template_id,
        "proof_sha256": getattr(value.proof, "proof_sha256", None),
        "family_authority_nonce": authority.authority_nonce,
        "family_authority_sha256": _runtime_family_authority_sha256(value),
    }


def _runtime_family_authority_sha256(value) -> str:
    authority = value.authority
    if value.family == "builtin_triangle":
        orientation = authority.triangle_orientation_authority
        return _digest({
            "callback_ir_sha256": authority.callback.ir_sha256,
            "callback_effect_digest": authority.callback.effect_digest,
            "schema_sha256": authority.schema.schema_sha256,
            "target_sha256": authority.target.target_sha256,
            "triangle_orientation_authority_sha256": (
                None if orientation is None else orientation.authority_sha256),
            "authority_nonce": authority.authority_nonce,
        })
    if value.family == "triangle_reduction":
        return _digest({
            "callback": authority.callback.ir_sha256,
            "effect": authority.callback.effect_digest,
            "schema": authority.schema.schema_sha256,
            "target": authority.target.target_sha256,
            "nonce": authority.authority_nonce,
        })
    if value.family == "bounded_relation":
        return _digest({
            "callback": authority.physical.callback.ir_sha256,
            "effect": authority.physical.callback.effect_digest,
            "physical_schema": authority.physical.schema.schema_sha256,
            "target": authority.physical.target.target_sha256,
            "relation_schema": authority.schema.schema_sha256,
            "nonce": authority.authority_nonce,
        })
    raise AssertionError(value.family)


def _issue_case_authorities(case, target):
    """Issue the test-only registry before any low-level compilation."""

    from rtdsl.v4_semantic_physical_admission import (
        PhysicalEncodingEligibility,
        _issue_compiler_physical_guarantee_registry,
        issue_registered_physical_guarantee_authority,
        issue_semantic_requirement_authority,
        physical_guarantee_registry_entry,
    )

    canonical = _build_family_inputs(case, target, diagnostic=False)
    semantic, canonical_physical = _accepted_declarations(
        case, callback=canonical.callback,
        schema_sha256=canonical.schema_sha256,
        geometry_family=canonical.geometry_family,
        orientation_contract_sha256=canonical.orientation_contract_sha256)
    semantic_authority = issue_semantic_requirement_authority(
        semantic,
        oracle_source_sha256=str(
            case["semantic_authority"]["oracle_source_sha256"]),
        issuer_domain="rtdl.app.goal5790_a1",
    )
    classifier_sha = _sha_file(Path(__file__).resolve())
    canonical_id = "goal5790_a1." + str(case["case_id"]) + ".canonical"
    entries = [physical_guarantee_registry_entry(
        canonical_id, canonical_physical,
        eligibility=PhysicalEncodingEligibility.CANONICAL_PRODUCTION,
        canonical_template_id=canonical.canonical_template_id,
        classifier_source_sha256=classifier_sha,
    )]
    diagnostic = None
    diagnostic_id = None
    diagnostic_physical = None
    if case["case_id"] != CASE_IDS[4]:
        diagnostic = _build_family_inputs(case, target, diagnostic=True)
        _semantic_again, diagnostic_physical = _accepted_declarations(
            case, callback=diagnostic.callback,
            schema_sha256=diagnostic.schema_sha256,
            geometry_family=diagnostic.geometry_family,
            orientation_contract_sha256=diagnostic.orientation_contract_sha256,
            diagnostic=True)
        diagnostic_id = (
            "goal5790_a1." + str(case["case_id"]) + ".diagnostic")
        entries.append(physical_guarantee_registry_entry(
            diagnostic_id, diagnostic_physical,
            eligibility=(
                PhysicalEncodingEligibility.DIAGNOSTIC_NONREGISTRABLE),
            canonical_template_id=None,
            classifier_source_sha256=classifier_sha,
        ))
    registry = _issue_compiler_physical_guarantee_registry(
        entries, registry_source_sha256=classifier_sha)
    canonical_authority = issue_registered_physical_guarantee_authority(
        registry, canonical_id)
    diagnostic_authority = (
        None if diagnostic_id is None else
        issue_registered_physical_guarantee_authority(registry, diagnostic_id))
    return SimpleNamespace(
        semantic_authority=semantic_authority,
        registry=registry,
        canonical=canonical,
        canonical_physical_authority=canonical_authority,
        diagnostic=diagnostic,
        diagnostic_physical_authority=diagnostic_authority,
        canonical_physical=canonical_physical,
        diagnostic_physical=diagnostic_physical,
        classifier_source_sha256=classifier_sha,
    )


def build_pre_run_case_authorities(case, target) -> dict[str, object]:
    """Inert pre-run snapshot consumed by the separately frozen T4 spec."""

    issued = _issue_case_authorities(case, target)
    early_reject = None
    diagnostic_attempt = None
    if case["case_id"] == CASE_IDS[4]:
        from rtdsl.v4_typed_physical_schema import PhysicalSchemaError
        attempt = _build_builtin_orientation_attempt(
            case, target, diagnostic=True)
        diagnostic_attempt = _builtin_orientation_attempt_snapshot(attempt)
        try:
            from rtdsl.v4_typed_physical_schema import verify_typed_physical_schema
            verify_typed_physical_schema(
                attempt.callback, attempt.schema, target=target,
                orientation_authorities={
                    attempt.orientation.authority_sha256: attempt.orientation})
        except PhysicalSchemaError as error:
            early_reject = {
                "gate": "verify_typed_physical_schema",
                "code": error.code,
                "path": error.path,
                "message": error.message,
            }
        else:  # pragma: no cover - hard safety assertion
            raise RuntimeError("swapped orientation escaped typed schema gate")
    return {
        "schema": "rtdl.goal5790_a1.pre_run_case_authorities.v1",
        "case_id": case["case_id"],
        "case_sha256": case["case_sha256"],
        "classifier_source_sha256": issued.classifier_source_sha256,
        "semantic_authority": issued.semantic_authority.to_dict(),
        "physical_registry": issued.registry.to_dict(),
        "canonical_physical_authority": (
            issued.canonical_physical_authority.to_dict()),
        "diagnostic_physical_authority": (
            None if issued.diagnostic_physical_authority is None
            else issued.diagnostic_physical_authority.to_dict()),
        "canonical_live_family": _family_live_snapshot(issued.canonical),
        "diagnostic_live_family": (
            None if issued.diagnostic is None
            else _family_live_snapshot(issued.diagnostic)),
        "diagnostic_early_reject": early_reject,
        "diagnostic_family_attempt": diagnostic_attempt,
        "diagnostic_transform_authority": _diagnostic_transform_authority(case),
        "low_level_compiler_call_count": 0,
        "native_prepare_call_count": 0,
        "native_execute_call_count": 0,
        "traversal_launch_count": 0,
    }


def _diagnostic_transform_authority(case) -> dict[str, object]:
    worker_path = Path(__file__).resolve()
    value: dict[str, object] = {
        "case_id": case["case_id"],
        "transform_id": case["unsafe_transform"]["transform_id"],
        "unsafe_transform_sha256": _digest(case["unsafe_transform"]),
        "implementation_path": worker_path.relative_to(ROOT).as_posix(),
        "implementation_sha256": _sha_file(worker_path),
        "test_only_nonregistrable": True,
        "production_authority_minted": False,
    }
    if case["case_id"] == CASE_IDS[2]:
        value["unchecked_u64_kernel_source_sha256"] = hashlib.sha256(
            _UNCHECKED_U64_CONTINUATION_SOURCE.encode("utf-8")).hexdigest()
        value["unchecked_u64_kernel_entry"] = (
            "goal5790_a1_unchecked_weighted_sum")
    if case["case_id"] == CASE_IDS[5]:
        value["strict_callback_source_sha256"] = hashlib.sha256(
            _strict_box_source().encode("utf-8")).hexdigest()
    value["transform_authority_sha256"] = _digest(value)
    return value


def build_pre_run_suite_authorities(suite, target) -> dict[str, object]:
    """Build the CPU-only authority snapshot that T4 seals into spec v2."""

    rows = [build_pre_run_case_authorities(case, target)
            for case in suite["cases"]]
    sources: dict[str, set[str]] = {
        "scripts/goal5790_a1_home_worker.py": {
            "trusted_test_classifier", "diagnostic_transform"},
        "scripts/goal5790_a1_rejected_encoding_cases.py": {
            "cpu_contract_suite", "route_independent_counterexample_oracle"},
        "src/rtdsl/v4_semantic_physical_admission.py": {
            "semantic_physical_calculus", "compiler_registry"},
        "src/rtdsl/v4_semantically_admitted_compiler.py": {
            "production_admission_facade", "atomic_runtime_gate"},
        PARTICLE_GATE_AUTHORITY_PATH: {
            "governance_authority", "particle_earliest_gate_ruling"},
    }
    for canonical, diagnostic in _TRUSTED_STAGE_SOURCES_BY_CASE.values():
        for path in set(canonical.values()) | set(diagnostic.values()):
            sources.setdefault(path, set()).add("physical_stage_implementation")
    for case in suite["cases"]:
        oracle = str(case["semantic_authority"]["oracle_source_path"])
        sources.setdefault(oracle, set()).add("independent_semantic_oracle")
    source_rows = [{
        "logical_path": path,
        "evidence_path": "PRE_RUN_SOURCE/" + path,
        "sha256": _sha_file(ROOT / path),
        "roles": sorted(roles),
    } for path, roles in sorted(sources.items())]
    if _sha_file(ROOT / PARTICLE_GATE_AUTHORITY_PATH) \
            != PARTICLE_GATE_AUTHORITY_SHA256:
        raise RuntimeError("Particle earliest-gate amendment authority drifted")
    result: dict[str, object] = {
        "schema": "rtdl.goal5790_a1.pre_run_suite_authorities.v1",
        "upstream_suite_sha256": suite["suite_sha256"],
        "target_sha256": target.target_sha256,
        "native_library_sha256": target.native_sha256,
        "pre_run_source_members": source_rows,
        "particle_gate_authority_path": PARTICLE_GATE_AUTHORITY_PATH,
        "particle_gate_authority_sha256": PARTICLE_GATE_AUTHORITY_SHA256,
        "cases": rows,
        "low_level_compiler_call_count": 0,
        "native_prepare_call_count": 0,
        "native_execute_call_count": 0,
        "traversal_launch_count": 0,
    }
    result["pre_run_suite_authorities_sha256"] = _digest(result)
    return result


def _accepted_builtin_program(case, target, args, *, source_semantics_sha256,
                              independent_oracle_sha256):
    """Use only the production semantic-admission wrapper for controls."""

    from rtdsl.v4_semantically_admitted_compiler import (
        admit_builtin_triangle_compilation,
        compile_semantically_admitted_builtin_triangle_executable,
    )

    issued = _issue_case_authorities(case, target)
    live = issued.canonical
    # The call site supplies these independent digests; the classifier must
    # have rebuilt exactly the same orientation authority from the case.
    orientation = live.authority.triangle_orientation_authority
    if orientation.author_source_sha256 != source_semantics_sha256 \
            or orientation.independent_cpu_oracle_sha256 \
                != independent_oracle_sha256:
        raise RuntimeError("built-in proof inputs diverged from live classifier")
    admission = admit_builtin_triangle_compilation(
        issued.semantic_authority, issued.canonical_physical_authority,
        authority=live.authority, plan=live.plan, abi=live.abi)
    executable, compiler_log = (
        compile_semantically_admitted_builtin_triangle_executable(
            admission, live.authority, live.plan, live.abi,
            **_compiler_kwargs(args)))
    return SimpleNamespace(
        authority=live.authority, plan=live.plan, abi=live.abi,
        executable=executable, compiler_log=compiler_log,
        admission=admission)


def _diagnostic_builtin_program(target, args, *, source_semantics_sha256,
                                independent_oracle_sha256):
    from rtdsl.v4_builtin_triangle_standard_library import (
        compile_standard_builtin_triangle_program,
    )
    return compile_standard_builtin_triangle_program(
        target,
        source_semantics_sha256=source_semantics_sha256,
        independent_oracle_sha256=independent_oracle_sha256,
        **_compiler_kwargs(args),
    )


def _program_identity(program, target, *, family: str) -> dict[str, object]:
    authority = program.authority
    callback = getattr(authority, "callback", None)
    if callback is None and hasattr(authority, "physical"):
        callback = authority.physical.callback
    schema = getattr(authority, "schema", None)
    if schema is None and hasattr(authority, "physical"):
        schema = authority.physical.schema
    executable = program.executable
    composed_program_sha256 = executable.composed.ptx_sha256
    if family.startswith("builtin_triangle.") \
            and family != "builtin_triangle.triangle_reduction":
        runtime_family = "builtin_triangle"
        program_bundle = "v4_builtin_triangle_callback_ir_four_role_composed"
    elif family == "builtin_triangle.triangle_reduction":
        runtime_family = "triangle_reduction"
        program_bundle = "v4_builtin_triangle_checked_reduction_composed"
    elif family == "custom_aabb.bounded_relation":
        runtime_family = "bounded_relation"
        program_bundle = "v4_custom_aabb_bounded_relation_composed"
    else:
        raise AssertionError(family)
    family_value = SimpleNamespace(
        family=runtime_family, authority=authority)
    return {
        "family": family,
        "callback_ir_sha256": callback.ir_sha256,
        "callback_effect_digest": callback.effect_digest,
        "physical_or_family_schema_sha256": schema.schema_sha256,
        "target_sha256": target.target_sha256,
        "abi_sha256": program.abi.abi_sha256,
        "plan_sha256": getattr(getattr(program, "plan", None), "plan_sha256", None),
        "contract_sha256": getattr(
            getattr(program, "contract", None), "contract_sha256", None),
        "executable_sha256": executable.executable_sha256,
        "composed_program_sha256": composed_program_sha256,
        "expected_program_bundle": program_bundle,
        "family_authority_nonce": authority.authority_nonce,
        "family_authority_sha256": _runtime_family_authority_sha256(
            family_value),
        "semantic_admission_sha256": getattr(
            getattr(program, "admission", None), "admission_sha256", None),
        "native_library_sha256": target.native_sha256,
    }


def _traversal_semantic_binding(
    program, target, *, family: str, buffer_binding_sha256: str | None = None,
) -> dict[str, object]:
    composed = program.executable.composed.ptx_sha256
    if family.startswith("builtin_triangle.") \
            and family != "builtin_triangle.triangle_reduction":
        if not isinstance(buffer_binding_sha256, str):
            raise RuntimeError("built-in triangle receipt lacks buffer binding")
        return {
            "authority_nonce": program.authority.authority_nonce,
            "schema_sha256": program.authority.schema.schema_sha256,
            "plan_sha256": program.plan.plan_sha256,
            "abi_sha256": program.abi.abi_sha256,
            "composed_ptx_sha256": composed,
            "native_library_sha256": target.native_sha256,
            "buffer_binding_sha256": buffer_binding_sha256,
        }
    return {
        "authority": program.authority.authority_nonce,
        "contract": program.contract.contract_sha256,
        "abi": program.abi.abi_sha256,
        "composed_ptx": composed,
        "native": target.native_sha256,
    }


def _f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", float(value)))[0]


def _rmq_data(case, *, diagnostic: bool):
    app = _load_module(
        "Paper-reproduction-apps/goal5783-held-out-rtxrmq/v4_whole_app.py",
        "goal5790_a1_rtxrmq_app")
    witness = case["minimal_witness"]
    values = tuple(witness["values"])
    left, right = (int(value) for value in witness["interval"])
    data = app.build_v4_input(values=values, intervals=((left, right),))
    if not diagnostic:
        return app, data
    count = len(values)
    if case["case_id"] == CASE_IDS[0]:
        queries = (((
            0.0, _f32(left / count), _f32(right / count)),
            (1.0, 0.0, 0.0), float(count + 1)),)
        return app, replace(data, queries=queries)
    if case["case_id"] == CASE_IDS[1]:
        order = sorted(range(count), key=lambda index: (values[index], -index))
        rank = {index: position + 1 for position, index in enumerate(order)}
        vertices = [list(row) for row in data.vertices]
        for index in range(count):
            for offset in range(3):
                vertices[3 * index + offset][0] = float(rank[index])
        return app, replace(
            data, vertices=tuple(tuple(row) for row in vertices))
    raise AssertionError("not an RMQ case")


def _run_rmq(case, arm: str, target, args) -> dict[str, object]:
    diagnostic = arm == "diagnostic_counterfactual"
    app, data = _rmq_data(case, diagnostic=diagnostic)
    source_semantics = _digest({
        "case_source_authority": case["source_authority"]["authority_sha256"],
        "family": "rtxrmq",
    })
    if diagnostic:
        program = _diagnostic_builtin_program(
            target, args,
            source_semantics_sha256=source_semantics,
            independent_oracle_sha256=data.independent_oracle_sha256)
    else:
        program = _accepted_builtin_program(
            case, target, args,
            source_semantics_sha256=source_semantics,
            independent_oracle_sha256=data.independent_oracle_sha256)
    runtime_input = _triangle_exact_input(
        family="builtin_triangle.rtxrmq",
        vertices=data.vertices, triangles=data.triangles,
        front_values=data.primitive_values,
        back_values=data.primitive_values, queries=data.queries)
    runtime_options = {
        "vertices": data.vertices,
        "triangles": data.triangles,
        "front_values": data.primitive_values,
        "back_values": data.primitive_values,
        "queries": data.queries,
        "expected_output": None,
        "native_library_path": args.native,
    }
    if diagnostic:
        from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
        executed = run_builtin_triangle_callback(
            program.authority, program.plan, program.abi, program.executable,
            **runtime_options)
    else:
        from rtdsl.v4_semantically_admitted_compiler import (
            run_semantically_admitted_builtin_triangle_callback,
        )
        executed = run_semantically_admitted_builtin_triangle_callback(
            program.executable, program.admission, program.authority,
            program.plan, program.abi, **runtime_options)
    if not _receipt_is_complete(executed.traversal_receipt):
        raise RuntimeError("RMQ traversal receipt is incomplete")
    semantic_binding = _traversal_semantic_binding(
        program, target, family="builtin_triangle.rtxrmq",
        buffer_binding_sha256=executed.buffer_binding_sha256)
    output = int(executed.output[0][2])
    expected, counterfactual = evaluate_case(case["case_id"], case["minimal_witness"])
    own = counterfactual if diagnostic else expected
    if output != own:
        raise RuntimeError(f"RMQ {arm} output mismatch: {output!r} != {own!r}")
    return {
        "declared_semantics": (
            "test_only_counterfactual_encoding" if diagnostic
            else "requested_semantic_contract"),
        "output": output,
        "own_oracle": own,
        "requested_semantic_oracle": expected,
        "matches_own_oracle": True,
        "matches_requested_semantics": output == expected,
        "counterexample_observed": diagnostic and output != expected,
        "execution_identity": _program_identity(
            program, target, family="builtin_triangle.rtxrmq"),
        **_executed_input(runtime_input),
        "declared_input_delta": (
            str(case["unsafe_transform"]["transform_id"])
            if diagnostic else "none"),
        "traversal_receipts": [executed.traversal_receipt],
        "traversal_semantic_bindings": [semantic_binding],
        "traversal_output_digest_inputs": [_jsonable(executed.output)],
        "expected_program_bundles": [
            "v4_builtin_triangle_callback_ir_four_role_composed"],
        "behaviorally_true_optix": True,
        "admitted_run_gate": not diagnostic,
        "compile_admission_certifies_concrete_runtime_arrays": False,
    }


def _run_particle(case, arm: str, target, args) -> dict[str, object]:
    diagnostic = arm == "diagnostic_counterfactual"
    witness = case["minimal_witness"]
    source_semantics = _digest({
        "case_source_authority": case["source_authority"]["authority_sha256"],
        "family": "particle_orientation",
    })
    if diagnostic:
        program = _diagnostic_builtin_program(
            target, args,
            source_semantics_sha256=source_semantics,
            independent_oracle_sha256=(
                case["semantic_authority"]["oracle_source_sha256"]))
    else:
        program = _accepted_builtin_program(
            case, target, args,
            source_semantics_sha256=source_semantics,
            independent_oracle_sha256=(
                case["semantic_authority"]["oracle_source_sha256"]))
    front = (int(witness["front_value"]),)
    back = (int(witness["back_value"]),)
    if diagnostic:
        front, back = back, front
    vertices = tuple(tuple(float(value) for value in row)
                     for row in witness["vertices"])
    triangles = (tuple(int(value) for value in witness["triangle"]),)
    queries = ((
            tuple(float(value) for value in witness["ray_origin"]),
            tuple(float(value) for value in witness["ray_direction"]), 10.0),)
    runtime_input = _triangle_exact_input(
        family="builtin_triangle.particle_orientation",
        vertices=vertices, triangles=triangles, front_values=front,
        back_values=back, queries=queries)
    runtime_options = {
        "vertices": vertices,
        "triangles": triangles,
        "front_values": front,
        "back_values": back,
        "queries": queries,
        "expected_output": None,
        "native_library_path": args.native,
    }
    if diagnostic:
        from rtdsl.v4_triangle_optix_runtime import run_builtin_triangle_callback
        executed = run_builtin_triangle_callback(
            program.authority, program.plan, program.abi, program.executable,
            **runtime_options)
    else:
        from rtdsl.v4_semantically_admitted_compiler import (
            run_semantically_admitted_builtin_triangle_callback,
        )
        executed = run_semantically_admitted_builtin_triangle_callback(
            program.executable, program.admission, program.authority,
            program.plan, program.abi, **runtime_options)
    if not _receipt_is_complete(executed.traversal_receipt):
        raise RuntimeError("Particle traversal receipt is incomplete")
    semantic_binding = _traversal_semantic_binding(
        program, target, family="builtin_triangle.particle_orientation",
        buffer_binding_sha256=executed.buffer_binding_sha256)
    output = list(map(int, executed.output[0]))
    expected, counterfactual = evaluate_case(case["case_id"], witness)
    own = counterfactual if diagnostic else expected
    if output != own:
        raise RuntimeError(f"Particle {arm} output mismatch: {output!r} != {own!r}")
    return {
        "declared_semantics": (
            "test_only_swapped_orientation" if diagnostic
            else "author_bound_front_back_orientation"),
        "output": output, "own_oracle": own,
        "requested_semantic_oracle": expected,
        "matches_own_oracle": True,
        "matches_requested_semantics": output == expected,
        "counterexample_observed": diagnostic and output != expected,
        "execution_identity": _program_identity(
            program, target, family="builtin_triangle.particle_orientation"),
        **_executed_input(runtime_input),
        "declared_input_delta": (
            "swap_front_values_with_back_values" if diagnostic else "none"),
        "traversal_receipts": [executed.traversal_receipt],
        "traversal_semantic_bindings": [semantic_binding],
        "traversal_output_digest_inputs": [_jsonable(executed.output)],
        "expected_program_bundles": [
            "v4_builtin_triangle_callback_ir_four_role_composed"],
        "behaviorally_true_optix": True,
        "admitted_run_gate": not diagnostic,
        "compile_admission_certifies_concrete_runtime_arrays": False,
    }


def _strict_box_source() -> str:
    from rtdsl.v4_box_relation_callback import BOX_RELATION_SOURCE

    inclusive = (
        "overlap = primitive.lower.x <= source_max_x and "
        "primitive.upper.x >= source_min_x and "
        "primitive.lower.y <= source_max_y and "
        "primitive.upper.y >= source_min_y")
    strict = (
        "overlap = primitive.lower.x < source_max_x and "
        "primitive.upper.x > source_min_x and "
        "primitive.lower.y < source_max_y and "
        "primitive.upper.y > source_min_y")
    if BOX_RELATION_SOURCE.count(inclusive) != 1:
        raise RuntimeError("closed-box callback comparator source drift")
    return BOX_RELATION_SOURCE.replace(inclusive, strict)


def _relation_proof(callback, case):
    from rtdsl.v4_callback_abi import AnyHitProofAuthority
    from rtdsl.v4_callback_ir import AnyHitDeliveryContract

    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "goal5790_a1_test_only_relation_order_independence",
            "callback": callback.ir_sha256,
            "case": case["case_sha256"],
        }),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _compile_relation_diagnostic(case, target, args):
    from rtdsl.v4_bounded_relation import (
        BoundedRelationEmissionSchema,
        compile_bounded_relation_contract,
        verify_bounded_relation_schema,
    )
    from rtdsl.v4_bounded_relation_optix_compiler import (
        compile_verified_bounded_relation_executable,
    )
    from rtdsl.v4_box_relation_callback import manifest, physical_schema
    from rtdsl.v4_callback_abi import compile_callback_abi
    from rtdsl.v4_callback_frontend import compile_callback_source
    from rtdsl.v4_typed_physical_schema import verify_typed_physical_schema

    callback = compile_callback_source(_strict_box_source(), manifest())
    physical = verify_typed_physical_schema(
        callback, physical_schema(callback), target=target)
    schema = BoundedRelationEmissionSchema(
        callback.ir_sha256, callback.effect_digest,
        physical.schema.schema_sha256, capacity=4,
        minimum_overlap_f32=0.0)
    authority = verify_bounded_relation_schema(physical, schema)
    proof = _relation_proof(callback, case)
    abi = compile_callback_abi(
        callback, any_hit_proof_authority=proof,
        physical_schema_authority=physical)
    contract = compile_bounded_relation_contract(
        authority, abi_sha256=abi.abi_sha256)
    executable, _ = compile_verified_bounded_relation_executable(
        authority, contract, abi, any_hit_proof_authority=proof,
        **_compiler_kwargs(args))
    holder = type("DiagnosticRelationProgram", (), {})()
    holder.authority = authority
    holder.proof = proof
    holder.abi = abi
    holder.contract = contract
    holder.executable = executable
    return holder


def _compile_relation_accepted(case, target, args):
    from rtdsl.v4_semantically_admitted_compiler import (
        admit_bounded_relation_compilation,
        compile_semantically_admitted_bounded_relation_executable,
    )

    issued = _issue_case_authorities(case, target)
    live = issued.canonical
    admission = admit_bounded_relation_compilation(
        issued.semantic_authority, issued.canonical_physical_authority,
        authority=live.authority, contract=live.contract, abi=live.abi)
    executable, compiler_log = (
        compile_semantically_admitted_bounded_relation_executable(
            admission, live.authority, live.contract, live.abi,
            any_hit_proof_authority=live.proof, **_compiler_kwargs(args)))
    return SimpleNamespace(
        authority=live.authority, proof=live.proof, abi=live.abi,
        contract=live.contract,
        executable=executable, compiler_log=compiler_log,
        admission=admission,
    )


def _run_relation(case, arm: str, target, args) -> dict[str, object]:
    diagnostic = arm == "diagnostic_counterfactual"
    program = (
        _compile_relation_diagnostic(case, target, args) if diagnostic
        else _compile_relation_accepted(case, target, args))
    witness = case["minimal_witness"]
    sources = (tuple(float(value) if index < 4 else int(value)
                     for index, value in enumerate(witness["source"])),)
    indexed = (tuple(float(value) if index < 4 else int(value)
                     for index, value in enumerate(witness["indexed"])),)
    expected, counterfactual = evaluate_case(case["case_id"], witness)
    own = counterfactual if diagnostic else expected
    own_rows = tuple(tuple(map(int, row)) for row in own)
    runtime_input = _relation_exact_input(
        indexed_boxes=indexed, source_boxes=sources, capacity=4)
    runtime_options = {
        "any_hit_proof_authority": program.proof,
        "indexed_boxes": indexed,
        "source_boxes": sources,
        "expected_rows": own_rows,
        "native_library_path": args.native,
    }
    if diagnostic:
        from rtdsl.v4_bounded_relation_optix_runtime import (
            run_bounded_relation_callback,
        )
        executed = run_bounded_relation_callback(
            program.authority, program.contract, program.abi,
            program.executable, **runtime_options)
    else:
        from rtdsl.v4_semantically_admitted_compiler import (
            run_semantically_admitted_bounded_relation_callback,
        )
        executed = run_semantically_admitted_bounded_relation_callback(
            program.executable, program.admission, program.authority,
            program.contract, program.abi, **runtime_options)
    if not _receipt_is_complete(executed.traversal_receipt):
        raise RuntimeError("LibRTS traversal receipt is incomplete")
    semantic_binding = _traversal_semantic_binding(
        program, target, family="custom_aabb.bounded_relation")
    output = [list(map(int, row)) for row in executed.rows]
    if output != own:
        raise RuntimeError(f"LibRTS {arm} output mismatch: {output!r} != {own!r}")
    return {
        "declared_semantics": (
            "test_only_strict_positive_width_overlap" if diagnostic
            else "closed_inclusive_aabb_overlap"),
        "output": output, "own_oracle": own,
        "requested_semantic_oracle": expected,
        "matches_own_oracle": True,
        "matches_requested_semantics": output == expected,
        "counterexample_observed": diagnostic and output != expected,
        "execution_identity": _program_identity(
            program, target, family="custom_aabb.bounded_relation"),
        **_executed_input(runtime_input),
        "declared_input_delta": "none",
        "traversal_receipts": [executed.traversal_receipt],
        "traversal_semantic_bindings": [semantic_binding],
        "traversal_output_digest_inputs": [_jsonable(executed.rows)],
        "expected_program_bundles": [
            "v4_custom_aabb_bounded_relation_composed"],
        "behaviorally_true_optix": True,
        "admitted_run_gate": not diagnostic,
        "compile_admission_certifies_concrete_runtime_arrays": False,
    }


def _triangle_proof(callback, case):
    from rtdsl.v4_callback_abi import AnyHitProofAuthority
    from rtdsl.v4_callback_ir import AnyHitDeliveryContract

    return AnyHitProofAuthority(
        callback_ir_sha256=callback.ir_sha256,
        effect_digest=callback.effect_digest,
        delivery_contract=AnyHitDeliveryContract.ORDER_INDEPENDENT_CANONICAL,
        proof_sha256=_digest({
            "kind": "goal5790_a1_minimal_hit_count_order_independence",
            "callback": callback.ir_sha256, "case": case["case_sha256"]}),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def _compile_triangle_diagnostic(case, target, args, *, weighted: bool):
    from rtdsl.v4_triangle_standard_library import (
        all_hit_count_schema,
        compile_count_callback,
        compile_standard_triangle_program,
        weighted_hit_count_schema,
    )
    callback = compile_count_callback()
    schema = (
        weighted_hit_count_schema(callback) if weighted
        else all_hit_count_schema(callback))
    proof = _triangle_proof(callback, case)
    return compile_standard_triangle_program(
        callback, schema, target, proof, **_compiler_kwargs(args))


def _compile_triangle_accepted(case, target, args, *, weighted: bool):
    from rtdsl.v4_semantically_admitted_compiler import (
        admit_triangle_reduction_compilation,
        compile_semantically_admitted_triangle_reduction_executable,
    )

    if not weighted:
        raise RuntimeError("accepted Triangle control must use weighted schema")
    issued = _issue_case_authorities(case, target)
    live = issued.canonical
    admission = admit_triangle_reduction_compilation(
        issued.semantic_authority, issued.canonical_physical_authority,
        authority=live.authority, contract=live.contract, abi=live.abi)
    executable, compiler_log = (
        compile_semantically_admitted_triangle_reduction_executable(
            admission, live.authority, live.contract, live.abi,
            any_hit_proof_authority=live.proof, **_compiler_kwargs(args)))
    return SimpleNamespace(
        authority=live.authority, proof=live.proof, abi=live.abi,
        contract=live.contract,
        executable=executable, compiler_log=compiler_log,
        admission=admission)


def _run_unchecked_u64_device_continuation(
    per_ray: Sequence[int], weights: Sequence[int], *, target_sha256: str,
    home_toolchain_identity_sha256: str,
) -> tuple[int, dict[str, object]]:
    """Execute the rejected modulo-U64 continuation on the CUDA partner.

    The inputs are the exact per-ray values returned by the preceding OptiX
    traversal.  The kernel is deliberately test-only and is never registered
    in the product compiler or public API.
    """

    import cupy as cp

    if len(per_ray) != len(weights) or not per_ray:
        raise ValueError("unchecked continuation needs equal nonempty columns")
    values_device = cp.asarray(tuple(per_ray), dtype=cp.uint64)
    weights_device = cp.asarray(tuple(weights), dtype=cp.uint64)
    output_device = cp.zeros(1, dtype=cp.uint64)
    kernel = cp.RawKernel(
        _UNCHECKED_U64_CONTINUATION_SOURCE,
        "goal5790_a1_unchecked_weighted_sum",
        options=("-std=c++11",))
    kernel(
        (1,), (1,),
        (values_device, weights_device, cp.uint64(len(per_ray)), output_device))
    cp.cuda.runtime.deviceSynchronize()
    output = int(output_device.get()[0])
    if cp.__version__ != "14.0.1":
        raise RuntimeError("unchecked diagnostic requires frozen Home CuPy 14.0.1")
    operation_recipe = {
        "operation": "unchecked_weighted_u64_product_sum",
        "arithmetic": "cuda_unsigned_long_long_modulo_2_pow_64",
        "grid": [1],
        "block": [1],
        "compiler_options": ["-std=c++11"],
        "input_origin": "exact_optix_per_ray_plus_frozen_query_weights",
        "host_fallback": False,
    }
    record = {
        "schema": "rtdl.goal5790_a1.test_only_unchecked_u64_device_continuation.v1",
        "test_only_nonregistrable": True,
        "production_authority_minted": False,
        "kernel_source": _UNCHECKED_U64_CONTINUATION_SOURCE,
        "kernel_source_sha256": hashlib.sha256(
            _UNCHECKED_U64_CONTINUATION_SOURCE.encode("utf-8")).hexdigest(),
        "kernel_entry": "goal5790_a1_unchecked_weighted_sum",
        "compiler_options": ["-std=c++11"],
        "cupy_version": cp.__version__,
        "cuda_runtime_version": int(cp.cuda.runtime.runtimeGetVersion()),
        "device_id": int(cp.cuda.runtime.getDevice()),
        "target_sha256": target_sha256,
        "frozen_home_authority_file_sha256": HOME_AUTHORITY_FILE_SHA256,
        "frozen_home_authority_receipt_sha256": (
            HOME_AUTHORITY_RECEIPT_SHA256),
        "home_toolchain_identity_sha256": home_toolchain_identity_sha256,
        "input_per_ray_sha256": _digest(list(map(int, per_ray))),
        "input_weights_sha256": _digest(list(map(int, weights))),
        "per_ray_u64": list(map(int, per_ray)),
        "weights_u64": list(map(int, weights)),
        "input_pair_sha256": _digest({
            "per_ray": list(map(int, per_ray)),
            "weights": list(map(int, weights)),
        }),
        "output_value": output,
        "output_sha256": _digest(output),
        "operation_recipe": operation_recipe,
        "operation_recipe_sha256": _digest(operation_recipe),
        "device_kernel_launch_count": 1,
        "host_synchronization_count": 1,
        "launch_count": 1,
        "synchronization_count": 1,
        "device_output_u64": output,
        "host_fallback_used": False,
        "evidence_kind": "trusted_test_harness_not_hardware_capability_claim",
        "registered_performance_timing_created": False,
    }
    return output, record


def _run_weighted_per_ray_diagnostic(
    program, *, vertices, triangles, queries, weights, event_capacity,
    native_library_path,
):
    """Capture the weighted producer without invoking the checked reducer.

    This is a private test-harness route, not a product runtime option.  It
    executes the same composed weighted callback and exact native symbol, then
    seals only the observed OptiX producer output.  The rejected continuation
    is executed separately by ``_run_unchecked_u64_device_continuation``.
    """

    import ctypes
    import math

    from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
    from rtdsl.v4_triangle_reduction import (
        compile_triangle_reduction_abi,
        compile_triangle_reduction_contract,
        verify_triangle_reduction_schema,
    )
    from rtdsl.v4_triangle_reduction_optix_compiler import (
        consume_verified_triangle_reduction_executable,
    )
    from rtdsl.v4_triangle_reduction_optix_runtime import (
        _Status,
        _configure,
        _digest as runtime_digest,
        _native_path,
        _typed_metadata,
    )

    fresh = verify_triangle_reduction_schema(
        program.authority.callback, program.authority.schema,
        target=program.authority.target)
    if fresh != program.authority \
            or compile_triangle_reduction_abi(
                fresh, any_hit_proof_authority=program.proof) != program.abi \
            or compile_triangle_reduction_contract(
                fresh, abi_sha256=program.abi.abi_sha256) != program.contract:
        raise RuntimeError("diagnostic triangle authority/ABI/contract drift")
    composed_ptx = consume_verified_triangle_reduction_executable(
        program.executable, fresh, program.contract, program.abi,
        any_hit_proof_authority=program.proof)
    vertex_flat = [float(value) for row in vertices for value in row]
    index_flat = [int(value) for row in triangles for value in row]
    if any(len(row) != 3 for row in vertices) \
            or any(len(row) != 3 for row in triangles) \
            or not all(math.isfinite(value) for value in vertex_flat):
        raise ValueError("invalid diagnostic triangle geometry")
    origin_flat: list[float] = []
    direction_flat: list[float] = []
    tmax_values: list[float] = []
    for origin, direction, tmax in queries:
        values = [float(value) for value in (*origin, *direction, tmax)]
        if len(origin) != 3 or len(direction) != 3 \
                or not all(math.isfinite(value) for value in values) \
                or tmax <= 0:
            raise ValueError("invalid diagnostic triangle query")
        origin_flat.extend(map(float, origin))
        direction_flat.extend(map(float, direction))
        tmax_values.append(float(tmax))
    normalized, primitive_u64, primitive_i64, primitive_u32 = _typed_metadata(
        fresh, {"query.weight": tuple(map(int, weights))},
        primitive_count=len(triangles), query_count=len(queries))
    if normalized.get("query.weight") != tuple(map(int, weights)):
        raise RuntimeError("diagnostic weighted metadata normalization drift")

    vertices_native = (ctypes.c_float * len(vertex_flat))(*vertex_flat)
    triangles_native = (ctypes.c_uint32 * len(index_flat))(*index_flat)
    origins_native = (ctypes.c_float * len(origin_flat))(*origin_flat)
    directions_native = (ctypes.c_float * len(direction_flat))(*direction_flat)
    tmax_native = (ctypes.c_float * len(tmax_values))(*tmax_values)
    per_ray = (ctypes.c_uint64 * len(queries))()
    event_count = ctypes.c_uint64()
    event_query = (ctypes.c_uint32 * event_capacity)()
    event_primitive = (ctypes.c_uint32 * event_capacity)()
    event_stable = (ctypes.c_uint64 * event_capacity)()
    event_signed = (ctypes.c_int64 * event_capacity)()
    event_include = (ctypes.c_uint32 * event_capacity)()
    statuses = (_Status * len(queries))()
    counters = (ctypes.c_uint64 * 7)()
    from rtdsl import optix_runtime
    library = optix_runtime._load_optix_library()
    native_path = _native_path(library, native_library_path)
    native_sha = hashlib.sha256(native_path.read_bytes()).hexdigest()
    if native_sha != fresh.target.native_sha256:
        raise RuntimeError("diagnostic native differs from target authority")
    symbol = _configure(library)
    error = ctypes.create_string_buffer(16_384)
    audit = OptixTraversalAuditSession.open(library=library)
    try:
        status = int(symbol(
            composed_ptx.encode("utf-8"),
            vertices_native, len(vertices), triangles_native, len(triangles),
            origins_native, directions_native, tmax_native, len(queries),
            primitive_u64, primitive_i64, primitive_u32, event_capacity,
            per_ray, ctypes.byref(event_count), event_query, event_primitive,
            event_stable, event_signed, event_include, statuses, counters,
            error, len(error)))
        if status:
            raise RuntimeError(
                error.value.decode("utf-8", errors="replace")
                or f"diagnostic native status {status}")
        status_rows = tuple(
            {name: int(getattr(row, name)) for name, _ in _Status._fields_}
            for row in statuses)
        counter_rows = tuple(int(value) for value in counters)
        required_mask = (1 << 1) | (1 << 5) | (1 << 6)
        if any(row["first_error_claimed"] or row["error_code"]
               or (row["invocation_mask"] & required_mask) != required_mask
               for row in status_rows) \
                or counter_rows[1] != len(queries) \
                or counter_rows[5] != len(queries) \
                or counter_rows[6] != len(queries) \
                or counter_rows[3] <= 0:
            raise RuntimeError("diagnostic weighted callback lifecycle incomplete")
        per_ray_values = tuple(int(value) for value in per_ray)
        output_sha = runtime_digest(list(per_ray_values))
        semantic_binding = {
            "authority": fresh.authority_nonce,
            "contract": program.contract.contract_sha256,
            "abi": program.abi.abi_sha256,
            "composed_ptx": hashlib.sha256(
                composed_ptx.encode("utf-8")).hexdigest(),
            "native": native_sha,
            "diagnostic_scope": "weighted_per_ray_producer_only",
        }
        receipt = audit.finish(
            semantic_digest=runtime_digest(semantic_binding),
            output_digest=output_sha,
            route_identity=(
                "goal5790_a1_test_only_weighted_per_ray_optix_producer"),
            expected_program_bundles=(
                "v4_builtin_triangle_checked_reduction_composed",),
        )
    except BaseException:
        audit.abort()
        raise
    if not _receipt_is_complete(receipt):
        raise RuntimeError("diagnostic weighted producer receipt is incomplete")
    return {
        "per_ray_u64": per_ray_values,
        "traversal_receipt": receipt,
        "role_counters": counter_rows,
        "native_library_sha256": native_sha,
        "composed_program_sha256": hashlib.sha256(
            composed_ptx.encode("utf-8")).hexdigest(),
        "traversal_semantic_binding": semantic_binding,
        "expected_program_bundle": (
            "v4_builtin_triangle_checked_reduction_composed"),
        "test_only_nonregistrable": True,
        "standard_product_reduction_receipt_minted": False,
    }


def _run_triangle(case, arm: str, target, args) -> dict[str, object]:
    diagnostic = arm == "diagnostic_counterfactual"
    overflow = case["case_id"] == CASE_IDS[2]
    # Overflow changes only the downstream arithmetic policy.  Its accepted
    # and diagnostic producer/input remain weighted and byte-identical.
    # Multiplicity is the one case whose diagnostic intentionally removes the
    # weight channel.
    weighted = overflow or not diagnostic
    program = (
        _compile_triangle_diagnostic(case, target, args, weighted=weighted)
        if diagnostic else
        _compile_triangle_accepted(case, target, args, weighted=weighted))
    vertices = ((-0.75, -0.75, 1.0), (0.75, -0.75, 1.0), (0.0, 0.75, 1.0))
    triangles = ((0, 1, 2),)
    queries = (
        ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 10.0),
        ((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), 10.0),
    )
    weights = tuple(int(value) for value in case["minimal_witness"]["weights"])
    metadata = {"query.weight": weights} if weighted else {}
    runtime_input = _triangle_exact_input(
        family="builtin_triangle.triangle_reduction",
        vertices=vertices, triangles=triangles, queries=queries,
        weights=weights if weighted else (), event_capacity=4)
    expected, counterfactual = evaluate_case(case["case_id"], case["minimal_witness"])

    runtime_options = {
        "any_hit_proof_authority": program.proof,
        "vertices": vertices,
        "triangles": triangles,
        "queries": queries,
        "metadata": metadata,
        "event_capacity": 4,
        "native_library_path": args.native,
    }

    def run_standard_route(*, expected_reduced_output):
        options = {
            **runtime_options,
            "expected_reduced_output": expected_reduced_output,
        }
        if diagnostic:
            from rtdsl.v4_triangle_reduction_optix_runtime import (
                run_builtin_triangle_reduction_callback,
            )
            return run_builtin_triangle_reduction_callback(
                program.authority, program.contract, program.abi,
                program.executable, **options)
        from rtdsl.v4_semantically_admitted_compiler import (
            run_semantically_admitted_triangle_reduction_callback,
        )
        return run_semantically_admitted_triangle_reduction_callback(
            program.executable, program.admission, program.authority,
            program.contract, program.abi, **options)

    # Overflow's accepted physical contract is fail-closed, not a fictitious
    # U64 encoding of 2^64.  The production atomic admitted-run gate invokes
    # the standard weighted checked route, which rejects before a traversal
    # receipt or output may be claimed.
    if overflow and not diagnostic:
        from rtdsl.v4_triangle_reduction import TriangleReductionError
        captured_error = None
        try:
            run_standard_route(expected_reduced_output=None)
        except TriangleReductionError as error:
            if error.code != "unsigned_overflow":
                raise RuntimeError(
                    f"checked route failed for the wrong reason: {error}") from error
            captured_error = error
        else:  # pragma: no cover - hard safety assertion
            raise RuntimeError("checked U64 route accepted an overflowing domain")
        assert captured_error is not None
        return {
            "declared_semantics": "checked_weighted_reduction",
            "output": None,
            "accepted_disposition": {
                "status": "FAIL_CLOSED_OVERFLOW",
                "error_type": type(captured_error).__name__,
                "error_code": captured_error.code,
                "error_path": captured_error.path,
                "output_produced": False,
            },
            "own_oracle": {
                "required_mathematical_value": expected,
                "required_disposition": "FAIL_CLOSED_OVERFLOW",
            },
            "requested_semantic_oracle": expected,
            "matches_own_oracle": True,
            "matches_requested_semantics": True,
            "correct_fail_closed": True,
            "counterexample_observed": False,
            "execution_identity": _program_identity(
                program, target, family="builtin_triangle.triangle_reduction"),
            **_executed_input(runtime_input),
            "declared_input_delta": "none",
            "traversal_receipts": [],
            "traversal_semantic_bindings": [],
            "traversal_output_digest_inputs": [],
            "expected_program_bundles": [],
            "behaviorally_true_optix": False,
            "admitted_run_gate": True,
            "compile_admission_certifies_concrete_runtime_arrays": False,
            "zero_receipt_reason": (
                "checked reducer rejected overflow before audit receipt capture"),
        }

    producer_diagnostic = None
    if overflow and diagnostic:
        producer_diagnostic = _run_weighted_per_ray_diagnostic(
            program, vertices=vertices, triangles=triangles,
            queries=queries, weights=weights, event_capacity=4,
            native_library_path=args.native)
        result = SimpleNamespace(
            per_ray_u64=producer_diagnostic["per_ray_u64"],
            traversal_receipt=producer_diagnostic["traversal_receipt"])
    else:
        result = run_standard_route(
            expected_reduced_output=(
                counterfactual if diagnostic else expected))
    if not _receipt_is_complete(result.traversal_receipt):
        raise RuntimeError("Triangle traversal receipt is incomplete")
    semantic_binding = (
        producer_diagnostic["traversal_semantic_binding"]
        if producer_diagnostic is not None else
        _traversal_semantic_binding(
            program, target, family="builtin_triangle.triangle_reduction"))

    unchecked_continuation = None
    if overflow:
        per_ray = tuple(int(value) for value in result.per_ray_u64)
        output, unchecked_continuation = _run_unchecked_u64_device_continuation(
            per_ray, weights, target_sha256=target.target_sha256,
            home_toolchain_identity_sha256=(
                args.home_machine["home_toolchain_identity_sha256"]))
        disposition = None
        own = counterfactual
        matches_requested = output == expected
        counterexample = output == counterfactual and output != expected
    else:
        output = int(result.reduced_output)
        disposition = None
        own = counterfactual if diagnostic else expected
        matches_requested = output == expected
        counterexample = diagnostic and output != expected
    if overflow and diagnostic and output != counterfactual:
        raise RuntimeError("unchecked U64 diagnostic did not wrap to the frozen value")
    if not overflow and output != own:
        raise RuntimeError("Triangle reduction output differs from its own oracle")
    return {
        "declared_semantics": (
            "test_only_unchecked_or_unweighted_continuation" if diagnostic
            else "checked_weighted_reduction"),
        "output": output,
        "accepted_disposition": disposition,
        "own_oracle": own,
        "requested_semantic_oracle": expected,
        "matches_own_oracle": True,
        "matches_requested_semantics": matches_requested,
        "counterexample_observed": counterexample,
        "execution_identity": _program_identity(
            program, target, family="builtin_triangle.triangle_reduction"),
        **_executed_input(runtime_input),
        "declared_input_delta": (
            "none" if overflow else (
                str(case["unsafe_transform"]["transform_id"])
                if diagnostic else "none")),
        "declared_physical_delta": (
            str(case["unsafe_transform"]["transform_id"])
            if diagnostic else "none"),
        "traversal_receipts": [result.traversal_receipt],
        "traversal_semantic_bindings": [semantic_binding],
        "traversal_output_digest_inputs": [
            list(map(int, result.per_ray_u64)) if producer_diagnostic is not None
            else int(result.reduced_output)],
        "expected_program_bundles": [
            "v4_builtin_triangle_checked_reduction_composed"],
        "traversal_receipt_claim_scope": (
            "optix_hit_collection_only__test_continuation_separately_bound"
            if diagnostic else "accepted_checked_route"),
        "per_ray_u64": list(map(int, result.per_ray_u64)),
        "test_only_device_continuation": unchecked_continuation,
        "test_only_optix_producer_diagnostic": producer_diagnostic,
        "behaviorally_true_optix": True,
        "admitted_run_gate": not diagnostic,
        "compile_admission_certifies_concrete_runtime_arrays": False,
    }


def _execution(case, arm: str, args) -> dict[str, object]:
    target = _target(args)
    if case["case_id"] in CASE_IDS[:2]:
        return _run_rmq(case, arm, target, args)
    if case["case_id"] in CASE_IDS[2:4]:
        return _run_triangle(case, arm, target, args)
    if case["case_id"] == CASE_IDS[4]:
        return _run_particle(case, arm, target, args)
    if case["case_id"] == CASE_IDS[5]:
        return _run_relation(case, arm, target, args)
    raise AssertionError("unknown case")


def run_worker(args) -> dict[str, object]:
    machine = _query_exact_home_machine(
        args.home_authority_sha256,
        args.home_authority_file,
        args.home_authority_file_sha256,
    )
    if args.cc != "61":
        raise RuntimeError("Goal5790-A1 worker accepts only Home CC6.1")
    args.home_machine = machine
    cache_policy = _require_isolated_non_authority_caches()
    suite, case = _case_from_suite(args.suite.resolve(), args.case_id)
    execution_spec, case_spec = _execution_spec_case(
        args.execution_spec, args.execution_spec_sha256,
        suite_sha256=str(suite["suite_sha256"]), case=case)
    if args.arm == "product_admission_reject":
        arm_result = _product_reject(case, args)
    else:
        arm_result = _execution(case, args.arm, args)
        if arm_result["matches_own_oracle"] is not True \
                or (arm_result["behaviorally_true_optix"] is not True
                    and arm_result.get("correct_fail_closed") is not True):
            raise RuntimeError("execution arm did not close its own semantics")
        if args.arm == "accepted_control" \
                and arm_result["matches_requested_semantics"] is not True:
            raise RuntimeError("accepted control did not satisfy requested semantics")
        if args.arm == "diagnostic_counterfactual" \
                and arm_result["counterexample_observed"] is not True:
            raise RuntimeError("diagnostic did not establish a counterexample")
    result: dict[str, object] = {
        "schema": SCHEMA, "status": "PASS",
        "case_id": case["case_id"], "case_sha256": case["case_sha256"],
        "upstream_suite_sha256": suite["suite_sha256"],
        "execution_spec_sha256": execution_spec["execution_spec_sha256"],
        "execution_spec_file_sha256": _sha_file(args.execution_spec.resolve()),
        "case_execution_spec_sha256": case_spec[
            "case_execution_spec_sha256"],
        "input_sha256": _digest(case["minimal_witness"]),
        "arm": args.arm, "parent_pid": os.getpid(),
        "home_machine": machine,
        "home_machine_authority_sha256": machine[
            "home_machine_authority_sha256"],
        "cache_policy": cache_policy,
        "arm_result": _jsonable(arm_result),
        "elapsed_values_recorded": False,
        "registered_performance_timing_created": False,
        "performance_claimed": False,
        "pod_used": machine["classification"] != "exact_home_lx1__not_pod",
        "formal_worker": False,
    }
    result["worker_result_sha256"] = canonical_sha256(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", required=True, type=Path)
    parser.add_argument("--case-id", required=True, choices=CASE_IDS)
    parser.add_argument("--arm", required=True, choices=sorted(ARMS))
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    parser.add_argument("--cc", required=True, choices=("61",))
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--expected-python", required=True)
    parser.add_argument("--expected-numba", required=True)
    parser.add_argument("--expected-numpy", required=True)
    parser.add_argument("--home-authority-sha256", required=True)
    parser.add_argument("--home-authority-file", required=True, type=Path)
    parser.add_argument("--home-authority-file-sha256", required=True)
    parser.add_argument("--execution-spec", required=True, type=Path)
    parser.add_argument("--execution-spec-sha256", required=True)
    args = parser.parse_args()
    for path, label in (
        (args.suite, "suite"), (args.native, "native"),
        (args.optix_include, "OptiX include"),
        (args.cuda_include, "CUDA include"),
    ):
        if not path.exists():
            raise FileNotFoundError(f"{label} path is absent: {path}")
    if args.output.exists():
        raise FileExistsError(args.output)
    result = run_worker(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8", newline="\n")
    print(json.dumps({
        "status": result["status"], "case_id": result["case_id"],
        "arm": result["arm"], "parent_pid": result["parent_pid"],
        "worker_result_sha256": result["worker_result_sha256"],
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
