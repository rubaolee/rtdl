#!/usr/bin/env python3
"""Materialize portable OptiX headers without rewriting build history.

The reviewed PyOptiX wheel receipt records the historical absolute header
checkout used for the build.  A new target must not pretend that the build
occurred at a different path.  This helper therefore preserves and validates
that receipt byte-for-byte, materializes its exact pinned header commit from an
offline Git bundle, and emits a separate target-specific successor receipt.
It performs no build, import, GPU operation, worker, clock read, or timing.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from typing import Any, Mapping, NoReturn
import zipfile


SCHEMA = "rtdl.goal5802.pyoptix_wheel_build_materialization_receipt.v1"
STATUS = "PASS__HISTORICAL_BUILD_PRESERVED__EXACT_HEADERS_MATERIALIZED"
ORIGINAL_SCHEMA = "rtdl.goal5800.pyoptix_clean_wheel_build_receipt.v1"
ORIGINAL_RECEIPT_SHA256 = (
    "ef7ec47448a4ef012094ee9f127a8844c030aaba8936cc09b78ba5e6efa7d2de")
ORIGINAL_RECEIPT_BYTES = 15901
ORIGINAL_SOURCE_PROJECTION_FILE_COUNT = 72
ORIGINAL_SOURCE_PROJECTION_SHA256 = (
    "fbe686453fbd22b00f680857c3d3ee4407699e25b5a06123c58f69f0f7a60c89")
ORIGINAL_HEADERS_ROOT = (
    "/home/lestat/work/goal5798_candidate_v8_prepare_run/upstream/optix-dev")
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"
HEADERS_COMMIT = "fff65c2a7c592f1ea5f1661ad7d2381cf965f9bd"
HEADERS_TREE = "c30f1b41cb64f6cba6290d7ad82686cc84922267"
PYOPTIX_WHEEL_SHA256 = (
    "a659ed6df6125daa9cd37481c957e592c234f1cf423edb6b55d91a0f00683c4b")
PYOPTIX_WHEEL_BYTES = 620161
EXTENSION_MEMBER = "optix/_optix.cpython-312-x86_64-linux-gnu.so"
EXTENSION_SHA256 = (
    "2e546d0daa497511c878dfd97c93266689ba4a3de1f563d4732137ac23ba0a36")
EXTENSION_BYTES = 2630616
HEX40 = re.compile(r"[0-9a-f]{40}\Z")
HEX64 = re.compile(r"[0-9a-f]{64}\Z")


class PyOptixProvenanceError(RuntimeError):
    """Fail-closed portable provenance error."""


def _fail(message: str) -> NoReturn:
    raise PyOptixProvenanceError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _sha_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def _no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            _fail(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> NoReturn:
    _fail(f"non-finite JSON value is forbidden: {value}")


def _regular(path: Path, label: str, *, executable: bool = False) -> Path:
    supplied = path.expanduser().absolute()
    try:
        resolved = supplied.resolve(strict=True)
        metadata = resolved.stat()
    except OSError as error:
        raise PyOptixProvenanceError(f"{label} is unreadable: {supplied}") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file: {resolved}")
    if executable and not os.access(resolved, os.X_OK):
        _fail(f"{label} is not executable: {resolved}")
    return resolved


def _file_record(path: Path, label: str, *, executable: bool = False) \
        -> dict[str, object]:
    supplied = path.expanduser().absolute()
    resolved = _regular(supplied, label, executable=executable)
    row: dict[str, object] = {
        "invocation_path": str(supplied),
        "resolved_path": str(resolved),
        "path_kind": "SYMLINK_TO_REGULAR_FILE" if supplied.is_symlink()
        else "REGULAR_FILE",
        "bytes": resolved.stat().st_size,
        "sha256": _sha_file(resolved),
    }
    if supplied.is_symlink():
        row["symlink_target"] = str(supplied.readlink())
    return row


def _strict_json(path: Path, label: str, *, canonical: bool) \
        -> tuple[dict[str, Any], bytes]:
    resolved = _regular(path, label)
    payload = resolved.read_bytes()
    try:
        value = json.loads(
            payload.decode("utf-8"), object_pairs_hook=_no_duplicates,
            parse_constant=_reject_constant,
        )
    except (UnicodeError, json.JSONDecodeError) as error:
        raise PyOptixProvenanceError(f"{label} is not strict UTF-8 JSON") from error
    if not isinstance(value, dict):
        _fail(f"{label} is not an object")
    if canonical and payload != _canonical(value) + b"\n":
        _fail(f"{label} is not canonical JSON plus terminal LF")
    return value, payload


def _write_new(path: Path, payload: bytes, *, mode: int = 0o644) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, mode)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _run_git(git: Path, receipt_root: Path, ordinal: int,
             arguments: list[str]) -> bytes:
    command = [str(git), *arguments]
    completed = subprocess.run(
        command, check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        env={
            **os.environ,
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_TERMINAL_PROMPT": "0",
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        },
    )
    root = receipt_root / f"{ordinal:02d}"
    _write_new(root / "argv.json", _canonical(command) + b"\n")
    _write_new(root / "stdout", completed.stdout)
    _write_new(root / "stderr", completed.stderr)
    _write_new(root / "exit_code", f"{completed.returncode}\n".encode("ascii"))
    if completed.returncode != 0:
        _fail(f"offline Git command {ordinal} failed")
    return completed.stdout


def _validate_original_receipt(
        value: Mapping[str, Any], wheel: Path, *, receipt_payload: bytes) \
        -> dict[str, object]:
    if len(receipt_payload) != ORIGINAL_RECEIPT_BYTES \
            or _sha(receipt_payload) != ORIGINAL_RECEIPT_SHA256:
        _fail("historical PyOptiX build receipt differs from frozen exact bytes")
    if set(value) != {
            "schema", "status", "transaction_kind", "pyoptix_source",
            "optix_headers", "build", "wheel",
            "registered_performance_timing_count"} \
            or value.get("schema") != ORIGINAL_SCHEMA \
            or value.get("status") \
            != "PASS__CLEAN_SOURCE_TO_WHEEL_BUILD__UNTIMED" \
            or value.get("transaction_kind") \
            != "build_provenance_not_performance" \
            or type(value.get("registered_performance_timing_count")) is not int \
            or value["registered_performance_timing_count"] != 0:
        _fail("historical PyOptiX build receipt envelope differs")
    source = value["pyoptix_source"]
    headers = value["optix_headers"]
    build = value["build"]
    wheel_row = value["wheel"]
    if not all(isinstance(item, Mapping)
               for item in (source, headers, build, wheel_row)):
        _fail("historical PyOptiX build receipt projection is absent")
    if source.get("commit") != PYOPTIX_COMMIT \
            or source.get("tree") != PYOPTIX_TREE \
            or headers.get("commit") != HEADERS_COMMIT \
            or headers.get("tree") != HEADERS_TREE \
            or type(headers.get("api_macro")) is not int \
            or headers["api_macro"] != 90000 \
            or headers.get("root") != ORIGINAL_HEADERS_ROOT \
            or type(build.get("exit_code")) is not int \
            or build["exit_code"] != 0:
        _fail("historical source/header/build identity differs")
    rows = source.get("archive_projection_files")
    if not isinstance(rows, list) \
            or source.get("archive_projection_file_count") != len(rows) \
            or len(rows) != ORIGINAL_SOURCE_PROJECTION_FILE_COUNT \
            or _digest(rows) != ORIGINAL_SOURCE_PROJECTION_SHA256:
        _fail("historical PyOptiX source projection is incomplete")
    paths: set[str] = set()
    for row in rows:
        if not isinstance(row, Mapping) or set(row) != {"path", "bytes", "sha256"} \
                or not isinstance(row["path"], str) \
                or not isinstance(row["bytes"], int) or row["bytes"] < 0 \
                or not isinstance(row["sha256"], str) \
                or HEX64.fullmatch(row["sha256"]) is None \
                or row["path"] in paths:
            _fail("historical PyOptiX source projection row differs")
        pure = PurePosixPath(row["path"])
        if pure.is_absolute() or ".." in pure.parts \
                or pure.as_posix() != row["path"]:
            _fail("historical PyOptiX source path is unsafe")
        paths.add(row["path"])
    wheel_bytes = wheel.read_bytes()
    if len(wheel_bytes) != PYOPTIX_WHEEL_BYTES \
            or _sha(wheel_bytes) != PYOPTIX_WHEEL_SHA256 \
            or wheel_row.get("bytes") != PYOPTIX_WHEEL_BYTES \
            or wheel_row.get("sha256") != PYOPTIX_WHEEL_SHA256 \
            or wheel_row.get("extension_member") != EXTENSION_MEMBER \
            or wheel_row.get("extension_bytes") != EXTENSION_BYTES \
            or wheel_row.get("extension_sha256") != EXTENSION_SHA256:
        _fail("historical PyOptiX wheel identity differs")
    try:
        with zipfile.ZipFile(wheel) as archive:
            extension = archive.read(EXTENSION_MEMBER)
    except (OSError, KeyError, zipfile.BadZipFile) as error:
        raise PyOptixProvenanceError("PyOptiX wheel extension is unreadable") from error
    if len(extension) != EXTENSION_BYTES or _sha(extension) != EXTENSION_SHA256:
        _fail("PyOptiX extension identity differs")
    return {
        "historical_optix_headers_root": str(headers["root"]),
        "source_projection_sha256": _digest(rows),
        "source_projection_file_count": len(rows),
        "frozen_historical_receipt_sha256": ORIGINAL_RECEIPT_SHA256,
        "frozen_historical_receipt_bytes": ORIGINAL_RECEIPT_BYTES,
    }


def _parse_inventory(payload: bytes) -> list[dict[str, object]]:
    rows = []
    seen: set[str] = set()
    for raw in payload.split(b"\0"):
        if not raw:
            continue
        header, separator, path_raw = raw.partition(b"\t")
        fields = header.split(b" ")
        if not separator or len(fields) != 3:
            _fail("OptiX header Git inventory row is malformed")
        try:
            mode = fields[0].decode("ascii")
            kind = fields[1].decode("ascii")
            blob = fields[2].decode("ascii")
            path = path_raw.decode("utf-8")
        except UnicodeError as error:
            raise PyOptixProvenanceError(
                "OptiX header Git inventory encoding differs") from error
        pure = PurePosixPath(path)
        if mode not in {"100644", "100755"} or kind != "blob" \
                or HEX40.fullmatch(blob) is None or pure.is_absolute() \
                or ".." in pure.parts or pure.as_posix() != path \
                or path in seen:
            _fail("OptiX header Git inventory entry is unsafe")
        seen.add(path)
        rows.append({"path": path, "mode": mode, "blob_sha1": blob})
    if not rows:
        _fail("OptiX header Git inventory is empty")
    return rows


def _verify_checkout(git: Path, checkout: Path,
                     receipt_root: Path | None = None,
                     ordinal_start: int = 20) -> dict[str, object]:
    def run(offset: int, args: list[str]) -> bytes:
        if receipt_root is None:
            completed = subprocess.run(
                [str(git), *args], check=False, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={**os.environ, "GIT_CONFIG_NOSYSTEM": "1",
                     "GIT_TERMINAL_PROMPT": "0"})
            if completed.returncode != 0:
                _fail("OptiX header checkout verification command failed")
            return completed.stdout
        return _run_git(git, receipt_root, ordinal_start + offset, args)

    commit = run(0, ["-C", str(checkout), "rev-parse", "HEAD"]) \
        .decode("ascii").strip()
    tree = run(1, ["-C", str(checkout), "rev-parse", "HEAD^{tree}"]) \
        .decode("ascii").strip()
    if commit != HEADERS_COMMIT or tree != HEADERS_TREE:
        _fail("materialized OptiX header commit/tree differs")
    autocrlf = run(2, ["-C", str(checkout), "config", "--get", "core.autocrlf"]) \
        .decode("ascii").strip().lower()
    if autocrlf != "false":
        _fail("materialized OptiX header checkout does not freeze autocrlf=false")
    if run(3, ["-C", str(checkout), "status", "--porcelain=v1",
               "--untracked-files=all"]):
        _fail("materialized OptiX header checkout is dirty")
    inventory_raw = run(
        4, ["-C", str(checkout), "ls-tree", "-rz", "--full-tree", commit])
    rows = _parse_inventory(inventory_raw)
    observed_paths = set()
    payload_bytes = 0
    expanded = []
    for row in rows:
        path = checkout / str(row["path"])
        if path.is_symlink() or not path.is_file():
            _fail(f"materialized OptiX header file is absent: {row['path']}")
        payload = path.read_bytes()
        blob = run(
            10 + len(expanded),
            ["-C", str(checkout), "cat-file", "blob", str(row["blob_sha1"])])
        if payload != blob:
            _fail(f"materialized OptiX header blob differs: {row['path']}")
        executable = bool(path.stat().st_mode & stat.S_IXUSR)
        if os.name == "posix" and executable != (row["mode"] == "100755"):
            _fail(f"materialized OptiX header execute mode differs: {row['path']}")
        observed_paths.add(str(row["path"]))
        payload_bytes += len(payload)
        expanded.append({
            **row, "bytes": len(payload), "sha256": _sha(payload),
        })
    worktree_paths = {
        path.relative_to(checkout).as_posix()
        for path in checkout.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(checkout).parts
    }
    if observed_paths != worktree_paths:
        _fail("materialized OptiX header worktree coverage differs")
    return {
        "path": str(checkout.resolve()),
        "commit": commit,
        "tree": tree,
        "core_autocrlf": autocrlf,
        "file_count": len(expanded),
        "payload_bytes": payload_bytes,
        "inventory_sha256": _digest(expanded),
    }


def _validate_receipt(value: Mapping[str, Any]) -> dict[str, Any]:
    expected = {
        "schema", "status", "original_build_receipt", "headers_bundle",
        "git_tool", "frozen_historical_receipt_authority",
        "historical_build_projection", "materialized_headers",
        "pyoptix_wheel", "claim_boundaries", "formal_worker_count",
        "registered_performance_timing_count", "gpu_kernel_launch_count",
        "clock_read_count", "receipt_sha256",
    }
    if set(value) != expected or value.get("schema") != SCHEMA \
            or value.get("status") != STATUS:
        _fail("PyOptiX provenance materialization receipt envelope differs")
    body = dict(value)
    seal = body.pop("receipt_sha256")
    if seal != _digest(body):
        _fail("PyOptiX provenance materialization receipt seal differs")
    for key in (
            "formal_worker_count", "registered_performance_timing_count",
            "gpu_kernel_launch_count", "clock_read_count"):
        if type(value.get(key)) is not int or value[key] != 0:
            _fail("PyOptiX provenance materialization zero lock differs")
    if value.get("claim_boundaries") != {
        "historical_build_path_rewritten": False,
        "historical_build_reexecuted": False,
        "target_header_materialization_is_not_a_rebuild": True,
        "network_access_required_on_target": False,
        "performance_claim_authorized": False,
        "execution_authority_consumed": False,
    }:
        _fail("PyOptiX provenance materialization claim boundary differs")
    if value.get("frozen_historical_receipt_authority") != {
        "bytes": ORIGINAL_RECEIPT_BYTES,
        "sha256": ORIGINAL_RECEIPT_SHA256,
        "source_projection_file_count": ORIGINAL_SOURCE_PROJECTION_FILE_COUNT,
        "source_projection_sha256": ORIGINAL_SOURCE_PROJECTION_SHA256,
        "historical_headers_root": ORIGINAL_HEADERS_ROOT,
    }:
        _fail("frozen historical PyOptiX receipt authority differs")
    return dict(value)


def validate_materialization_receipt(path: Path) -> dict[str, Any]:
    value, _ = _strict_json(
        path, "PyOptiX provenance materialization receipt", canonical=True)
    value = _validate_receipt(value)
    for label, key in (
            ("historical build receipt", "original_build_receipt"),
            ("OptiX headers bundle", "headers_bundle"),
            ("Git tool", "git_tool"),
            ("PyOptiX wheel", "pyoptix_wheel")):
        row = value[key]
        if not isinstance(row, Mapping):
            _fail(f"{label} record is absent")
        current = _file_record(
            Path(str(row["invocation_path"])), label,
            executable=(key == "git_tool"))
        if current != row:
            _fail(f"{label} changed after materialization")
    original, original_payload = _strict_json(
        Path(str(value["original_build_receipt"]["invocation_path"])),
        "historical build receipt", canonical=False)
    projection = _validate_original_receipt(
        original, Path(str(value["pyoptix_wheel"]["invocation_path"])),
        receipt_payload=original_payload)
    if projection != value["historical_build_projection"]:
        _fail("historical build projection changed")
    checkout = Path(str(value["materialized_headers"]["path"]))
    git = Path(str(value["git_tool"]["invocation_path"]))
    observed = _verify_checkout(git, checkout)
    if observed != value["materialized_headers"]:
        _fail("materialized OptiX header checkout changed")
    return value


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    output = args.output_directory.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    git = _regular(args.git, "Git tool", executable=True)
    bundle = _regular(args.headers_bundle, "OptiX headers bundle")
    wheel = _regular(args.pyoptix_wheel, "PyOptiX wheel")
    original, original_payload = _strict_json(
        args.original_build_receipt, "historical PyOptiX build receipt",
        canonical=False)
    projection = _validate_original_receipt(
        original, wheel, receipt_payload=original_payload)
    output.mkdir(parents=True)
    receipts = output / "git_receipts"
    checkout = output / "optix_headers"
    try:
        _run_git(git, receipts, 1, ["bundle", "verify", str(bundle)])
        _run_git(git, receipts, 2, [
            "clone", "--no-checkout", "--no-hardlinks", str(bundle),
            str(checkout),
        ])
        _run_git(git, receipts, 3, [
            "-C", str(checkout), "config", "core.autocrlf", "false"])
        _run_git(git, receipts, 4, [
            "-C", str(checkout), "config", "core.eol", "lf"])
        _run_git(git, receipts, 5, [
            "-C", str(checkout), "checkout", "--detach", HEADERS_COMMIT])
        materialized = _verify_checkout(
            git, checkout, receipt_root=receipts, ordinal_start=20)
        value: dict[str, Any] = {
            "schema": SCHEMA,
            "status": STATUS,
            "original_build_receipt": _file_record(
                args.original_build_receipt, "historical build receipt"),
            "headers_bundle": _file_record(bundle, "OptiX headers bundle"),
            "git_tool": _file_record(args.git, "Git tool", executable=True),
            "frozen_historical_receipt_authority": {
                "bytes": ORIGINAL_RECEIPT_BYTES,
                "sha256": ORIGINAL_RECEIPT_SHA256,
                "source_projection_file_count": (
                    ORIGINAL_SOURCE_PROJECTION_FILE_COUNT),
                "source_projection_sha256": ORIGINAL_SOURCE_PROJECTION_SHA256,
                "historical_headers_root": ORIGINAL_HEADERS_ROOT,
            },
            "historical_build_projection": projection,
            "materialized_headers": materialized,
            "pyoptix_wheel": _file_record(wheel, "PyOptiX wheel"),
            "claim_boundaries": {
                "historical_build_path_rewritten": False,
                "historical_build_reexecuted": False,
                "target_header_materialization_is_not_a_rebuild": True,
                "network_access_required_on_target": False,
                "performance_claim_authorized": False,
                "execution_authority_consumed": False,
            },
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
        }
        value["receipt_sha256"] = _digest(value)
        _write_new(output / "receipt.json", _canonical(value) + b"\n")
        validate_materialization_receipt(output / "receipt.json")
        return value
    except BaseException as error:
        failure = {
            "schema": "rtdl.goal5802.pyoptix_provenance_terminal_failure.v1",
            "status": "TERMINAL_FAILURE__PRESERVE__NO_RETRY_OR_ROOT_REUSE",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "execution_authority_consumed": False,
        }
        failure["failure_sha256"] = _digest(failure)
        try:
            _write_new(
                output / "terminal_failure.json", _canonical(failure) + b"\n")
        except (OSError, FileExistsError):
            pass
        raise


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("materialize")
    build.add_argument("--git", type=Path, required=True)
    build.add_argument("--headers-bundle", type=Path, required=True)
    build.add_argument("--original-build-receipt", type=Path, required=True)
    build.add_argument("--pyoptix-wheel", type=Path, required=True)
    build.add_argument("--output-directory", type=Path, required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--receipt", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "materialize":
        value = materialize(args)
    else:
        value = validate_materialization_receipt(args.receipt)
    print(json.dumps({
        "status": value["status"],
        "receipt_sha256": value["receipt_sha256"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
        "execution_authority_consumed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
