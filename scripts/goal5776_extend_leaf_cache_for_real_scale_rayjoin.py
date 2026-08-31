#!/usr/bin/env python3
"""Create a successor leaf cache containing the real-scale RayJoin ABI key."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import sys

import numba
import numpy as np

from rtdsl.v4_callback_numba_codegen import (
    formal_numba_leaf_cache_lifecycle_metadata,
    materialize_formal_numba_leaf_cache_manifest,
)
from rtdsl.v4_typed_physical_schema import ReferenceTargetProfile


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    name = "goal5776_real_scale_rayjoin_cache_population"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _make_writable(root: Path) -> None:
    for path in (root, *root.rglob("*")):
        mode = path.stat().st_mode
        path.chmod(mode | stat.S_IWUSR)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--base-cache-root", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--native", required=True, type=Path)
    parser.add_argument("--optix-include", required=True, type=Path)
    parser.add_argument("--cuda-include", required=True, type=Path)
    args = parser.parse_args()
    source = args.source_root.resolve()
    base_cache = args.base_cache_root.resolve()
    output = args.output_root.resolve()
    if output.exists():
        raise FileExistsError(output)
    output.mkdir(parents=False)
    cache = output / "cache"
    shutil.copytree(base_cache, cache)
    _make_writable(cache)
    os.environ["RTDL_V4_FORMAL_LEAF_CACHE"] = str(cache)
    os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST", None)
    os.environ.pop("RTDL_V4_FORMAL_LEAF_CACHE_MANIFEST_SHA256", None)
    native = args.native.resolve()
    target = ReferenceTargetProfile(
        provider="optix", optix_sdk="9.0.0", compute_capability="6.1",
        native_sha256=_sha(native), supports_custom_aabb=True,
        supports_builtin_triangle=True,
    )
    app = _load(
        source / "Paper-reproduction-apps/rayjoin-paper/v4_whole_app.py"
    )
    before = formal_numba_leaf_cache_lifecycle_metadata()
    compiled = app.compile_v4_real_scale_six_batch(
        lsi_capacity=1_000_000, target=target, compute_capability=(6, 1),
        optix_include=args.optix_include.resolve(),
        cuda_include=args.cuda_include.resolve(),
        expected_python_version=platform.python_version(),
        expected_numba_version=numba.__version__,
        expected_numpy_version=np.__version__,
    )
    if len(compiled) != 6:
        raise RuntimeError("RayJoin real-scale compiler did not return full authority")
    after = formal_numba_leaf_cache_lifecycle_metadata()
    manifest = output / "MANIFEST.json"
    materialize_formal_numba_leaf_cache_manifest(cache, manifest)
    document = json.loads(manifest.read_text(encoding="utf-8"))
    result = {
        "schema": "rtdl.goal5776.real_scale_rayjoin_leaf_cache_extension.v1",
        "base_cache_root": str(base_cache),
        "base_entry_count": len(tuple(base_cache.iterdir())),
        "successor_entry_count": int(document["entry_count"]),
        "cache_hit_delta": int(after["hit_count"]) - int(before["hit_count"]),
        "cache_miss_delta": int(after["miss_count"]) - int(before["miss_count"]),
        "cache_disabled_delta": (
            int(after["disabled_count"]) - int(before["disabled_count"])
        ),
        "real_scale_lsi_capacity": 1_000_000,
        "native_library_sha256": _sha(native),
        "manifest_sha256": _sha(manifest),
        "registered_performance_observation_created": False,
        "real_scale_application_worker_executed": False,
    }
    if result["cache_miss_delta"] <= 0 or result["cache_disabled_delta"] != 0:
        raise RuntimeError("RayJoin real-scale cache extension did not add its missing key")
    (output / "RESULT.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    for path in sorted(cache.rglob("*"), reverse=True):
        path.chmod(path.stat().st_mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
    cache.chmod(cache.stat().st_mode & ~stat.S_IWUSR & ~stat.S_IWGRP & ~stat.S_IWOTH)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
