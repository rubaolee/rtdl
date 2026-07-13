#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as _dt
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import shlex
import subprocess
import tarfile
import tempfile
from typing import Any, Iterable


ROOT_DIR = Path(__file__).resolve().parents[3]
APP_DIR = ROOT_DIR / "Paper-reproduction-apps" / "rt-barneshut-paper"

REQUIRED_RELATIVE_PATHS = (
    "src",
    "scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
    "Paper-reproduction-apps/README.md",
    "Paper-reproduction-apps/rt-barneshut-paper",
)

CRITICAL_ARCHIVE_ENTRIES = (
    "src/rtdsl/__init__.py",
    "scripts/goal2547_barnes_hut_3d_scalar_subtree_kernel.py",
    "Paper-reproduction-apps/README.md",
    "Paper-reproduction-apps/rt-barneshut-paper/README.md",
    "Paper-reproduction-apps/rt-barneshut-paper/data/manifest.json",
    "Paper-reproduction-apps/rt-barneshut-paper/author_contract_reference.py",
    "Paper-reproduction-apps/rt-barneshut-paper/rt_barneshut_reproduction.py",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/apply_author_official_patch.py",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/check_pod_environment.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/setup_author_official.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_contract_rtdl_cuda_gate.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_comparator_gate.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.py",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_author_source_contract_gate.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.py",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.py",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_generic_aggregate_force_same_input_gate.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_rtdl_comparison_gate.sh",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_performance_gate.py",
    "Paper-reproduction-apps/rt-barneshut-paper/scripts/run_same_input_performance_gate.sh",
)

EXCLUDED_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    "__pycache__",
    "_data",
    "_runs",
    "_work",
}


def _now_stamp() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _remote_target(*, user: str, host: str) -> str:
    return host if "@" in host else f"{user}@{host}"


def _ssh_base_args(args: argparse.Namespace) -> list[str]:
    command = [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        f"ConnectTimeout={args.connect_timeout}",
        "-o",
        "StrictHostKeyChecking=no",
        "-p",
        str(args.port),
    ]
    if args.identity:
        command.extend(["-i", str(args.identity)])
    return command


def _ssh_command(args: argparse.Namespace, remote_command: str) -> list[str]:
    return _ssh_base_args(args) + [_remote_target(user=args.user, host=args.host), remote_command]


def _run_local(command: list[str], *, input_bytes: bytes | None = None) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(command, input=input_bytes, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def _parse_remote_env(entries: list[str]) -> dict[str, str]:
    env: dict[str, str] = {}
    for entry in entries:
        if "=" not in entry:
            raise SystemExit(f"--remote-env must be KEY=VALUE, got: {entry}")
        key, value = entry.split("=", 1)
        if not key or not (key[0].isalpha() or key[0] == "_") or not all(ch.isalnum() or ch == "_" for ch in key):
            raise SystemExit(f"--remote-env has invalid environment variable name: {key!r}")
        env[key] = value
    return env


def _remote_env_exports(args: argparse.Namespace) -> str:
    env = _parse_remote_env(args.remote_env)
    if not env:
        return ""
    return " ".join(f"export {key}={shlex.quote(value)};" for key, value in sorted(env.items())) + " "


def _has_excluded_part(relative_path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in relative_path.parts)


def _iter_manifest_files() -> Iterable[Path]:
    for relative in REQUIRED_RELATIVE_PATHS:
        path = ROOT_DIR / relative
        if path.is_file():
            if not _has_excluded_part(Path(relative)):
                yield path
            continue
        if path.is_dir():
            for dirpath, dirnames, filenames in os.walk(path, topdown=True, followlinks=False):
                current = Path(dirpath)
                dirnames[:] = [
                    name
                    for name in dirnames
                    if not _has_excluded_part((current / name).relative_to(ROOT_DIR))
                ]
                for filename in filenames:
                    child = current / filename
                    child_relative = child.relative_to(ROOT_DIR)
                    if _has_excluded_part(child_relative):
                        continue
                    if not child.is_file():
                        continue
                    yield child
            continue
        raise FileNotFoundError(f"required path is missing: {relative}")


def _archive_names(payload: bytes) -> list[str]:
    with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as tar:
        return sorted(member.name for member in tar.getmembers())


def _build_source_archive() -> tuple[bytes, dict[str, Any]]:
    files = sorted(set(_iter_manifest_files()))
    with tempfile.TemporaryFile() as raw:
        with tarfile.open(fileobj=raw, mode="w:gz") as tar:
            for path in files:
                tar.add(path, arcname=path.relative_to(ROOT_DIR).as_posix(), recursive=False)
        raw.seek(0)
        payload = raw.read()
    names = _archive_names(payload)
    excluded_entries_found = [
        name for name in names if _has_excluded_part(Path(*PurePosixPath(name).parts))
    ]
    required_entries_present = {
        relative: any(name == relative or name.startswith(f"{relative}/") for name in names)
        for relative in REQUIRED_RELATIVE_PATHS
    }
    critical_entries_present = {relative: relative in names for relative in CRITICAL_ARCHIVE_ENTRIES}
    manifest = {
        "file_count": len(files),
        "included_roots": list(REQUIRED_RELATIVE_PATHS),
        "critical_entries": list(CRITICAL_ARCHIVE_ENTRIES),
        "excluded_parts": sorted(EXCLUDED_PARTS),
        "excluded_entries_found": excluded_entries_found,
        "required_entries_present": required_entries_present,
        "critical_entries_present": critical_entries_present,
        "safe_to_upload": (
            not excluded_entries_found
            and all(required_entries_present.values())
            and all(critical_entries_present.values())
        ),
        "archive_bytes": len(payload),
    }
    return payload, manifest


def _safe_extract_tar(tar: tarfile.TarFile, destination: Path) -> None:
    destination_resolved = destination.resolve()
    members = tar.getmembers()
    for member in members:
        target = (destination / member.name).resolve()
        if target != destination_resolved and destination_resolved not in target.parents:
            raise RuntimeError(f"refusing to extract tar member outside destination: {member.name}")
    for member in members:
        target = destination / member.name
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True)
            continue
        if not member.isfile():
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        source = tar.extractfile(member)
        if source is None:
            raise RuntimeError(f"tar member has no file payload: {member.name}")
        with source, target.open("wb") as output:
            shutil.copyfileobj(source, output)


def _pull_remote_runs(args: argparse.Namespace, destination: Path) -> dict[str, Any]:
    remote_runs = PurePosixPath(args.remote_dir) / "Paper-reproduction-apps" / "rt-barneshut-paper" / "_runs"
    remote_command = (
        f"if [ -d {shlex.quote(str(remote_runs))} ]; then "
        f"tar -C {shlex.quote(str(remote_runs.parent))} -czf - _runs; "
        "else exit 44; fi"
    )
    proc = _run_local(_ssh_command(args, remote_command))
    result = {
        "returncode": proc.returncode,
        "stderr": proc.stderr.decode("utf-8", errors="replace")[-4000:],
        "stdout_bytes": len(proc.stdout),
        "destination": str(destination),
    }
    if proc.returncode == 0:
        destination.mkdir(parents=True, exist_ok=True)
        with tarfile.open(fileobj=io.BytesIO(proc.stdout), mode="r:gz") as tar:
            _safe_extract_tar(tar, destination)
    return result


def _init_summary(args: argparse.Namespace, run_id: str) -> dict[str, Any]:
    return {
        "mode": "rt_barneshut_remote_full_pod_gate",
        "paper_reproduction_complete": False,
        "host": args.host,
        "port": args.port,
        "remote_dir": args.remote_dir,
        "remote_env_keys": sorted(_parse_remote_env(args.remote_env)),
        "run_id": run_id,
    }


def run_package_only(args: argparse.Namespace) -> dict[str, Any]:
    run_id = args.run_id or _now_stamp()
    local_run_dir = APP_DIR / "_runs" / "remote_full_pod_gate" / run_id
    local_run_dir.mkdir(parents=True, exist_ok=True)

    archive, archive_manifest = _build_source_archive()
    summary = _init_summary(args, run_id)
    summary["archive"] = archive_manifest
    summary["overall_status"] = "package_ready" if archive_manifest["safe_to_upload"] else "package_invalid"
    summary["archive_bytes_checked"] = len(archive)
    _write_json(local_run_dir / "summary.json", summary)
    return summary


def run_remote_gate(args: argparse.Namespace) -> dict[str, Any]:
    run_id = args.run_id or _now_stamp()
    local_run_dir = APP_DIR / "_runs" / "remote_full_pod_gate" / run_id
    local_run_dir.mkdir(parents=True, exist_ok=True)

    summary = _init_summary(args, run_id)

    archive_manifest: dict[str, Any] | None = None
    if not args.skip_upload:
        archive, archive_manifest = _build_source_archive()
        summary["archive"] = archive_manifest
        mkdir = _run_local(_ssh_command(args, f"rm -rf {shlex.quote(args.remote_dir)} && mkdir -p {shlex.quote(args.remote_dir)}"))
        summary["remote_prepare"] = {
            "returncode": mkdir.returncode,
            "stdout": mkdir.stdout.decode("utf-8", errors="replace")[-4000:],
            "stderr": mkdir.stderr.decode("utf-8", errors="replace")[-4000:],
        }
        if mkdir.returncode != 0:
            summary["overall_status"] = "failed_remote_prepare"
            _write_json(local_run_dir / "summary.json", summary)
            return summary
        unpack = _run_local(
            _ssh_command(args, f"tar -xzf - -C {shlex.quote(args.remote_dir)}"),
            input_bytes=archive,
        )
        summary["remote_unpack"] = {
            "returncode": unpack.returncode,
            "stdout": unpack.stdout.decode("utf-8", errors="replace")[-4000:],
            "stderr": unpack.stderr.decode("utf-8", errors="replace")[-4000:],
        }
        if unpack.returncode != 0:
            summary["overall_status"] = "failed_remote_unpack"
            _write_json(local_run_dir / "summary.json", summary)
            return summary

    gate_command = (
        f"cd {shlex.quote(args.remote_dir)} && "
        f"{_remote_env_exports(args)}"
        "bash Paper-reproduction-apps/rt-barneshut-paper/scripts/run_full_pod_reproduction_gate.sh"
    )
    gate = _run_local(_ssh_command(args, gate_command))
    summary["remote_gate"] = {
        "returncode": gate.returncode,
        "stdout": gate.stdout.decode("utf-8", errors="replace")[-8000:],
        "stderr": gate.stderr.decode("utf-8", errors="replace")[-8000:],
    }

    pulled_dir = local_run_dir / "pulled"
    summary["pull_remote_runs"] = _pull_remote_runs(args, pulled_dir)
    pulled_summary = pulled_dir / "_runs" / "full_pod_reproduction_gate" / "summary.json"
    if pulled_summary.exists():
        try:
            summary["remote_full_gate_summary"] = json.loads(pulled_summary.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - diagnostic only
            summary["remote_full_gate_summary"] = {"json_read_error": repr(exc), "path": str(pulled_summary)}

    remote_gate_summary = summary.get("remote_full_gate_summary")
    if isinstance(remote_gate_summary, dict):
        summary["paper_reproduction_complete"] = bool(remote_gate_summary.get("paper_reproduction_complete"))
        summary["overall_status"] = remote_gate_summary.get("overall_status", "remote_gate_finished")
    elif gate.returncode == 0:
        summary["overall_status"] = "remote_gate_passed_but_summary_missing"
    else:
        summary["overall_status"] = "remote_gate_failed"

    if archive_manifest is None:
        summary["archive"] = {"skipped_upload": True}
    _write_json(local_run_dir / "summary.json", summary)
    return summary


def _validate_args(args: argparse.Namespace) -> None:
    if args.package_only:
        return
    if not args.host:
        raise SystemExit("--host is required unless --package-only is used")
    if args.port is None:
        raise SystemExit("--port is required unless --package-only is used")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upload current RT-BarnesHut paper app to a Linux POD and run the full gate.")
    parser.add_argument("--host", default=None, help="POD host or user@host.")
    parser.add_argument("--port", default=None, type=int, help="POD ssh port.")
    parser.add_argument("--user", default="root", help="SSH user when --host does not include user@.")
    parser.add_argument("--identity", type=Path, default=None, help="Optional SSH private key.")
    parser.add_argument("--remote-dir", default="/tmp/rtdl_rt_barneshut_paper", help="Remote workspace directory.")
    parser.add_argument("--connect-timeout", type=int, default=8)
    parser.add_argument("--run-id", default=None)
    parser.add_argument("--package-only", action="store_true", help="Build and validate the upload package without SSH.")
    parser.add_argument("--skip-upload", action="store_true", help="Reuse an existing remote workspace and only run/pull gates.")
    parser.add_argument(
        "--remote-env",
        action="append",
        default=[],
        metavar="KEY=VALUE",
        help="Environment variable exported before the remote full gate command. May be repeated.",
    )
    args = parser.parse_args(argv)
    _validate_args(args)

    summary = run_package_only(args) if args.package_only else run_remote_gate(args)
    print(json.dumps(summary, indent=2, sort_keys=True))
    if args.package_only:
        return 0 if summary.get("overall_status") == "package_ready" else 2
    return 0 if summary.get("paper_reproduction_complete") else 2


if __name__ == "__main__":
    raise SystemExit(main())
