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


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _output_path(command: list[str]) -> Path | None:
    for index, token in enumerate(command):
        if token == "--output-json" and index + 1 < len(command):
            return ROOT / command[index + 1]
    return None


def _median(stats: Any) -> float | None:
    if isinstance(stats, dict) and isinstance(stats.get("median_sec"), (int, float)):
        return float(stats["median_sec"])
    return None


def _find_result_for_app(payload: dict[str, Any], app: str) -> dict[str, Any] | None:
    results = payload.get("results")
    if not isinstance(results, list):
        return None
    for result in results:
        if isinstance(result, dict) and result.get("app") == app:
            return result
    return None


def _extract_artifact_metrics(entry: dict[str, Any], artifact: dict[str, Any]) -> dict[str, Any]:
    app = str(entry["app"])
    if app == "database_analytics":
        results = artifact.get("results")
        optix = None
        if isinstance(results, list):
            optix = next((row for row in results if isinstance(row, dict) and row.get("backend") == "optix"), None)
        if not isinstance(optix, dict):
            return {"artifact_status": "unrecognized", "note": "no optix result row found"}
        return {
            "artifact_status": "ok",
            "one_shot_total_sec": optix.get("one_shot_total_sec"),
            "prepare_total_sec": optix.get("prepared_session_prepare_total_sec"),
            "warm_query_median_sec": _median(optix.get("prepared_session_warm_query_sec")),
            "close_sec": optix.get("prepared_session_close_sec"),
            "speedup_one_shot_over_warm_query_median": optix.get("speedup_one_shot_over_warm_query_median"),
            "phase_contract_present": isinstance(optix.get("phase_contract"), dict),
        }
    if app in {"outlier_detection", "dbscan_clustering"}:
        result = _find_result_for_app(artifact, app)
        if result is None:
            return {"artifact_status": "unrecognized", "note": f"no {app} result row found"}
        return {
            "artifact_status": "ok",
            "one_shot_total_sec": result.get("one_shot_total_sec"),
            "prepare_sec": result.get("prepared_optix_prepare_sec"),
            "warm_query_median_sec": _median(result.get("prepared_optix_warm_query_sec")),
            "postprocess_median_sec": _median(result.get("prepared_optix_postprocess_sec")),
            "validation_median_sec": _median(result.get("prepared_optix_validation_sec")),
            "validation_mode": result.get("validation_mode"),
            "speedup_one_shot_over_warm_query_median": result.get("speedup_one_shot_over_warm_query_median"),
            "phase_contract_present": isinstance(result.get("phase_contract"), dict),
        }
    if app == "robot_collision_screening":
        phases = artifact.get("phases")
        if not isinstance(phases, dict):
            return {"artifact_status": "unrecognized", "note": "no phases object found"}
        return {
            "artifact_status": "ok",
            "mode": artifact.get("mode"),
            "input_mode": artifact.get("input_mode"),
            "result_mode": artifact.get("result_mode"),
            "pose_count": artifact.get("pose_count"),
            "edge_ray_count": artifact.get("edge_ray_count"),
            "colliding_pose_count": (artifact.get("result") or {}).get("colliding_pose_count")
            if isinstance(artifact.get("result"), dict)
            else None,
            "prepare_scene_sec": phases.get("optix_prepare_scene_sec"),
            "prepare_rays_sec": phases.get("optix_prepare_rays_sec"),
            "prepare_pose_indices_sec": phases.get("optix_prepare_pose_indices_sec"),
            "warm_query_median_sec": _median(phases.get("prepared_pose_flags_warm_query_sec")),
            "oracle_validate_sec": phases.get("oracle_validate_sec"),
            "matches_oracle": artifact.get("matches_oracle"),
            "validated": artifact.get("validated"),
        }
    return {"artifact_status": "not_applicable", "note": "no extractor for app"}


def analyze(summary_path: Path) -> dict[str, Any]:
    summary = _load_json(summary_path)
    rows: list[dict[str, Any]] = []
    for item in summary.get("results", []):
        if not isinstance(item, dict):
            continue
        result = item.get("result", {})
        command = result.get("command", []) if isinstance(result, dict) else []
        artifact_path = _output_path(command) if isinstance(command, list) else None
        row = {
            "app": item.get("app"),
            "path_name": item.get("path_name"),
            "claim_scope": item.get("claim_scope"),
            "non_claim": item.get("non_claim"),
            "runner_status": result.get("status") if isinstance(result, dict) else "unknown",
            "runner_returncode": result.get("returncode") if isinstance(result, dict) else None,
            "artifact_path": str(artifact_path) if artifact_path is not None else None,
        }
        if row["runner_status"] == "dry_run":
            row["artifact_status"] = "dry_run_not_expected"
        elif artifact_path is None:
            row["artifact_status"] = "missing_output_json_argument"
        elif not artifact_path.exists():
            row["artifact_status"] = "missing"
        else:
            try:
                artifact = _load_json(artifact_path)
                row.update(_extract_artifact_metrics(item, artifact))
            except Exception as exc:
                row["artifact_status"] = "parse_failed"
                row["note"] = str(exc)
        rows.append(row)
    failures = [
        row for row in rows
        if row.get("runner_status") not in {"ok", "dry_run"}
        or row.get("artifact_status") in {"missing", "parse_failed", "unrecognized", "missing_output_json_argument"}
    ]
    return {
        "suite": "goal762_rtx_cloud_artifact_report",
        "summary_path": str(summary_path),
        "runner_status": summary.get("status"),
        "dry_run": bool(summary.get("dry_run")),
        "git_head": summary.get("git_head"),
        "nvidia_smi": summary.get("nvidia_smi"),
        "entry_count": len(rows),
        "failure_count": len(failures),
        "rows": rows,
        "status": "ok" if not failures else "needs_attention",
        "boundary": (
            "This report checks cloud artifacts and summarizes phase metrics. It does not authorize RTX speedup claims; "
            "claims require human/AI review of correctness, phase separation, hardware metadata, and comparison baselines."
        ),
    }


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal762 RTX Cloud Artifact Report",
        "",
        "## Verdict",
        "",
        f"Status: `{payload['status']}`.",
        "",
        payload["boundary"],
        "",
        "## Run Metadata",
        "",
        f"- summary_path: `{payload['summary_path']}`",
        f"- runner_status: `{payload.get('runner_status')}`",
        f"- dry_run: `{payload.get('dry_run')}`",
        f"- git_head: `{payload.get('git_head')}`",
        f"- failure_count: `{payload.get('failure_count')}`",
        "",
        "## Artifact Table",
        "",
        "| App | Path | Runner | Artifact | Warm query median (s) | Postprocess median (s) | Validation / oracle (s) | Non-claim |",
        "|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for row in payload["rows"]:
        validation = row.get("validation_median_sec", row.get("oracle_validate_sec"))
        lines.append(
            "| "
            + " | ".join(
                [
                    _fmt(row.get("app")),
                    _fmt(row.get("path_name")),
                    _fmt(row.get("runner_status")),
                    _fmt(row.get("artifact_status")),
                    _fmt(row.get("warm_query_median_sec")),
                    _fmt(row.get("postprocess_median_sec")),
                    _fmt(validation),
                    _fmt(row.get("non_claim")),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "## Required Review",
            "",
            "- Confirm the machine is RTX-class and `nvidia-smi` metadata matches the intended cloud resource.",
            "- Confirm all `artifact_status` cells are `ok` before interpreting timings.",
            "- Compare against explicit baselines separately; this report intentionally does not compute public speedup claims.",
            "- Keep DB, fixed-radius summary, and robot pose-flag claim scopes separate.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Analyze Goal761 RTX cloud artifacts and write a conservative report.")
    parser.add_argument("--summary-json", default="docs/reports/goal761_rtx_cloud_run_all_summary.json")
    parser.add_argument("--output-json")
    parser.add_argument("--output-md", default="docs/reports/goal762_rtx_cloud_artifact_report.md")
    args = parser.parse_args(argv)
    payload = analyze(ROOT / args.summary_json)
    if args.output_json:
        Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    if args.output_md:
        Path(args.output_md).write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0 if payload["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
