#!/usr/bin/env python3
"""Launch Goal5844 from Git, stream evidence back, and reverify it locally."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

from scripts.goal5844_verify_gpu_engineering_result import verify_result_root

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "scripts" / "current_pod_ssh.py"
DEFAULT_KEY = Path.home() / ".ssh" / "id_ed25519_rtdl_codex"


def _capture(command: list[str], *, cwd: Path = ROOT) -> str:
    return subprocess.run(
        command, cwd=cwd, check=True, text=True, capture_output=True
    ).stdout.strip()


def build_remote_command(
    *,
    repository_url: str,
    expected_commit: str,
    remote_checkout: str,
    remote_output: str,
) -> str:
    checkout = shlex.quote(remote_checkout)
    output = shlex.quote(remote_output)
    commit = shlex.quote(expected_commit)
    remote = shlex.quote(repository_url)
    return "\n".join(
        (
            "set -euo pipefail",
            f"test ! -e {checkout}",
            f"test ! -e {output}",
            f"git init -q {checkout}",
            f"git -C {checkout} remote add origin {remote}",
            f"git -C {checkout} fetch -q --depth 1 origin {commit}",
            f"git -C {checkout} checkout -q --detach FETCH_HEAD",
            f'test "$(git -C {checkout} rev-parse HEAD)" = {commit}',
            f"cd {checkout}",
            f"bash scripts/goal5844_pod_prepare_and_run.sh {commit} {output}",
        )
    )


def _wrapper_prefix(args: argparse.Namespace) -> list[str]:
    return [
        sys.executable,
        str(WRAPPER),
        "--host",
        args.host,
        "--port",
        str(args.port),
        "--user",
        args.user,
        "--identity",
        str(args.identity.expanduser()),
        "--connect-timeout",
        str(args.connect_timeout),
    ]


def _run(command: list[str]) -> None:
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode:
        raise RuntimeError(f"Goal5844 launcher command failed: {command!r}")


def _stream_download(prefix: list[str], remote: str, local: Path) -> None:
    destination = local.expanduser().absolute()
    if destination.exists() or destination.is_symlink():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(f".{destination.name}.partial.{os.getpid()}")
    try:
        with partial.open("xb") as stream:
            completed = subprocess.run(
                prefix + ["exec", f"cat -- {shlex.quote(remote)}"],
                cwd=ROOT,
                check=False,
                stdout=stream,
            )
        if completed.returncode:
            raise RuntimeError(f"Goal5844 SSH stream download failed: {remote}")
        partial.replace(destination)
    finally:
        partial.unlink(missing_ok=True)


def _safe_extract(archive_path: Path, destination: Path) -> None:
    with tarfile.open(archive_path, "r:gz") as archive:
        seen: set[str] = set()
        for member in archive.getmembers():
            path = Path(member.name)
            canonical = path.as_posix().rstrip("/")
            if (
                path.is_absolute()
                or ".." in path.parts
                or not canonical
                or canonical == "."
                or canonical != member.name.rstrip("/")
                or member.issym()
                or member.islnk()
                or not (member.isfile() or member.isdir())
                or canonical.casefold() in seen
            ):
                raise RuntimeError("Goal5844 return archive contains an unsafe member")
            seen.add(canonical.casefold())
        destination.mkdir(parents=True, exist_ok=False)
        if "filter" in tarfile.TarFile.extractall.__code__.co_varnames:
            archive.extractall(destination, filter="data")
        else:  # pragma: no cover - Python 3.11 compatibility.
            archive.extractall(destination)


def _retrieve_failure_evidence(
    prefix: list[str], remote_output: str, local_root: Path
) -> Path:
    archive = Path(str(local_root) + ".failure.tar.gz")
    checksum = Path(str(archive) + ".sha256")
    extraction = Path(str(local_root) + ".failure")
    _stream_download(prefix, remote_output + ".failure.tar.gz", archive)
    _stream_download(prefix, remote_output + ".failure.tar.gz.sha256", checksum)
    checksum_fields = checksum.read_text(encoding="utf-8").split()
    observed = hashlib.sha256(archive.read_bytes()).hexdigest()
    if len(checksum_fields) < 1 or checksum_fields[0] != observed:
        raise RuntimeError("Goal5844 failure archive SHA256 differs")
    _safe_extract(archive, extraction)
    return extraction


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--user", default="root")
    parser.add_argument("--identity", type=Path, default=DEFAULT_KEY)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--remote-ref")
    parser.add_argument("--remote-base", default="/workspace")
    parser.add_argument("--local-output", type=Path, required=True)
    parser.add_argument("--connect-timeout", type=int, default=15)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    if re.fullmatch(r"[0-9a-f]{40}", args.expected_commit) is None:
        raise ValueError("Goal5844 expected commit must be a full hash")
    if args.local_output.exists() or args.local_output.is_symlink():
        raise FileExistsError(args.local_output)
    if _capture(["git", "status", "--porcelain=v1", "--untracked-files=all"]):
        raise RuntimeError("Goal5844 launcher requires a clean local checkout")
    if _capture(["git", "rev-parse", "HEAD"]) != args.expected_commit:
        raise RuntimeError("Goal5844 launcher HEAD differs from expected commit")
    branch = args.remote_ref or _capture(["git", "branch", "--show-current"])
    if not branch:
        raise RuntimeError("Goal5844 remote ref is required from detached HEAD")
    repository_url = _capture(["git", "remote", "get-url", "origin"])
    remote_row = _capture(
        ["git", "ls-remote", "--heads", "origin", f"refs/heads/{branch}"]
    )
    if not remote_row or remote_row.split()[0] != args.expected_commit:
        raise RuntimeError("Goal5844 expected commit is not the remote branch tip")

    token = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    stem = f"goal5844-{args.expected_commit[:12]}-{token}"
    remote_checkout = f"{args.remote_base.rstrip('/')}/{stem}-source"
    remote_output = f"{args.remote_base.rstrip('/')}/{stem}-run"
    command = build_remote_command(
        repository_url=repository_url,
        expected_commit=args.expected_commit,
        remote_checkout=remote_checkout,
        remote_output=remote_output,
    )
    prefix = _wrapper_prefix(args)
    local_root = args.local_output.expanduser().absolute()
    if args.dry_run:
        print(
            json.dumps(
                {
                    "remote_command": command,
                    "remote_archive": remote_output + ".tar.gz",
                    "local_output": str(args.local_output.expanduser().absolute()),
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    _run(prefix + ["preflight"])
    try:
        _run(prefix + ["exec", command])
    except RuntimeError as error:
        try:
            failure_root = _retrieve_failure_evidence(prefix, remote_output, local_root)
        except Exception as retrieval_error:
            raise RuntimeError(
                "Goal5844 pod transaction failed and no verified failure bundle "
                "could be retrieved"
            ) from retrieval_error
        raise RuntimeError(
            f"Goal5844 pod transaction failed; diagnostics: {failure_root}"
        ) from error

    archive = Path(str(local_root) + ".tar.gz")
    checksum = Path(str(archive) + ".sha256")
    _stream_download(prefix, remote_output + ".tar.gz", archive)
    _stream_download(prefix, remote_output + ".tar.gz.sha256", checksum)
    checksum_fields = checksum.read_text(encoding="utf-8").split()
    observed = hashlib.sha256(archive.read_bytes()).hexdigest()
    if len(checksum_fields) < 1 or checksum_fields[0] != observed:
        raise RuntimeError("Goal5844 streamed archive SHA256 differs")
    _safe_extract(archive, local_root)
    verified = verify_result_root(
        local_root / "comparison", expected_source_commit=args.expected_commit
    )
    verification_path = local_root / "LOCAL_INDEPENDENT_VERIFICATION.json"
    verification_path.write_text(
        json.dumps(verified, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": verified["status"],
                "local_output": str(local_root),
                "archive_sha256": observed,
                "summary_result_sha256": verified["summary_result_sha256"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
