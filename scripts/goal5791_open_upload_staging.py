#!/usr/bin/env python3
"""Open the exact Goal5791 upload-staging root after Stage-A approval.

This helper is executed only after the already-authorized first-entry stdin
bootstrap has verified its own source, the complete helper bytes, and Python.
It observes that both frozen roots are absent, creates only the upload
staging root, and emits one sealed receipt.  It does not accept payload bytes,
create the target materialization root, import product code, launch a worker,
or time anything.  Target prepare later verifies this receipt and the exact
staged file set before creating the materialization root.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re


SCHEMA = "rtdl.goal5791.upload_staging_open_receipt.v1"
STATUS = (
    "UPLOAD_STAGING_CREATED__TARGET_MATERIALIZATION_ROOT_REMAINS_ABSENT")
RECEIPT_NAME = "UPLOAD_STAGING_OPEN_RECEIPT.json"
STAGED_UPLOAD_RELATIVE_PATHS = {
    "bundle": "GOAL5791_PRE_POD_BUNDLE.tar.gz",
    "data_bundle": "GOAL5791_DATA_BUNDLE.tar.gz",
    "wheelhouse": "GOAL5791_DEPENDENCY_WHEELHOUSE.tar.gz",
    "optix_headers": "GOAL5791_OPTIX_HEADERS.tar.gz",
    "owner_authority": "OWNER_TARGET_PREPARE_AUTHORITY.json",
    "target_prepare": "TARGET_PREPARE.py",
}
CLEANUP_DISPOSITION = (
    "REMOVE_UPLOAD_STAGING_ONLY_AFTER_TARGET_EVIDENCE_LOCAL_PRESERVATION")
FIRST_ENTRY_OBSERVATION_SCHEMA = (
    "rtdl.goal5791.first_entry_stdin_bootstrap_observation.v1")

# This exact source is passed as the ``-c`` argument to /usr/bin/python3.
# It reads its own actual command-line source from /proc before doing anything
# else, verifies the complete helper stdin bytes and the frozen Python
# identity, and only then compiles/executes those verified helper bytes.  The
# SSH command remains an explicitly disclosed honest-operator TCB boundary.
FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE = """import hashlib
import os
from pathlib import Path
import platform
import sys

def _sha_file(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()

if len(sys.argv) < 6:
    raise SystemExit(90)
expected_bootstrap_sha, expected_helper_sha, expected_python_path, expected_python_sha, expected_python_version = sys.argv[1:6]
cmdline = Path("/proc/self/cmdline").read_bytes().split(b"\\0")
if len(cmdline) < 3 or cmdline[1] != b"-c":
    raise SystemExit(91)
actual_bootstrap_source = cmdline[2]
actual_bootstrap_sha = hashlib.sha256(actual_bootstrap_source).hexdigest()
if actual_bootstrap_sha != expected_bootstrap_sha:
    raise SystemExit(92)
helper = sys.stdin.buffer.read()
actual_helper_sha = hashlib.sha256(helper).hexdigest()
if actual_helper_sha != expected_helper_sha:
    raise SystemExit(93)
actual_python_path = os.path.abspath(sys.executable)
actual_python_sha = _sha_file(actual_python_path)
actual_python_version = platform.python_version()
if (actual_python_path != expected_python_path or actual_python_sha != expected_python_sha or actual_python_version != expected_python_version):
    raise SystemExit(94)
observation = {
    "schema": "rtdl.goal5791.first_entry_stdin_bootstrap_observation.v1",
    "bootstrap_source_sha256": actual_bootstrap_sha,
    "bootstrap_source_verified_before_helper_exec": True,
    "observed_staging_helper_size_bytes": len(helper),
    "observed_staging_helper_sha256": actual_helper_sha,
    "staging_helper_verified_before_exec": True,
    "python_executable_path": actual_python_path,
    "python_executable_sha256": actual_python_sha,
    "python_version": actual_python_version,
    "python_identity_verified_before_root_creation": True,
}
sys.argv = ["<verified_goal5791_upload_staging>", *sys.argv[6:]]
namespace = {
    "__name__": "__main__",
    "__file__": "<verified_goal5791_upload_staging>",
    "__goal5791_first_entry_observation__": observation,
}
exec(compile(helper, namespace["__file__"], "exec"), namespace, namespace)
"""
FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE_SHA256 = hashlib.sha256(
    FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE.encode("utf-8")).hexdigest()


class UploadStagingError(RuntimeError):
    pass


def _digest(value: object) -> str:
    data = json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _sha256(value: object, label: str) -> str:
    if not isinstance(value, str) \
            or re.fullmatch(r"[0-9a-f]{64}", value) is None \
            or value == "0" * 64:
        raise UploadStagingError(f"{label} is not a non-placeholder SHA-256")
    return value


def _narrow_posix_root(value: str, label: str) -> Path:
    pure = PurePosixPath(value)
    if pure.as_posix() != value or not pure.is_absolute() \
            or value in ("/", "/root", "/tmp", "/workspace") \
            or any(part in (".", "..") for part in pure.parts) \
            or "goal5791" not in pure.name.lower():
        raise UploadStagingError(f"{label} is not a narrow POSIX root")
    return Path(value)


def _endpoint(*, ssh_user: str, host: str, port: int) -> dict[str, object]:
    if not ssh_user or any(character.isspace() for character in ssh_user) \
            or not host or any(character.isspace() for character in host) \
            or type(port) is not int or not 1 <= port <= 65535:
        raise UploadStagingError("credential-free POD endpoint is invalid")
    source = {"ssh_user": ssh_user, "host": host, "port": port}
    return {**source, "identity_sha256": _digest(source)}


def _first_entry_observation(value: object) -> dict[str, object]:
    expected = {
        "schema", "bootstrap_source_sha256",
        "bootstrap_source_verified_before_helper_exec",
        "observed_staging_helper_size_bytes",
        "observed_staging_helper_sha256", "staging_helper_verified_before_exec",
        "python_executable_path", "python_executable_sha256", "python_version",
        "python_identity_verified_before_root_creation",
    }
    if not isinstance(value, dict) or set(value) != expected \
            or value["schema"] != FIRST_ENTRY_OBSERVATION_SCHEMA \
            or _sha256(value["bootstrap_source_sha256"],
                       "bootstrap source SHA-256") \
                != value["bootstrap_source_sha256"] \
            or value["bootstrap_source_sha256"] \
                != FIRST_ENTRY_STDIN_BOOTSTRAP_SOURCE_SHA256 \
            or value["bootstrap_source_verified_before_helper_exec"] is not True \
            or type(value["observed_staging_helper_size_bytes"]) is not int \
            or value["observed_staging_helper_size_bytes"] <= 0 \
            or _sha256(value["observed_staging_helper_sha256"],
                       "observed staging helper SHA-256") \
                != value["observed_staging_helper_sha256"] \
            or value["staging_helper_verified_before_exec"] is not True \
            or value["python_executable_path"] != "/usr/bin/python3" \
            or _sha256(value["python_executable_sha256"],
                       "Python executable SHA-256") \
                != value["python_executable_sha256"] \
            or value["python_version"] != "3.12.3" \
            or value["python_identity_verified_before_root_creation"] is not True:
        raise UploadStagingError("first-entry bootstrap observation is invalid")
    return dict(value)


def open_staging(
    *, upload_staging_root: str, target_materialization_root: str,
    owner_authority_sha256: str, first_entry_observation: object,
    ssh_user: str, host: str, port: int,
) -> dict[str, object]:
    staging = _narrow_posix_root(upload_staging_root, "upload staging root")
    work = _narrow_posix_root(
        target_materialization_root, "target materialization root")
    if staging == work or staging in work.parents or work in staging.parents:
        raise UploadStagingError("staging and materialization roots overlap")
    if os.path.lexists(staging) or os.path.lexists(work):
        raise FileExistsError(
            "both Goal5791 roots must be absent at first target entry")
    for parent in (staging.parent, work.parent):
        if not parent.is_dir() or parent.is_symlink():
            raise UploadStagingError("target root parent is not a real directory")
    authority_sha = _sha256(
        owner_authority_sha256, "owner authority SHA-256")
    observation = _first_entry_observation(first_entry_observation)
    endpoint = _endpoint(ssh_user=ssh_user, host=host, port=port)
    staging.mkdir(mode=0o700)
    body = {
        "schema": SCHEMA,
        "goal": 5791,
        "status": STATUS,
        "owner_target_prepare_authority_file_sha256": authority_sha,
        "bootstrap_source_sha256": observation["bootstrap_source_sha256"],
        "bootstrap_source_verified_before_helper_exec": True,
        "staging_helper_source_sha256": observation[
            "observed_staging_helper_sha256"],
        "observed_staging_helper_size_bytes": observation[
            "observed_staging_helper_size_bytes"],
        "staging_helper_verified_before_exec": True,
        "python_executable_path": observation["python_executable_path"],
        "python_executable_sha256": observation[
            "python_executable_sha256"],
        "python_version": observation["python_version"],
        "python_identity_verified_before_root_creation": True,
        "upload_staging_root": upload_staging_root,
        "target_materialization_root": target_materialization_root,
        "pod_endpoint": endpoint,
        "both_roots_observed_absent_before_staging_creation": True,
        "upload_staging_root_created_create_only": True,
        "target_materialization_root_created_by_staging_helper": False,
        "expected_uploaded_relative_paths": STAGED_UPLOAD_RELATIVE_PATHS,
        "upload_staging_cleanup_disposition": CLEANUP_DISPOSITION,
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }
    receipt = {**body, "receipt_sha256": _digest(body)}
    receipt_path = staging / RECEIPT_NAME
    with receipt_path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(receipt, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    receipt_path.chmod(receipt_path.stat().st_mode & ~0o222)
    if receipt_path.stat().st_mode & 0o222 or work.exists() \
            or work.is_symlink():
        raise UploadStagingError("create-only staging postcondition failed")
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--upload-staging-root", required=True)
    parser.add_argument("--target-materialization-root", required=True)
    parser.add_argument("--owner-authority-sha256", required=True)
    parser.add_argument("--pod-ssh-user", required=True)
    parser.add_argument("--pod-host", required=True)
    parser.add_argument("--pod-port", type=int, required=True)
    args = parser.parse_args()
    observation = globals().get("__goal5791_first_entry_observation__")
    if observation is None:
        raise UploadStagingError(
            "Goal5791 staging helper requires the verified stdin bootstrap")
    value = open_staging(
        upload_staging_root=args.upload_staging_root,
        target_materialization_root=args.target_materialization_root,
        owner_authority_sha256=args.owner_authority_sha256,
        first_entry_observation=observation,
        ssh_user=args.pod_ssh_user, host=args.pod_host, port=args.pod_port,
    )
    print(json.dumps(value, sort_keys=True))


if __name__ == "__main__":
    main()
