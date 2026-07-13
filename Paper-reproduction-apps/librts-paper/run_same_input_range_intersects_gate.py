from __future__ import annotations

import argparse
import json
import platform
import subprocess
from pathlib import Path

from librts_reproduction import APP_DIR, run_range_intersects
from run_same_input_point_contains_gate import (
    PINNED_AUTHOR_COMMIT,
    _sha256,
    parse_author_summary,
    verify_author_source,
)


def build_gate_summary(
    *,
    boxes_path: Path,
    queries_path: Path,
    expected_path: Path,
    author_stdout: str,
    author_command: list[str],
    author_commit: str = PINNED_AUTHOR_COMMIT,
    environment_label: str = "unspecified",
    gpu_label: str = "unspecified",
) -> dict[str, object]:
    author = parse_author_summary(author_stdout)
    rtdl = run_range_intersects(
        boxes_path=boxes_path,
        box_queries_path=queries_path,
        expected_path=expected_path,
        backend="optix",
    )
    expected_count = int(rtdl["expected"]["valid_count"])
    matched = bool(
        rtdl["matched"]
        and rtdl["fixture"]["predicate_discriminating"]
        and rtdl["rtdl"]["rt_core_accelerated"]
        and rtdl["rtdl"]["complete_candidate_coverage"]
        and int(author["result_count"]) == expected_count
        and int(rtdl["rtdl"]["result_count"]) == expected_count
        and len(rtdl["rtdl"]["candidate_id_rows"]) == expected_count
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.same_input_range_intersects.v1",
        "status": (
            "bounded_same_input_range_intersects_count_and_rtdl_rows_matched"
            if matched
            else "bounded_same_input_range_intersects_mismatch"
        ),
        "matched": matched,
        "environment": {
            "label": environment_label,
            "host": platform.node(),
            "platform": platform.platform(),
            "gpu": gpu_label,
            "performance_evidence_authorized": False,
        },
        "input_identity": {
            "same_files_passed_to_author_and_rtdl": True,
            "boxes_path": str(boxes_path),
            "boxes_sha256": _sha256(boxes_path),
            "queries_path": str(queries_path),
            "queries_sha256": _sha256(queries_path),
            "expected_path": str(expected_path),
            "expected_sha256": _sha256(expected_path),
        },
        "semantics": {
            "operation": "range_intersects",
            "direction": "indexed_box_intersects_query_box",
            "boundary_policy": "inclusive_min_max",
            "expected_count": expected_count,
            "range_contains_count": int(rtdl["expected"]["range_contains_count"]),
            "predicate_discriminating": rtdl["fixture"]["predicate_discriminating"],
        },
        "author": {
            "implementation": "RTSpatial rtspatial_exec at pinned commit",
            "backend": "optix",
            "commit": author_commit,
            "commit_matches_pin": author_commit == PINNED_AUTHOR_COMMIT,
            "command": author_command,
            "stdout": author_stdout,
            **author,
            "pair_rows_exposed": False,
        },
        "rtdl": rtdl["rtdl"],
        "claim_boundary": {
            "bounded_same_input_result_count_agreement": matched,
            "predicate_semantics_discriminated": rtdl["fixture"]["predicate_discriminating"],
            "rtdl_native_pair_rows_matched": rtdl["matched"],
            "author_pair_relation_agreement_claimed": False,
            "mutable_index_parity_claimed": False,
            "performance_claimed": False,
            "embree_evidence_used": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def run_gate(
    *,
    author_exec: Path,
    author_source: Path,
    boxes_path: Path,
    queries_path: Path,
    expected_path: Path,
    environment_label: str,
    gpu_label: str,
) -> dict[str, object]:
    author_commit = verify_author_source(author_source)
    command = [
        str(author_exec),
        f"--box={boxes_path}",
        f"--box_query={queries_path}",
        "--predicate=intersects",
        "--load_factor=1",
        "--parallelism=1",
    ]
    completed = subprocess.run(
        command,
        cwd=author_exec.parent,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"author rtspatial_exec failed with exit {completed.returncode}: "
            f"{completed.stderr.strip()}"
        )
    return build_gate_summary(
        boxes_path=boxes_path,
        queries_path=queries_path,
        expected_path=expected_path,
        author_stdout=completed.stdout,
        author_command=command,
        author_commit=author_commit,
        environment_label=environment_label,
        gpu_label=gpu_label,
    )


def main() -> int:
    fixture_dir = APP_DIR / "data" / "fixtures"
    parser = argparse.ArgumentParser(description="LibRTS bounded same-input intersects gate")
    parser.add_argument("--author-exec", required=True, type=Path)
    parser.add_argument("--author-source", required=True, type=Path)
    parser.add_argument("--boxes", type=Path, default=fixture_dir / "tiny_boxes.wkt")
    parser.add_argument(
        "--queries", type=Path, default=fixture_dir / "tiny_range_queries.wkt"
    )
    parser.add_argument(
        "--expected",
        type=Path,
        default=fixture_dir / "tiny_range_intersects_expected.json",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--environment-label", default="unspecified")
    parser.add_argument("--gpu-label", default="unspecified")
    args = parser.parse_args()
    payload = run_gate(
        author_exec=args.author_exec.resolve(),
        author_source=args.author_source.resolve(),
        boxes_path=args.boxes.resolve(),
        queries_path=args.queries.resolve(),
        expected_path=args.expected.resolve(),
        environment_label=args.environment_label,
        gpu_label=args.gpu_label,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
