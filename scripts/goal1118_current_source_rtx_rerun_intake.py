#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1118 current-source RTX rerun intake"
DEFAULT_PACKET = ROOT / "docs/reports/goal1116_current_source_rtx_rerun_packet_2026-04-29.json"
DEFAULT_INPUT_DIR = ROOT / "docs/reports/goal1116_current_source_rtx_rerun_packet"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict) or key not in value:
            return None
        value = value[key]
    return value


def _median_query_sec(app: str, data: dict[str, Any]) -> float | None:
    if app == "robot_collision_screening":
        value = _nested(data, ("phases", "prepared_pose_flags_warm_query_sec", "median_sec"))
    else:
        value = _nested(data, ("scenario", "timings_sec", "optix_query_sec", "median_sec"))
    return None if value is None else float(value)


def _matches_oracle(app: str, data: dict[str, Any]) -> bool | None:
    if app == "robot_collision_screening":
        value = data.get("matches_oracle")
    else:
        value = _nested(data, ("scenario", "result", "matches_oracle"))
    return None if value is None else bool(value)


def _mode(app: str, data: dict[str, Any]) -> str | None:
    if app == "robot_collision_screening":
        value = data.get("mode")
    else:
        value = _nested(data, ("scenario", "mode"))
    return None if value is None else str(value)


def _source_commit(data: dict[str, Any]) -> str | None:
    value = data.get("source_commit")
    return None if value is None else str(value)


def _validate_row(row: dict[str, Any], *, input_dir: Path) -> dict[str, Any]:
    output_name = Path(str(row["output_json"])).name
    path = input_dir / output_name
    result: dict[str, Any] = {
        "app": row["app"],
        "path_name": row["path_name"],
        "phase": row["phase"],
        "output_json": str(path),
        "exists": path.exists(),
        "valid": False,
        "findings": [],
    }
    if not path.exists():
        result["findings"].append("missing_output_json")
        return result

    data = _load_json(path)
    result["source_commit"] = _source_commit(data)
    result["mode"] = _mode(row["app"], data)
    result["matches_oracle"] = _matches_oracle(row["app"], data)
    result["median_query_sec"] = _median_query_sec(row["app"], data)

    if not result["source_commit"]:
        result["findings"].append("missing_source_commit")
    if result["mode"] != "optix":
        result["findings"].append("not_optix_mode")
    if row["requires_validation"] and result["matches_oracle"] is not True:
        result["findings"].append("validation_did_not_match_oracle")
    if row["contains_skip_validation"] and result["matches_oracle"] is not None:
        result["findings"].append("timing_row_claimed_oracle_match")
    floor = row["timing_floor_sec"]
    if floor is not None:
        if result["median_query_sec"] is None:
            result["findings"].append("missing_median_query_sec")
        elif float(result["median_query_sec"]) < float(floor):
            result["findings"].append("median_query_below_timing_floor")

    result["valid"] = not result["findings"]
    return result


def build_intake(*, packet_path: Path = DEFAULT_PACKET, input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    packet = _load_json(packet_path)
    rows = [_validate_row(row, input_dir=input_dir) for row in packet["rows"]]
    runner_log = input_dir / "goal1116_runner.log"
    source_commits = sorted({row.get("source_commit") for row in rows if row.get("source_commit")})
    rows_valid = all(row["valid"] for row in rows)
    same_source_commit = len(source_commits) == 1
    runner_log_exists = runner_log.exists()
    public_speedup_claim_authorized = False
    valid = rows_valid and same_source_commit and runner_log_exists and not public_speedup_claim_authorized
    return {
        "goal": GOAL,
        "date": DATE,
        "packet": str(packet_path),
        "input_dir": str(input_dir),
        "rows": rows,
        "summary": {
            "row_count": len(rows),
            "valid_row_count": sum(1 for row in rows if row["valid"]),
            "missing_row_count": sum(1 for row in rows if not row["exists"]),
            "source_commits": source_commits,
            "same_source_commit": same_source_commit,
            "runner_log_exists": runner_log_exists,
            "public_speedup_claim_authorized": public_speedup_claim_authorized,
        },
        "valid": valid,
        "boundary": (
            "Goal1118 intakes Goal1116 current-source RTX rerun artifacts. It does not run cloud, "
            "does not authorize release, does not change public wording, and does not authorize public RTX speedup claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1118 Current-Source RTX Rerun Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "| --- | ---: |",
    ]
    for key, value in payload["summary"].items():
        lines.append(f"| `{key}` | `{value}` |")
    lines.extend(
        [
            "",
            "## Rows",
            "",
            "| App | Phase | Exists | Valid | Source commit | Median query sec | Findings |",
            "| --- | --- | --- | --- | --- | ---: | --- |",
        ]
    )
    for row in payload["rows"]:
        findings = ", ".join(row["findings"])
        median = "" if row.get("median_query_sec") is None else f"{float(row['median_query_sec']):.6f}"
        lines.append(
            f"| `{row['app']}` | `{row['phase']}` | `{row['exists']}` | `{row['valid']}` | "
            f"`{row.get('source_commit', '')}` | `{median}` | {findings} |"
        )
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake Goal1116 current-source RTX rerun artifacts.")
    parser.add_argument("--packet-json", type=Path, default=DEFAULT_PACKET)
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument("--output-json", type=Path, default=ROOT / "docs/reports/goal1118_current_source_rtx_rerun_intake_2026-04-29.json")
    parser.add_argument("--output-md", type=Path, default=ROOT / "docs/reports/goal1118_current_source_rtx_rerun_intake_2026-04-29.md")
    args = parser.parse_args(argv)
    payload = build_intake(packet_path=args.packet_json, input_dir=args.input_dir)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], **payload["summary"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
