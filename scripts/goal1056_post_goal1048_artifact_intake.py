#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal1052_post_goal1048_cloud_batch_manifest import build_manifest


DATE = "2026-04-28"
GOAL = "Goal1056 post-Goal1048 artifact intake"
DEFAULT_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal1052_post_goal1048_cloud_batch"


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # pragma: no cover - exercised through status fields
        return None, f"{type(exc).__name__}: {exc}"


def _artifact_path(row: dict[str, Any], artifact_dir: Path) -> Path:
    output_json = row.get("output_json")
    if not isinstance(output_json, str) or not output_json:
        return artifact_dir / f"{row['path_name']}.json"
    return artifact_dir / Path(output_json).name


def _diagnostic_status(row: dict[str, Any], artifact: dict[str, Any]) -> tuple[str, str]:
    app = str(row["app"])
    if row.get("contains_skip_validation"):
        return "blocked", "diagnostic manifest row still contains --skip-validation"
    if app == "facility_knn_assignment":
        if (artifact.get("parameters") or {}).get("skip_validation") is True:
            return "blocked", "facility artifact was collected with skip_validation"
        scenario = artifact.get("scenario")
        if not isinstance(scenario, dict):
            return "blocked", "facility artifact has no scenario object"
        result = scenario.get("result")
        if not isinstance(result, dict):
            return "blocked", "facility artifact has no scenario.result object"
        if scenario.get("mode") != "optix":
            return "blocked", "facility artifact is not optix mode"
        if result.get("matches_oracle") is not True:
            return "blocked", "facility artifact does not prove matches_oracle true"
        return "diagnostic_validated", "facility diagnostic row has optix mode and oracle parity"
    if app == "robot_collision_screening":
        if artifact.get("validated") is not True:
            return "blocked", "robot artifact was not validation-enabled"
        if artifact.get("matches_oracle") is not True:
            return "blocked", "robot artifact does not prove matches_oracle true"
        if artifact.get("mode") != "optix":
            return "blocked", "robot artifact is not optix mode"
        if artifact.get("input_mode") != "python_objects":
            return "blocked", "robot diagnostic artifact must use validation-capable python_objects input"
        if artifact.get("result_mode") != "pose_flags":
            return "blocked", "robot diagnostic artifact must use validation-capable pose_flags result mode"
        return "diagnostic_validated", "robot diagnostic row has optix mode and oracle parity"
    return "candidate_for_review", "not a diagnostic rerun row"


def _source_commit(artifact: dict[str, Any]) -> Any:
    if artifact.get("source_commit"):
        return artifact["source_commit"]
    if artifact.get("RTDL_SOURCE_COMMIT"):
        return artifact["RTDL_SOURCE_COMMIT"]
    environment = artifact.get("environment")
    if isinstance(environment, dict):
        return environment.get("source_commit")
    return None


def build_intake(artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    manifest = build_manifest()
    rows = manifest["diagnostic_validation_reruns"] + manifest["same_semantics_review_candidates"]
    intake_rows: list[dict[str, Any]] = []

    for row in rows:
        path = _artifact_path(row, artifact_dir)
        base = {
            "app": row["app"],
            "path_name": row["path_name"],
            "batch": row["batch"],
            "expected_output_json": row["output_json"],
            "artifact_path": str(path),
            "contains_skip_validation": row["contains_skip_validation"],
            "public_speedup_claim_authorized": False,
        }
        if not path.exists():
            intake_rows.append(
                {
                    **base,
                    "artifact_status": "missing",
                    "review_status": "needs_cloud_artifact",
                    "reason": "expected output JSON has not been copied back from the pod",
                }
            )
            continue
        artifact, error = _load_json(path)
        if artifact is None:
            intake_rows.append(
                {
                    **base,
                    "artifact_status": "unreadable_json",
                    "review_status": "blocked",
                    "reason": error,
                }
            )
            continue
        if row["batch"] == "diagnostic_validation_rerun":
            status, reason = _diagnostic_status(row, artifact)
        else:
            status, reason = "candidate_for_same_semantics_review", "artifact exists; requires separate bounded review"
        intake_rows.append(
            {
                **base,
                "artifact_status": "present",
                "review_status": status,
                "reason": reason,
                "source_commit": _source_commit(artifact),
            }
        )

    status_counts: dict[str, int] = {}
    for row in intake_rows:
        status = str(row["review_status"])
        status_counts[status] = status_counts.get(status, 0) + 1
    missing_count = sum(1 for row in intake_rows if row["artifact_status"] == "missing")
    blocked_count = status_counts.get("blocked", 0)
    diagnostic_validated_count = status_counts.get("diagnostic_validated", 0)
    overall_status = (
        "blocked"
        if blocked_count
        else "ready_for_same_semantics_review"
        if missing_count == 0 and diagnostic_validated_count == 2
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
        "diagnostic_validated_count": diagnostic_validated_count,
        "blocked_count": blocked_count,
        "status_counts": status_counts,
        "overall_status": overall_status,
        "public_speedup_claim_authorized_count": 0,
        "rows": intake_rows,
        "valid": blocked_count == 0,
        "boundary": (
            "This intake checks copied Goal1052 cloud artifacts only. It does not run cloud, "
            "authorize release, or authorize public RTX speedup wording."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1056 Post-Goal1048 Artifact Intake",
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
        f"- diagnostic validated: `{payload['diagnostic_validated_count']}`",
        f"- blocked rows: `{payload['blocked_count']}`",
        f"- public speedup claims authorized: `{payload['public_speedup_claim_authorized_count']}`",
        "",
        "## Rows",
        "",
        "| App | Path | Batch | Artifact | Review status | Reason |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            "| "
            f"`{row['app']}` | "
            f"`{row['path_name']}` | "
            f"`{row['batch']}` | "
            f"`{row['artifact_status']}` | "
            f"`{row['review_status']}` | "
            f"{row['reason']} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1052 post-Goal1048 cloud artifacts.")
    parser.add_argument("--artifact-dir", type=Path, default=DEFAULT_ARTIFACT_DIR)
    parser.add_argument(
        "--output-json",
        default="docs/reports/goal1056_post_goal1048_artifact_intake_2026-04-28.json",
    )
    parser.add_argument(
        "--output-md",
        default="docs/reports/goal1056_post_goal1048_artifact_intake_2026-04-28.md",
    )
    args = parser.parse_args()
    payload = build_intake(args.artifact_dir)
    output_json = ROOT / args.output_json
    output_md = ROOT / args.output_md
    output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"json": str(output_json), "md": str(output_md), "overall_status": payload["overall_status"]}))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
