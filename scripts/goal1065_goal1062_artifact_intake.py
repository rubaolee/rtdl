#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.goal1062_blocked_rtx_wording_rerun_manifest import build_manifest


DATE = "2026-04-28"
GOAL = "Goal1065 Goal1062 artifact intake"
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal1062_blocked_rtx_wording_rerun"


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover
        return None, f"{type(exc).__name__}: {exc}"


def _artifact_path(row: dict[str, Any], artifact_dir: Path) -> Path:
    output = Path(str(row["output_json"]))
    return artifact_dir / output.name


def _nested(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = data
    for part in path:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _validation_status(row: dict[str, Any], artifact: dict[str, Any]) -> tuple[str, str]:
    app = row["app"]
    if row["contains_skip_validation"]:
        return "blocked", "manifest validation row unexpectedly contains --skip-validation"
    if app == "facility_knn_assignment":
        if _nested(artifact, ("parameters", "skip_validation")) is True:
            return "blocked", "facility validation artifact was collected with skip_validation"
        if _nested(artifact, ("scenario", "mode")) != "optix":
            return "blocked", "facility validation artifact is not optix mode"
        if _nested(artifact, ("scenario", "result", "matches_oracle")) is not True:
            return "blocked", "facility validation artifact does not prove matches_oracle true"
        return "validation_passed", "facility validation artifact proves optix oracle parity"
    if app == "robot_collision_screening":
        if artifact.get("validated") is not True:
            return "blocked", "robot validation artifact was not validation-enabled"
        if artifact.get("matches_oracle") is not True:
            return "blocked", "robot validation artifact does not prove matches_oracle true"
        if artifact.get("mode") != "optix":
            return "blocked", "robot validation artifact is not optix mode"
        if artifact.get("input_mode") != "python_objects":
            return "blocked", "robot validation artifact must use python_objects input"
        if artifact.get("result_mode") != "pose_flags":
            return "blocked", "robot validation artifact must use pose_flags result mode"
        return "validation_passed", "robot validation artifact proves optix oracle parity"
    return "blocked", f"unexpected validation app {app}"


def _timing_phase_sec(row: dict[str, Any], artifact: dict[str, Any]) -> float | None:
    app = row["app"]
    if app == "facility_knn_assignment":
        stats = _nested(artifact, ("scenario", "timings_sec", "optix_query_sec"))
        if isinstance(stats, dict):
            value = stats.get("median_sec")
            if value is None:
                value = stats.get("max_sec")
            if value is None:
                value = stats.get("min_sec")
            return float(value) if isinstance(value, (int, float)) else None
        return float(stats) if isinstance(stats, (int, float)) else None
    if app == "robot_collision_screening":
        value = _nested(artifact, ("phases", "prepared_pose_flags_warm_query_sec", "median_sec"))
        return float(value) if isinstance(value, (int, float)) else None
    return None


def _timing_status(row: dict[str, Any], artifact: dict[str, Any]) -> tuple[str, str, float | None]:
    if not row["contains_skip_validation"]:
        return "blocked", "timing row should be explicitly timing-only with --skip-validation", None
    phase_sec = _timing_phase_sec(row, artifact)
    if phase_sec is None:
        return "blocked", "timing artifact does not expose the expected RTX phase", None
    floor = row["timing_floor_sec"]
    if isinstance(floor, (int, float)) and phase_sec < float(floor):
        return "timing_below_floor", f"RTX phase {phase_sec:.6f}s is below {float(floor):.3f}s floor", phase_sec
    return "timing_floor_passed", f"RTX phase {phase_sec:.6f}s passes timing floor", phase_sec


def build_intake(artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    manifest = build_manifest()
    rows: list[dict[str, Any]] = []
    for row in manifest["rows"]:
        path = _artifact_path(row, artifact_dir)
        base = {
            "app": row["app"],
            "path_name": row["path_name"],
            "phase": row["phase"],
            "expected_output_json": row["output_json"],
            "artifact_path": str(path),
            "public_speedup_claim_authorized": False,
        }
        if not path.exists():
            rows.append(
                {
                    **base,
                    "artifact_status": "missing",
                    "review_status": "needs_cloud_artifact",
                    "reason": "expected Goal1062 artifact has not been copied back from the pod",
                    "rtx_phase_sec": None,
                }
            )
            continue
        artifact, error = _load_json(path)
        if artifact is None:
            rows.append(
                {
                    **base,
                    "artifact_status": "unreadable_json",
                    "review_status": "blocked",
                    "reason": error,
                    "rtx_phase_sec": None,
                }
            )
            continue
        if row["phase"] == "correctness_validation":
            status, reason = _validation_status(row, artifact)
            phase_sec = None
        else:
            status, reason, phase_sec = _timing_status(row, artifact)
        rows.append(
            {
                **base,
                "artifact_status": "present",
                "review_status": status,
                "reason": reason,
                "rtx_phase_sec": phase_sec,
                "source_commit": (
                    artifact.get("source_commit")
                    or artifact.get("RTDL_SOURCE_COMMIT")
                    or (artifact.get("environment") or {}).get("source_commit")
                ),
            }
        )

    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["review_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    missing_count = status_counts.get("needs_cloud_artifact", 0)
    blocked_count = status_counts.get("blocked", 0)
    validation_passed = status_counts.get("validation_passed", 0)
    timing_passed = status_counts.get("timing_floor_passed", 0)
    timing_below = status_counts.get("timing_below_floor", 0)
    overall_status = (
        "blocked"
        if blocked_count
        else "ready_for_public_wording_review"
        if missing_count == 0 and validation_passed == 2 and timing_passed == 2
        else "timing_floor_not_met"
        if missing_count == 0 and validation_passed == 2 and timing_below > 0
        else "needs_cloud_artifacts"
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "artifact_dir": str(artifact_dir),
        "manifest_goal": manifest["goal"],
        "expected_artifact_count": len(rows),
        "present_artifact_count": len(rows) - missing_count,
        "missing_artifact_count": missing_count,
        "validation_passed_count": validation_passed,
        "timing_floor_passed_count": timing_passed,
        "timing_below_floor_count": timing_below,
        "blocked_count": blocked_count,
        "status_counts": status_counts,
        "overall_status": overall_status,
        "public_speedup_claim_authorized_count": 0,
        "rows": rows,
        "valid": blocked_count == 0,
        "boundary": (
            "This intake checks copied Goal1062 artifacts only. It does not run cloud, "
            "change public wording, authorize release, or authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1065 Goal1062 Artifact Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Overall status: `{payload['overall_status']}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- expected artifacts: `{payload['expected_artifact_count']}`",
        f"- present artifacts: `{payload['present_artifact_count']}`",
        f"- missing artifacts: `{payload['missing_artifact_count']}`",
        f"- validation passed: `{payload['validation_passed_count']}`",
        f"- timing floor passed: `{payload['timing_floor_passed_count']}`",
        f"- timing below floor: `{payload['timing_below_floor_count']}`",
        f"- blocked rows: `{payload['blocked_count']}`",
        f"- public speedup claims authorized: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Rows",
        "",
        "| App | Path | Phase | Artifact | Review status | RTX phase | Reason |",
        "| --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for row in payload["rows"]:
        phase = "" if row["rtx_phase_sec"] is None else f"{float(row['rtx_phase_sec']):.6f}"
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['phase']}` | "
            f"`{row['artifact_status']}` | `{row['review_status']}` | `{phase}` | {row['reason']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake copied Goal1062 cloud artifacts.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument("--output-json", default="docs/reports/goal1065_goal1062_artifact_intake_2026-04-28.json")
    parser.add_argument("--output-md", default="docs/reports/goal1065_goal1062_artifact_intake_2026-04-28.md")
    args = parser.parse_args(argv)
    payload = build_intake(args.artifact_dir)
    json_path = ROOT / args.output_json
    md_path = ROOT / args.output_md
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(json_path), "md": str(md_path), "overall_status": payload["overall_status"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
