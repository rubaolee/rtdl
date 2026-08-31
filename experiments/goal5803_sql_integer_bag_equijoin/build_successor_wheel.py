#!/usr/bin/env python3
"""Build and verify the packaging-only repaired-v14 RTDL wheel.

The input must be the exact repaired source root.  The script performs no
network access and changes no source byte.  It requires the repaired public
runtime core, builds one pure-Python wheel, then proves that every packaged
``rtdsl`` member is byte-identical to its source counterpart.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile


EXPECTED_REPAIRED_CORE_SHA256 = (
    "36fdecbc86e60807a49326377e0d74415f7777867cbaa638f52b82342a4bf526")
EXPECTED_RTDSL_INIT_SHA256 = (
    "1598fbfb01846687d7c0a247e022798f32ed71090816f7d1ca6639f7a536cb04")
WHEEL_PROJECT_NAME = "rtdl-source-tree"
WHEEL_VERSION = "4.0.0rc1"


def sha_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(payload: object) -> bytes:
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def _fail(message: str) -> None:
    raise RuntimeError(message)


def source_rtdsl_projection(source_root: Path) -> tuple[dict[str, object], ...]:
    """Return exactly the package members selected by ``pyproject.toml``."""

    package_root = source_root.resolve() / "src" / "rtdsl"
    if not package_root.is_dir():
        _fail(f"missing source package root: {package_root}")
    rows: list[dict[str, object]] = []
    for path in sorted(package_root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        relative = path.relative_to(package_root).as_posix()
        if path.suffix == ".py" or (
                relative.startswith("schemas/") and path.suffix == ".json"):
            rows.append({
                "path": f"rtdsl/{relative}",
                "bytes": path.stat().st_size,
                "sha256": sha_file(path),
            })
    if not rows:
        _fail("source rtdsl projection is empty")
    by_path = {row["path"]: row for row in rows}
    core = by_path.get("rtdsl/v4_rtdlexe.py")
    init = by_path.get("rtdsl/__init__.py")
    if core is None or core["sha256"] != EXPECTED_REPAIRED_CORE_SHA256:
        _fail(f"source is not the repaired-v14 core: {core!r}")
    if init is None or init["sha256"] != EXPECTED_RTDSL_INIT_SHA256:
        _fail(f"source has an unexpected public package initializer: {init!r}")
    return tuple(rows)


def source_build_input_projection(
    source_root: Path,
) -> tuple[dict[str, object], ...]:
    """Bind every copied build input and reject ambiguous filesystem types."""

    root = source_root.resolve()
    required_top_level = ("pyproject.toml",)
    optional_top_level = ("README.md", "VERSION")
    rows: list[dict[str, object]] = []
    for name in (*required_top_level, *optional_top_level):
        path = root / name
        if not path.exists():
            if name in optional_top_level:
                continue
            _fail(f"missing required wheel build input: {path}")
        if not path.is_file() or path.is_symlink():
            _fail(f"wheel build input must be a regular file: {path}")
        rows.append({
            "path": name,
            "bytes": path.stat().st_size,
            "sha256": sha_file(path),
        })
    rows.extend({
        "path": f"src/{row['path']}",
        "bytes": row["bytes"],
        "sha256": row["sha256"],
    } for row in source_rtdsl_projection(root))
    return tuple(rows)


def _tool_identity(module_name: str, distribution_name: str) -> dict[str, object]:
    module = importlib.import_module(module_name)
    raw_path = getattr(module, "__file__", None)
    if not isinstance(raw_path, str):
        _fail(f"build tool has no module path: {module_name}")
    path = Path(raw_path).resolve()
    return {
        "module": module_name,
        "distribution": distribution_name,
        "version": importlib.metadata.version(distribution_name),
        "module_path": str(path),
        "module_sha256": sha_file(path),
    }


def _copy_build_inputs(
    source_root: Path, staging_root: Path,
    rows: tuple[dict[str, object], ...],
) -> None:
    for row in rows:
        relative = Path(str(row["path"]))
        source = source_root / relative
        target = staging_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() or target.is_symlink():
            raise FileExistsError(target)
        with source.open("rb") as input_stream, target.open("xb") as output_stream:
            shutil.copyfileobj(input_stream, output_stream)
        if target.stat().st_size != row["bytes"] or sha_file(target) != row["sha256"]:
            _fail(f"disposable build copy drift: {relative.as_posix()}")


def wheel_rtdsl_projection(wheel_path: Path) -> tuple[dict[str, object], ...]:
    wheel = wheel_path.resolve()
    if not wheel.is_file() or wheel.is_symlink():
        _fail(f"wheel must be a regular file: {wheel}")
    rows: list[dict[str, object]] = []
    with zipfile.ZipFile(wheel, "r") as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            _fail("wheel contains duplicate member names")
        for info in sorted(archive.infolist(), key=lambda row: row.filename):
            name = info.filename
            if info.is_dir() or not name.startswith("rtdsl/"):
                continue
            if name.endswith(".pyc") or "/__pycache__/" in name:
                _fail(f"wheel contains generated Python cache data: {name}")
            payload = archive.read(info)
            rows.append({
                "path": name,
                "bytes": len(payload),
                "sha256": sha_bytes(payload),
            })
    if not rows:
        _fail("wheel rtdsl projection is empty")
    return tuple(rows)


def verify_wheel_against_source(
    source_root: Path, wheel_path: Path,
) -> dict[str, object]:
    source_rows = source_rtdsl_projection(source_root)
    wheel_rows = wheel_rtdsl_projection(wheel_path)
    if source_rows != wheel_rows:
        source_by_path = {row["path"]: row for row in source_rows}
        wheel_by_path = {row["path"]: row for row in wheel_rows}
        _fail(json.dumps({
            "wheel_source_projection_mismatch": True,
            "missing_from_wheel": sorted(set(source_by_path) - set(wheel_by_path)),
            "extra_in_wheel": sorted(set(wheel_by_path) - set(source_by_path)),
            "different": sorted(
                path for path in set(source_by_path) & set(wheel_by_path)
                if source_by_path[path] != wheel_by_path[path]),
        }, sort_keys=True))
    projection_sha = sha_bytes(canonical_bytes(list(source_rows)))
    return {
        "schema": "rtdl.goal5803.repaired_v14_wheel_projection.v1",
        "status": "PASS__WHOLE_RTDSL_WHEEL_PROJECTION_EXACT",
        "wheel": {
            "path": str(wheel_path.resolve()),
            "bytes": wheel_path.stat().st_size,
            "sha256": sha_file(wheel_path),
        },
        "source_root": str(source_root.resolve()),
        "rtdsl_member_count": len(source_rows),
        "rtdsl_projection_sha256": projection_sha,
        "rtdsl_members": list(source_rows),
        "repaired_core_sha256": EXPECTED_REPAIRED_CORE_SHA256,
        "public_init_sha256": EXPECTED_RTDSL_INIT_SHA256,
        "source_and_wheel_member_sets_identical": True,
        "source_and_wheel_member_bytes_identical": True,
        "wheel_execution_mode": True,
        "network_call_count": 0,
    }


def build_successor_wheel(
    *, source_root: Path, output_wheel: Path, output_receipt: Path,
) -> dict[str, object]:
    source_root = source_root.resolve()
    output_wheel = output_wheel.resolve()
    output_receipt = output_receipt.resolve()
    for path in (output_wheel, output_receipt):
        if path.exists() or path.is_symlink():
            raise FileExistsError(path)
    source_before = source_build_input_projection(source_root)
    source_projection_sha = sha_bytes(canonical_bytes(list(source_before)))
    python_path = Path(sys.executable).resolve()
    tools = {
        "python": {
            "version": sys.version,
            "executable": str(python_path),
            "executable_sha256": sha_file(python_path),
        },
        "pip": _tool_identity("pip", "pip"),
        "setuptools": _tool_identity("setuptools", "setuptools"),
        "wheel": _tool_identity("wheel", "wheel"),
    }
    output_wheel.parent.mkdir(parents=True, exist_ok=True)
    output_receipt.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="goal5803_sql_wheel_") as raw:
        temporary = Path(raw)
        staging = temporary / "source"
        staging.mkdir()
        _copy_build_inputs(source_root, staging, source_before)
        built_directory = temporary / "built"
        built_directory.mkdir()
        environment = dict(os.environ)
        environment.update({
            "PIP_NO_INDEX": "1",
            "PIP_DISABLE_PIP_VERSION_CHECK": "1",
            "PIP_NO_CACHE_DIR": "1",
            "SOURCE_DATE_EPOCH": "315532800",
        })
        command = [
            sys.executable, "-m", "pip", "wheel",
            "--no-deps", "--no-build-isolation", "--disable-pip-version-check",
            "--wheel-dir", str(built_directory), str(staging),
        ]
        completed = subprocess.run(
            command, check=False, capture_output=True, env=environment)
        if completed.returncode != 0:
            _fail(
                "offline wheel build failed: "
                + completed.stderr.decode("utf-8", errors="replace"))
        wheels = tuple(built_directory.glob("*.whl"))
        if len(wheels) != 1:
            _fail(f"offline build emitted {len(wheels)} wheels")
        built = wheels[0]
        source_after = source_build_input_projection(source_root)
        if source_after != source_before:
            _fail("original repaired-v14 source changed during wheel build")
        receipt = verify_wheel_against_source(source_root, built)
        with output_wheel.open("xb") as stream:
            with built.open("rb") as source:
                shutil.copyfileobj(source, stream)
    if sha_file(output_wheel) != receipt["wheel"]["sha256"]:
        _fail("copied wheel differs from the verified temporary build")
    receipt["wheel"] = {
        "path": str(output_wheel),
        "bytes": output_wheel.stat().st_size,
        "sha256": sha_file(output_wheel),
    }
    receipt.update({
        "build": {
            "command": [
                "python", "-m", "pip", "wheel", "--no-deps",
                "--no-build-isolation", "--disable-pip-version-check",
                "--wheel-dir", "<fresh-temporary-directory>",
                "<exact-repaired-v14-source-root>",
            ],
            "pip_no_index": True,
            "pip_no_cache": True,
            "source_date_epoch": 315532800,
            "source_mutation_performed": False,
            "core_or_native_change_performed": False,
            "packaging_only": True,
            "exit_code": completed.returncode,
            "stdout_bytes": len(completed.stdout),
            "stdout_sha256": sha_bytes(completed.stdout),
            "stderr_bytes": len(completed.stderr),
            "stderr_sha256": sha_bytes(completed.stderr),
            "tool_identities": tools,
            "original_source_projection_before_sha256": source_projection_sha,
            "original_source_projection_after_sha256": sha_bytes(
                canonical_bytes(list(source_after))),
            "original_source_unchanged": source_after == source_before,
            "disposable_copy_used": True,
            "original_source_used_as_build_working_directory": False,
        },
        "receipt_create_only": True,
    })
    with output_receipt.open("xb") as stream:
        stream.write(
            json.dumps(receipt, indent=2, sort_keys=True).encode("utf-8")
            + b"\n")
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--output-wheel", type=Path, required=True)
    parser.add_argument("--output-receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = build_successor_wheel(
        source_root=args.source_root,
        output_wheel=args.output_wheel,
        output_receipt=args.output_receipt,
    )
    print(json.dumps(receipt, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = [
    "EXPECTED_REPAIRED_CORE_SHA256",
    "EXPECTED_RTDSL_INIT_SHA256",
    "build_successor_wheel",
    "canonical_bytes",
    "sha_bytes",
    "sha_file",
    "source_build_input_projection",
    "source_rtdsl_projection",
    "verify_wheel_against_source",
    "wheel_rtdsl_projection",
]
