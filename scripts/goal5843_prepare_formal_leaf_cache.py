#!/usr/bin/env python3
"""Populate and seal Goal5843's explicit formal Numba leaf cache."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from experiments.goal5842_causal_admission.tasks import build_task
from experiments.goal5843_post_r1_baseline.contracts import (
    CACHE_PREPARATION_SCHEMA,
    TASKS,
    digest,
    load_preregistration,
    sha256_file,
)
from experiments.goal5843_post_r1_baseline.runtime import (
    create_json,
    git_head,
    git_status_short,
)


ROOT = Path(__file__).resolve().parents[1]


def validate_cache_lifecycle(
    before: dict[str, object],
    after_fill: dict[str, object],
    after_verify: dict[str, object],
) -> tuple[int, int, int]:
    fill_misses = int(after_fill["miss_count"]) - int(before["miss_count"])
    verify_hits = int(after_verify["hit_count"]) - int(after_fill["hit_count"])
    verify_misses = int(after_verify["miss_count"]) - int(after_fill["miss_count"])
    if fill_misses <= 0:
        raise RuntimeError("formal cache creation produced no entries")
    if verify_hits <= 0 or verify_misses != 0:
        raise RuntimeError("sealed formal cache replay was not hit-only")
    return fill_misses, verify_hits, verify_misses


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg = load_preregistration(
        args.preregistration.resolve(), ROOT, verify_files=True
    )
    if git_status_short(ROOT):
        raise RuntimeError("formal cache preparation requires a clean repository")
    for name in (
        "RTDL_V4_FORMAL_LEAF_CACHE",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST",
        "RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256",
    ):
        if os.environ.get(name):
            raise RuntimeError(f"ambient formal cache authority forbidden: {name}")
    cache_root = args.cache_root.absolute()
    manifest_path = args.manifest.absolute()
    if cache_root.exists() or cache_root.is_symlink():
        raise FileExistsError(f"cache root already exists: {cache_root}")
    if manifest_path.exists() or manifest_path.is_symlink():
        raise FileExistsError(f"cache manifest already exists: {manifest_path}")
    from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain
    from rtdsl.v4_callback_numba_codegen import (
        formal_numba_leaf_cache_lifecycle_metadata,
        materialize_formal_numba_leaf_cache_manifest,
    )

    capability_text = os.environ.get("GOAL5843_COMPUTE_CAPABILITY")
    if not capability_text:
        import subprocess

        capability_text = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=compute_cap",
                "--format=csv,noheader,nounits",
            ],
            check=True,
            text=True,
            capture_output=True,
        ).stdout.strip()
    capability = tuple(int(part) for part in capability_text.split("."))
    target = V4Target.from_native(
        args.native.resolve(strict=True),
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
    )
    writable = FormalNumbaLeafCachePolicy(cache_root)
    writable_toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        formal_leaf_cache=writable,
    )
    before = formal_numba_leaf_cache_lifecycle_metadata()
    executable_identities = {}
    for task_id in TASKS:
        task = build_task(task_id)
        program = task.route_factory().compile()
        materialized = program.materialize(target=target, toolchain=writable_toolchain)
        executable_identities[task_id] = materialized.identity.to_dict()
    after_fill = formal_numba_leaf_cache_lifecycle_metadata()
    materialize_formal_numba_leaf_cache_manifest(cache_root, manifest_path)
    manifest_sha = sha256_file(manifest_path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if type(manifest.get("entry_count")) is not int or manifest["entry_count"] <= 0:
        raise RuntimeError("formal cache manifest is empty")
    sealed = FormalNumbaLeafCachePolicy(cache_root, manifest_path, manifest_sha)
    sealed_toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        formal_leaf_cache=sealed,
    )
    sealed_identities = {}
    for task_id in TASKS:
        task = build_task(task_id)
        program = task.route_factory().compile()
        materialized = program.materialize(target=target, toolchain=sealed_toolchain)
        sealed_identities[task_id] = materialized.identity.to_dict()
    after_verify = formal_numba_leaf_cache_lifecycle_metadata()
    if executable_identities != sealed_identities:
        raise RuntimeError("sealed formal cache changed executable identity")
    fill_misses, verify_hits, verify_misses = validate_cache_lifecycle(
        before, after_fill, after_verify
    )
    result: dict[str, object] = {
        "schema": CACHE_PREPARATION_SCHEMA,
        "status": "PASS__CREATE_ONLY_CACHE_SEALED_READ_ONLY_BEFORE_WORKER_ZERO",
        "source_commit": git_head(ROOT),
        "preregistration_sha256": prereg["preregistration_sha256"],
        "native_library_sha256": sha256_file(args.native.resolve(strict=True)),
        "compute_capability": capability_text,
        "cache_root": str(cache_root.resolve(strict=True)),
        "manifest": str(manifest_path.resolve(strict=True)),
        "manifest_file_sha256": manifest_sha,
        "entry_count": manifest["entry_count"],
        "entries_sha256": manifest["entries_sha256"],
        "create_only_miss_count": fill_misses,
        "sealed_verification_hit_count": verify_hits,
        "sealed_verification_miss_count": verify_misses,
        "executable_identities": executable_identities,
        "gpu_complete_execution_count": 0,
        "goal5843_registered_estimand_timing_observation_count": 0,
    }
    result["preparation_sha256"] = digest(result)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
