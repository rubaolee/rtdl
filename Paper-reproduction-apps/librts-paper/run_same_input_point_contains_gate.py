from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path

from librts_reproduction import APP_DIR, run_local_point_contains


AUTHOR_RESULT_RE = re.compile(
    r"RT,\s+load\s+(?P<load_ms>[0-9.eE+-]+)\s+ms,\s+query\s+"
    r"(?P<query_ms>[0-9.eE+-]+)\s+ms,\s+results:\s+(?P<count>[0-9]+)"
)
PINNED_AUTHOR_COMMIT = "52509e8022abeab722f5a9a89d1917e8b481defe"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_author_summary(stdout: str) -> dict[str, object]:
    match = AUTHOR_RESULT_RE.search(stdout)
    if match is None:
        raise ValueError("author rtspatial_exec output lacks the expected result summary")
    return {
        "load_ms_diagnostic_only": float(match.group("load_ms")),
        "query_ms_diagnostic_only": float(match.group("query_ms")),
        "result_count": int(match.group("count")),
    }


def verify_author_source(author_source: Path) -> str:
    commit_result = subprocess.run(
        ["git", "-C", str(author_source), "rev-parse", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    author_commit = commit_result.stdout.strip()
    if commit_result.returncode != 0 or author_commit != PINNED_AUTHOR_COMMIT:
        raise RuntimeError(
            "author checkout does not match the pinned commit: "
            f"expected {PINNED_AUTHOR_COMMIT}, got {author_commit or '<unavailable>'}"
        )
    return author_commit


def build_gate_summary(
    *,
    boxes_path: Path,
    points_path: Path,
    expected_path: Path,
    author_stdout: str,
    author_command: list[str],
    author_commit: str = PINNED_AUTHOR_COMMIT,
    environment_label: str = "unspecified",
    gpu_label: str = "unspecified",
) -> dict[str, object]:
    author = parse_author_summary(author_stdout)
    rtdl = run_local_point_contains(
        boxes_path=boxes_path,
        points_path=points_path,
        expected_path=expected_path,
        backend="optix",
    )
    expected_count = int(rtdl["expected"]["valid_count"])
    author_count = int(author["result_count"])
    matched = bool(
        rtdl["matched"]
        and rtdl["rtdl"]["rt_core_accelerated"]
        and author_count == expected_count
        and int(rtdl["rtdl"]["valid_count"]) == expected_count
    )
    return {
        "schema": "rtdl.paper_reproduction.librts.same_input_point_contains.v1",
        "status": (
            "bounded_same_input_point_contains_count_matched"
            if matched
            else "bounded_same_input_point_contains_count_mismatch"
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
            "points_path": str(points_path),
            "points_sha256": _sha256(points_path),
            "expected_path": str(expected_path),
            "expected_sha256": _sha256(expected_path),
        },
        "author": {
            "implementation": "RTSpatial rtspatial_exec at pinned commit",
            "commit": author_commit,
            "commit_matches_pin": author_commit == PINNED_AUTHOR_COMMIT,
            "backend": "optix",
            "command": author_command,
            "stdout": author_stdout,
            **author,
            "pair_rows_exposed": False,
        },
        "rtdl": {
            "backend": rtdl["rtdl"]["backend"],
            "public_api": rtdl["rtdl"]["public_api"],
            "contract": rtdl["rtdl"]["contract"],
            "result_count": rtdl["rtdl"]["valid_count"],
            "candidate_id_rows": rtdl["rtdl"]["candidate_id_rows"],
            "rows_match_local_exact_fixture": rtdl["matched"],
            "rt_core_accelerated": rtdl["rtdl"]["rt_core_accelerated"],
            "native_engine_customization": rtdl["rtdl"]["native_engine_customization"],
        },
        "expected": rtdl["expected"],
        "claim_boundary": {
            "bounded_same_input_result_count_agreement": matched,
            "author_pair_relation_agreement_claimed": False,
            "mutable_index_parity_claimed": False,
            "ray_multicast_equivalence_claimed": False,
            "paper_dataset_or_figure_reproduction_claimed": False,
            "performance_claimed": False,
            "embree_evidence_used": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def run_gate(
    *,
    author_exec: Path,
    boxes_path: Path,
    points_path: Path,
    expected_path: Path,
    author_source: Path,
    environment_label: str,
    gpu_label: str,
) -> dict[str, object]:
    author_commit = verify_author_source(author_source)
    command = [
        str(author_exec),
        f"--box={boxes_path}",
        f"--point_query={points_path}",
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
        points_path=points_path,
        expected_path=expected_path,
        author_stdout=completed.stdout,
        author_command=command,
        author_commit=author_commit,
        environment_label=environment_label,
        gpu_label=gpu_label,
    )


def main() -> int:
    fixture_dir = APP_DIR / "data" / "fixtures"
    parser = argparse.ArgumentParser(description="LibRTS bounded same-input point gate")
    parser.add_argument("--author-exec", required=True, type=Path)
    parser.add_argument("--author-source", required=True, type=Path)
    parser.add_argument("--boxes", type=Path, default=fixture_dir / "tiny_boxes.wkt")
    parser.add_argument("--points", type=Path, default=fixture_dir / "tiny_points.wkt")
    parser.add_argument(
        "--expected",
        type=Path,
        default=fixture_dir / "tiny_point_contains_expected.json",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--environment-label", default="unspecified")
    parser.add_argument("--gpu-label", default="unspecified")
    args = parser.parse_args()
    payload = run_gate(
        author_exec=args.author_exec.resolve(),
        boxes_path=args.boxes.resolve(),
        points_path=args.points.resolve(),
        expected_path=args.expected.resolve(),
        author_source=args.author_source.resolve(),
        environment_label=args.environment_label,
        gpu_label=args.gpu_label,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
