#!/usr/bin/env python3
"""Create-only Goal5749 compiler artifacts and optional functional GPU run."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np

from rtdsl.v4_callback_poc import (
    CallbackRole,
    StatusCode,
    compile_numba_leaf_isolated,
    compile_numba_scalar_probe_isolated,
    generate_numba_leaf,
    generate_numba_scalar_probe,
    module_identity,
    verify_callback_source,
)


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "history/internal_docs/goal5749_amendment_a1_composed_numba_leaf_policy_20260811.json"
SOURCE_PATH = ROOT / "examples/v4/verified_sphere_callbacks.rtdl.py"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stable(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode()).hexdigest()


def _version(command: list[str]) -> str:
    completed = subprocess.run(command, capture_output=True, text=True, check=True)
    return (completed.stdout + completed.stderr).strip()


def _preflight(policy: dict[str, object], lane: str) -> tuple[int, int]:
    import numba
    backend = policy["backend"]
    assert isinstance(backend, dict)
    if platform.python_version() != backend["python"]:
        raise RuntimeError(f"Python identity mismatch: {platform.python_version()} != {backend['python']}")
    if numba.__version__ != backend["numba"] or np.__version__ != backend["numpy"]:
        raise RuntimeError("Numba/NumPy identity mismatch")
    target = next(item for item in policy["target_lanes"] if item["name"] == lane)
    return tuple(target["compute_capability"])


def _required_env_path(name: str, *, file: bool = False) -> Path:
    raw = os.environ.get(name)
    if not raw:
        raise RuntimeError(f"{name} must bind the exact execution identity")
    path = Path(raw).resolve()
    if not (path.is_file() if file else path.is_dir()):
        raise RuntimeError(f"{name} does not resolve to the required {'file' if file else 'directory'}: {path}")
    return path


def _target_identity(policy: dict[str, object], lane: str, cc: tuple[int, int]) -> dict[str, object]:
    target = next(item for item in policy["target_lanes"] if item["name"] == lane)
    completed = subprocess.run(
        ["nvidia-smi", "--query-gpu=name,driver_version,uuid,compute_cap", "--format=csv,noheader"],
        capture_output=True, text=True, check=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError(f"Goal5749 requires exactly one visible GPU, observed {len(rows)}")
    fields = [field.strip() for field in rows[0].split(",")]
    if len(fields) != 4:
        raise RuntimeError(f"unexpected nvidia-smi identity row: {rows[0]!r}")
    gpu_name, driver_version, gpu_uuid, observed_cc = fields
    expected_gpu = target.get("gpu", target.get("gpu_class"))
    if gpu_name != expected_gpu:
        raise RuntimeError(f"GPU identity mismatch: {gpu_name!r} != {expected_gpu!r}")
    if observed_cc != f"{cc[0]}.{cc[1]}":
        raise RuntimeError(f"compute capability mismatch: {observed_cc!r} != {cc[0]}.{cc[1]}")
    native = _required_env_path("RTDL_OPTIX_LIB", file=True)
    cuda_prefix = _required_env_path("RTDL_V4_CUDA_PREFIX")
    optix_prefix = _required_env_path("RTDL_V4_OPTIX_PREFIX")
    nvcc = cuda_prefix / "bin" / "nvcc"
    optix_h = optix_prefix / "include" / "optix.h"
    if not nvcc.is_file() or not optix_h.is_file():
        raise RuntimeError("frozen CUDA/OptiX development identity is incomplete")
    nvcc_version = _version([str(nvcc), "--version"])
    if "V12.8.93" not in nvcc_version:
        raise RuntimeError(f"nvcc identity mismatch: {nvcc_version}")
    optix_text = optix_h.read_text(encoding="utf-8", errors="replace")
    if not re.search(r"^#define\s+OPTIX_VERSION\s+90000\s*$", optix_text, re.MULTILINE):
        raise RuntimeError("OptiX SDK identity mismatch: expected OPTIX_VERSION 90000")
    source_archive_sha256 = os.environ.get("RTDL_V4_SOURCE_ARCHIVE_SHA256", "")
    source_commit = os.environ.get("RTDL_V4_SOURCE_COMMIT", "")
    if not re.fullmatch(r"[0-9a-f]{64}", source_archive_sha256):
        raise RuntimeError("RTDL_V4_SOURCE_ARCHIVE_SHA256 must be an exact lowercase SHA-256")
    if not re.fullmatch(r"[0-9a-f]{7,64}", source_commit):
        raise RuntimeError("RTDL_V4_SOURCE_COMMIT must be an exact lowercase Git identity")
    return {
        "gpu_name": gpu_name,
        "driver_version": driver_version,
        "gpu_uuid": gpu_uuid,
        "compute_capability": observed_cc,
        "native_path": str(native),
        "native_sha256": _sha256(native),
        "source_archive_sha256": source_archive_sha256,
        "source_commit": source_commit,
        "cuda_prefix": str(cuda_prefix),
        "nvcc_version": nvcc_version,
        "nvcc_sha256": _sha256(nvcc),
        "optix_prefix": str(optix_prefix),
        "optix_h_sha256": _sha256(optix_h),
    }


def _variant_source(source: str, name: str) -> str:
    if name == "ab_tie_prefer_larger_id":
        old = "hit_t == best_t and hit_id < best_id"
        new = "hit_t == best_t and hit_id > best_id"
    elif name == "invalid_nonfinite_hit":
        old = "            return optix.hit(t=t, item_id=item_id)"
        new = ("            bad_t = radius * 3.4e38\n"
               "            bad_t2 = bad_t * 2.0\n"
               "            return optix.hit(t=bad_t2, item_id=item_id)")
    elif name == "invalid_u32_overflow":
        old = "        return optix.accept_continue(best_t=hit_t, best_id=hit_id)"
        new = ("        overflow_id = hit_id + 4294967295\n"
               "        return optix.accept_continue(best_t=hit_t, best_id=overflow_id)")
    else:
        raise ValueError(f"unknown source variant {name}")
    if source.count(old) != 1:
        raise RuntimeError(f"source variant {name} did not match its frozen source row")
    return source.replace(old, new)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--lane", required=True, choices=(
        "home_linux_behavioral_feasibility", "modern_rtx_portability_confirmation"))
    parser.add_argument("--output", required=True)
    parser.add_argument("--run-native", action="store_true")
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    cc = _preflight(policy, args.lane)
    source = SOURCE_PATH.read_text(encoding="utf-8")
    module = verify_callback_source(source)
    compiled: dict[tuple[str, str], object] = {}
    artifact_rows: list[dict[str, object]] = []
    for mode in policy["diagnostic_matrix"]["leaf_numeric_modes"]:
        for role in CallbackRole:
            leaf = generate_numba_leaf(module, role, numeric_mode=mode)
            artifact = compile_numba_leaf_isolated(
                leaf,
                compute_capability=cc,
                accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                                  policy["backend"]["ptx_isa_max"]),
                allowed_external_symbols=frozenset(),
            )
            compiled[(mode, role.value)] = artifact
            ptx_path = output / f"{mode}__{role.value}.ptx"
            ptx_path.write_text(artifact.ptx, encoding="utf-8")
            metadata = dataclasses.asdict(artifact)
            metadata.pop("ptx")
            metadata["ptx_path"] = ptx_path.name
            artifact_rows.append(metadata)
        scalar = compile_numba_scalar_probe_isolated(
            generate_numba_scalar_probe(module, numeric_mode=mode),
            compute_capability=cc,
            accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                              policy["backend"]["ptx_isa_max"]),
            allowed_external_symbols=frozenset(),
        )
        compiled[(mode, "scalar_probe")] = scalar
        scalar_path = output / f"{mode}__scalar_probe.ptx"
        scalar_path.write_text(scalar.ptx, encoding="utf-8")
        scalar_metadata = dataclasses.asdict(scalar)
        scalar_metadata.pop("ptx")
        scalar_metadata["ptx_path"] = scalar_path.name
        artifact_rows.append(scalar_metadata)
    variant_compiled: dict[str, tuple[object, dict[str, object]]] = {}
    variant_rows: list[dict[str, object]] = []
    for variant in (
        "ab_tie_prefer_larger_id", "invalid_nonfinite_hit", "invalid_u32_overflow"
    ):
        variant_module = verify_callback_source(_variant_source(source, variant))
        variant_artifacts: dict[str, object] = {}
        for role in CallbackRole:
            artifact = compile_numba_leaf_isolated(
                generate_numba_leaf(variant_module, role, numeric_mode="strict"),
                compute_capability=cc,
                accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                                  policy["backend"]["ptx_isa_max"]),
                allowed_external_symbols=frozenset(),
            )
            variant_artifacts[role.value] = artifact
            path = output / f"variant__{variant}__{role.value}.ptx"
            path.write_text(artifact.ptx, encoding="utf-8")
            variant_rows.append({
                "variant": variant,
                "artifact": {key: value for key, value in dataclasses.asdict(artifact).items()
                             if key != "ptx"},
                "ptx_path": path.name,
            })
        scalar = compile_numba_scalar_probe_isolated(
            generate_numba_scalar_probe(variant_module, numeric_mode="strict"),
            compute_capability=cc,
            accepted_ptx_isa=(policy["backend"]["ptx_isa_min"],
                              policy["backend"]["ptx_isa_max"]),
            allowed_external_symbols=frozenset(),
        )
        variant_artifacts["scalar_probe"] = scalar
        path = output / f"variant__{variant}__scalar_probe.ptx"
        path.write_text(scalar.ptx, encoding="utf-8")
        variant_rows.append({
            "variant": variant,
            "artifact": {key: value for key, value in dataclasses.asdict(scalar).items()
                         if key != "ptx"},
            "ptx_path": path.name,
        })
        variant_compiled[variant] = (variant_module, variant_artifacts)
    runs: list[dict[str, object]] = []
    diagnostic_runs: list[dict[str, object]] = []
    target_identity = None
    if args.run_native:
        target_identity = _target_identity(policy, args.lane, cc)
        from rtdsl.v4_optix_callback_runtime import run_verified_callback_poc
        spheres = (((5.0, 0.0, 0.0), 1.0, 9),
                   ((5.0, 0.0, 0.0), 1.0, 3),
                   ((8.0, 0.0, 0.0), 1.0, 3))
        rays = (((0.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
                ((0.0, 4.0, 0.0), (1.0, 0.0, 0.0)),
                ((10.0, 0.0, 0.0), (-1.0, 0.0, 0.0)))
        for wrapper_mode in policy["diagnostic_matrix"]["wrapper_numeric_modes"]:
            for leaf_mode in policy["diagnostic_matrix"]["leaf_numeric_modes"]:
                artifacts = [compiled[(leaf_mode, role.value)] for role in CallbackRole]
                for route in policy["diagnostic_matrix"]["link_routes"]:
                    result = run_verified_callback_poc(
                        module, artifacts, spheres=spheres, rays=rays,
                        tmin=0.0, tmax=100.0, route=route,
                        wrapper_numeric_mode=wrapper_mode,
                        scalar_probe=compiled[(leaf_mode, "scalar_probe")])
                    row = dataclasses.asdict(result)
                    row["traversal_receipt_path"] = (
                        f"receipt__{wrapper_mode}__{leaf_mode}__{route}.json")
                    (output / row["traversal_receipt_path"]).write_text(
                        json.dumps(result.traversal_receipt, indent=2, sort_keys=True) + "\n")
                    row.pop("traversal_receipt")
                    runs.append(row)
        base_primary = next(
            row for row in runs
            if row["wrapper_numeric_mode"] == "strict"
            and all(mode == "strict" for mode in row["leaf_numeric_modes"])
            and row["route"] == "ordinary_composed"
        )
        ab_module, ab_artifacts = variant_compiled["ab_tie_prefer_larger_id"]
        ab_result = run_verified_callback_poc(
            ab_module,
            [ab_artifacts[role.value] for role in CallbackRole],
            spheres=spheres,
            rays=rays,
            tmin=0.0,
            tmax=100.0,
            route="ordinary_composed",
            wrapper_numeric_mode="strict",
            scalar_probe=ab_artifacts["scalar_probe"],
        )
        if ab_result.output_sha256 == base_primary["output_sha256"]:
            raise RuntimeError("callback A/B mutation did not change the physical output")
        diagnostic_runs.append({
            "kind": "ab_semantic_mutation",
            "base_output_sha256": base_primary["output_sha256"],
            "mutated_output_sha256": ab_result.output_sha256,
            "output_changed": True,
            "result": {key: value for key, value in dataclasses.asdict(ab_result).items()
                       if key != "traversal_receipt"},
        })
        for variant, expected_status in (
            ("invalid_nonfinite_hit", StatusCode.NONFINITE_EFFECT),
            ("invalid_u32_overflow", StatusCode.U32_OVERFLOW),
        ):
            bad_module, bad_artifacts = variant_compiled[variant]
            failure = run_verified_callback_poc(
                bad_module,
                [bad_artifacts[role.value] for role in CallbackRole],
                spheres=spheres,
                rays=rays,
                tmin=0.0,
                tmax=100.0,
                route="ordinary_composed",
                wrapper_numeric_mode="strict",
                scalar_probe=bad_artifacts["scalar_probe"],
                expected_device_failure_status=int(expected_status),
            )
            diagnostic_runs.append({
                "kind": variant,
                "expected_status": int(expected_status),
                "output_accepted": False,
                "result": dataclasses.asdict(failure),
            })
    result = {
        "schema": "rtdl.goal5749.callback_poc_lane_result.v1",
        "goal": 5749,
        "lane": args.lane,
        "functional_gpu_execution_performed": bool(args.run_native),
        "policy_sha256": _sha256(POLICY_PATH),
        "source_path": str(SOURCE_PATH.relative_to(ROOT)).replace("\\", "/"),
        "source_file_sha256": _sha256(SOURCE_PATH),
        "callback_module": module_identity(module),
        "compute_capability": cc,
        "target_identity": target_identity,
        "python": platform.python_version(),
        "numba_artifacts": artifact_rows,
        "variant_numba_artifacts": variant_rows,
        "functional_runs": runs,
        "diagnostic_runs": diagnostic_runs,
        "registered_performance_timing_count": 0,
        "performance_claimed": False,
    }
    result["result_sha256"] = _stable(result)
    result_path = output / "RESULT.json"
    result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    manifest = []
    for path in sorted(item for item in output.iterdir() if item.is_file()):
        manifest.append({"path": path.name, "size": path.stat().st_size, "sha256": _sha256(path)})
    (output / "MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "result": str(result_path), "result_sha256": _sha256(result_path),
        "numba_artifact_count": len(artifact_rows), "functional_run_count": len(runs),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
