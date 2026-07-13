#!/usr/bin/env python3
"""Build the Goal5418 Figure-5 Level-B same-POD execution packet.

This script is app-owned.  It reads the Goal5417 matrix plan and emits a
command/readiness packet for a future POD execution goal.  It intentionally
does not run the matrix by default and does not report any performance ratio.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
from typing import Any, Iterable


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
DEFAULT_PLAN = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5417_figure5_level_b_same_pod_matrix_plan.json"
)
DEFAULT_AUTHOR_SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5298_author_graphics_precheck_summary_pod.json"
)
DEFAULT_SUMMARY = (
    ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "results"
    / "xhd_goal5418_figure5_level_b_same_pod_matrix_readiness.json"
)
RTDL_HD_EXEC = "Paper-reproduction-apps/x-hd-paper/scripts/run_xhd_rtdl_hd_exec.py"
GRAPHICS_RTDL_PREPROCESSING_FLAGS = ["--translate-each-input-to-min-bound"]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _shell_join(command: list[str]) -> str:
    return " ".join(shlex.quote(str(part)) for part in command)


def _author_bin(args: argparse.Namespace) -> str:
    if args.author_bin:
        return str(args.author_bin)
    if DEFAULT_AUTHOR_SUMMARY.exists():
        summary = _read_json(DEFAULT_AUTHOR_SUMMARY)
        if summary.get("author_bin"):
            return str(summary["author_bin"])
    return "<author_hd_exec>"


def _author_command(
    case: dict[str, Any],
    *,
    author_bin: str,
    output_dir: str,
    serialize_dir: str,
    repeat: int,
) -> list[str]:
    return [
        author_bin,
        "-input1",
        str(case["input1"]),
        "-input2",
        str(case["input2"]),
        "-input_type",
        str(case["input_type"]),
        "-n_dims",
        str(case["n_dims"]),
        "-serialize",
        serialize_dir,
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "-repeat",
        str(repeat),
        "-json",
        f"{output_dir}/{case['case_id']}_author.json",
        "-overwrite=true",
        "-check=false",
        "-normalize=false",
        "-lb=256",
    ]


def _normalized_route_label(route_label: str) -> str:
    return route_label.replace("_if_operational", "")


def _rtdl_command(
    case: dict[str, Any],
    *,
    route_label: str,
    output_dir: str,
    grid_shape: str,
    max_inline_points: int,
) -> list[str]:
    normalized = _normalized_route_label(route_label)
    command = [
        "py",
        RTDL_HD_EXEC,
        "-input1",
        str(case["input1"]),
        "-input2",
        str(case["input2"]),
        "-input_type",
        str(case["input_type"]),
        "-n_dims",
        str(case["n_dims"]),
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "-json",
        f"{output_dir}/{case['case_id']}_{normalized}_rtdl.json",
        "-overwrite=true",
        "-check=false",
        "--rtdl-route",
        normalized,
        "--grid-shape",
        grid_shape,
        "--max-inline-points",
        str(max_inline_points),
        *GRAPHICS_RTDL_PREPROCESSING_FLAGS,
    ]
    return command


def _graphics_rows(plan: dict[str, Any], args: argparse.Namespace) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    author_bin = _author_bin(args)
    for case in plan["primary_graphics_candidates"]:
        if not bool(case.get("include")):
            continue
        author_cmd = _author_command(
            case,
            author_bin=author_bin,
            output_dir=str(args.remote_output_dir),
            serialize_dir=str(args.remote_serialize_dir),
            repeat=int(args.author_repeat),
        )
        route_commands = []
        for route_label in case["planned_rtdl_routes"]:
            route_cmd = _rtdl_command(
                case,
                route_label=str(route_label),
                output_dir=str(args.remote_output_dir),
                grid_shape=str(args.grid_shape),
                max_inline_points=int(args.max_inline_points),
            )
            route_commands.append(
                {
                    "route_label": _normalized_route_label(str(route_label)),
                    "condition": (
                        "execute_if_operational"
                        if str(route_label).endswith("_if_operational")
                        else "execute"
                    ),
                    "command": route_cmd,
                    "command_text": _shell_join(route_cmd),
                }
            )
        rows.append(
            {
                "case_id": case["case_id"],
                "category": "graphics",
                "input_identity_level": "level_b_same_source_public_graphics",
                "point_counts": case["point_counts"],
                "paper_log_hd_result_if_available": case["paper_log_hd_result"],
                "prior_author_rerun_hd_result": case["author_rerun_hd_result"],
                "prior_rtdl_hd_result": case["prior_rtdl_hd_result"],
                "author_command": author_cmd,
                "author_command_text": _shell_join(author_cmd),
                "rtdl_route_commands": route_commands,
                "planned_denominator_columns": plan["planned_denominator_columns"],
                "required_rtdl_preprocessing": ["translate_each_input_to_min_bound"],
                "ratio_authorized": False,
            }
        )
    return rows


def _secondary_geo_rows(plan: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for case in plan["secondary_bounded_geo_candidates"]:
        rows.append(
            {
                "case_id": case["case_id"],
                "category": case["category"],
                "input_identity_level": "level_b_bounded_geo_fixture",
                "point_counts": case["point_counts"],
                "prior_author_hd_result": case["author_hd_result"],
                "prior_rtdl_hd_result": case["prior_rtdl_hd_result"],
                "prior_abs_diff": case["prior_abs_diff"],
                "execution_status": "deferred_secondary_bounded_geo",
                "reason": (
                    "Bounded geo rows use partner/Triton gate scripts rather than "
                    "the current graphics hd_exec-compatible route packet.  They "
                    "should be executed only after paths and runner family are "
                    "restated in a separate geo execution packet."
                ),
                "ratio_authorized": False,
            }
        )
    return rows


def build_readiness(args: argparse.Namespace) -> dict[str, Any]:
    plan = _read_json(Path(args.plan))
    if plan.get("schema") != "rtdl.paper_reproduction.xhd.goal5417.figure5_level_b_same_pod_matrix_plan.v1":
        raise ValueError("Goal5418 readiness requires the Goal5417 matrix plan")
    graphics_rows = _graphics_rows(plan, args)
    secondary_geo_rows = _secondary_geo_rows(plan)
    command_count = sum(1 + len(row["rtdl_route_commands"]) for row in graphics_rows)
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5418.figure5_level_b_same_pod_matrix_readiness.v1",
        "goal": "Goal5418",
        "status": "figure5_level_b_same_pod_matrix_execution_packet_ready__dry_run_only",
        "matched": True,
        "source_plan": str(args.plan),
        "dry_run_only": True,
        "same_pod_execution_claimed": False,
        "matrix_rows_executed": 0,
        "graphics_case_count": len(graphics_rows),
        "graphics_command_count": command_count,
        "secondary_geo_case_count": len(secondary_geo_rows),
        "graphics_execution_rows": graphics_rows,
        "secondary_geo_rows": secondary_geo_rows,
        "pod_wrapper": {
            "required": True,
            "preflight": "py scripts/current_pod_ssh.py --host <host> --port <port> preflight",
            "exec": "py scripts/current_pod_ssh.py --host <host> --port <port> exec \"<remote command>\"",
            "naked_ssh_allowed": False,
        },
        "claim_boundary": {
            "execution_packet_claimed": True,
            "same_pod_execution_claimed": False,
            "figure5_reproduction_claimed": False,
            "performance_ratio_claimed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "full_xhd_paper_reproduction_claimed": False,
        },
        "recommended_next": {
            "name": "Goal5419_run_figure5_level_b_same_pod_graphics_matrix_on_pod",
            "requires_pod_endpoint": True,
            "requires_preflight": True,
            "input": "Goal5418 command packet",
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", type=Path, default=DEFAULT_PLAN)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY)
    parser.add_argument("--author-bin")
    parser.add_argument("--remote-output-dir", default="/tmp/xhd_goal5418/results")
    parser.add_argument("--remote-serialize-dir", default="/tmp/xhd_goal5418/ser")
    parser.add_argument("--author-repeat", type=int, default=1)
    parser.add_argument("--grid-shape", default="32,32,32")
    parser.add_argument("--max-inline-points", type=int, default=512)
    args = parser.parse_args(list(argv) if argv is not None else None)
    payload = build_readiness(args)
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"schema": payload["schema"], "matched": payload["matched"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
