#!/usr/bin/env python3
"""Check whether this RTDL checkout is ready for source-tree use."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
EXPECTED_VERSION = "v3.0.2"


def _status_line(status: str, name: str, detail: str) -> str:
    return f"[{status.upper():4}] {name}: {detail}"


def _check(name: str, status: str, detail: str, *, required: bool = True) -> dict[str, Any]:
    return {"name": name, "status": status, "detail": detail, "required": required}


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _path_candidates_exist(candidates: list[Path]) -> list[Path]:
    return [path for path in candidates if path.exists()]


def _library_candidates(stem: str) -> list[Path]:
    return [
        ROOT / "build" / f"lib{stem}.so",
        ROOT / "build" / f"lib{stem}.dylib",
        ROOT / "build" / f"{stem}.dll",
        ROOT / "build" / f"lib{stem}.dll",
    ]


def _run_smoke() -> dict[str, Any]:
    env = os.environ.copy()
    sep = ";" if os.name == "nt" else ":"
    env["PYTHONPATH"] = f"{SRC}{sep}{ROOT}{sep}{env.get('PYTHONPATH', '')}".rstrip(sep)
    command = [sys.executable, str(ROOT / "examples" / "current" / "getting_started" / "rtdl_hello_world.py")]
    try:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=20,
            check=False,
        )
    except Exception as exc:  # pragma: no cover - defensive wrapper
        return _check("hello-world smoke", "fail", f"could not run: {exc}", required=True)

    if completed.returncode == 0:
        return _check("hello-world smoke", "pass", "examples/current/getting_started/rtdl_hello_world.py ran")
    detail = (completed.stderr or completed.stdout).strip().splitlines()
    message = detail[-1] if detail else f"exit code {completed.returncode}"
    return _check("hello-world smoke", "fail", message, required=True)


def _v3_current_test_matrix_check() -> dict[str, Any]:
    try:
        from scripts import run_test_matrix

        modules = run_test_matrix.group_modules("v3_current")
    except Exception as exc:  # pragma: no cover - defensive import check
        return _check("V3 current test matrix", "fail", f"could not load v3_current group: {exc}")

    if not modules:
        return _check("V3 current test matrix", "fail", "v3_current group has no modules")
    return _check(
        "V3 current test matrix",
        "pass",
        f"scripts/run_test_matrix.py --group v3_current ({len(modules)} modules)",
    )


def _v3_c_abi_surface_check() -> dict[str, Any]:
    prep = ROOT / "docs" / "history" / "v4_preparatory_embedding"
    staging = prep / "staging"
    examples = prep / "examples" / "embedding"
    required_files = (
        staging / "include" / "rtdl" / "rtdl.h",
        ROOT / "src" / "native" / "rtdl_c_api.cpp",
        examples / "c_api_aabb2_overlap_client.c",
        examples / "c_api_direct_link_client.c",
        examples / "c_api_host_runtime_client.c",
        examples / "c_api_cuda_buffer_metadata_client.c",
        examples / "python_ctypes_client.py",
        examples / "python_ctypes_aabb2_query_client.py",
        examples / "python_ctypes_cuda_buffer_metadata_client.py",
        examples / "python_ctypes_dlpack_like_metadata_client.py",
        examples / "README.md",
        staging / "packaging" / "rtdl-c-api.pc",
        staging / "packaging" / "rtdl-c-api-config.cmake",
    )
    missing = [path.relative_to(ROOT).as_posix() for path in required_files if not path.exists()]
    makefile = ROOT / "Makefile"
    makefile_text = makefile.read_text(encoding="utf-8") if makefile.exists() else ""
    if "build-c-api:" not in makefile_text:
        missing.append("Makefile build-c-api target")
    if "stage-c-api:" not in makefile_text:
        missing.append("Makefile stage-c-api target")
    if "package-c-api-stage:" not in makefile_text:
        missing.append("Makefile package-c-api-stage target")
    if "stage-c-api-prefix:" not in makefile_text:
        missing.append("Makefile stage-c-api-prefix target")
    if missing:
        return _check(
            "V4 preparatory C ABI surface",
            "warn",
            "missing optional V4 preparatory files: " + ", ".join(missing),
            required=False,
        )
    return _check(
        "V4 preparatory C ABI surface",
        "pass",
        "optional V4 preparatory files fenced under docs/history/v4_preparatory_embedding/staging: archived draft header, make build-c-api/stage-c-api/stage-c-api-prefix/package-c-api-stage, pkg-config and CMake metadata, C examples including host runtime and CUDA metadata, Python ctypes examples including CUDA and DLPack-like metadata",
        required=False,
    )


def _v3_c_abi_docs_check() -> dict[str, Any]:
    prep = ROOT / "docs" / "history" / "v4_preparatory_embedding"
    required_files = (
        prep / "v3_0_c_abi_draft.md",
        prep / "v3_0_c_abi_stability_policy.md",
        prep / "v3_0_c_abi_ownership_threading_contract.md",
        prep / "v3_0_c_abi_staging_contract.md",
        prep / "v3_0_c_abi_symbol_manifest_v0_1_3.json",
        prep / "v3_0_zero_copy_interop_contract.md",
        prep / "v3_0_toolchain_support_matrix.md",
        prep / "v3_0_binding_and_device_interop_matrix.md",
    )
    missing = [path.relative_to(ROOT).as_posix() for path in required_files if not path.exists()]
    history_readme = prep / "README.md"
    history_text = history_readme.read_text(encoding="utf-8") if history_readme.exists() else ""
    required_links = (
        "V4 Preparatory Embedding Archive",
        "V3.0 excludes embedding/SDK/zero-copy work",
        "do not make V3.0 an SDK or embeddability release",
    )
    missing_links = [link for link in required_links if link not in history_text]
    if missing or missing_links:
        detail_parts = []
        if missing:
            detail_parts.append("missing files: " + ", ".join(missing))
        if missing_links:
            detail_parts.append("missing history archive wording: " + ", ".join(missing_links))
        return _check(
            "V4 preparatory C ABI docs",
            "warn",
            "; ".join(detail_parts),
            required=False,
        )
    return _check(
        "V4 preparatory C ABI docs",
        "pass",
        "optional V4 preparatory docs: draft, stability, ownership/threading, symbol manifest, zero-copy, toolchain support, binding/device interop docs",
        required=False,
    )


def gather_checks(*, run_smoke: bool = False, include_v4_prep: bool = False) -> dict[str, Any]:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    checks: list[dict[str, Any]] = []

    version_file = ROOT / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else ""
    checks.append(
        _check(
            "version marker",
            "pass" if version == EXPECTED_VERSION else "fail",
            version or "VERSION is missing",
        )
    )

    required_paths = {
        "src/rtdsl": ROOT / "src" / "rtdsl" / "__init__.py",
        "front page": ROOT / "README.md",
        "top-level tutorials": ROOT / "tutorials" / "current" / "README.md",
        "current examples": ROOT / "examples" / "current" / "README.md",
        "v3.0.2 release package": ROOT / "docs" / "release_reports" / "v3_0_2" / "README.md",
        "V3 app-author strategy": ROOT / "docs" / "learn" / "v3_0_app_author_implementation_strategy.md",
    }
    for name, path in required_paths.items():
        checks.append(_check(name, "pass" if path.exists() else "fail", path.relative_to(ROOT).as_posix()))

    checks.append(_v3_current_test_matrix_check())
    if include_v4_prep:
        checks.append(_v3_c_abi_surface_check())
        checks.append(_v3_c_abi_docs_check())

    editable_metadata = ROOT / "pyproject.toml"
    checks.append(
        _check(
            "optional editable source-tree metadata",
            "pass" if editable_metadata.exists() else "warn",
            editable_metadata.relative_to(ROOT).as_posix(),
            required=False,
        )
    )

    checks.append(
        _check(
            "python version",
            "pass" if sys.version_info >= (3, 10) else "warn",
            platform.python_version(),
            required=False,
        )
    )

    core_modules = {"rtdsl": "rtdsl", "numpy": "numpy"}
    for name, module in core_modules.items():
        checks.append(_check(f"module {name}", "pass" if _module_available(module) else "fail", module))

    optional_modules = {
        "imageio": "imageio",
        "imageio-ffmpeg": "imageio_ffmpeg",
        "cupy": "cupy",
        "numba": "numba",
    }
    for name, module in optional_modules.items():
        checks.append(
            _check(
                f"optional module {name}",
                "pass" if _module_available(module) else "warn",
                module,
                required=False,
            )
        )

    optix_env = os.environ.get("RTDL_OPTIX_LIBRARY") or os.environ.get("RTDL_OPTIX_LIB")
    optix_candidates = _path_candidates_exist(_library_candidates("rtdl_optix"))
    if optix_env:
        optix_status = "pass" if Path(optix_env).exists() else "warn"
        optix_detail = optix_env
    elif optix_candidates:
        optix_status = "pass"
        optix_detail = optix_candidates[0].relative_to(ROOT).as_posix()
    else:
        optix_status = "warn"
        optix_detail = "set RTDL_OPTIX_LIBRARY or build/librtdl_optix.so for OptiX examples"
    checks.append(_check("optional OptiX library", optix_status, optix_detail, required=False))

    embree_candidates = _path_candidates_exist(_library_candidates("rtdl_embree"))
    checks.append(
        _check(
            "optional Embree library",
            "pass" if embree_candidates else "warn",
            embree_candidates[0].relative_to(ROOT).as_posix()
            if embree_candidates
            else "build/librtdl_embree.so/dylib/dll not found",
            required=False,
        )
    )

    if run_smoke:
        checks.append(_run_smoke())

    required_failures = [item for item in checks if item["required"] and item["status"] == "fail"]
    warnings = [item for item in checks if item["status"] == "warn"]
    return {
        "tool": "rtdl_source_tree_doctor",
        "repo": str(ROOT),
        "version": version,
        "checks": checks,
        "required_failures": required_failures,
        "warnings": warnings,
        "ok": not required_failures,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the RTDL source-tree environment.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="treat optional warnings as failures")
    parser.add_argument("--run-smoke", action="store_true", help="run the portable hello-world example")
    parser.add_argument(
        "--include-v4-prep",
        action="store_true",
        help="also check archived V4 preparatory embedding/C ABI surfaces",
    )
    args = parser.parse_args(argv)

    payload = gather_checks(run_smoke=args.run_smoke, include_v4_prep=args.include_v4_prep)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("RTDL Source Tree Doctor")
        print(f"repo: {payload['repo']}")
        print(f"version: {payload['version'] or 'unknown'}")
        for item in payload["checks"]:
            print(_status_line(item["status"], item["name"], item["detail"]))
        if payload["required_failures"]:
            print("Required checks failed. Fix those before running current examples.")
        elif payload["warnings"]:
            print("Core source-tree checks passed. Optional warnings only affect native/partner paths.")
        else:
            print("All checked source-tree and optional paths are available.")

    if payload["required_failures"] or (args.strict and payload["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
