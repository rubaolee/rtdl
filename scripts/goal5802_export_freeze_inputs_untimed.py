#!/usr/bin/env python3
"""Create and verify the five exact Goal5802 freeze inputs.

This helper is deliberately limited to deterministic, local materialization.
It does not import a GPU runtime, read a clock, run a worker, or authorize a
measurement.  The output directory is create-only and carries a self-sealed
receipt over every emitted byte.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
from typing import Any, Mapping, NoReturn

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from experiments.goal5802_premeasurement.contract import (
    _instrument_context,
    _source_record,
    build_cold_schedule,
    build_schedule,
    operation_contract,
)
from experiments.goal5802_premeasurement.workload import workload_authority


SCHEMA = "rtdl.goal5802.freeze_input_export_receipt.v1"
ARTIFACTS = (
    ("workload_authority", "workload_authority.json"),
    ("operation_contract", "operation_contract.json"),
    ("comparative_schedule", "comparative_schedule_432.json"),
    ("build_cold_schedule", "build_cold_schedule_72.json"),
    ("instrument_source_manifest", "instrument_source_manifest.json"),
)


class FreezeInputExportError(RuntimeError):
    """Fail-closed export or verification error."""


def _fail(message: str) -> NoReturn:
    raise FreezeInputExportError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _strict_json(path: Path, label: str) -> Any:
    if path.is_symlink():
        _fail(f"{label} may not be a symlink")
    try:
        metadata = path.stat()
        payload = path.read_bytes()
    except OSError as error:
        raise FreezeInputExportError(f"{label} is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise FreezeInputExportError(f"{label} is not UTF-8 JSON") from error
    if payload != _canonical(value) + b"\n":
        _fail(f"{label} is not exact canonical JSON plus LF")
    return value


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _git_identity(root: Path) -> dict[str, str]:
    def one(argument: str) -> str:
        try:
            completed = subprocess.run(
                ["git", "-C", str(root), "rev-parse", argument],
                check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            value = completed.stdout.decode("ascii").strip()
        except (OSError, subprocess.CalledProcessError, UnicodeError) as error:
            raise FreezeInputExportError(
                "repository Git identity is unavailable") from error
        if len(value) != 40 \
                or any(character not in "0123456789abcdef" for character in value):
            _fail("repository Git identity is malformed")
        return value

    return {"commit": one("HEAD^{commit}"), "tree": one("HEAD^{tree}")}


def build_values(root: Path) -> dict[str, object]:
    """Rebuild all five values from the controlling implementation."""

    root = root.expanduser().resolve(strict=True)
    repaired_contract, source_paths = _instrument_context()
    if not isinstance(repaired_contract, str) or not source_paths \
            or len(source_paths) != len(set(source_paths)):
        _fail("instrument context is empty or has duplicate paths")
    values: dict[str, object] = {
        "workload_authority": workload_authority(),
        "operation_contract": operation_contract(),
        "comparative_schedule": build_schedule(),
        "build_cold_schedule": build_cold_schedule(),
        "instrument_source_manifest": [
            _source_record(root, relative) for relative in source_paths
        ],
    }
    if len(values["comparative_schedule"]) != 432:
        _fail("comparative schedule is not exactly 432 rows")
    if len(values["build_cold_schedule"]) != 72:
        _fail("build-cold schedule is not exactly 72 rows")
    manifest = values["instrument_source_manifest"]
    if not isinstance(manifest, list) or not manifest \
            or len({str(row["path"]) for row in manifest}) != len(manifest):
        _fail("instrument source manifest is empty or has duplicate paths")
    return values


def _artifact_rows(values: Mapping[str, object]) -> list[dict[str, object]]:
    rows = []
    for role, name in ARTIFACTS:
        payload = _canonical(values[role]) + b"\n"
        rows.append({
            "role": role,
            "path": name,
            "bytes": len(payload),
            "sha256": _sha(payload),
            "canonical_value_sha256": _digest(values[role]),
        })
    return rows


def build_receipt(root: Path, values: Mapping[str, object]) -> dict[str, object]:
    manifest = values["instrument_source_manifest"]
    assert isinstance(manifest, list)
    body: dict[str, object] = {
        "schema": SCHEMA,
        "status": "PASS__FIVE_EXACT_FREEZE_INPUTS_EXPORTED__UNTIMED",
        "repository_identity": _git_identity(root),
        "source_identity_boundary": {
            "manifest_binds_actual_worktree_bytes": True,
            "working_tree_clean_claimed": False,
            "separate_exact_source_packet_verification_required": True,
        },
        "artifacts": _artifact_rows(values),
        "row_counts": {
            "comparative_schedule": len(values["comparative_schedule"]),
            "build_cold_schedule": len(values["build_cold_schedule"]),
            "instrument_source_manifest": len(manifest),
        },
        "authority_digests": {
            role: _digest(values[role]) for role, _ in ARTIFACTS
        },
        "execution_scope": {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
            "execution_authority_consumed": False,
            "pod_execution_authorized": False,
            "performance_claim_authorized": False,
        },
        "create_only": True,
    }
    return {**body, "receipt_sha256": _digest(body)}


def export(root: Path, output: Path) -> dict[str, object]:
    root = root.expanduser().resolve(strict=True)
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    values = build_values(root)
    receipt = build_receipt(root, values)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    for role, name in ARTIFACTS:
        _write_create_only(output / name, _canonical(values[role]) + b"\n")
    _write_create_only(
        output / "export_receipt.json", _canonical(receipt) + b"\n")
    verify(root, output)
    return receipt


def verify(root: Path, output: Path) -> dict[str, object]:
    root = root.expanduser().resolve(strict=True)
    output = output.expanduser().resolve(strict=True)
    if output.is_symlink() or not output.is_dir():
        _fail("freeze-input output is not a real directory")
    expected_names = {name for _, name in ARTIFACTS} | {"export_receipt.json"}
    observed_names = {item.name for item in output.iterdir()}
    if observed_names != expected_names:
        _fail("freeze-input output member set differs")
    values = build_values(root)
    for role, name in ARTIFACTS:
        observed = _strict_json(output / name, role)
        if observed != values[role]:
            _fail(f"exported {role} differs from authoritative rebuild")
    receipt = _strict_json(output / "export_receipt.json", "export receipt")
    if not isinstance(receipt, dict) or receipt.get("schema") != SCHEMA:
        _fail("export receipt envelope differs")
    body = dict(receipt)
    seal = body.pop("receipt_sha256", None)
    if seal != _digest(body):
        _fail("export receipt seal differs")
    if receipt != build_receipt(root, values):
        _fail("export receipt differs from exact rebuild")
    return receipt


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or verify the five untimed Goal5802 freeze inputs")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("export", "verify"):
        command = commands.add_parser(name)
        command.add_argument("--root", type=Path, required=True)
        command.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "export":
        receipt = export(args.root, args.output_directory)
    else:
        receipt = verify(args.root, args.output_directory)
    print(json.dumps({
        "status": receipt["status"],
        "receipt_sha256": receipt["receipt_sha256"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
