#!/usr/bin/env python3
"""Collect and verify the exact offline Goal5802 Python wheelhouse.

This helper never downloads, installs, imports, or executes a supplied wheel.
It accepts eight explicit local wheel files, validates their METADATA, WHEEL,
and RECORD payloads through the Goal5802 combined-runtime validator, copies
them create-only under portable canonical names, and seals a path-independent
manifest.  The same wheel bytes therefore produce the same manifest on
Windows and Linux.
"""

from __future__ import annotations

import argparse
from email.parser import BytesParser
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
from typing import Any, Iterable, Mapping, NoReturn
import zipfile

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import goal5802_build_combined_runtime_untimed as combined


MANIFEST_SCHEMA = "rtdl.goal5802.offline_python_wheelhouse_manifest.v1"
FAILURE_SCHEMA = "rtdl.goal5802.offline_python_wheelhouse_failure.v1"
PROFILE = "GOAL5802_PYOPTIX_AND_RTDL_SHARED_RUNTIME_V1"

# This is the complete non-seed runtime set required by the matched PyOptiX
# and RTDL arms.  virtualenv/pip are an explicitly separate bootstrap input.
REQUIRED_DISTRIBUTIONS: tuple[tuple[str, str], ...] = (
    ("pyoptix", "9.1.0"),
    ("numpy", "2.4.4"),
    ("cupy-cuda12x", "14.0.1"),
    ("cuda-python", "12.9.7"),
    ("cuda-bindings", "12.9.7"),
    ("cuda-pathfinder", "1.6.1"),
    ("numba", "0.65.1"),
    ("llvmlite", "0.47.0"),
)
REQUIRED_VERSION_MAP = dict(REQUIRED_DISTRIBUTIONS)
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
WHEEL_TAG_RE = re.compile(
    r"[A-Za-z0-9_.]+-[A-Za-z0-9_.]+-[A-Za-z0-9_.]+\Z")


class OfflineWheelhouseError(RuntimeError):
    """Fail-closed offline-wheelhouse error."""


def _fail(message: str) -> NoReturn:
    raise OfflineWheelhouseError(message)


def _canonical(value: object) -> bytes:
    return json.dumps(
        value, allow_nan=False, separators=(",", ":"), sort_keys=True,
    ).encode("utf-8")


def _digest(value: object) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _sha_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _write_create_only(path: Path, payload: bytes) -> None:
    if path.exists() or path.is_symlink():
        raise FileExistsError(path)
    path.parent.mkdir(parents=True, exist_ok=True)
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


def _strict_json(path: Path, label: str) -> Any:
    if path.is_symlink():
        _fail(f"{label} may not be a symlink")
    try:
        metadata = path.stat()
        payload = path.read_bytes()
    except OSError as error:
        raise OfflineWheelhouseError(f"{label} is unreadable") from error
    if not stat.S_ISREG(metadata.st_mode):
        _fail(f"{label} is not a regular file")
    try:
        value = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as error:
        raise OfflineWheelhouseError(f"{label} is not UTF-8 JSON") from error
    if payload != _canonical(value) + b"\n":
        _fail(f"{label} is not exact canonical JSON plus LF")
    return value


def _parse_wheel_spec(value: str) -> tuple[str, Path]:
    supplied_name, separator, supplied_path = value.partition("=")
    if not separator or not supplied_name or not supplied_path:
        _fail("--wheel must be DISTRIBUTION=PATH")
    try:
        name = combined._normalize_distribution(supplied_name)
    except combined.CombinedRuntimeError as error:
        raise OfflineWheelhouseError(str(error)) from error
    return name, Path(supplied_path)


def _wheel_tag(path: Path) -> str:
    try:
        with zipfile.ZipFile(path) as archive:
            wheel_names = [
                info.filename for info in archive.infolist()
                if not info.is_dir()
                and info.filename.endswith(".dist-info/WHEEL")
            ]
            if len(wheel_names) != 1:
                _fail(f"wheel has no unique WHEEL metadata: {path.name}")
            metadata = BytesParser().parsebytes(archive.read(wheel_names[0]))
    except (OSError, zipfile.BadZipFile) as error:
        raise OfflineWheelhouseError(f"wheel WHEEL metadata is unreadable: {path}") from error
    tags = metadata.get_all("Tag") or []
    if not tags or any(not WHEEL_TAG_RE.fullmatch(tag) for tag in tags):
        _fail(f"wheel has an invalid or absent compatibility tag: {path.name}")
    # A wheel containing multiple valid tags may safely be named with any one
    # of those declared tags.  Choosing the lexical minimum is deterministic.
    return sorted(set(tags))[0]


def _canonical_wheel_filename(
        distribution: str, version: str, wheel_tag: str) -> str:
    distribution_token = re.sub(r"[-_.]+", "_", distribution)
    version_token = re.sub(r"[^A-Za-z0-9_.]+", "_", version)
    if not distribution_token or not version_token:
        _fail("wheel filename projection is empty")
    return f"{distribution_token}-{version_token}-{wheel_tag}.whl"


def _wheel_projection(path: Path, ordinal: int) -> dict[str, object]:
    try:
        generic = combined._wheel_record(f"package_{ordinal:03d}", path, ordinal)
    except (combined.CombinedRuntimeError, OSError) as error:
        raise OfflineWheelhouseError(str(error)) from error
    wheel_tag = _wheel_tag(Path(str(generic["resolved_path"])))
    distribution = str(generic["distribution"])
    version = str(generic["version"])
    return {
        "ordinal": ordinal,
        "distribution": distribution,
        "metadata_name": str(generic["metadata_name"]),
        "version": version,
        "saved_path": (
            "wheels/" + _canonical_wheel_filename(
                distribution, version, wheel_tag)),
        "bytes": int(generic["bytes"]),
        "sha256": str(generic["sha256"]),
        "member_count": int(generic["member_count"]),
        "member_tree_sha256": str(generic["member_tree_sha256"]),
        "wheel_tag": wheel_tag,
    }


def _manifest_body(wheels: list[dict[str, object]]) -> dict[str, object]:
    return {
        "schema": MANIFEST_SCHEMA,
        "status": "PASS__EXACT_PINNED_WHEELS_COLLECTED__NO_DOWNLOAD",
        "profile": PROFILE,
        "required_distributions": REQUIRED_VERSION_MAP,
        "wheel_count": len(wheels),
        "payload_bytes": sum(int(row["bytes"]) for row in wheels),
        "wheel_set_sha256": _digest(wheels),
        "wheels": wheels,
        "collection_policy": {
            "explicit_local_wheel_inputs_only": True,
            "implicit_download_allowed": False,
            "network_access_attempt_count": 0,
            "subprocess_invocation_count": 0,
            "package_install_count": 0,
            "wheel_import_or_execution_count": 0,
        },
        "execution_scope": {
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "clock_read_count": 0,
            "execution_authority_consumed": False,
        },
    }


def _validate_manifest_envelope(value: Any) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {
            "schema", "status", "profile", "required_distributions",
            "wheel_count", "payload_bytes", "wheel_set_sha256", "wheels",
            "collection_policy", "execution_scope", "manifest_sha256"}:
        _fail("offline wheelhouse manifest envelope differs")
    body = dict(value)
    seal = body.pop("manifest_sha256")
    if not isinstance(seal, str) or not SHA256_RE.fullmatch(seal) \
            or seal != _digest(body):
        _fail("offline wheelhouse manifest seal differs")
    if value["schema"] != MANIFEST_SCHEMA \
            or value["status"] != "PASS__EXACT_PINNED_WHEELS_COLLECTED__NO_DOWNLOAD" \
            or value["profile"] != PROFILE \
            or value["required_distributions"] != REQUIRED_VERSION_MAP:
        _fail("offline wheelhouse manifest profile differs")
    wheels = value["wheels"]
    if not isinstance(wheels, list) or len(wheels) != len(REQUIRED_DISTRIBUTIONS):
        _fail("offline wheelhouse wheel count differs")
    if isinstance(value["wheel_count"], bool) \
            or value["wheel_count"] != len(wheels):
        _fail("offline wheelhouse wheel_count differs")
    if value["wheel_set_sha256"] != _digest(wheels):
        _fail("offline wheelhouse wheel set seal differs")
    if isinstance(value["payload_bytes"], bool) \
            or value["payload_bytes"] != sum(int(row.get("bytes", -1)) for row in wheels):
        _fail("offline wheelhouse payload byte count differs")
    expected_policy = _manifest_body([])["collection_policy"]
    expected_scope = _manifest_body([])["execution_scope"]
    if value["collection_policy"] != expected_policy \
            or value["execution_scope"] != expected_scope:
        _fail("offline wheelhouse no-network/no-execution boundary differs")
    return value


def _copy_exact(source: Path, destination: Path, expected: Mapping[str, object]) -> None:
    try:
        # The same opened source identity supplies both the digest check and
        # the destination bytes.  A check/reopen pair would be fail-closed
        # after the destination recount, but would still permit an avoidable
        # concurrent-replacement denial that terminalizes a create-only root.
        payload = combined._read_regular_file_once(source)
    except (combined.CombinedRuntimeError, OSError) as error:
        raise OfflineWheelhouseError(str(error)) from error
    if len(payload) != expected["bytes"] \
            or hashlib.sha256(payload).hexdigest() != expected["sha256"]:
        _fail(f"wheel changed before collection: {source.expanduser().absolute()}")
    _write_create_only(destination, payload)


def collect(output: Path, wheel_specs: Iterable[str]) -> dict[str, object]:
    output = output.expanduser().absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError(output)
    parsed = [_parse_wheel_spec(value) for value in wheel_specs]
    if len(parsed) != len(REQUIRED_DISTRIBUTIONS):
        _fail("exactly eight explicit pinned runtime wheels are required")
    supplied_names = [name for name, _ in parsed]
    if len(supplied_names) != len(set(supplied_names)):
        _fail("duplicate supplied distribution name")
    if set(supplied_names) != set(REQUIRED_VERSION_MAP):
        missing = sorted(set(REQUIRED_VERSION_MAP) - set(supplied_names))
        extra = sorted(set(supplied_names) - set(REQUIRED_VERSION_MAP))
        _fail(f"runtime wheel set differs; missing={missing}; extra={extra}")
    supplied = dict(parsed)
    rows: list[dict[str, object]] = []
    sources: list[Path] = []
    for ordinal, (name, expected_version) in enumerate(
            REQUIRED_DISTRIBUTIONS, 1):
        source = supplied[name]
        row = _wheel_projection(source, ordinal)
        if row["distribution"] != name:
            _fail(f"supplied label/METADATA distribution mismatch: {name}")
        if row["version"] != expected_version:
            _fail(
                f"pinned version mismatch for {name}: "
                f"{row['version']} != {expected_version}")
        rows.append(row)
        sources.append(source)
    saved_paths = [str(row["saved_path"]) for row in rows]
    if len(saved_paths) != len(set(saved_paths)):
        _fail("canonical wheel paths collide")
    body = _manifest_body(rows)
    manifest = {**body, "manifest_sha256": _digest(body)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.mkdir()
    try:
        for source, row in zip(sources, rows, strict=True):
            _copy_exact(source, output / str(row["saved_path"]), row)
        _write_create_only(
            output / "wheelhouse_manifest.json", _canonical(manifest) + b"\n")
    except BaseException as error:
        failure = {
            "schema": FAILURE_SCHEMA,
            "status": "TERMINAL_CREATE_ONLY_WHEELHOUSE_COLLECTION_FAILURE__NO_REUSE",
            "error_type": type(error).__name__,
            "error_message": str(error),
            "formal_worker_count": 0,
            "registered_performance_timing_count": 0,
            "gpu_kernel_launch_count": 0,
            "retry_or_replacement_authorized": False,
        }
        failure["failure_receipt_sha256"] = _digest(failure)
        try:
            _write_create_only(
                output / "terminal_failure_receipt.json",
                _canonical(failure) + b"\n")
        except (OSError, FileExistsError):
            pass
        raise
    return manifest


def verify(output: Path) -> dict[str, object]:
    output = output.expanduser().resolve(strict=True)
    if output.is_symlink() or not output.is_dir():
        _fail("offline wheelhouse root is not a real directory")
    if (output / "terminal_failure_receipt.json").exists():
        _fail("offline wheelhouse is terminal-failed")
    value = _validate_manifest_envelope(
        _strict_json(output / "wheelhouse_manifest.json", "wheelhouse manifest"))
    expected_paths = {"wheelhouse_manifest.json"}
    for ordinal, ((name, version), row) in enumerate(
            zip(REQUIRED_DISTRIBUTIONS, value["wheels"], strict=True), 1):
        if not isinstance(row, dict) or set(row) != {
                "ordinal", "distribution", "metadata_name", "version",
                "saved_path", "bytes", "sha256", "member_count",
                "member_tree_sha256", "wheel_tag"}:
            _fail("offline wheelhouse row envelope differs")
        if isinstance(row["ordinal"], bool) or row["ordinal"] != ordinal \
                or row["distribution"] != name or row["version"] != version:
            _fail("offline wheelhouse row order/name/version differs")
        relative = PurePosixPath(str(row["saved_path"]))
        if relative.is_absolute() or ".." in relative.parts \
                or len(relative.parts) != 2 or relative.parts[0] != "wheels":
            _fail("offline wheelhouse saved path is unsafe")
        path = output / Path(*relative.parts)
        rebuilt = _wheel_projection(path, ordinal)
        if rebuilt != row:
            _fail(f"offline wheel identity differs: {relative}")
        expected_paths.add(relative.as_posix())
    observed_paths: set[str] = set()
    for path in sorted(output.rglob("*")):
        if path.is_symlink():
            _fail(f"offline wheelhouse contains a symlink: {path}")
        if path.is_file():
            observed_paths.add(path.relative_to(output).as_posix())
    if observed_paths != expected_paths:
        _fail("offline wheelhouse member set differs")
    return value


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect/verify the exact offline Goal5802 Python wheelhouse")
    commands = parser.add_subparsers(dest="command", required=True)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("--output-directory", type=Path, required=True)
    collect_parser.add_argument(
        "--wheel", action="append", required=True,
        help="explicit DISTRIBUTION=PATH; repeat exactly once for each pinned package")
    verify_parser = commands.add_parser("verify")
    verify_parser.add_argument("--output-directory", type=Path, required=True)
    return parser


def main() -> int:
    args = _parser().parse_args()
    if args.command == "collect":
        result = collect(args.output_directory, args.wheel)
    else:
        result = verify(args.output_directory)
    print(json.dumps({
        "status": result["status"],
        "manifest_sha256": result["manifest_sha256"],
        "wheel_count": result["wheel_count"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
