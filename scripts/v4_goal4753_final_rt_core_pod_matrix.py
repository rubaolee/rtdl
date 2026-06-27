#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rtdsl.v4_goal4750_unified_rt_core_runner import MATRIX_OUTPUT_ROOT
from rtdsl.v4_goal4750_unified_rt_core_runner import POD
from rtdsl.v4_goal4750_unified_rt_core_runner import SPATIAL_SHAPE_PAIR_SERIOUS_DATASET
from rtdsl.v4_goal4750_unified_rt_core_runner import SPATIAL_SHAPE_PAIR_SMOKE_DATASET
from rtdsl.v4_goal4750_unified_rt_core_runner import TRIANGLE_FIXTURE
from rtdsl.v4_goal4750_unified_rt_core_runner import build_dry_run


SCHEMA = "rtdl.v4.goal4753.final_rt_core_pod_matrix_runner.v1"
DATE = "2026-06-26"
DEFAULT_OUTPUT = ROOT / "future" / "v4" / "evidence" / "v4_goal4753_final_rt_core_pod_matrix_2026-06-26"


def _ssh_key() -> str:
    key = str(POD["ssh_key"])
    if key.startswith("~/"):
        return str(Path.home() / key[2:])
    return key


def _ssh_base() -> list[str]:
    return [
        "ssh",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=20",
        "-o",
        "StrictHostKeyChecking=no",
        "root@" + str(POD["host"]),
        "-p",
        str(POD["port"]),
        "-i",
        _ssh_key(),
    ]


def _remote_run(command: str, *, timeout_sec: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [*_ssh_base(), command],
        text=True,
        capture_output=True,
        timeout=timeout_sec,
        check=False,
    )


def _quote_command(command: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def _export_env(env: dict[str, str]) -> str:
    return " ".join(
        f"{key}={shlex.quote(str(value))}"
        for key, value in sorted(env.items())
    )


def _remote_command(row: dict[str, Any]) -> str:
    root = shlex.quote(str(row["root"]))
    env = _export_env(dict(row["env_contract"]))
    command = _quote_command([str(item) for item in row["command"]])
    return f"cd {root} && {env} {command}"


def _copy_compat_libraries() -> dict[str, Any]:
    remote = """
set -eu
v4=/root/rtdl_v4_candidate_pod/build/librtdl_optix.so
test -f "$v4"
mkdir -p /root/rtdl_v2_14_tag/build /root/rtdl_v3_0_2_tag/build
cp "$v4" /root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so
cp "$v4" /root/rtdl_v3_0_2_tag/build/librtdl_optix.v4compat.so
ls -l /root/rtdl_v2_14_tag/build/librtdl_optix.v4compat.so /root/rtdl_v3_0_2_tag/build/librtdl_optix.v4compat.so
""".strip()
    started = time.perf_counter()
    proc = _remote_run(remote, timeout_sec=120)
    return {
        "step": "copy_compat_libraries",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "elapsed_sec": time.perf_counter() - started,
    }


def _generate_triangle_fixture() -> dict[str, Any]:
    env = {
        "PYTHONPATH": "/root/rtdl_v4_candidate_pod/src:/root/rtdl_v4_candidate_pod",
    }
    remote = (
        f"mkdir -p {shlex.quote(str(Path(TRIANGLE_FIXTURE).parent))} && "
        "cd /root/rtdl_v4_candidate_pod && "
        f"{_export_env(env)} /root/rtdl_v4_venv/bin/python "
        "scripts/goal2631_generate_triangle_k4_binary.py "
        f"--output {shlex.quote(TRIANGLE_FIXTURE)} --cliques 32768"
    )
    started = time.perf_counter()
    proc = _remote_run(remote, timeout_sec=300)
    return {
        "step": "generate_triangle_fixture",
        "fixture": TRIANGLE_FIXTURE,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "elapsed_sec": time.perf_counter() - started,
    }


def _generate_spatial_shape_pair_fixture(profile: str) -> dict[str, Any]:
    dataset = SPATIAL_SHAPE_PAIR_SERIOUS_DATASET if profile == "serious" else SPATIAL_SHAPE_PAIR_SMOKE_DATASET
    left_raw, right_raw = [part.strip() for part in dataset.split("+", 1)]
    grid = 64 if profile == "serious" else 32
    remote = f"""
set -eu
mkdir -p {shlex.quote(MATRIX_OUTPUT_ROOT)}
cd /root/rtdl_v4_candidate_pod
PYTHONPATH=/root/rtdl_v4_candidate_pod/src:/root/rtdl_v4_candidate_pod /root/rtdl_v4_venv/bin/python - <<'PY'
from pathlib import Path
from rtdsl.datasets import write_cdb
from scripts.v4_goal4681_shape_pair_relation_pod_benchmark import _make_square_grid_cdb

grid = {grid}
left_path = Path({left_raw!r})
right_path = Path({right_raw!r})
left_path.parent.mkdir(parents=True, exist_ok=True)
left = _make_square_grid_cdb(
    name=f"goal4753_left_square_grid_{{grid}}",
    grid=grid,
    spacing=1.0,
    side=0.72,
    offset_x=0.0,
    offset_y=0.0,
    face_base=1000000,
)
right = _make_square_grid_cdb(
    name=f"goal4753_right_square_grid_{{grid}}",
    grid=grid,
    spacing=1.0,
    side=0.72,
    offset_x=0.35,
    offset_y=0.35,
    face_base=2000000,
)
write_cdb(left, left_path)
write_cdb(right, right_path)
print(f"wrote spatial shape-pair grid{{grid}}: {{left_path}} + {{right_path}}")
PY
test -f {shlex.quote(left_raw)}
test -f {shlex.quote(right_raw)}
""".strip()
    started = time.perf_counter()
    proc = _remote_run(remote, timeout_sec=300)
    return {
        "step": "generate_spatial_shape_pair_fixture",
        "profile": profile,
        "dataset": dataset,
        "returncode": proc.returncode,
        "stdout": proc.stdout,
        "stderr": proc.stderr,
        "elapsed_sec": time.perf_counter() - started,
    }


def _select_rows(payload: dict[str, Any], apps: set[str] | None, versions: set[str] | None) -> list[dict[str, Any]]:
    rows = list(payload["rows"])
    if apps:
        rows = [row for row in rows if str(row["app"]) in apps]
    if versions:
        rows = [row for row in rows if str(row["version"]) in versions]
    return rows


def _run_row(row: dict[str, Any], *, out_dir: Path, timeout_sec: int) -> dict[str, Any]:
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stem = f"{row['version']}_{row['app']}"
    stdout_path = raw_dir / f"{stem}.json"
    stderr_path = raw_dir / f"{stem}.stderr.txt"
    remote = _remote_command(row)
    print(f"[goal4753] BEGIN {stem}", flush=True)
    started_unix = time.time()
    started = time.perf_counter()
    try:
        proc = _remote_run(remote, timeout_sec=timeout_sec)
        timed_out = False
        error = None
    except subprocess.TimeoutExpired as exc:
        proc = subprocess.CompletedProcess(args=[], returncode=124, stdout="", stderr=str(exc))
        timed_out = True
        error = f"timeout after {timeout_sec} seconds"
    elapsed = time.perf_counter() - started
    stdout_path.write_text(proc.stdout, encoding="utf-8", errors="replace")
    stderr_path.write_text(proc.stderr, encoding="utf-8", errors="replace")
    parse_ok = False
    json_error = None
    if proc.stdout.strip():
        try:
            json.loads(proc.stdout)
            parse_ok = True
        except Exception as exc:  # noqa: BLE001 - record parser failure, keep running matrix
            json_error = str(exc)
    print(f"[goal4753] END {stem} rc={proc.returncode} json={parse_ok} elapsed={elapsed:.3f}s", flush=True)
    return {
        "app": row["app"],
        "version": row["version"],
        "command": row["command"],
        "remote_command": remote,
        "root": row["root"],
        "stdout_json": str(stdout_path),
        "stderr": str(stderr_path),
        "returncode": int(proc.returncode),
        "timed_out": timed_out,
        "error": error,
        "json_parse_ok": parse_ok,
        "json_error": json_error,
        "elapsed_sec": elapsed,
        "started_unix": started_unix,
        "ended_unix": time.time(),
    }


def run_matrix(
    *,
    out_dir: Path,
    apps: set[str] | None,
    versions: set[str] | None,
    profile: str,
    timeout_sec: int,
    dry_run: bool,
) -> dict[str, Any]:
    dry = build_dry_run(profile=profile)
    rows = _select_rows(dry, apps, versions)
    if dry_run:
        return {
            "schema": SCHEMA,
            "status": "dry_run_only_not_executed",
            "date": DATE,
            "pod": POD,
            "profile": profile,
            "row_count_requested": len(rows),
            "row_count": len(rows),
            "rows": rows,
            "claim_boundary": {
                "pod_timing_executed": False,
                "release_authorized": False,
                "public_speed_claim_authorized": False,
            },
        }

    out_dir.mkdir(parents=True, exist_ok=True)
    preflight = [
        _copy_compat_libraries(),
        _generate_triangle_fixture(),
    ]
    if any(row["app"] == "spatial_rayjoin" for row in rows):
        preflight.append(_generate_spatial_shape_pair_fixture(profile))
    executions = []
    if any(int(item["returncode"]) != 0 for item in preflight):
        status = "preflight_failed_no_matrix"
    else:
        for row in rows:
            executions.append(_run_row(row, out_dir=out_dir, timeout_sec=timeout_sec))
        status = "pod_matrix_complete" if all(int(item["returncode"]) == 0 for item in executions) else "pod_matrix_complete_with_failures"
    summary = {
        "schema": SCHEMA,
        "status": status,
        "date": DATE,
        "pod": POD,
        "source_dry_run_schema": dry["schema"],
        "profile": profile,
        "row_count_requested": len(rows),
        "row_count_executed": len(executions),
        "preflight": preflight,
        "executions": executions,
        "returncode_failures": [
            item for item in executions if int(item["returncode"]) != 0
        ],
        "json_parse_failures": [
            item for item in executions if item["json_parse_ok"] is not True
        ],
        "claim_boundary": {
            "release_authorized": False,
            "public_speed_claim_authorized": False,
            "whole_app_high_performance_claim_authorized": False,
            "all_benchmark_speedup_claim_authorized": False,
        },
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    return summary


def _split_filter(value: str | None) -> set[str] | None:
    if not value:
        return None
    return {item.strip() for item in value.split(",") if item.strip()}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the final V4.0 V2/V3/V4 NVIDIA RT-core POD matrix.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--apps", help="comma-separated app filter")
    parser.add_argument("--versions", help="comma-separated version filter")
    parser.add_argument("--profile", choices=("smoke", "serious"), default="serious")
    parser.add_argument("--timeout-sec", type=int, default=3600)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    payload = run_matrix(
        out_dir=args.out_dir,
        apps=_split_filter(args.apps),
        versions=_split_filter(args.versions),
        profile=args.profile,
        timeout_sec=int(args.timeout_sec),
        dry_run=bool(args.dry_run),
    )
    print(json.dumps({k: payload[k] for k in ("schema", "status", "row_count_requested") if k in payload}, indent=2))
    if payload["status"] in {"preflight_failed_no_matrix", "pod_matrix_complete_with_failures"}:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
