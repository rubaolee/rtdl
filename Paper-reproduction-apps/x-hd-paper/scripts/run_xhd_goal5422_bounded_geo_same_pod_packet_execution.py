#!/usr/bin/env python3
"""Execute the Goal5421 bounded-geo packet through the project POD wrapper."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import textwrap
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
PACKET = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5421_bounded_geo_same_pod_packet_plan.json"
)
OUT = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5422_bounded_geo_same_pod_packet_execution.json"
)
RAW_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "results" / "goal5422_raw"
WRAPPER = ROOT / "scripts" / "current_pod_ssh.py"


def _run_local(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _wrapper_base(host: str, port: int) -> list[str]:
    return [sys.executable, str(WRAPPER), "--host", host, "--port", str(port)]


def _exec_remote(host: str, port: int, command: str) -> subprocess.CompletedProcess[str]:
    return _run_local(_wrapper_base(host, port) + ["exec", command])


def _download(host: str, port: int, remote: str, local: Path) -> subprocess.CompletedProcess[str]:
    local.parent.mkdir(parents=True, exist_ok=True)
    return _run_local(_wrapper_base(host, port) + ["download", remote, str(local)])


def _remote_python_run(
    *,
    host: str,
    port: int,
    command: list[str],
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    payload = {"command": command, "cwd": cwd, "env": env or {}}
    code = f"""
import json
import os
import subprocess
import sys
import time

payload = json.loads({json.dumps(json.dumps(payload))})
env = os.environ.copy()
env.update(payload["env"])
start = time.perf_counter()
completed = subprocess.run(
    payload["command"],
    cwd=payload["cwd"],
    env=env,
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
)
elapsed = time.perf_counter() - start
print(json.dumps({{
    "returncode": completed.returncode,
    "remote_process_wall_sec": elapsed,
    "stdout_tail": completed.stdout[-8000:],
    "stderr_tail": completed.stderr[-8000:],
}}, sort_keys=True))
sys.exit(completed.returncode)
"""
    remote = "python3 - <<'PY'\n" + textwrap.dedent(code).strip() + "\nPY"
    completed = _exec_remote(host, port, remote)
    if completed.returncode != 0:
        raise RuntimeError(
            "remote command failed\n"
            f"command={command!r}\n"
            f"stdout={completed.stdout}\n"
            f"stderr={completed.stderr}"
        )
    lines = [line for line in completed.stdout.splitlines() if line.strip()]
    if not lines:
        raise RuntimeError("remote command produced no JSON output")
    return json.loads(lines[-1])


def _rtdl_command_from_packet(row: dict[str, Any]) -> tuple[list[str], str, dict[str, str]]:
    command = row["rtdl"]["command"]
    try:
        python_index = command.index("python3")
    except ValueError as exc:
        raise ValueError(f"missing python3 in RTDL command for {row['case_id']}") from exc
    script_and_args = command[python_index + 1 :]
    return (
        ["python3", *script_and_args],
        "/tmp/rtdl_goal5419",
        {
            "PYTHONPATH": "src:.",
            "RTDL_OPTIX_LIBRARY": "/tmp/rtdl_goal5419/build/librtdl_optix.so",
        },
    )


def _remote_output_paths(row: dict[str, Any]) -> tuple[str, str]:
    author_command = row["author"]["command"]
    rtdl_command = row["rtdl"]["command"]
    return (
        author_command[author_command.index("-json") + 1],
        rtdl_command[rtdl_command.index("--summary") + 1],
    )


def run_packet(packet: dict[str, Any]) -> dict[str, Any]:
    host = str(packet["pod"]["host"])
    port = int(packet["pod"]["port"])
    setup = _exec_remote(host, port, "; ".join(packet["execution"]["setup_commands"]))
    if setup.returncode != 0:
        raise RuntimeError(f"remote setup failed: {setup.stdout}\n{setup.stderr}")

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    for row in packet["rows"]:
        author_remote, rtdl_remote = _remote_output_paths(row)
        case_id = str(row["case_id"])

        author_run = _remote_python_run(
            host=host,
            port=port,
            command=row["author"]["command"],
        )
        rtdl_cmd, rtdl_cwd, rtdl_env = _rtdl_command_from_packet(row)
        rtdl_run = _remote_python_run(
            host=host,
            port=port,
            command=rtdl_cmd,
            cwd=rtdl_cwd,
            env=rtdl_env,
        )

        local_author = RAW_DIR / f"{case_id}_author.json"
        local_rtdl = RAW_DIR / f"{case_id}_rtdl_summary.json"
        for remote, local in ((author_remote, local_author), (rtdl_remote, local_rtdl)):
            downloaded = _download(host, port, remote, local)
            if downloaded.returncode != 0:
                raise RuntimeError(f"download failed for {remote}: {downloaded.stdout}\n{downloaded.stderr}")

        author_json = json.loads(local_author.read_text(encoding="utf-8"))
        rtdl_json = json.loads(local_rtdl.read_text(encoding="utf-8"))
        author_hd = float(author_json["HDResult"])
        rtdl_hd = float(rtdl_json["rtdl"]["HDResult"])
        tolerance = float(row["comparison"]["tolerance"])
        abs_diff = abs(author_hd - rtdl_hd)
        rows.append(
            {
                "case_id": case_id,
                "paper_pair": row["paper_pair"],
                "input_identity_level": row["input_identity_level"],
                "point_counts": [rtdl_json["input"]["point_count_a"], rtdl_json["input"]["point_count_b"]],
                "author": {
                    "HDResult": author_hd,
                    "Running_AvgTime_ms": author_json.get("Running", {}).get("AvgTime"),
                    "remote_process_wall_sec": author_run["remote_process_wall_sec"],
                    "local_json": str(local_author),
                },
                "rtdl": {
                    "HDResult": rtdl_hd,
                    "route": rtdl_json["rtdl"]["route"],
                    "partner": rtdl_json["rtdl"]["partner"],
                    "triton_strategy": rtdl_json["rtdl"]["triton_strategy"],
                    "partner_reference_contract": rtdl_json["rtdl"]["partner_reference_contract"],
                    "native_engine_row_contract": rtdl_json["rtdl"]["native_engine_row_contract"],
                    "per_source_witness_exact": rtdl_json["rtdl"]["per_source_witness_exact"],
                    "run_phases": rtdl_json["run_phases"],
                    "remote_process_wall_sec": rtdl_run["remote_process_wall_sec"],
                    "local_json": str(local_rtdl),
                },
                "comparison": {
                    "abs_diff": abs_diff,
                    "tolerance": tolerance,
                    "matched": bool(abs_diff <= tolerance),
                    "comparison_reference": "directed_input1_to_input2",
                },
                "claim_boundary": {
                    "level_b_bounded_geo_correctness_claimed": bool(abs_diff <= tolerance),
                    "exact_paper_dataset_reproduction_claimed": False,
                    "geo_figure5_reproduction_claimed": False,
                    "author_rt_core_algorithm_equivalence_claimed": False,
                    "performance_ratio_claimed": False,
                    "full_paper_reproduction_claimed": False,
                },
            }
        )

    matched = all(bool(row["comparison"]["matched"]) for row in rows)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5422.bounded_geo_same_pod_packet_execution.v1",
        "goal": "Goal5422",
        "status": (
            "bounded_geo_same_pod_packet_executed__level_b_only_no_ratio"
            if matched
            else "bounded_geo_same_pod_packet_mismatch__level_b_only_no_ratio"
        ),
        "matched": matched,
        "row_count": len(rows),
        "rows": rows,
        "pod": packet["pod"],
        "source_packet": str(PACKET),
        "claim_boundary": {
            "bounded_geo_execution_claimed": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "geo_figure5_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "author_rt_core_algorithm_equivalence_claimed": False,
            "explicit_lb_reopened": False,
            "route_micro_optimization_goal_authorized": False,
        },
        "denominator_policy": packet["denominator_policy"],
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--packet", default=str(PACKET))
    parser.add_argument("--summary", default=str(OUT))
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    packet = json.loads(Path(args.packet).read_text(encoding="utf-8"))
    payload = run_packet(packet)
    out = Path(args.summary)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"matched": payload["matched"], "status": payload["status"]}, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
