from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


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


def _run(args: argparse.Namespace, remote_command: str) -> int:
    cmd = _ssh_base(args) + [remote_command]
    if args.dry_run:
        print(" ".join(cmd))
        return 0
    return subprocess.run(cmd, check=False).returncode


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
    exec_parser.add_argument("remote_command", nargs=argparse.REMAINDER)
    upload_parser = sub.add_parser("upload", help="Upload one file using the fixed POD key.")
    upload_parser.add_argument("local")
    upload_parser.add_argument("remote")
    download_parser = sub.add_parser("download", help="Download one file using the fixed POD key.")
    download_parser.add_argument("remote")
    download_parser.add_argument("local")

    args = parser.parse_args(argv)
    if not args.host or not args.port:
        raise SystemExit("host and port are required; pass --host/--port or set RTDL_POD_HOST/RTDL_POD_PORT")

    if args.command == "preflight":
        return _run(args, DEFAULT_PREFLIGHT)
    if args.command == "exec":
        if not args.remote_command:
            raise SystemExit("exec requires a remote command")
        return _run(args, " ".join(args.remote_command))
    if args.command == "upload":
        return _upload(args)
    if args.command == "download":
        return _download(args)
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
