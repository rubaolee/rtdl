#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-29"
GOAL = "Goal1136 changed-path RTX pod artifact intake"
DEFAULT_INPUT_DIR = ROOT / "docs" / "reports" / "goal1135_changed_path_rtx_pod"


EXPECTED = {
    "bootstrap_goal1135.json": ("ok", None),
    "database_analytics_compact_summary.json": ("ok", None),
    "graph_visibility_edges_gate.json": ("pass", True),
    "road_hazard_native_summary_count.json": ("pass", True),
    "polygon_pair_overlap_phase_gate.json": ("pass", None),
    "polygon_set_jaccard_phase_gate.json": ("pass", None),
    "hausdorff_threshold_phase_gate.json": (None, None),
}


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nested(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    value: Any = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
    return value


def _status(data: dict[str, Any]) -> str | None:
    if "status" in data:
        return str(data["status"])
    results = data.get("results")
    if isinstance(results, list) and results and isinstance(results[0], dict):
        value = results[0].get("status")
        return None if value is None else str(value)
    return None


def _review_artifact(name: str, input_dir: Path) -> dict[str, Any]:
    expected_status, expected_strict = EXPECTED[name]
    path = input_dir / name
    row: dict[str, Any] = {
        "artifact": name,
        "path": str(path),
        "exists": path.exists(),
        "valid": False,
        "findings": [],
    }
    if not path.exists():
        row["findings"].append("missing_artifact")
        return row

    data = _load(path)
    status = _status(data)
    strict_pass = data.get("strict_pass")
    row.update(
        {
            "status": status,
            "strict_pass": strict_pass,
            "copies": data.get("copies") or _nested(data, ("parameters", "copies")),
            "schema_version": data.get("schema_version"),
        }
    )
    if expected_status is not None and status != expected_status:
        row["findings"].append(f"unexpected_status:{status}")
    if expected_strict is not None and strict_pass is not expected_strict:
        row["findings"].append(f"unexpected_strict_pass:{strict_pass}")

    if name == "database_analytics_compact_summary.json":
        result = data.get("results", [{}])[0]
        native = result.get("reported_native_db_phase_totals_sec", {})
        if result.get("output_mode") != "compact_summary":
            row["findings"].append("db_not_compact_summary")
        if native.get("counter_status") != "exported":
            row["findings"].append("db_native_counters_not_exported")
        if result.get("reported_run_phase_totals_sec", {}).get("row_materializing_operation_count") != 0:
            row["findings"].append("db_row_materializing_operations_present")
        row["warm_query_median_sec"] = result.get("prepared_session_warm_query_sec", {}).get("median_sec")
        row["native_traversal_sec"] = native.get("traversal_sec")

    if name == "hausdorff_threshold_phase_gate.json":
        if data.get("schema_version") != "goal887_prepared_decision_phase_contract_v1":
            row["findings"].append("hausdorff_unexpected_schema")
        if _nested(data, ("scenario", "result", "matches_oracle")) is not True:
            row["findings"].append("hausdorff_oracle_not_matched")
        if _nested(data, ("scenario", "mode")) != "optix":
            row["findings"].append("hausdorff_not_optix")
        row["claim_boundary"] = "capability_phase_only_not_speedup_claim"
        row["optix_query_median_sec"] = _nested(data, ("scenario", "timings_sec", "optix_query_sec", "median_sec"))

    row["valid"] = not row["findings"]
    return row


def build_intake(input_dir: Path = DEFAULT_INPUT_DIR) -> dict[str, Any]:
    rows = [_review_artifact(name, input_dir) for name in sorted(EXPECTED)]
    log_dir = input_dir / "logs"
    expected_logs = {
        "database_analytics_compact_summary.log",
        "graph_visibility_edges_gate.log",
        "graph_visibility_edges_gate_rerun.log",
        "road_hazard_native_summary_count.log",
        "polygon_pair_overlap_phase_gate.log",
        "polygon_set_jaccard_phase_gate.log",
        "hausdorff_threshold_phase_gate.log",
    }
    present_logs = sorted(p.name for p in log_dir.glob("*.log")) if log_dir.exists() else []
    missing_logs = sorted(expected_logs.difference(present_logs))
    valid = all(row["valid"] for row in rows) and not missing_logs
    return {
        "goal": GOAL,
        "date": DATE,
        "input_dir": str(input_dir),
        "artifact_count": len(rows),
        "valid_artifact_count": sum(1 for row in rows if row["valid"]),
        "missing_logs": missing_logs,
        "valid": valid,
        "rows": rows,
        "boundary": (
            "This intake checks copied Goal1135 changed-path RTX artifacts only. "
            "It does not authorize public RTX speedup claims, release, or broad whole-app acceleration claims."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1136 Changed-Path RTX Pod Artifact Intake",
        "",
        f"Date: {payload['date']}",
        "",
        f"Valid: `{str(payload['valid']).lower()}`",
        "",
        payload["boundary"],
        "",
        "## Artifacts",
        "",
        "| Artifact | Status | Strict | Copies | Valid | Findings |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        findings = ", ".join(row["findings"])
        lines.append(
            f"| `{row['artifact']}` | `{row.get('status')}` | `{row.get('strict_pass')}` | "
            f"`{row.get('copies')}` | `{row['valid']}` | {findings} |"
        )
    lines.extend(["", "## Logs", ""])
    if payload["missing_logs"]:
        lines.append(f"Missing logs: `{payload['missing_logs']}`")
    else:
        lines.append("All expected replay logs are present.")
    lines.extend(["", "## Boundary", "", payload["boundary"], ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intake copied Goal1135 changed-path RTX pod artifacts.")
    parser.add_argument("--input-dir", type=Path, default=DEFAULT_INPUT_DIR)
    parser.add_argument(
        "--output-json",
        type=Path,
        default=ROOT / "docs/reports/goal1136_changed_path_rtx_pod_artifact_intake_2026-04-29.json",
    )
    parser.add_argument(
        "--output-md",
        type=Path,
        default=ROOT / "docs/reports/goal1136_changed_path_rtx_pod_artifact_intake_2026-04-29.md",
    )
    args = parser.parse_args(argv)
    payload = build_intake(args.input_dir)
    args.output_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    args.output_md.write_text(to_markdown(payload), encoding="utf-8")
    print(json.dumps({"valid": payload["valid"], "valid_artifact_count": payload["valid_artifact_count"]}, sort_keys=True))
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
