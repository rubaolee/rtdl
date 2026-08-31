#!/usr/bin/env python3
"""Separate true pre-signing BUILD_COLD diagnostic worker for Goal5802.

BUILD_COLD is deliberately not a noninferiority regime.  Each invocation must
create its arm-local pre-deployment build product from source in a new
directory.  Merely reading a prebuilt executable, PTX, or ``.rtdlexe`` is a
failed row.  No output is called deployable: signing, trust-package append,
installation, and deployment are outside this explicitly disclosed boundary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any, Callable, Mapping

from .contract import ARMS, TASKS, validate_freeze
from .controller import (
    consume_formal_worker_live_capability,
    validate_execution_authority,
    validate_formal_worker_preflight_gate,
)
from .runtime_manifest import (
    digest as runtime_digest,
    numba_llvmlite_runtime_authority,
    validate_runtime_manifest,
)


BUILD_REGIME = "BUILD_COLD_ABSOLUTE_DIAGNOSTIC"


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"JSON root is not an object: {path}")
    return value


def _record(path: Path) -> dict[str, object]:
    if path.is_symlink():
        raise RuntimeError(f"BUILD_COLD output is a symlink: {path}")
    path = path.resolve(strict=True)
    if not path.is_file():
        raise RuntimeError(f"BUILD_COLD output is not a regular file: {path}")
    return {"path": str(path), "bytes": path.stat().st_size, "sha256": _sha(path)}


def run_true_build(
        builder: Callable[[], Mapping[str, Path]], *,
        clock: Callable[[], int] = time.perf_counter_ns,
        local_untimed: bool = False) -> dict[str, Any]:
    """Time exactly one true builder; output hashing occurs after the timer."""

    if local_untimed:
        outputs = dict(builder())
        duration = None
    else:
        start = clock()
        outputs = dict(builder())
        end = clock()
        duration = end - start
        if duration <= 0:
            raise RuntimeError("BUILD_COLD timer produced a nonpositive duration")
    if not outputs:
        raise RuntimeError("BUILD_COLD produced no pre-deployment build product")
    records = {role: _record(path) for role, path in outputs.items()}
    return {
        "duration_ns": duration,
        "outputs": records,
        "true_build_executed": True,
        "prebuilt_product_read_as_build": False,
        "build_boundary": "PRE_SIGNING_PRE_DEPLOYMENT_BUILD_PRODUCT",
        "deployable_product_claimed": False,
        "signing_or_trust_governance_inside_timer": False,
        "registered_performance_timing_count": 0 if local_untimed else 1,
        "output_hashing_inside_timer": False,
    }


def _create_output_root(path: Path) -> Path:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.mkdir(parents=True)
    return path.resolve(strict=True)


def _build_relation_compaction_cubin(
        runtime: Mapping[str, Any], root: Path) -> Path:
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from scripts.goal5802_prepare_matched_ptx_untimed import (
        _compile_target_cubin,
    )
    source = Path(runtime["files"]["compaction_source"]["path"])
    cubin, _architecture, _options = _compile_target_cubin(
        source, baseline,
        str(runtime["target_observation"]["compute_capability"]))
    output = root / "relation_semantic_compaction.cubin"
    output.write_bytes(cubin)
    return output


def _pyoptix_builder(
        runtime: Mapping[str, Any], output_root: Path, *, task: str):
    def build() -> Mapping[str, Path]:
        root = _create_output_root(output_root)
        from experiments.goal5796_matched import pyoptix_baseline as baseline
        from scripts.goal5802_prepare_matched_ptx_untimed import (
            _compile_exact_ptx,
        )
        files = runtime["files"]
        directories = runtime["directories"]
        ptx, _options, _target = _compile_exact_ptx(
            Path(files["device_source"]["path"]),
            Path(directories["optix_include"]["path"]),
            Path(directories["cuda_include"]["path"]),
            baseline,
            str(runtime["target_observation"]["compute_capability"]),
        )
        if not ptx or b".version" not in ptx[:4096]:
            raise RuntimeError("PyOptiX BUILD_COLD emitted invalid PTX")
        output = root / "matched.ptx"
        output.write_bytes(ptx)
        outputs = {"matched_ptx": output}
        if task == TASKS[0]:
            outputs["relation_semantic_compaction_cubin"] = \
                _build_relation_compaction_cubin(runtime, root)
        return outputs
    return build


def _recipe_argv(
        recipe: Mapping[str, Any], *, runtime: Mapping[str, Any],
        output_binary: Path) -> list[str]:
    if recipe.get("schema") != "rtdl.goal5802.direct_build_recipe.v2" \
            or set(recipe) != {"schema", "argv_template", "recipe_sha256"}:
        raise RuntimeError("Direct BUILD_COLD recipe schema differs")
    unsigned = dict(recipe)
    observed = unsigned.pop("recipe_sha256")
    expected = hashlib.sha256(json.dumps(
        unsigned, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()
    if observed != expected:
        raise RuntimeError("Direct BUILD_COLD recipe self-digest mismatch")
    template = recipe["argv_template"]
    if not isinstance(template, list) or not template \
            or not all(isinstance(item, str) and item for item in template):
        raise RuntimeError("Direct BUILD_COLD argv template invalid")
    fixed_prefix = [
        "{CXX}", "-std=c++17", "-O3", "-DNDEBUG",
        "-Wall", "-Wextra", "-Werror",
        "-I{OPTIX_INCLUDE}", "-I{CUDA_INCLUDE}",
        "-I{CUDA_INCLUDE}/nv", "{DIRECT_SOURCE}",
    ]
    fixed_suffix = ["-lcuda", "-lnvrtc", "-ldl", "-o", "{OUTPUT}"]
    library_tokens = template[len(fixed_prefix):-len(fixed_suffix)]
    if template[:len(fixed_prefix)] != fixed_prefix \
            or template[-len(fixed_suffix):] != fixed_suffix \
            or len(library_tokens) != len(set(library_tokens)) \
            or any(not token.startswith("-L")
                   or not Path(token[2:]).is_absolute()
                   or "{" in token or "}" in token
                   for token in library_tokens):
        raise RuntimeError("Direct BUILD_COLD compile-option grammar differs")
    files = runtime["files"]
    directories = runtime["directories"]
    replacements = {
        "{CXX}": str(files["cxx_compiler"]["path"]),
        "{DIRECT_SOURCE}": str(files["direct_scalar_source"]["path"]),
        "{OPTIX_INCLUDE}": str(directories["optix_include"]["path"]),
        "{CUDA_INCLUDE}": str(directories["cuda_include"]["path"]),
        "{OUTPUT}": str(output_binary),
    }
    argv: list[str] = []
    seen: set[str] = set()
    for token in template:
        expanded = token
        for marker, value in replacements.items():
            if marker in expanded:
                seen.add(marker)
                expanded = expanded.replace(marker, value)
        if "{" in expanded or "}" in expanded:
            raise RuntimeError("Direct BUILD_COLD recipe has unknown placeholder")
        argv.append(expanded)
    if seen != set(replacements) or argv[0] != replacements["{CXX}"]:
        raise RuntimeError("Direct BUILD_COLD recipe omits a required binding")
    if argv.count(str(output_binary)) != 1:
        raise RuntimeError("Direct BUILD_COLD output appears other than once")
    return argv


def _direct_builder(
        runtime: Mapping[str, Any], output_root: Path, *, task: str,
        worker_id: str, freeze_sha: str, authority_sha: str,
        runtime_sha: str):
    def build() -> Mapping[str, Path]:
        root = _create_output_root(output_root)
        files = runtime["files"]
        directories = runtime["directories"]
        binary = root / "direct_scalar_worker"
        recipe = _read_json(Path(files["direct_build_recipe"]["path"]))
        argv = _recipe_argv(recipe, runtime=runtime, output_binary=binary)
        compiled = subprocess.run(argv, capture_output=True, check=False)
        if compiled.returncode != 0 or not binary.is_file():
            raise RuntimeError({
                "direct_compile_exit": compiled.returncode,
                "stdout_sha256": hashlib.sha256(compiled.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(compiled.stderr).hexdigest(),
            })
        ptx = root / "matched.ptx"
        environment = dict(os.environ)
        environment["GOAL5802_BUILD_WORKER_PID"] = str(os.getpid())
        environment["GOAL5802_EXECUTION_AUTHORITY_SHA256"] = authority_sha
        environment["GOAL5802_RUNTIME_MANIFEST_SHA256"] = runtime_sha
        built = subprocess.run([
            str(binary), "--worker-id", worker_id,
            "--task", task,
            "--freeze-sha256", freeze_sha,
            "--authority-sha256", authority_sha,
            "--runtime-manifest-sha256", runtime_sha,
            "--device-source", str(files["device_source"]["path"]),
            "--optix-include", str(directories["optix_include"]["path"]),
            "--cuda-include", str(directories["cuda_include"]["path"]),
            "--compute-architecture", "compute_" + str(
                runtime["target_observation"]["compute_capability"]
            ).replace(".", ""),
            "--build-ptx-output", str(ptx),
        ], env=environment, capture_output=True, check=False)
        if built.returncode != 0 or not ptx.is_file():
            raise RuntimeError({
                "direct_nvrtc_exit": built.returncode,
                "stdout_sha256": hashlib.sha256(built.stdout).hexdigest(),
                "stderr_sha256": hashlib.sha256(built.stderr).hexdigest(),
            })
        outputs = {"direct_executable": binary, "matched_ptx": ptx}
        if task == TASKS[0]:
            outputs["relation_semantic_compaction_cubin"] = \
                _build_relation_compaction_cubin(runtime, root)
        return outputs
    return build


def _rtdl_builder(
        runtime: Mapping[str, Any], output_root: Path, *, task: str,
        worker_id: str):
    def build() -> Mapping[str, Path]:
        root = _create_output_root(output_root)
        from rtdsl import RTDLExecutableBuildRoots, build_rtdlexe
        from rtdsl.v4 import (
            AnyHitProtocolProof,
            BoundedRelationProtocol,
            TriangleReductionMode,
            TriangleReductionProtocol,
            V4Target,
            V4Toolchain,
            compile_protocol_program,
            standard_protocol_physical_plan,
        )
        import numba
        import llvmlite

        files = runtime["files"]
        directories = runtime["directories"]
        proof_path = Path(files["callback_proof"]["path"])
        if task.startswith("CUSTOM_AABB"):
            protocol = BoundedRelationProtocol(
                capacity=4096, minimum_overlap_f32=1.0)
        else:
            protocol = TriangleReductionProtocol(
                TriangleReductionMode.WEIGHTED_HIT_COUNT)
        physical = standard_protocol_physical_plan(protocol)
        proof = AnyHitProtocolProof(
            callback_ir_sha256=physical.callback_ir_sha256,
            effect_digest=physical.effect_digest,
            proof_sha256=_sha(proof_path),
            proof_kind="external_machine_checked_order_independence_v1",
        )
        cc_text = str(runtime["target_observation"]["compute_capability"])
        if re.fullmatch(r"[0-9]+\.[0-9]+", cc_text) is None:
            raise RuntimeError("BUILD_COLD compute capability invalid")
        cc = tuple(map(int, cc_text.split(".")))
        target = V4Target.from_native(
            files["native_library"]["path"],
            optix_sdk=directories["optix_sdk"]["path"],
            compute_capability=cc,
        )
        toolchain = V4Toolchain.current(
            compute_capability=cc,
            optix_include=directories["optix_include"]["path"],
            cuda_include=directories["cuda_include"]["path"],
        )
        nvcc = subprocess.run(
            [files["nvcc"]["path"], "--version"], check=True,
            capture_output=True, text=True).stdout.strip()
        roots = RTDLExecutableBuildRoots(
            llvmlite_version=llvmlite.__version__,
            cuda_toolkit_version=nvcc.splitlines()[-1],
            link_options=("max_trace_depth=1", "debug=none"),
        )
        program = compile_protocol_program(
            protocol, physical_plan=physical, any_hit_proof=proof)
        materialized = program.materialize(target=target, toolchain=toolchain)
        authority = root / "candidate.authority.json"
        built = build_rtdlexe(
            materialized,
            artifact_directory=root / "artifacts",
            authority_path=authority,
            build_roots=roots,
            deployment_id=f"goal5802/build-cold/{task}/{worker_id}",
        )
        if not built.artifact_path.is_file() or not authority.is_file():
            raise RuntimeError("RTDL BUILD_COLD did not emit candidate pair")
        return {
            "unsigned_rtdlexe": built.artifact_path,
            "detached_unsigned_authority": authority,
        }
    return build


def _rtdsl_import_identity(
        runtime: Mapping[str, Any], *, task: str) -> dict[str, object]:
    """Bind every live RTDL module used by BUILD_COLD to the sealed package."""

    package = runtime["directories"]["rtdsl_package"]
    package_root = Path(str(package["path"])).resolve(strict=True)
    package_rows = package.get("files")
    if not isinstance(package_rows, list):
        raise RuntimeError("BUILD_COLD sealed rtdsl package rows absent")
    by_path = {
        str(row.get("path")): row for row in package_rows
        if isinstance(row, Mapping) and isinstance(row.get("path"), str)}
    if len(by_path) != len(package_rows):
        raise RuntimeError("BUILD_COLD sealed rtdsl package rows malformed")
    module_rows: list[dict[str, object]] = []
    observed_names: set[str] = set()
    for name, module in sorted(sys.modules.items()):
        if name != "rtdsl" and not name.startswith("rtdsl."):
            continue
        raw_path = getattr(module, "__file__", None)
        if not isinstance(raw_path, str) or not raw_path:
            raise RuntimeError(f"BUILD_COLD RTDL module has no file: {name}")
        path = Path(raw_path).resolve(strict=True)
        if not path.is_file() or path.is_symlink() \
                or not path.is_relative_to(package_root):
            raise RuntimeError(
                f"BUILD_COLD RTDL module escapes sealed package: {name}")
        relative = "rtdsl/" + path.relative_to(package_root).as_posix()
        expected = by_path.get(relative)
        actual = {
            "module": name,
            "path": str(path),
            "relative_path": relative,
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        }
        if not isinstance(expected, Mapping) \
                or actual["bytes"] != expected.get("bytes") \
                or actual["sha256"] != expected.get("sha256"):
            raise RuntimeError(
                f"BUILD_COLD RTDL module differs from sealed package: {name}")
        module_rows.append(actual)
        observed_names.add(name)
    required = {
        "rtdsl", "rtdsl.v4", "rtdsl.v4_callback_lifecycle",
        "rtdsl.v4_rtdlexe",
        ("rtdsl.v4_bounded_relation_optix_compiler"
         if task == TASKS[0]
         else "rtdsl.v4_triangle_standard_library"),
    }
    if task != TASKS[0]:
        required.add("rtdsl.v4_triangle_reduction_optix_compiler")
    if not required.issubset(observed_names):
        raise RuntimeError({
            "BUILD_COLD_required_rtdsl_modules_absent": sorted(
                required - observed_names)})
    return {
        "schema": "rtdl.goal5802.build_cold_rtdsl_import_identity.v1",
        "status": "PASS__ALL_LOADED_RTDL_MODULES_FROM_SEALED_PACKAGE",
        "rtdsl_package_file_count": package["file_count"],
        "rtdsl_package_tree_sha256": package["tree_sha256"],
        "required_module_names": sorted(required),
        "loaded_rtdsl_modules": module_rows,
        "loaded_rtdsl_modules_sha256": hashlib.sha256(json.dumps(
            module_rows, sort_keys=True, separators=(",", ":"),
            allow_nan=False).encode("utf-8")).hexdigest(),
    }


def _compiler_runtime_identity(
        runtime: Mapping[str, Any]) -> dict[str, object]:
    """Bind the actually loaded RTDL build compiler modules to host authority."""

    host_path = Path(str(runtime["files"]["host_runtime_provenance"]["path"]))
    host_runtime = _read_json(host_path)
    authority = numba_llvmlite_runtime_authority(
        host_runtime, runtime["files"])
    expected_distributions = {
        str(row["name"]): row for row in authority["distributions"]}
    expected_modules = {
        str(row["name"]): row for row in authority["loaded_module_files"]}
    rows: list[dict[str, object]] = []
    for name in ("numba", "llvmlite"):
        module = sys.modules.get(name)
        raw_path = getattr(module, "__file__", None)
        version = getattr(module, "__version__", None)
        if module is None or not isinstance(raw_path, str) or not raw_path \
                or not isinstance(version, str) or not version:
            raise RuntimeError(
                f"BUILD_COLD compiler module was not actually loaded: {name}")
        path = Path(raw_path).resolve(strict=True)
        actual = {
            "name": name,
            "version": version,
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        }
        expected_distribution = expected_distributions.get(name)
        expected_module = expected_modules.get(name)
        if not path.is_file() or not isinstance(expected_distribution, Mapping) \
                or not isinstance(expected_module, Mapping) \
                or actual["version"] != expected_distribution.get("version") \
                or actual["path"] != expected_module.get("path") \
                or actual["bytes"] != expected_module.get("bytes") \
                or actual["sha256"] != expected_module.get("sha256"):
            raise RuntimeError(
                f"BUILD_COLD compiler module differs from sealed runtime: {name}")
        rows.append(actual)
    unsigned: dict[str, object] = {
        "schema": "rtdl.goal5802.build_cold_compiler_runtime_identity.v1",
        "status": "PASS__ACTUAL_NUMBA_LLVM_LITE_MATCH_SEALED_RUNTIME",
        "compiler_runtime_authority_sha256": authority["authority_sha256"],
        "actual_loaded_module_files": rows,
        "actual_loaded_module_files_sha256": runtime_digest(rows),
    }
    return {**unsigned, "identity_sha256": runtime_digest(unsigned)}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--worker-id", required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--runtime-manifest", type=Path, required=True)
    parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    root = args.root.resolve(strict=True)
    freeze = _read_json(args.freeze)
    validate_freeze(freeze, root)
    runtime = _read_json(args.runtime_manifest)
    validate_runtime_manifest(runtime)
    freeze_sha = _sha(args.freeze)
    runtime_sha = _sha(args.runtime_manifest)
    authority = _read_json(args.execution_authority)
    validate_execution_authority(
        authority, freeze_sha256=freeze_sha,
        runtime_manifest_sha256=runtime_sha)
    authority_sha = _sha(args.execution_authority)
    if os.environ.get("GOAL5802_FORMAL_CONTROLLER_PID") != str(os.getppid()) \
            or os.environ.get("GOAL5802_EXECUTION_AUTHORITY_SHA256") \
            != authority_sha \
            or os.environ.get("GOAL5802_RUNTIME_MANIFEST_SHA256") != runtime_sha:
        raise RuntimeError("BUILD_COLD worker was not born under exact controller")
    # Reject direct entry before choosing or importing any measured builder.
    # This is an operator-entry lineage guard, not malicious-owner auth.
    validate_formal_worker_preflight_gate(
        runtime_manifest_sha256=runtime_sha)
    consume_formal_worker_live_capability(
        worker_id=args.worker_id, runtime_manifest_sha256=runtime_sha)
    matches = [row for row in freeze["build_cold_absolute_schedule"]
               if row["worker_id"] == args.worker_id]
    if len(matches) != 1 or matches[0]["arm"] != args.arm \
            or matches[0]["task"] != args.task:
        raise RuntimeError("BUILD_COLD worker/schedule row mismatch")
    if args.arm.startswith("B_NVIDIA_PYOPTIX"):
        builder = _pyoptix_builder(
            runtime, args.output_directory, task=args.task)
    elif args.arm == "A_DIRECT_CUDA_OPTIX":
        builder = _direct_builder(
            runtime, args.output_directory, task=args.task,
            worker_id=args.worker_id, freeze_sha=freeze_sha,
            authority_sha=authority_sha, runtime_sha=runtime_sha)
    else:
        builder = _rtdl_builder(
            runtime, args.output_directory, task=args.task,
            worker_id=args.worker_id)
    result = run_true_build(builder)
    rtdsl_import_identity = (
        _rtdsl_import_identity(runtime, task=args.task)
        if args.arm == ARMS[2] else None)
    compiler_runtime_identity = (
        _compiler_runtime_identity(runtime)
        if args.arm == ARMS[2] else None)
    result.update({
        "schema": "rtdl.goal5802.build_cold_worker_result.v1",
        "status": "PASS",
        "worker_id": args.worker_id,
        "task": args.task,
        "arm": args.arm,
        "regime": BUILD_REGIME,
        "freeze_file_sha256": freeze_sha,
        "execution_authority_sha256": authority_sha,
        "runtime_manifest_sha256": runtime_sha,
        "comparative_gate": False,
        "unconditional_publication": True,
        "rtdsl_import_identity": rtdsl_import_identity,
        "compiler_runtime_identity": compiler_runtime_identity,
    })
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
