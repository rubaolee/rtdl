#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.goal1084_facility_recentered_rtx_pod_packet import build_packet as build_facility_packet
from scripts.goal1093_barnes_hut_20m_contract_packet import build_packet as build_barnes_packet


DATE = "2026-04-29"
GOAL = "Goal1096 current RTX pod artifact intake"
DEFAULT_ARTIFACT_ROOT = ROOT / "docs" / "reports"


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"


def _nested(data: dict[str, Any], path: tuple[str, ...]) -> Any:
    value: Any = data
    for part in path:
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


def _artifact_path(row: dict[str, Any], artifact_root: Path) -> Path:
    output = Path(str(row["output_json"]))
    return artifact_root / output.parent.name / output.name


def _median_optix_query_sec(artifact: dict[str, Any]) -> float | None:
    value = _nested(artifact, ("scenario", "timings_sec", "optix_query_sec"))
    if isinstance(value, dict):
        median = value.get("median_sec")
        return float(median) if isinstance(median, (int, float)) else None
    return float(value) if isinstance(value, (int, float)) else None


def _validate_common(row: dict[str, Any], artifact: dict[str, Any]) -> tuple[bool, str]:
    if artifact.get("schema_version") != "goal887_prepared_decision_phase_contract_v1":
        return False, "artifact has unexpected schema_version"
    if _nested(artifact, ("scenario", "mode")) != "optix":
        return False, "artifact scenario mode is not optix"
    if bool(_nested(artifact, ("parameters", "skip_validation"))) != bool(row["contains_skip_validation"]):
        return False, "artifact skip_validation does not match packet row"
    return True, "common artifact fields match packet row"


def _validate_facility(row: dict[str, Any], artifact: dict[str, Any]) -> tuple[str, str, float | None]:
    ok, reason = _validate_common(row, artifact)
    if not ok:
        return "blocked", reason, None
    if _nested(artifact, ("scenario", "scenario")) != "facility_service_coverage_recentered":
        return "blocked", "facility artifact scenario is not facility_service_coverage_recentered", None
    if _nested(artifact, ("scenario", "coordinate_mapping")) != "copy_local_recentered_queries_canonical_depots":
        return "blocked", "facility artifact is missing recentered coordinate mapping", None
    if _nested(artifact, ("scenario", "result", "matches_oracle")) is not True:
        return "blocked", "facility artifact does not prove matches_oracle true", None
    phase_sec = _median_optix_query_sec(artifact)
    if phase_sec is None:
        return "blocked", "facility artifact does not expose optix_query median", None
    floor = row["timing_floor_sec"]
    if isinstance(floor, (int, float)) and phase_sec < float(floor):
        return "timing_below_floor", f"facility RTX phase {phase_sec:.6f}s is below {float(floor):.3f}s floor", phase_sec
    return "validation_and_timing_passed", "facility artifact proves oracle parity and timing floor", phase_sec


def _validate_barnes(row: dict[str, Any], artifact: dict[str, Any]) -> tuple[str, str, float | None]:
    ok, reason = _validate_common(row, artifact)
    if not ok:
        return "blocked", reason, None
    if _nested(artifact, ("scenario", "scenario")) != "barnes_hut_node_coverage":
        return "blocked", "Barnes-Hut artifact scenario is not barnes_hut_node_coverage", None
    if _nested(artifact, ("scenario", "result", "barnes_tree_depth")) != row["barnes_tree_depth"]:
        return "blocked", "Barnes-Hut tree depth does not match packet row", None
    if _nested(artifact, ("scenario", "result", "hit_threshold")) != row["hit_threshold"]:
        return "blocked", "Barnes-Hut hit threshold does not match packet row", None
    if _nested(artifact, ("scenario", "result", "node_count")) != row["node_count"]:
        return "blocked", "Barnes-Hut node count does not match packet row", None

    phase_sec = _median_optix_query_sec(artifact)
    if row["requires_validation"]:
        if _nested(artifact, ("scenario", "result", "matches_oracle")) is not True:
            return "blocked", "Barnes-Hut validation artifact does not prove matches_oracle true", None
        return "validation_passed", "Barnes-Hut artifact proves depth-8 oracle parity", phase_sec

    if phase_sec is None:
        return "blocked", "Barnes-Hut timing artifact does not expose optix_query median", None
    floor = row["timing_floor_sec"]
    if isinstance(floor, (int, float)) and phase_sec < float(floor):
        return "timing_below_floor", f"Barnes-Hut RTX phase {phase_sec:.6f}s is below {float(floor):.3f}s floor", phase_sec
    return "timing_floor_passed", "Barnes-Hut timing artifact passes timing floor", phase_sec


def _review_row(row: dict[str, Any], artifact_root: Path) -> dict[str, Any]:
    path = _artifact_path(row, artifact_root)
    base = {
        "app": row["app"],
        "path_name": row["path_name"],
        "phase": row["phase"],
        "expected_output_json": row["output_json"],
        "artifact_path": str(path),
        "requires_validation": row["requires_validation"],
        "contains_skip_validation": row["contains_skip_validation"],
        "timing_floor_sec": row["timing_floor_sec"],
        "public_speedup_claim_authorized": False,
    }
    if not path.exists():
        return {
            **base,
            "artifact_status": "missing",
            "review_status": "needs_cloud_artifact",
            "reason": "expected current RTX pod artifact has not been copied back",
            "rtx_phase_sec": None,
            "source_commit": None,
        }
    artifact, error = _load_json(path)
    if artifact is None:
        return {
            **base,
            "artifact_status": "unreadable_json",
            "review_status": "blocked",
            "reason": error,
            "rtx_phase_sec": None,
            "source_commit": None,
        }
    if row["app"] == "facility_knn_assignment":
        status, reason, phase_sec = _validate_facility(row, artifact)
    elif row["app"] == "barnes_hut_force_app":
        status, reason, phase_sec = _validate_barnes(row, artifact)
    else:
        status, reason, phase_sec = "blocked", f"unexpected app {row['app']}", None
    return {
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


def build_intake(artifact_root: Path = DEFAULT_ARTIFACT_ROOT) -> dict[str, Any]:
    facility_packet = build_facility_packet()
    barnes_packet = build_barnes_packet()
    packet_rows = [
        {**row, "packet_goal": facility_packet["goal"]} for row in facility_packet["rows"]
    ] + [
        {**row, "packet_goal": barnes_packet["goal"]} for row in barnes_packet["rows"]
    ]
    rows = [_review_row(row, artifact_root) for row in packet_rows]

    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row["review_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    missing_count = status_counts.get("needs_cloud_artifact", 0)
    blocked_count = status_counts.get("blocked", 0)
    timing_below = status_counts.get("timing_below_floor", 0)
    all_expected_present = missing_count == 0
    all_evidence_passed = (
        status_counts.get("validation_and_timing_passed", 0) == 1
        and status_counts.get("validation_passed", 0) == 1
        and status_counts.get("timing_floor_passed", 0) == 1
    )
    overall_status = (
        "blocked"
        if blocked_count
        else "ready_for_2ai_review_not_public_claim"
        if all_expected_present and all_evidence_passed
        else "timing_floor_not_met"
        if all_expected_present and timing_below > 0
        else "needs_cloud_artifacts"
    )
    return {
        "goal": GOAL,
        "date": DATE,
        "artifact_root": str(artifact_root),
        "expected_artifact_count": len(rows),
        "present_artifact_count": len(rows) - missing_count,
        "missing_artifact_count": missing_count,
        "blocked_count": blocked_count,
        "timing_below_floor_count": timing_below,
        "status_counts": status_counts,
        "overall_status": overall_status,
        "public_speedup_claim_authorized_count": 0,
        "source_packets": [
            "docs/reports/goal1084_facility_recentered_rtx_pod_packet_2026-04-29.json",
            "docs/reports/goal1093_barnes_hut_20m_contract_packet_2026-04-29.json",
        ],
        "rows": rows,
        "valid": blocked_count == 0,
        "boundary": (
            "This intake checks copied Goal1084 and Goal1093 artifacts only. It does not run cloud, "
            "does not change public wording, does not authorize release, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1096 Current RTX Pod Artifact Intake",
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
        f"- blocked rows: `{payload['blocked_count']}`",
        f"- timing below floor: `{payload['timing_below_floor_count']}`",
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


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake copied current RTX pod artifacts.")
    parser.add_argument("--artifact-root", type=Path, default=DEFAULT_ARTIFACT_ROOT)
    parser.add_argument("--output-json", default="docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.json")
    parser.add_argument("--output-md", default="docs/reports/goal1096_current_rtx_pod_artifact_intake_2026-04-29.md")
    args = parser.parse_args()
    payload = build_intake(args.artifact_root)
    (ROOT / args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / args.output_md).write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"overall_status": payload["overall_status"], "valid": payload["valid"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
