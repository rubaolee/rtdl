#!/usr/bin/env python3
"""Build or exactly reuse signed Goal5848 relation/triangle AOT candidates."""

from __future__ import annotations

import argparse
import atexit
import hashlib
import importlib.metadata
import json
import os
import statistics
import subprocess
import sys
import time
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5848_strong_baseline.aot_requests import (
    TASK_REQUESTS,
    request_for_task,
)
from experiments.goal5848_strong_baseline.contracts import (
    AOT_HIT_REPETITIONS,
    TASKS,
    digest,
    ratio_ppm,
    strict_json_loads,
)
from experiments.goal5848_strong_baseline.controller import _new_output_root
from rtdsl.v4_aot_cache import resolve_exact_aot

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


def _write_create(path: Path, value: dict[str, object]) -> None:
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        payload = json.dumps(value, indent=2, sort_keys=True).encode() + b"\n"
        with os.fdopen(descriptor, "wb", closefd=True) as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _unlink_signing_private_files(
    signing: Mapping[str, Mapping[str, object]],
) -> None:
    for task_id, task_signing in signing.items():
        private = Path(str(task_signing["private"]))
        if private.exists() or private.is_symlink():
            private.unlink()
        if private.exists() or private.is_symlink():
            raise RuntimeError(
                f"Goal5848 private key path survived unlink: {task_id}"
            )


def _validate_native_manifest(
    path: Path,
    native: Path,
    *,
    expected_source_commit: str,
    optix_sdk: str,
    compute_capability: tuple[int, int],
) -> dict[str, object]:
    value = strict_json_loads(
        path.resolve(strict=True).read_text(encoding="utf-8"),
        label="Goal5848 native build manifest",
    )
    build_input = value.get("build_input")
    if (
        not isinstance(value, dict)
        or not isinstance(build_input, dict)
        or value.get("schema")
        != "rtdl.v4.optix_native_snapshot_build.v3"
        or value.get("status") != "PASS__MINIMAL_RTDLEXE_AOT_NATIVE"
        or value.get("deployment_profile") != "rtdlexe_aot_runtime_v1"
        or value.get("git_commit") != expected_source_commit
        or value.get("git_commit_after_build") != expected_source_commit
        or value.get("git_status_before_build") != []
        or value.get("git_status_after_build") != []
        or value.get("dirty_build_authorized") is not False
        or value.get("native_bytes") != native.stat().st_size
        or value.get("native_sha256") != _sha256_file(native)
        or value.get("all_required_symbols_exported") is not True
        or value.get("all_exports_allowlisted") is not True
        or value.get("unexpected_exported_symbols") != []
        or value.get("eager_nvrtc_dependency") is not False
        or "nvrtc" in str(value.get("dynamic_dependencies", "")).lower()
        or build_input.get("expected_optix_sdk") != optix_sdk
        or build_input.get("compute_capability") != list(compute_capability)
        or not isinstance(build_input.get("optix_header_inventory"), list)
        or not isinstance(build_input.get("cuda_header_inventory"), list)
    ):
        raise RuntimeError("Goal5848 minimal native build manifest differs")
    return value


def _validate_signing_roots(
    path: Path,
    signing: dict[str, dict[str, object]],
) -> str:
    resolved = path.resolve(strict=True)
    value = strict_json_loads(
        resolved.read_text(encoding="utf-8"),
        label="Goal5848 signing-root receipt",
    )
    if not isinstance(value, dict):
        raise TypeError("Goal5848 signing-root receipt must be an object")
    unsigned = dict(value)
    seal = unsigned.pop("receipt_sha256", None)
    rows = value.get("rows")
    if (
        seal != digest(unsigned)
        or value.get("schema") != "rtdl.goal5848.test_signing_roots.v1"
        or value.get("status")
        != "PASS__TWO_DISTINCT_TEST_ONLY_ROOTS_CREATED"
        or value.get("private_key_paths_must_be_unlinked_by_aot_builder")
        is not True
        or value.get("production_key_custody_attested") is not False
        or value.get("registered_performance_timing_count") != 0
        or value.get("formal_worker_count") != 0
        or not isinstance(rows, dict)
        or set(rows) != {"relation", "triangle"}
    ):
        raise RuntimeError("Goal5848 signing-root receipt differs")
    for task in TASKS:
        label = str(TASK_REQUESTS[task]["label"])
        receipt_row = rows[label]
        current = signing[task]
        if (
            not isinstance(receipt_row, dict)
            or receipt_row.get("private_path") != str(current["private"])
            or receipt_row.get("public_path") != str(current["public"])
            or receipt_row.get("private_sha256")
            != _sha256_file(Path(str(current["private"])))
            or receipt_row.get("public_sha256")
            != _sha256_file(Path(str(current["public"])))
        ):
            raise RuntimeError("Goal5848 signing-root identity differs")
    return _sha256_file(resolved)


def _verifier(
    paths,
    *,
    request,
) -> dict[str, object]:
    from rtdsl import v4_rtdlexe as runtime

    deployment = runtime.install_rtdlexe_deployment(
        trust_root_path=paths["trust_root"],
        trust_head_path=paths["trust_head"],
        trust_package_path=paths["trust_package"],
        deployment_id=request.deployment_id,
    )
    loaded = runtime.load_rtdlexe(
        paths["artifact"],
        authority_path=paths["authority"],
        deployment=deployment,
    )
    target = loaded.product_projection["target_toolchain"]
    artifact = strict_json_loads(
        paths["artifact"].read_text(encoding="utf-8"),
        label="Goal5848 built RTDL artifact",
    )
    declaration = artifact.get("protocol_declaration")
    if (
        loaded.family != request.family
        or loaded.deployment_id != request.deployment_id
        or not isinstance(target, Mapping)
        or target.get("target_sha256") != request.target_sha256
        or target.get("native_library_sha256")
        != request.native_library_sha256
        or not isinstance(declaration, dict)
        or declaration.get("task_semantics_sha256")
        != request.task_semantics_sha256
        or loaded.family_executable_identity_sha256 is None
    ):
        raise RuntimeError("Goal5848 cached deployment binding differs")
    return {
        "artifact_sha256": loaded.artifact_sha256,
        "authority_sha256": loaded.authority_sha256,
        "family": loaded.family,
        "deployment_id": loaded.deployment_id,
        "executable_identity_sha256": loaded.executable_identity_sha256,
        "family_executable_identity_sha256": (
            loaded.family_executable_identity_sha256
        ),
        "target_sha256": target["target_sha256"],
        "native_library_sha256": target["native_library_sha256"],
    }


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
    parser.add_argument("--leaf-cache-root", type=Path, required=True)
    parser.add_argument("--aot-cache-root", type=Path, required=True)
    parser.add_argument("--relation-signing-private", type=Path, required=True)
    parser.add_argument("--relation-signing-public", type=Path, required=True)
    parser.add_argument("--triangle-signing-private", type=Path, required=True)
    parser.add_argument("--triangle-signing-public", type=Path, required=True)
    parser.add_argument("--signing-roots-receipt", type=Path, required=True)
    parser.add_argument(
        "--unlink-signing-private-after-build",
        action="store_true",
    )
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--hit-repetitions", type=int, default=AOT_HIT_REPETITIONS)
    parser.add_argument("--require-cold-first", action="store_true")
    args = parser.parse_args()
    if args.hit_repetitions != AOT_HIT_REPETITIONS:
        raise ValueError("Goal5848 cache hit repetitions differ from protocol")
    if not args.unlink_signing_private_after_build:
        raise ValueError("Goal5848 requires post-build private-key path unlink")
    source_commit = _git("rev-parse", "HEAD")
    source_tree = _git("rev-parse", "HEAD^{tree}")
    if (
        source_commit != args.expected_source_commit
        or _git("status", "--porcelain=v1", "--untracked-files=all")
    ):
        raise RuntimeError("Goal5848 AOT build requires exact clean source")
    output_root = _new_output_root(args.output_root)
    output_root.mkdir(parents=True)
    native = args.native.resolve(strict=True)
    native_manifest_path = args.native_build_manifest.resolve(strict=True)
    capability = tuple(int(item) for item in args.compute_capability.split("."))
    if len(capability) != 2:
        raise ValueError("Goal5848 compute capability must have two components")
    native_manifest = _validate_native_manifest(
        native_manifest_path,
        native,
        expected_source_commit=source_commit,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
    )
    versions = {
        name: importlib.metadata.version(name)
        for name in ("numba", "numpy", "llvmlite")
    }
    build_roots_mapping = {
        "llvmlite_version": versions["llvmlite"],
        "cuda_toolkit_version": args.cuda_toolkit_version,
        "link_options": ["max_trace_depth=1", "debug=none"],
        "wrapper_numeric_policy": "strict",
        "leaf_numeric_policy": "strict",
        "composer_schema": "rtdl.v4.composed_callback_ptx.v1",
    }
    native_sha256 = _sha256_file(native)
    native_manifest_sha256 = _sha256_file(native_manifest_path)
    signing = {
        TASKS[0]: {
            "private": args.relation_signing_private.resolve(strict=True),
            "public": args.relation_signing_public.resolve(strict=True),
        },
        TASKS[1]: {
            "private": args.triangle_signing_private.resolve(strict=True),
            "public": args.triangle_signing_public.resolve(strict=True),
        },
    }
    if len({row["private"] for row in signing.values()}) != len(signing):
        raise RuntimeError("Goal5848 task signing private keys must be distinct")
    for row in signing.values():
        if row["private"].is_symlink() or row["public"].is_symlink():
            raise RuntimeError("Goal5848 signing paths cannot be symbolic")
        row["public_sha256"] = _sha256_file(row["public"])
    signing_roots_receipt_sha256 = _validate_signing_roots(
        args.signing_roots_receipt, signing
    )
    atexit.register(_unlink_signing_private_files, signing)
    rows = {}
    total_started = time.perf_counter_ns()
    for task_id in TASKS:
        task_row = TASK_REQUESTS[task_id]
        label = str(task_row["label"])
        task_signing = signing[task_id]
        request = request_for_task(
            task_id,
            source_commit=source_commit,
            source_tree=source_tree,
            native_library_sha256=native_sha256,
            native_build_manifest_sha256=native_manifest_sha256,
            optix_sdk=args.optix_sdk,
            compute_capability=args.compute_capability,
            python_version=sys.version.split()[0],
            numba_version=versions["numba"],
            numpy_version=versions["numpy"],
            llvmlite_version=versions["llvmlite"],
            cuda_toolkit_version=args.cuda_toolkit_version,
            build_roots=build_roots_mapping,
            trust_root_file_sha256=str(task_signing["public_sha256"]),
        )
        producer_calls = 0

        def producer(
            root: Path,
            *,
            current_task=task_id,
            current_request=request,
            current_signing=task_signing,
        ):
            nonlocal producer_calls
            producer_calls += 1
            root.mkdir(parents=True)
            (root / "artifacts").mkdir()
            from experiments.goal5842_causal_admission.tasks import build_task
            from rtdsl.v4 import (
                FormalNumbaLeafCachePolicy,
                V4Target,
                V4Toolchain,
            )
            from rtdsl.v4_rtdlexe import (
                RTDLExecutableBuildRoots,
                build_family_rtdlexe,
            )
            from scripts.goal5801_rtdlexe_trust import freeze

            target = V4Target.from_native(
                native,
                optix_sdk=args.optix_sdk,
                compute_capability=capability,
            )
            if target.profile.target_sha256 != current_request.target_sha256:
                raise RuntimeError("Goal5848 precompiler target identity differs")
            toolchain = V4Toolchain.current(
                compute_capability=capability,
                optix_include=args.optix_include.resolve(strict=True),
                cuda_include=args.cuda_include.resolve(strict=True),
                formal_leaf_cache=FormalNumbaLeafCachePolicy(
                    args.leaf_cache_root.expanduser().absolute()
                ),
            )
            roots = RTDLExecutableBuildRoots(
                llvmlite_version=versions["llvmlite"],
                cuda_toolkit_version=args.cuda_toolkit_version,
                link_options=("max_trace_depth=1", "debug=none"),
            )
            task = build_task(current_task)
            materialized = task.route_factory().compile().materialize(
                target=target,
                toolchain=toolchain,
            )
            authority = root / "authority.json"
            built = build_family_rtdlexe(
                materialized,
                artifact_directory=root / "artifacts",
                authority_path=authority,
                build_roots=roots,
                deployment_id=current_request.deployment_id,
            )
            package = root / "package.json"
            head = root / "head.json"
            freeze(
                private_path=Path(str(current_signing["private"])),
                root_path=Path(str(current_signing["public"])),
                authority_path=authority,
                output_path=package,
                head_output_path=head,
                previous_path=None,
            )
            return {
                "artifact": built.artifact_path,
                "authority": authority,
                "trust_root": Path(str(current_signing["public"])),
                "trust_head": head,
                "trust_package": package,
            }

        def verify(paths, *, current_request=request):
            return _verifier(paths, request=current_request)

        first_started = time.perf_counter_ns()
        entry = resolve_exact_aot(
            request,
            cache_root=args.aot_cache_root,
            producer=producer,
            verifier=verify,
        )
        first_ns = time.perf_counter_ns() - first_started
        if args.require_cold_first and entry.cache_hit:
            raise RuntimeError("Goal5848 required cold cache entry already existed")
        hit_durations = []
        before_hits = producer_calls
        for _ in range(args.hit_repetitions):
            started = time.perf_counter_ns()
            hit = resolve_exact_aot(
                request,
                cache_root=args.aot_cache_root,
                producer=producer,
                verifier=verify,
            )
            hit_durations.append(time.perf_counter_ns() - started)
            if not hit.cache_hit or hit.producer_invoked:
                raise RuntimeError("Goal5848 exact repeat was not a cache hit")
        if producer_calls != before_hits:
            raise RuntimeError("Goal5848 cache hit invoked compiler producer")
        median_hit_ns = int(statistics.median(hit_durations))
        output_paths = entry.output_paths
        verification = entry.verification
        if not isinstance(verification, dict):
            raise TypeError("Goal5848 AOT verification capability differs")
        rows[label] = {
            "task": task_id,
            "deployment_id": request.deployment_id,
            "artifact": str(output_paths["artifact"]),
            "artifact_sha256": entry.output_sha256["artifact"],
            "authority": str(output_paths["authority"]),
            "authority_sha256": entry.output_sha256["authority"],
            "public": str(output_paths["trust_root"]),
            "public_sha256": entry.output_sha256["trust_root"],
            "package": str(output_paths["trust_package"]),
            "package_sha256": entry.output_sha256["trust_package"],
            "head": str(output_paths["trust_head"]),
            "head_sha256": entry.output_sha256["trust_head"],
            "executable_identity_sha256": verification[
                "executable_identity_sha256"
            ],
            "family_executable_identity_sha256": verification[
                "family_executable_identity_sha256"
            ],
            "aot_request_identity_sha256": request.identity_sha256,
            "aot_request": request.to_mapping(),
            "cache_entry": str(entry.entry_path),
            "first_resolution_cache_hit": entry.cache_hit,
            "first_resolution_ns": first_ns,
            "producer_invocation_count": producer_calls,
            "exact_hit_repetitions": args.hit_repetitions,
            "exact_hit_durations_ns": hit_durations,
            "exact_hit_median_ns": median_hit_ns,
            "exact_hit_over_first_resolution_ppm": ratio_ppm(
                median_hit_ns, first_ns
            ),
            "all_hit_producer_invocation_deltas_zero": True,
            "test_only_signing_private_path_unlinked_after_freeze": False,
        }
    _unlink_signing_private_files(signing)
    atexit.unregister(_unlink_signing_private_files)
    for task_id in TASKS:
        label = str(TASK_REQUESTS[task_id]["label"])
        rows[label][
            "test_only_signing_private_path_unlinked_after_freeze"
        ] = True
    result = {
        "schema": "rtdl.goal5848.aot_candidates.v1",
        "status": "PASS__EXACT_AOT_CACHE_AND_CANDIDATES_VERIFIED",
        "source_commit": source_commit,
        "source_tree": source_tree,
        "native": str(native),
        "native_bytes": native.stat().st_size,
        "native_sha256": native_sha256,
        "native_build_manifest": str(native_manifest_path),
        "native_build_manifest_sha256": native_manifest_sha256,
        "native_build_id": native_manifest["build_id"],
        "optix_sdk": args.optix_sdk,
        "compute_capability": list(capability),
        "build_roots": build_roots_mapping,
        "signing_trust_root_sha256": {
            str(TASK_REQUESTS[task]["label"]): signing[task]["public_sha256"]
            for task in TASKS
        },
        "signing_roots_receipt": str(
            args.signing_roots_receipt.resolve(strict=True)
        ),
        "signing_roots_receipt_sha256": signing_roots_receipt_sha256,
        "aot_cache_root": str(
            args.aot_cache_root.expanduser().absolute().resolve(strict=True)
        ),
        "rows": rows,
        "total_resolution_ns": time.perf_counter_ns() - total_started,
        "claim_boundary": {
            "test_only_signing": True,
            "gpu_execution_performed": False,
            "cache_timings_are_engineering_until_formal_freeze": True,
            "public_or_manuscript_claim_authorized": False,
        },
    }
    result["manifest_sha256"] = digest(result)
    _write_create(output_root / "manifest.json", result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
