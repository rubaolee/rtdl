#!/usr/bin/env python3
"""Run the local X-HD ACM artifact-to-command-packet pipeline.

This app-owned orchestrator connects the Goal5335-Goal5339 local tools:

  zip inspection -> candidate hash mapping -> workload mapping review
  -> candidate materialization -> mapped same-input command packet

It is intentionally not an executor. It does not run author ``hd_exec``, RTDL,
POD, or the Goal5340 output comparator.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import zipfile
from typing import Any, Dict, Iterable, List


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_xhd_mapped_candidate_same_input_gate_packet import build_packet  # noqa: E402
from inspect_xhd_acm_supplement_zip import inspect_zip  # noqa: E402
from map_xhd_acm_candidate_bytes_hashes import build_mapping  # noqa: E402
from review_xhd_candidate_workload_mapping import DEFAULT_TARGET_MATRIX, build_review  # noqa: E402


def _write_json(path: pathlib.Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _safe_zip_member_path(name: str) -> pathlib.PurePosixPath:
    path = pathlib.PurePosixPath(name.replace("\\", "/"))
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"unsafe zip member path: {name}")
    return path


def _materialize_candidates(
    zip_path: pathlib.Path,
    candidate_mappings: Iterable[Dict[str, Any]],
    materialized_root: pathlib.Path,
) -> Dict[str, Any]:
    materialized_root.mkdir(parents=True, exist_ok=True)
    records: List[Dict[str, Any]] = []
    with zipfile.ZipFile(zip_path) as zf:
        names = set(zf.namelist())
        for candidate in candidate_mappings:
            candidate_path = str(candidate.get("path", "")).replace("\\", "/")
            if not candidate_path:
                continue
            record: Dict[str, Any] = {
                "candidate_path": candidate_path,
                "hash_status": candidate.get("status"),
                "materialized": False,
                "materialized_path": None,
                "error": None,
            }
            try:
                member_path = _safe_zip_member_path(candidate_path)
                if candidate_path not in names:
                    raise FileNotFoundError(f"candidate path missing in zip: {candidate_path}")
                target = materialized_root / member_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(zf.read(candidate_path))
                record["materialized"] = True
                record["materialized_path"] = str(target.resolve())
            except Exception as exc:
                record["error"] = f"{type(exc).__name__}: {exc}"
            records.append(record)
    return {
        "materialized_root": str(materialized_root.resolve()),
        "candidate_count": len(records),
        "materialized_count": sum(1 for record in records if record["materialized"]),
        "records": records,
    }


def run_pipeline(
    *,
    zip_path: pathlib.Path,
    mapping_spec_path: pathlib.Path,
    output_root: pathlib.Path,
    target_matrix_path: pathlib.Path,
    author_bin: str,
    rtdl_route: str,
    reviewer_name: str,
    contact_or_source: str,
) -> Dict[str, Any]:
    zip_path = zip_path.resolve()
    mapping_spec_path = mapping_spec_path.resolve()
    output_root = output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    artifacts_dir = output_root / "artifacts"
    materialized_root = output_root / "materialized"
    gate_output_dir = output_root / "gate-output"

    inspection = inspect_zip(zip_path, reviewer_name=reviewer_name, contact_or_source=contact_or_source)
    inspection_path = artifacts_dir / "inspection.json"
    _write_json(inspection_path, inspection)

    candidate_mapping = build_mapping(zip_path)
    candidate_mapping_path = artifacts_dir / "candidate_mapping.json"
    _write_json(candidate_mapping_path, candidate_mapping)

    materialization = _materialize_candidates(
        zip_path,
        candidate_mapping.get("candidate_mappings", []),
        materialized_root,
    )
    materialization_path = artifacts_dir / "materialization.json"
    _write_json(materialization_path, materialization)

    workload_review = build_review(candidate_mapping_path, mapping_spec_path, target_matrix_path.resolve())
    workload_review_path = artifacts_dir / "workload_review.json"
    _write_json(workload_review_path, workload_review)

    packet = build_packet(
        workload_review_path,
        materialized_root=materialized_root,
        output_dir=gate_output_dir,
        author_bin=author_bin,
        rtdl_route=rtdl_route,
    )
    packet_path = artifacts_dir / "mapped_candidate_same_input_gate_packet.json"
    _write_json(packet_path, packet)

    if packet.get("classification") == "mapped_candidate_same_input_gate_commands_ready":
        classification = "local_artifact_pipeline_packet_ready__await_pod_execution"
        pod_allowed_next = True
    else:
        classification = "local_artifact_pipeline_not_pod_ready"
        pod_allowed_next = False

    return {
        "schema": "rtdl.paper_reproduction.xhd.acm_artifact_to_packet_pipeline.v1",
        "zip_path": str(zip_path),
        "mapping_spec_path": str(mapping_spec_path),
        "target_matrix_path": str(target_matrix_path.resolve()),
        "output_root": str(output_root),
        "classification": classification,
        "pod_allowed_next": pod_allowed_next,
        "requires_pod_wrapper": True,
        "commands_executed": False,
        "artifacts": {
            "inspection_json": str(inspection_path),
            "candidate_mapping_json": str(candidate_mapping_path),
            "materialization_json": str(materialization_path),
            "workload_review_json": str(workload_review_path),
            "mapped_candidate_same_input_gate_packet_json": str(packet_path),
        },
        "intermediate_classifications": {
            "candidate_mapping": candidate_mapping.get("classification"),
            "workload_review": workload_review.get("classification"),
            "gate_packet": packet.get("classification"),
        },
        "materialization_summary": {
            "candidate_count": materialization["candidate_count"],
            "materialized_count": materialization["materialized_count"],
        },
        "next_action": _next_action(classification),
        "claim_boundary": {
            "commands_executed": False,
            "same_input_gate_passed": False,
            "exact_paper_dataset_reproduction_claimed": False,
            "figure5_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
        "pod_usage": {
            "used": False,
            "expected_next": pod_allowed_next,
            "reason": "Local artifact-to-packet pipeline only. POD begins in a separate execution goal when packet is command-ready.",
        },
        "not_allowed": [
            "claiming commands were executed by this pipeline",
            "claiming same-input correctness from this pipeline",
            "claiming exact paper dataset reproduction from this pipeline",
            "claiming Figure 5 reproduction from this pipeline",
            "claiming full X-HD paper reproduction from this pipeline",
            "claiming author-vs-RTDL performance ratio from this pipeline",
            "running POD without scripts/current_pod_ssh.py",
        ],
    }


def _next_action(classification: str) -> str:
    if classification == "local_artifact_pipeline_packet_ready__await_pod_execution":
        return "open a separate POD execution goal using scripts/current_pod_ssh.py, then compare outputs with Goal5340"
    return "repair artifact, hash mapping, workload mapping, or materialized files before any POD execution"


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=pathlib.Path)
    parser.add_argument("mapping_spec_json", type=pathlib.Path)
    parser.add_argument("--output-root", type=pathlib.Path, required=True)
    parser.add_argument("--target-matrix", type=pathlib.Path, default=DEFAULT_TARGET_MATRIX)
    parser.add_argument("--author-bin", default="hd_exec")
    parser.add_argument("--rtdl-route", default="auto")
    parser.add_argument("--reviewer-name", default="local ACM-access reviewer")
    parser.add_argument("--contact-or-source", default="local artifact pipeline")
    parser.add_argument("--output", type=pathlib.Path, default=None)
    args = parser.parse_args(argv)

    try:
        summary = run_pipeline(
            zip_path=args.zip_path,
            mapping_spec_path=args.mapping_spec_json,
            output_root=args.output_root,
            target_matrix_path=args.target_matrix,
            author_bin=args.author_bin,
            rtdl_route=args.rtdl_route,
            reviewer_name=args.reviewer_name,
            contact_or_source=args.contact_or_source,
        )
    except Exception as exc:
        print(f"ACM artifact-to-packet pipeline failed: {exc}", file=sys.stderr)
        return 2

    text = json.dumps(summary, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
