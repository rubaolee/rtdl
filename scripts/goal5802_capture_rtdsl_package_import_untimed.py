#!/usr/bin/env python3
"""Import the complete Goal5802 RTDL compiler path from one sealed package.

This child is intentionally standalone.  It imports no experiment helper and
performs no timing or GPU work.  The controller executes it with the clean
Python in isolated/safe-path mode before formal worker zero.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
from pathlib import Path
import sys


MODULES = (
    "rtdsl",
    "rtdsl.v4",
    "rtdsl.v4_callback_lifecycle",
    "rtdsl.v4_bounded_relation_optix_compiler",
    "rtdsl.v4_triangle_standard_library",
    "rtdsl.v4_triangle_reduction_optix_compiler",
    "rtdsl.v4_rtdlexe",
)


def _sha(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            value.update(block)
    return value.hexdigest()


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")


def _package_identity(root: Path) -> tuple[int, str]:
    rows: list[dict[str, object]] = []
    for path in sorted(root.rglob("*")):
        if path.is_symlink():
            raise RuntimeError(f"sealed package contains symlink: {path}")
        if path.is_file():
            relative = path.relative_to(root).as_posix()
            if relative.startswith("__pycache__/") \
                    or "/__pycache__/" in relative \
                    or relative.endswith((".pyc", ".pyo")):
                raise RuntimeError("sealed package gained a bytecode cache")
            rows.append({
                "path": f"rtdsl/{relative}",
                "bytes": path.stat().st_size,
                "sha256": _sha(path),
            })
        elif not path.is_dir():
            raise RuntimeError(f"sealed package contains special path: {path}")
    return len(rows), hashlib.sha256(_canonical(rows)).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--package-file-count", type=int, required=True)
    parser.add_argument("--package-tree-sha256", required=True)
    args = parser.parse_args()
    root = args.package_root.resolve(strict=True)
    if root.name != "rtdsl" or not root.is_dir() or root.is_symlink() \
            or args.package_file_count <= 0 \
            or len(args.package_tree_sha256) != 64 \
            or any(ch not in "0123456789abcdef"
                   for ch in args.package_tree_sha256):
        raise RuntimeError("sealed package arguments differ")

    for name in MODULES:
        importlib.import_module(name)
    observed_count, observed_tree = _package_identity(root)
    if observed_count != args.package_file_count \
            or observed_tree != args.package_tree_sha256:
        raise RuntimeError("sealed package changed during isolated imports")
    rows: list[dict[str, object]] = []
    for name in MODULES:
        module = sys.modules[name]
        raw_path = getattr(module, "__file__", None)
        if not isinstance(raw_path, str) or not raw_path:
            raise RuntimeError(f"imported module has no file: {name}")
        path = Path(raw_path).resolve(strict=True)
        if path.is_symlink() or not path.is_file() \
                or not path.is_relative_to(root):
            raise RuntimeError(f"imported module escapes sealed package: {name}")
        rows.append({
            "module": name,
            "path": str(path),
            "relative_path": "rtdsl/" + path.relative_to(root).as_posix(),
            "bytes": path.stat().st_size,
            "sha256": _sha(path),
        })
    value: dict[str, object] = {
        "schema": "rtdl.goal5802.rtdsl_package_import_preflight.v1",
        "status": "PASS__CLEAN_PYTHON_IMPORTED_SEALED_RTDSL_PACKAGE",
        "python_executable": str(Path(sys.executable).resolve(strict=True)),
        "package_root": str(root),
        "rtdsl_package_file_count": args.package_file_count,
        "rtdsl_package_tree_sha256": args.package_tree_sha256,
        "required_module_names": list(MODULES),
        "imported_modules": rows,
        "clock_read_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "formal_worker_count": 0,
    }
    value["receipt_sha256"] = hashlib.sha256(_canonical(value)).hexdigest()
    print(json.dumps(value, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
