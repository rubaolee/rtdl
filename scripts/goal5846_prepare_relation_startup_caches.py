#!/usr/bin/env python3
"""Create, seal, and replay Goal5846's two compiler caches exactly once."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

from experiments.goal5842_causal_admission.contracts import RELATION_TASK, digest
from experiments.goal5842_causal_admission.tasks import build_task
from experiments.goal5844_compact_execution.provenance import write_json_create
from scripts.goal5844_run_gpu_engineering_comparison import (
    _validate_native_build_manifest,
)


ROOT = Path(__file__).resolve().parents[1]


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _measure(action):
    started = time.perf_counter_ns()
    result = action()
    return result, time.perf_counter_ns() - started


def _snapshot(root: Path) -> tuple[tuple[str, int, str], ...]:
    resolved = root.resolve(strict=True)
    rows = []
    for path in sorted(resolved.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"Goal5846 cache contains a symlink: {path}")
        if path.is_file():
            rows.append((
                path.relative_to(resolved).as_posix(),
                path.stat().st_size,
                _sha256_file(path),
            ))
    if not rows:
        raise RuntimeError(f"Goal5846 cache is empty: {resolved}")
    return tuple(rows)


def _outside_repository(path: Path) -> Path:
    absolute = path.expanduser().absolute()
    parent = absolute.parent.resolve(strict=True)
    candidate = parent / absolute.name
    try:
        candidate.relative_to(ROOT.resolve(strict=True))
    except ValueError:
        return candidate
    raise RuntimeError("Goal5846 generated caches must remain outside Git")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--leaf-cache-root", type=Path, required=True)
    parser.add_argument("--leaf-cache-manifest", type=Path, required=True)
    parser.add_argument("--executable-cache-root", type=Path, required=True)
    parser.add_argument("--executable-cache-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5846 cache preparation requires clean source")
    if _git("rev-parse", "HEAD") != args.expected_source_commit:
        raise RuntimeError("Goal5846 cache preparation source differs")
    generated = (
        _outside_repository(args.leaf_cache_root),
        _outside_repository(args.leaf_cache_manifest),
        _outside_repository(args.executable_cache_root),
        _outside_repository(args.executable_cache_manifest),
        _outside_repository(args.output),
    )
    if len(set(generated)) != len(generated):
        raise RuntimeError("Goal5846 generated paths must be distinct")
    for path in generated:
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)

    from rtdsl.v4 import (
        FormalNumbaLeafCachePolicy,
        V4ExecutableCachePolicy,
        V4Target,
        V4Toolchain,
        materialize_executable_cache_manifest,
    )
    from rtdsl.v4_callback_numba_codegen import (
        formal_numba_leaf_cache_lifecycle_metadata,
        materialize_formal_numba_leaf_cache_manifest,
    )

    capability = tuple(int(part) for part in args.compute_capability.split("."))
    if len(capability) != 2:
        raise ValueError("Goal5846 compute capability must have two components")
    native = args.native.resolve(strict=True)
    native_build_manifest = args.native_build_manifest.resolve(strict=True)
    _validate_native_build_manifest(
        native_build_manifest,
        native,
        source_commit=args.expected_source_commit,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    task = build_task(RELATION_TASK)
    writable = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
        formal_leaf_cache=FormalNumbaLeafCachePolicy(generated[0]),
        executable_cache=V4ExecutableCachePolicy(generated[2]),
    )
    lifecycle_before = formal_numba_leaf_cache_lifecycle_metadata()
    fill_started = time.perf_counter_ns()
    route, route_ns = _measure(task.route_factory)
    program, admission_ns = _measure(route.compile)
    materialized, materialize_ns = _measure(
        lambda: program.materialize(target=target, toolchain=writable)
    )
    fill_total_ns = time.perf_counter_ns() - fill_started
    fill_identity = materialized.identity.to_dict()
    lifecycle_after_fill = formal_numba_leaf_cache_lifecycle_metadata()

    materialize_formal_numba_leaf_cache_manifest(generated[0], generated[1])
    materialize_executable_cache_manifest(generated[2], generated[3])
    leaf_manifest_sha256 = _sha256_file(generated[1])
    executable_manifest_sha256 = _sha256_file(generated[3])
    before_replay = {
        "leaf": _snapshot(generated[0]),
        "executable": _snapshot(generated[2]),
    }
    sealed = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
        formal_leaf_cache=FormalNumbaLeafCachePolicy(
            generated[0], generated[1], leaf_manifest_sha256
        ),
        executable_cache=V4ExecutableCachePolicy(
            generated[2], generated[3], executable_manifest_sha256
        ),
    )
    replay_route = task.route_factory()
    replay_program = replay_route.compile()
    replay_materialized, replay_ns = _measure(
        lambda: replay_program.materialize(target=target, toolchain=sealed)
    )
    lifecycle_after_replay = formal_numba_leaf_cache_lifecycle_metadata()
    after_replay = {
        "leaf": _snapshot(generated[0]),
        "executable": _snapshot(generated[2]),
    }
    if before_replay != after_replay:
        raise RuntimeError("Goal5846 sealed replay changed cache bytes")
    if replay_materialized.identity.to_dict() != fill_identity:
        raise RuntimeError("Goal5846 sealed replay executable identity differs")
    if (
        int(lifecycle_after_fill["miss_count"])
            <= int(lifecycle_before["miss_count"])
        or int(lifecycle_after_replay["miss_count"])
            != int(lifecycle_after_fill["miss_count"])
    ):
        raise RuntimeError("Goal5846 leaf-cache fill/replay lifecycle differs")

    leaf_manifest = json.loads(generated[1].read_text(encoding="utf-8"))
    executable_manifest = json.loads(generated[3].read_text(encoding="ascii"))
    result: dict[str, object] = {
        "schema": "rtdl.goal5846.relation_startup_cache_preparation.v1",
        "status": "PASS__FIRST_FILL_SEALED_AND_HIT_ONLY_REPLAY",
        "source_commit": args.expected_source_commit,
        "source_tree": _git("rev-parse", "HEAD^{tree}"),
        "task": RELATION_TASK,
        "native_library": {
            "path": str(native),
            "bytes": native.stat().st_size,
            "sha256": _sha256_file(native),
        },
        "native_build_manifest": {
            "path": str(native_build_manifest),
            "sha256": _sha256_file(native_build_manifest),
        },
        "first_ever_cache_fill": {
            "route_declaration_ns": route_ns,
            "generic_admission_ns": admission_ns,
            "materialize_and_compile_ns": materialize_ns,
            "total_ns": fill_total_ns,
            "registered_performance_sample": False,
        },
        "sealed_replay_ns": replay_ns,
        "leaf_cache": {
            "root": str(generated[0].resolve(strict=True)),
            "manifest": str(generated[1].resolve(strict=True)),
            "manifest_sha256": leaf_manifest_sha256,
            "entry_count": leaf_manifest["entry_count"],
            "entries_sha256": leaf_manifest["entries_sha256"],
            "snapshot": [list(row) for row in before_replay["leaf"]],
        },
        "executable_cache": {
            "root": str(generated[2].resolve(strict=True)),
            "manifest": str(generated[3].resolve(strict=True)),
            "manifest_sha256": executable_manifest_sha256,
            "entry_count": executable_manifest["entry_count"],
            "entries_sha256": executable_manifest["entries_sha256"],
            "snapshot": [list(row) for row in before_replay["executable"]],
        },
        "executable_identity": fill_identity,
        "claim_boundary": {
            "cache_fill_excluded_from_formal_estimand": True,
            "gpu_execution_performed": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    result["preparation_sha256"] = digest(result)
    write_json_create(generated[4], result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
