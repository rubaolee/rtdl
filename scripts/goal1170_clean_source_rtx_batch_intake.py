#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1170 clean-source RTX batch artifact intake"
DEFAULT_INPUT_DIR = ROOT / "docs/reports/goal1170_clean_source_rtx_claim_grade_batch"
DEFAULT_JSON = ROOT / "docs/reports/goal1170_clean_source_rtx_batch_intake_2026-04-30.json"
DEFAULT_MD = ROOT / "docs/reports/goal1170_clean_source_rtx_batch_intake_2026-04-30.md"

EXPECTED = {
    "database_compact_summary.json": {"dirty_allowed": False},
    "graph_visibility_edges.json": {"dirty_allowed": False},
    "road_hazard_native_summary.json": {"dirty_allowed": False},
    "polygon_pair_candidate_discovery.json": {"dirty_allowed": False},
    "polygon_jaccard_safe_chunk.json": {"dirty_allowed": False},
    "hausdorff_threshold_prepared.json": {"dirty_allowed": False},
    "ann_candidate_65536_timing.json": {"dirty_allowed": False, "timing_only": True},
    "robot_pose_count_262144_timing.json": {"dirty_allowed": False, "timing_only": True},
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], *keys: str) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _source_commit(data: dict[str, Any]) -> str:
    value = data.get("source_commit")
    return "" if value is None else str(value)


def _review(path: Path, policy: dict[str, Any]) -> dict[str, Any]:
    row: dict[str, Any] = {
        "artifact": path.name,
        "path": str(path),
        "exists": path.exists(),
        "valid": False,
        "findings": [],
    }
    if not path.exists():
        row["findings"].append("missing_artifact")
        return row
    data = _load(path)
    source_commit = _source_commit(data)
    row["source_commit"] = source_commit
    if "local-dirty" in source_commit and not policy.get("dirty_allowed", False):
        row["findings"].append("dirty_source_marker")
    if policy.get("timing_only"):
        row["timing_only"] = True
        if path.name.startswith("ann_"):
            if _nested(data, "scenario", "result", "matches_oracle") is not None:
                row["findings"].append("ann_timing_row_claims_oracle")
        if path.name.startswith("robot_"):
            if data.get("validated") is not False or data.get("matches_oracle") is not None:
                row["findings"].append("robot_timing_row_claims_validation")
    else:
        row["timing_only"] = False
    row["status"] = data.get("status")
    row["valid"] = not row["findings"]
    return row


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    rows = [_review(input_dir / name, policy) for name, policy in EXPECTED.items()]
    missing = [row["artifact"] for row in rows if not row["exists"]]
    dirty = [row["artifact"] for row in rows if "dirty_source_marker" in row["findings"]]
    valid = all(row["valid"] for row in rows)
    return {
        "goal": GOAL,
        "date": DATE,
        "input_dir": str(input_dir),
        "valid": valid,
        "artifact_count": len(rows),
        "valid_artifact_count": sum(1 for row in rows if row["valid"]),
        "missing_artifacts": missing,
        "dirty_source_artifacts": dirty,
        "rows": rows,
        "boundary": (
            "This intake can accept clean-source Goal1170 RTX artifacts for review. "
            "It does not authorize public wording by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1170 Clean-Source RTX Batch Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        "| Artifact | Exists | Valid | Timing only | Findings |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in payload["rows"]:
        lines.append(
            f"| `{row['artifact']}` | `{row['exists']}` | `{row['valid']}` | "
            f"`{row.get('timing_only')}` | `{row['findings']}` |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake copied Goal1170 clean-source RTX artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--output-md", type=Path, default=DEFAULT_MD)
    args = parser.parse_args(argv)
    payload = build_intake(args.input_dir)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "artifact_count": payload["artifact_count"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
