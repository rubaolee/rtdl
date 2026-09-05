#!/usr/bin/env python3
"""Build and sign deploy-only family .rtdlexe candidates for Goal5847."""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import (
    RELATION_TASK,
    TRIANGLE_TASK,
)
from experiments.goal5842_causal_admission.tasks import build_task
from experiments.goal5847_aot_startup.contracts import digest
from scripts.goal5801_rtdlexe_trust import create_root, freeze

ROOT = Path(__file__).resolve().parents[1]
TASKS = (RELATION_TASK, TRIANGLE_TASK)
LABELS = {RELATION_TASK: "relation", TRIANGLE_TASK: "triangle"}


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


def _validate_native_manifest(
    path: Path,
    native: Path,
    *,
    expected_source_commit: str,
    optix_sdk: str,
    compute_capability: tuple[int, int],
) -> dict[str, object]:
    from scripts.build_v4_optix_native_snapshot import (
        RTDLEXE_AOT_REQUIRED_SYMBOLS,
    )

    value = json.loads(path.resolve(strict=True).read_text(encoding="utf-8"))
    build_input = value.get("build_input")
    if not isinstance(build_input, dict) \
            or value.get("schema") != "rtdl.v4.optix_native_snapshot_build.v3" \
            or value.get("status") != "PASS__MINIMAL_RTDLEXE_AOT_NATIVE" \
            or value.get("deployment_profile") != "rtdlexe_aot_runtime_v1" \
            or value.get("git_commit") != expected_source_commit \
            or value.get("git_commit_after_build") != expected_source_commit \
            or value.get("git_status_before_build") != [] \
            or value.get("git_status_after_build") != [] \
            or value.get("dirty_build_authorized") is not False \
            or value.get("native_bytes") != native.stat().st_size \
            or value.get("native_sha256") != _sha256_file(native) \
            or value.get("all_required_symbols_exported") is not True \
            or value.get("all_exports_allowlisted") is not True \
            or value.get("unexpected_exported_symbols") != [] \
            or value.get("exported_symbol_match_mode") \
                != "exact_nm_dynamic_defined_name" \
            or value.get("required_symbols") != list(RTDLEXE_AOT_REQUIRED_SYMBOLS) \
            or value.get("runtime_compiler_linkage") \
                != "lazy_dlopen_build_pinned" \
            or value.get("eager_nvrtc_dependency") is not False \
            or "nvrtc" in str(value.get("dynamic_dependencies", "")).lower() \
            or build_input.get("expected_optix_sdk") != optix_sdk \
            or build_input.get("compute_capability") \
                != list(compute_capability):
        raise RuntimeError("Goal5847 minimal native build manifest differs")
    return value


def _write_create(path: Path, value: dict[str, object]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    descriptor = os.open(path, flags, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(
                json.dumps(value, indent=2, sort_keys=True).encode("utf-8")
                + b"\n"
            )
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--native-build-manifest", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cuda-toolkit-version", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    args = parser.parse_args()

    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    if source_commit != args.expected_source_commit \
            or _git("status", "--porcelain=v1", "--untracked-files=all"):
        raise RuntimeError("Goal5847 candidate build requires exact clean source")
    output_root = args.output_root.expanduser().absolute()
    cache_root = args.cache_root.expanduser().absolute()
    for path in (output_root, cache_root):
        try:
            path.relative_to(ROOT.resolve(strict=True))
        except ValueError:
            pass
        else:
            raise RuntimeError("Goal5847 generated build state must remain outside Git")
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    output_root.mkdir(parents=True)
    (output_root / "artifacts").mkdir()
    cache_root.mkdir(parents=True)

    from rtdsl.v4 import (
        FormalNumbaLeafCachePolicy,
        V4Target,
        V4Toolchain,
    )
    from rtdsl.v4_rtdlexe import (
        RTDLExecutableBuildRoots,
        build_family_rtdlexe,
    )

    native = args.native.resolve(strict=True)
    native_manifest_path = args.native_build_manifest.resolve(strict=True)
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    if len(capability) != 2:
        raise ValueError("Goal5847 compute capability must have two components")
    native_manifest = _validate_native_manifest(
        native_manifest_path,
        native,
        expected_source_commit=source_commit,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
    )
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
        formal_leaf_cache=FormalNumbaLeafCachePolicy(cache_root),
    )
    roots = RTDLExecutableBuildRoots(
        llvmlite_version=importlib.metadata.version("llvmlite"),
        cuda_toolkit_version=args.cuda_toolkit_version,
        link_options=("max_trace_depth=1", "debug=none"),
    )
    rows: dict[str, object] = {}
    build_started = time.perf_counter_ns()
    for task_id in TASKS:
        label = LABELS[task_id]
        task = build_task(task_id)
        task_started = time.perf_counter_ns()
        materialized = task.route_factory().compile().materialize(
            target=target,
            toolchain=toolchain,
        )
        authority = output_root / f"{label}.authority.json"
        deployment_id = f"goal5847-{label}-slot"
        built = build_family_rtdlexe(
            materialized,
            artifact_directory=output_root / "artifacts",
            authority_path=authority,
            build_roots=roots,
            deployment_id=deployment_id,
        )
        public = output_root / f"{label}.public.json"
        package = output_root / f"{label}.package.json"
        head = output_root / f"{label}.head.json"
        with tempfile.TemporaryDirectory(prefix=f"goal5847-{label}-key-") as tmp:
            private = Path(tmp) / "private.json"
            create_root(
                private_path=private,
                public_path=public,
                key_id=f"TEST_ONLY_goal5847_{label}",
                bits=2048,
            )
            freeze(
                private_path=private,
                root_path=public,
                authority_path=authority,
                output_path=package,
                head_output_path=head,
                previous_path=None,
            )
        rows[label] = {
            "task": task_id,
            "deployment_id": deployment_id,
            "artifact": str(built.artifact_path.resolve(strict=True)),
            "artifact_sha256": _sha256_file(built.artifact_path),
            "authority": str(authority.resolve(strict=True)),
            "authority_sha256": _sha256_file(authority),
            "public": str(public.resolve(strict=True)),
            "public_sha256": _sha256_file(public),
            "package": str(package.resolve(strict=True)),
            "package_sha256": _sha256_file(package),
            "head": str(head.resolve(strict=True)),
            "head_sha256": _sha256_file(head),
            "executable_identity_sha256": (
                built.executable_identity_sha256
            ),
            "family_executable_identity_sha256": (
                built.family_executable_identity_sha256
            ),
            "materialize_build_and_sign_ns": (
                time.perf_counter_ns() - task_started
            ),
            "test_only_signing_key_destroyed_after_freeze": True,
        }
    result: dict[str, object] = {
        "schema": "rtdl.goal5847.aot_candidates.v1",
        "status": "PASS__DEPLOY_ONLY_FAMILY_CANDIDATES_BUILT",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "native": str(native),
        "native_bytes": native.stat().st_size,
        "native_sha256": _sha256_file(native),
        "native_build_manifest": str(native_manifest_path),
        "native_build_manifest_sha256": _sha256_file(native_manifest_path),
        "native_build_id": native_manifest["build_id"],
        "optix_sdk": args.optix_sdk,
        "compute_capability": list(capability),
        "build_roots": {
            "llvmlite_version": roots.llvmlite_version,
            "cuda_toolkit_version": roots.cuda_toolkit_version,
            "link_options": list(roots.link_options),
        },
        "rows": rows,
        "total_build_ns": time.perf_counter_ns() - build_started,
        "claim_boundary": {
            "test_only_signing": True,
            "production_key_custody_attested": False,
            "gpu_execution_performed": False,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    result["manifest_sha256"] = digest(result)
    _write_create(output_root / "manifest.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
