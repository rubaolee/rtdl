#!/usr/bin/env python3
"""Create-only modern-RTX materialization and token smoke helper.

Unlike the Home helper, this script does not decide whether a target is
authorized.  The enclosing Goal5791 target-prepare transaction must first
validate the owner authority, GPU, toolchain, source, native, dependencies,
and create-only root.  This helper only compiles/inspects the exact program or
runs one untimed K4 token-path lane.  It cannot create formal workers or a
registered timing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")).hexdigest()


def _inspect(args, legacy, app) -> dict[str, object]:
    import cupy as cp
    from rtdsl.v4_checked_u64_device_reduction import (
        checked_u64_downstream_operation_identity,
        checked_u64_downstream_operation_sha256,
    )

    _, executor, program = legacy._compile_executor(args, app)
    try:
        recipes = {
            variant: checked_u64_downstream_operation_identity(
                variant,
                target_identity_sha256=executor.target_identity_sha256,
                cupy_version=cp.__version__,
            )
            for variant in ("fusion_off", "fusion_on")
        }
        recipe_sha = {
            variant: checked_u64_downstream_operation_sha256(
                variant,
                target_identity_sha256=executor.target_identity_sha256,
                cupy_version=cp.__version__,
            )
            for variant in ("fusion_off", "fusion_on")
        }
        ptx = legacy._ptx_program_identity(program)
        return {
            "schema": "rtdl.goal5791.target_program_inspection.v1",
            "status": "PASS__COMPILE_AND_IDENTITY_ONLY",
            "provider_identity": "optix",
            "program_bundle_identity": (
                "v4_builtin_triangle_checked_reduction_composed"),
            "callback_ir_sha256": executor.callback_ir_sha256,
            "callback_authority_nonce": executor.callback_authority_nonce,
            "contract_sha256": executor.contract_sha256,
            "abi_sha256": executor.abi_sha256,
            "composed_program_sha256": executor.composed_program_sha256,
            "composed_ptx_sha256": executor.composed_program_sha256,
            "native_library_sha256": executor.native_library_sha256,
            "target_identity_sha256": executor.target_identity_sha256,
            "fusion_off_downstream_operation_recipe": recipes["fusion_off"],
            "fusion_on_downstream_operation_recipe": recipes["fusion_on"],
            "fusion_off_downstream_operation_recipe_sha256": recipe_sha[
                "fusion_off"],
            "fusion_on_downstream_operation_recipe_sha256": recipe_sha[
                "fusion_on"],
            "cupy_version": cp.__version__,
            "ptx_program_identity": ptx,
            "ptx_program_identity_sha256": _digest(ptx),
            "token_api_present": True,
            "application_worker_executed": False,
            "optix_launch_executed": False,
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "performance_or_compiler_fusion_claimed": False,
        }
    finally:
        executor.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("inspect-target", "functional"),
                        required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--compute-capability", choices=("89",), required=True)
    parser.add_argument("--optix-sdk", default="9.0.0")
    parser.add_argument("--shared-freeze", type=Path)
    parser.add_argument("--target-materialization", type=Path)
    parser.add_argument("--edge-file", type=Path)
    parser.add_argument("--neutral-prewarm-edge", type=Path)
    parser.add_argument("--variant", choices=("fusion_on", "fusion_off"))
    parser.add_argument("--lifecycle", choices=("cold", "prepared"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if args.mode == "functional":
        cache_spelling = os.environ.get("CUPY_CACHE_DIR")
        if not cache_spelling:
            raise RuntimeError("Goal5791 target smoke cache is not isolated")
        cache = Path(cache_spelling)
        if cache.is_symlink() or not cache.is_dir() or any(cache.iterdir()):
            raise RuntimeError(
                "Goal5791 target smoke cache is not initially empty")
        args.fresh_private_cupy_cache_at_process_start = True
    source = args.source_root.resolve()
    sys.path.insert(0, str(source))
    sys.path.insert(0, str(source / "src"))
    from scripts import goal5790_home_functional_validation as legacy
    from scripts import goal5791_home_token_validation as token_core

    os.environ["RTDL_OPTIX_LIB"] = str(args.native.resolve())
    os.environ["RTDL_OPTIX_LIBRARY"] = str(args.native.resolve())
    app = legacy._load(
        source / "Paper-reproduction-apps/triangle-counting-paper/v4_whole_app.py",
        f"goal5791_target_triangle_{os.getpid()}",
    )
    if args.mode == "inspect-target":
        value = _inspect(args, legacy, app)
    else:
        required = (
            args.shared_freeze, args.target_materialization, args.edge_file,
            args.variant, args.lifecycle,
        )
        if any(item is None for item in required):
            raise ValueError("target functional mode omitted an argument")
        args.input_kind = "small"
        args.dataset = "four_vertex_clique"
        args.expected_triangle_count = 4
        args.max_relation_rows = 1_000_000
        args.execution_environment_class = "MODERN_RTX_CREATE_ONLY_PREPARE"
        args.pod_used = True
        value = token_core._functional(args, legacy, app)
        value["schema"] = "rtdl.goal5791.target_token_functional_lane.v1"
        value["status"] = "PASS__CREATE_ONLY_TOKEN_SMOKE"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(value, indent=2, sort_keys=True) + "\n",
        encoding="utf-8", newline="\n",
    )
    print(json.dumps({
        "mode": args.mode,
        "status": value["status"],
        "output": str(args.output),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
