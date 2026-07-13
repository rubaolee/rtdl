#!/usr/bin/env python3
"""Build an X-HD mapped-candidate same-input gate packet.

This app-owned helper follows ``review_xhd_candidate_workload_mapping.py``. It
requires an accepted clean workload mapping and, optionally, a materialized
candidate root containing the mapped files. When files are present, it emits
author ``hd_exec`` and RTDL ``hd_exec``-compatible command plans for a later
POD gate. It does not execute those commands and does not claim reproduction.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from typing import Any, Dict, List


ROOT = pathlib.Path(__file__).resolve().parents[3]
RTDL_HD_EXEC = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_rtdl_hd_exec.py"


def _load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return data


def _resolve_candidate(root: pathlib.Path | None, candidate_path: str) -> Dict[str, Any]:
    normalized = candidate_path.replace("\\", "/")
    if root is None:
        return {
            "candidate_path": normalized,
            "materialized_path": None,
            "exists": False,
            "status": "not_checked__no_materialized_root",
        }
    path = (root / pathlib.PurePosixPath(normalized)).resolve()
    return {
        "candidate_path": normalized,
        "materialized_path": str(path),
        "exists": path.exists() and path.is_file(),
        "status": "materialized_file_present" if path.exists() and path.is_file() else "materialized_file_missing",
    }


def _command_paths(output_dir: pathlib.Path, workload_id: str) -> Dict[str, pathlib.Path]:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in workload_id)
    return {
        "author_json": output_dir / f"{safe}.author_hd_exec.json",
        "rtdl_json": output_dir / f"{safe}.rtdl_hd_exec.json",
        "comparison_json": output_dir / f"{safe}.comparison.json",
    }


def _build_workload_packet(
    workload: Dict[str, Any],
    *,
    materialized_root: pathlib.Path | None,
    output_dir: pathlib.Path,
    author_bin: str,
    rtdl_route: str,
) -> Dict[str, Any]:
    workload_id = str(workload["workload_id"])
    input1 = _resolve_candidate(materialized_root, str(workload["input1"]["candidate_path"]))
    input2 = _resolve_candidate(materialized_root, str(workload["input2"]["candidate_path"]))
    paths = _command_paths(output_dir, workload_id)
    files_ready = bool(input1["exists"] and input2["exists"])
    input1_arg = input1["materialized_path"] or f"<materialized-root>/{input1['candidate_path']}"
    input2_arg = input2["materialized_path"] or f"<materialized-root>/{input2['candidate_path']}"
    n_dims = int(workload["n_dims"])
    input_type = str(workload["input_type"])

    author_command = [
        author_bin,
        "-input1",
        input1_arg,
        "-input2",
        input2_arg,
        "-n_dims",
        str(n_dims),
        "-input_type",
        input_type,
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "-json",
        str(paths["author_json"]),
        "-overwrite=true",
        "-check=false",
    ]
    rtdl_command = [
        sys.executable,
        str(RTDL_HD_EXEC),
        "-input1",
        input1_arg,
        "-input2",
        input2_arg,
        "-n_dims",
        str(n_dims),
        "-input_type",
        input_type,
        "-variant",
        "rt",
        "-execution",
        "gpu",
        "-json",
        str(paths["rtdl_json"]),
        "--rtdl-route",
        rtdl_route,
    ]
    return {
        "workload_id": workload_id,
        "figure": workload.get("figure"),
        "direction": workload.get("direction"),
        "n_dims": n_dims,
        "input_type": input_type,
        "input1": input1,
        "input2": input2,
        "files_ready": files_ready,
        "author_command": author_command,
        "rtdl_command": rtdl_command,
        "expected_outputs": {key: str(value) for key, value in paths.items()},
        "claim_boundary": {
            "commands_executed": False,
            "same_input_gate_passed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }


def build_packet(
    review_path: pathlib.Path,
    *,
    materialized_root: pathlib.Path | None,
    output_dir: pathlib.Path,
    author_bin: str,
    rtdl_route: str,
) -> Dict[str, Any]:
    review = _load_json(review_path)
    errors: List[str] = []
    if review.get("schema") != "rtdl.paper_reproduction.xhd.candidate_workload_mapping_review.v1":
        errors.append("mapping review schema mismatch")
    if review.get("classification") != "accepted_workload_mapping_ready_for_same_input_gate":
        errors.append(f"mapping review is not accepted: {review.get('classification')}")
    if review.get("invalid_workload_review_count") not in {0, "0"}:
        errors.append("mapping review has invalid workload rows")
    if review.get("pod_allowed_next") is not True:
        errors.append("mapping review does not allow a later POD gate")

    workloads = [
        dict(workload)
        for workload in review.get("workload_reviews", [])
        if isinstance(workload, dict) and workload.get("valid") is True
    ]
    packets = [
        _build_workload_packet(
            workload,
            materialized_root=materialized_root,
            output_dir=output_dir,
            author_bin=author_bin,
            rtdl_route=rtdl_route,
        )
        for workload in workloads
    ]
    if not packets:
        errors.append("no valid workload reviews available")

    all_files_ready = bool(packets and all(packet["files_ready"] for packet in packets))
    if errors:
        classification = "mapping_review_not_ready_for_same_input_gate"
        pod_allowed_next = False
    elif all_files_ready:
        classification = "mapped_candidate_same_input_gate_commands_ready"
        pod_allowed_next = True
    else:
        classification = "accepted_mapping_but_candidate_files_not_materialized"
        pod_allowed_next = False

    return {
        "schema": "rtdl.paper_reproduction.xhd.mapped_candidate_same_input_gate_packet.v1",
        "mapping_review_path": str(review_path),
        "materialized_root": None if materialized_root is None else str(materialized_root),
        "output_dir": str(output_dir),
        "classification": classification,
        "pod_allowed_next": pod_allowed_next,
        "requires_pod_wrapper": True,
        "commands_executed": False,
        "workload_packet_count": len(packets),
        "workload_packets": packets,
        "errors": errors,
        "sufficient_to_claim_exact_input": False,
        "claim_boundary": {
            "same_input_gate_passed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "not_allowed": [
            "claiming exact paper dataset reproduction from this packet alone",
            "claiming Figure 5 reproduction from this packet alone",
            "claiming full X-HD paper reproduction from this packet alone",
            "claiming author-vs-RTDL performance ratio from this packet alone",
            "running commands without scripts/current_pod_ssh.py when POD is used",
        ],
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping_review_json", type=pathlib.Path)
    parser.add_argument("--materialized-root", type=pathlib.Path, default=None)
    parser.add_argument("--output-dir", type=pathlib.Path, required=True)
    parser.add_argument("--author-bin", default="hd_exec")
    parser.add_argument("--rtdl-route", default="auto")
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        packet = build_packet(
            args.mapping_review_json,
            materialized_root=args.materialized_root.resolve() if args.materialized_root else None,
            output_dir=args.output_dir.resolve(),
            author_bin=args.author_bin,
            rtdl_route=args.rtdl_route,
        )
    except Exception as exc:
        print(f"mapped candidate same-input packet failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(packet, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
