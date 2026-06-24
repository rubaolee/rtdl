#!/usr/bin/env python3
"""Check whether this RTDL checkout has the current V3 source-tree surface."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tomllib
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
EXPECTED_VERSION = "v3.0.0"
EXPECTED_PROJECT_VERSION = "3.0.0"


def _status_line(status: str, name: str, detail: str) -> str:
    label = "INFO" if status == "warn" else status.upper()
    return f"[{label:4}] {name}: {detail}"


def _check(name: str, status: str, detail: str, *, required: bool = True) -> dict[str, Any]:
    return {"name": name, "status": status, "detail": detail, "required": required}


def _module_available(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def _library_candidates(stem: str) -> list[Path]:
    return [
        ROOT / "build" / f"lib{stem}.so",
        ROOT / "build" / f"lib{stem}.dylib",
        ROOT / "build" / f"{stem}.dll",
        ROOT / "build" / f"lib{stem}.dll",
    ]


def _existing_paths(candidates: list[Path]) -> list[Path]:
    return [path for path in candidates if path.exists()]


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
        return _check("hello-world smoke", "fail", f"could not run: {exc}")

    if completed.returncode == 0:
        return _check("hello-world smoke", "pass", "examples/current/getting_started/rtdl_hello_world.py ran")
    detail = (completed.stderr or completed.stdout).strip().splitlines()
    message = detail[-1] if detail else f"exit code {completed.returncode}"
    return _check("hello-world smoke", "fail", message)


def _v3_current_matrix_check() -> dict[str, Any]:
    try:
        from scripts import run_test_matrix

        modules = run_test_matrix.group_modules("v3_current_surface")
    except Exception as exc:  # pragma: no cover - defensive import check
        return _check("current V3 test matrix", "fail", f"could not load v3_current_surface group: {exc}")

    if not modules:
        return _check("current V3 test matrix", "fail", "v3_current_surface group has no modules")
    return _check(
        "current V3 test matrix",
        "pass",
        f"scripts/run_test_matrix.py --group v3_current_surface ({len(modules)} modules)",
    )


def gather_checks(*, run_smoke: bool = False) -> dict[str, Any]:
    if str(SRC) not in sys.path:
        sys.path.insert(0, str(SRC))
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    checks: list[dict[str, Any]] = []

    version_file = ROOT / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else ""
    checks.append(
        _check(
            "current V3 marker",
            "pass" if version == EXPECTED_VERSION else "fail",
            "VERSION" if version == EXPECTED_VERSION else (version or "VERSION is missing"),
        )
    )

    pyproject = ROOT / "pyproject.toml"
    if pyproject.exists():
        project_version = tomllib.loads(pyproject.read_text(encoding="utf-8")).get("project", {}).get("version", "")
        checks.append(
            _check(
                "pyproject V3 package version",
                "pass" if project_version == EXPECTED_PROJECT_VERSION else "fail",
                "project.version" if project_version == EXPECTED_PROJECT_VERSION else (project_version or "project.version missing"),
            )
        )
    else:
        checks.append(_check("pyproject V3 package version", "fail", "pyproject.toml missing"))

    required_paths = {
        "front page": ROOT / "README.md",
        "docs index": ROOT / "docs" / "README.md",
        "current V3 status": ROOT / "docs" / "current_v3_status.md",
        "public documentation map": ROOT / "docs" / "public_documentation_map.md",
        "tutorials path": ROOT / "tutorials" / "README.md",
        "V3 tutorial path": ROOT / "tutorials" / "current" / "README.md",
        "examples path": ROOT / "examples" / "README.md",
        "performance wording guide": ROOT / "docs" / "learn" / "performance_wording.md",
        "source-tree doctor docs": ROOT / "docs" / "learn" / "source_tree_doctor.md",
        "V3 hello world": ROOT / "examples" / "current" / "getting_started" / "rtdl_hello_world.py",
    }
    for name, path in required_paths.items():
        checks.append(_check(name, "pass" if path.exists() else "fail", path.relative_to(ROOT).as_posix()))

    checks.append(_v3_current_matrix_check())

    checks.append(
        _check(
            "module rtdsl",
            "pass" if _module_available("rtdsl") else "fail",
            "rtdsl" if _module_available("rtdsl") else "module not importable",
        )
    )
    checks.append(
        _check(
            "module numpy",
            "pass" if _module_available("numpy") else "fail",
            "numpy" if _module_available("numpy") else "module not importable",
        )
    )
    for module_name in ("imageio", "imageio_ffmpeg", "cupy", "numba"):
        checks.append(
            _check(
                f"optional module {module_name}",
                "pass" if _module_available(module_name) else "warn",
                module_name,
                required=False,
            )
        )

    optix = _existing_paths(_library_candidates("rtdl_optix"))
    checks.append(
        _check(
            "optional OptiX library",
            "pass" if optix else "warn",
            optix[0].relative_to(ROOT).as_posix() if optix else "build/librtdl_optix.so/dylib/dll not found",
            required=False,
        )
    )
    embree = _existing_paths(_library_candidates("rtdl_embree"))
    checks.append(
        _check(
            "optional Embree library",
            "pass" if embree else "warn",
            embree[0].relative_to(ROOT).as_posix() if embree else "build/librtdl_embree.so/dylib/dll not found",
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
        "status": "current_v3_ready" if not required_failures else "current_v3_blocked",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check the current RTDL V3 source-tree state.")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="treat optional warnings as failures")
    parser.add_argument("--run-smoke", action="store_true", help="run the portable hello-world example")
    parser.add_argument("--show-optional", action="store_true", help="show optional native/partner dependency checks")
    args = parser.parse_args(argv)

    payload = gather_checks(run_smoke=args.run_smoke)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print("RTDL V3 Source Tree Doctor")
        print(f"repo: {payload['repo']}")
        print("surface: current V3")
        for item in payload["checks"]:
            if not item["required"] and not args.show_optional:
                continue
            print(_status_line(item["status"], item["name"], item["detail"]))
        if payload["required_failures"]:
            print("Required checks failed. Fix those before running the current V3 gate.")
        elif payload["warnings"]:
            print("Core V3 checks passed. Optional native/partner extras can be installed when needed.")
        else:
            print("All checked V3 source-tree paths and optional dependencies are available.")

    if payload["required_failures"] or (args.strict and payload["warnings"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
