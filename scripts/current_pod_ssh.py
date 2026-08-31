from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import tarfile


DEFAULT_KEY = Path.home() / ".ssh" / "id_ed25519_rtdl_codex_current_pod"
DEFAULT_PREFLIGHT = (
    "set -e; "
    "echo POD_OK; "
    "hostname; "
    "(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader || nvidia-smi)"
)


def _ssh_base(args: argparse.Namespace) -> list[str]:
    key = Path(args.identity).expanduser()
    if not key.exists():
        raise SystemExit(f"missing POD identity file: {key}")
    return [
        "ssh",
        "-i",
        str(key),
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        f"ConnectTimeout={args.connect_timeout}",
        "-p",
        str(args.port),
        f"{args.user}@{args.host}",
    ]


def _run(
    args: argparse.Namespace, remote_command: str, *,
    stdin_file: str | None = None,
) -> int:
    cmd = _ssh_base(args) + [remote_command]
    if args.dry_run:
        print(" ".join(cmd))
        return 0
    if stdin_file is None:
        return subprocess.run(cmd, check=False).returncode
    path = Path(stdin_file).expanduser()
    if not path.is_file():
        raise SystemExit(f"missing stdin file: {path}")
    with path.open("rb") as stream:
        return subprocess.run(cmd, check=False, stdin=stream).returncode


def _scp_base(args: argparse.Namespace) -> list[str]:
    key = Path(args.identity).expanduser()
    if not key.exists():
        raise SystemExit(f"missing POD identity file: {key}")
    return [
        "scp",
        "-i",
        str(key),
        "-o",
        "IdentitiesOnly=yes",
        "-o",
        "BatchMode=yes",
        "-o",
        "StrictHostKeyChecking=no",
        "-o",
        f"ConnectTimeout={args.connect_timeout}",
        "-P",
        str(args.port),
    ]


def _upload(args: argparse.Namespace) -> int:
    local = Path(args.local).expanduser()
    if not local.exists():
        raise SystemExit(f"missing local upload file: {local}")
    remote = f"{args.user}@{args.host}:{args.remote}"
    cmd = _scp_base(args) + [str(local), remote]
    if args.dry_run:
        print(" ".join(cmd))
        return 0
    return subprocess.run(cmd, check=False).returncode


def _download(args: argparse.Namespace) -> int:
    local = Path(args.local).expanduser()
    local.parent.mkdir(parents=True, exist_ok=True)
    remote = f"{args.user}@{args.host}:{args.remote}"
    cmd = _scp_base(args) + [remote, str(local)]
    if args.dry_run:
        print(" ".join(cmd))
        return 0
    return subprocess.run(cmd, check=False).returncode


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stage_a_first_entry(args: argparse.Namespace) -> int:
    authority_path = Path(args.authority).expanduser()
    bundle_path = Path(args.bundle).expanduser()
    helper_path = Path(args.helper).expanduser()
    for path in (authority_path, bundle_path, helper_path):
        if not path.is_file():
            raise SystemExit(f"missing Stage-A first-entry input: {path}")
    authority_bytes = authority_path.read_bytes()
    authority = json.loads(authority_bytes.decode("utf-8"))
    bundle_bytes = bundle_path.read_bytes()
    if authority.get("bundle_sha256") != _sha256(bundle_bytes):
        raise SystemExit("Stage-A first-entry bundle/authority drift")
    with tarfile.open(fileobj=io.BytesIO(bundle_bytes), mode="r:gz") as archive:
        manifest_member = archive.getmember("BUNDLE_MANIFEST.json")
        helper_member = archive.getmember("HARNESS/OPEN_UPLOAD_STAGING.py")
        manifest_stream = archive.extractfile(manifest_member)
        helper_stream = archive.extractfile(helper_member)
        if manifest_stream is None or helper_stream is None:
            raise SystemExit("Stage-A first-entry bundle member unreadable")
        manifest = json.loads(manifest_stream.read().decode("utf-8"))
        bundled_helper = helper_stream.read()
    helper_bytes = helper_path.read_bytes()
    if helper_bytes != bundled_helper:
        raise SystemExit("Stage-A first-entry helper is not exact bundle bytes")
    helper_row = next(
        (row for row in manifest.get("payloads", [])
         if row.get("path") == "HARNESS/OPEN_UPLOAD_STAGING.py"),
        None,
    )
    if helper_row is None or helper_row.get("sha256") != _sha256(helper_bytes) \
            or helper_row.get("size_bytes") != len(helper_bytes):
        raise SystemExit("Stage-A first-entry helper manifest drift")
    endpoint = authority.get("execution_target", {}).get("pod_endpoint", {})
    if endpoint.get("ssh_user") != args.user \
            or endpoint.get("host") != args.host \
            or endpoint.get("port") != args.port \
            or not isinstance(endpoint.get("identity_sha256"), str) \
            or len(endpoint["identity_sha256"]) != 64:
        raise SystemExit("Stage-A first-entry endpoint drift")
    if authority.get("schema") \
            != "rtdl.goal5791.owner_create_only_target_prepare_authority.v1" \
            or authority.get("status") \
            != "OWNER_AUTHORIZED_EXACTLY_ONCE_CREATE_ONLY_TARGET_PREPARE" \
            or authority.get("authorization", {}).get(
                "authorizes_pod_connection") is not True:
        raise SystemExit("Stage-A first-entry authority is not executable")
    bootstrap = authority["first_entry_stdin_bootstrap"]
    target = authority["required_target"]
    execution = authority["execution_target"]
    remote_argv = [
        "/usr/bin/python3", "-c", bootstrap["source"],
        bootstrap["source_sha256"], helper_row["sha256"],
        target["base_python_executable_path"],
        target["base_python_executable_sha256"],
        target["base_python_version"],
        "--upload-staging-root", execution["upload_staging_root"],
        "--target-materialization-root",
        execution["target_materialization_root"],
        "--owner-authority-sha256", _sha256(authority_bytes),
        "--pod-ssh-user", args.user,
        "--pod-host", args.host,
        "--pod-port", str(args.port),
    ]
    return _run(
        args, shlex.join(remote_argv), stdin_file=str(helper_path))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "RTDL POD SSH wrapper. Always uses the current project POD key and "
            "runs with IdentitiesOnly=yes so default/old keys cannot shadow it."
        )
    )
    parser.add_argument("--host", default=os.environ.get("RTDL_POD_HOST"))
    parser.add_argument("--port", type=int, default=os.environ.get("RTDL_POD_PORT"))
    parser.add_argument("--user", default=os.environ.get("RTDL_POD_USER", "root"))
    parser.add_argument(
        "--identity",
        default=os.environ.get("RTDL_POD_KEY", str(DEFAULT_KEY)),
        help="POD identity file; defaults to ~/.ssh/id_ed25519_rtdl_codex_current_pod",
    )
    parser.add_argument("--connect-timeout", type=int, default=10)
    parser.add_argument("--dry-run", action="store_true")

    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("preflight", help="Run hostname + nvidia-smi sanity check.")
    exec_parser = sub.add_parser("exec", help="Run a remote command after using the fixed POD key.")
    exec_parser.add_argument(
        "--stdin-file",
        help="Forward one local file byte-for-byte to the remote command stdin.",
    )
    exec_parser.add_argument("remote_command", nargs=argparse.REMAINDER)
    upload_parser = sub.add_parser("upload", help="Upload one file using the fixed POD key.")
    upload_parser.add_argument("local")
    upload_parser.add_argument("remote")
    download_parser = sub.add_parser("download", help="Download one file using the fixed POD key.")
    download_parser.add_argument("remote")
    download_parser.add_argument("local")
    first_entry_parser = sub.add_parser(
        "stage-a-first-entry",
        help=(
            "Run the exact Goal5791 Stage-A bootstrap/helper without shell "
            "newline rewriting."),
    )
    first_entry_parser.add_argument("--authority", required=True)
    first_entry_parser.add_argument("--bundle", required=True)
    first_entry_parser.add_argument("--helper", required=True)

    args = parser.parse_args(argv)
    if not args.host or not args.port:
        raise SystemExit("host and port are required; pass --host/--port or set RTDL_POD_HOST/RTDL_POD_PORT")

    if args.command == "preflight":
        return _run(args, DEFAULT_PREFLIGHT)
    if args.command == "exec":
        if not args.remote_command:
            raise SystemExit("exec requires a remote command")
        return _run(
            args, " ".join(args.remote_command), stdin_file=args.stdin_file)
    if args.command == "upload":
        return _upload(args)
    if args.command == "download":
        return _download(args)
    if args.command == "stage-a-first-entry":
        return _stage_a_first_entry(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
