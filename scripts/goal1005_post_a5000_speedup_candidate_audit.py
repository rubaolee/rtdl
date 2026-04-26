#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import tarfile
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts.goal971_post_goal969_baseline_speedup_review_package import build_package
from scripts.goal978_rtx_speedup_claim_candidate_audit import (
    INTERNAL_ONLY,
    NEEDS_TIMING,
    REJECT,
    RTX_CANDIDATE,
    _baseline_rows,
    _load_json,
    _positive_number,
)
import rtdsl as rt


GOAL = "Goal1005 post-A5000 speedup candidate audit"
DATE = "2026-04-26"
SUMMARY = ROOT / "docs" / "reports" / "cloud_2026_04_26" / "goal1003_rtx_a5000_final_merged_summary_2026-04-26.json"
BUNDLE = ROOT / "docs" / "reports" / "cloud_2026_04_26" / "goal1003_rtx_a5000_artifacts_with_report_2026-04-26-v2.tgz"
EXPECTED_COMMIT = "914122ecd2f2c73f6a51ec2d5b04ca3d575d5681"


def _median(value: Any) -> float | None:
    if isinstance(value, dict):
        return _positive_number(value.get("median_sec"))
    return _positive_number(value)


def _artifact_path(row: dict[str, Any]) -> str:
    command = row.get("result", {}).get("command", [])
    if not isinstance(command, list):
        raise ValueError(f"missing command for {row.get('app')} / {row.get('path_name')}")
    for index, token in enumerate(command):
        if token == "--output-json" and index + 1 < len(command):
            return str(command[index + 1])
    raise ValueError(f"missing --output-json for {row.get('app')} / {row.get('path_name')}")


def _load_bundle_json(bundle: Path, artifact_path: str) -> dict[str, Any]:
    with tarfile.open(bundle) as archive:
        member = archive.extractfile(artifact_path)
        if member is None:
            raise FileNotFoundError(artifact_path)
        return json.load(member)


def _find_result(artifact: dict[str, Any], app: str) -> dict[str, Any]:
    results = artifact.get("results")
    if isinstance(results, list):
        for result in results:
            if isinstance(result, dict) and result.get("app") == app:
                return result
        if len(results) == 1 and isinstance(results[0], dict):
            return results[0]
        raise ValueError(f"artifact has multiple results but none match app {app!r}")
    return artifact


def _rtx_phase_seconds(app: str, path_name: str, artifact: dict[str, Any]) -> tuple[str, float | None]:
    selected = _find_result(artifact, app)

    phases = artifact.get("phases")
    if isinstance(phases, dict) and "prepared_pose_flags_warm_query_sec" in phases:
        return "prepared_pose_flags_warm_query_sec.median_sec", _median(
            phases.get("prepared_pose_flags_warm_query_sec")
        )

    value = selected.get("prepared_optix_warm_query_sec")
    if value is not None:
        return "prepared_optix_warm_query_sec.median_sec", _median(value)

    value = selected.get("prepared_session_warm_query_sec")
    if value is not None:
        return "prepared_session_warm_query_sec.median_sec", _median(value)

    scenario = artifact.get("scenario")
    if isinstance(scenario, dict):
        timings = scenario.get("timings_sec")
        if isinstance(timings, dict) and "optix_query" in timings:
            return "scenario.timings_sec.optix_query", _median(timings.get("optix_query"))
        if isinstance(timings, dict) and "optix_query_sec" in timings:
            return "scenario.timings_sec.optix_query_sec", _median(timings.get("optix_query_sec"))

    timings = artifact.get("timings_sec")
    if isinstance(timings, dict) and "optix_query_sec" in timings:
        return "timings_sec.optix_query_sec", _median(timings.get("optix_query_sec"))

    records = artifact.get("records")
    if isinstance(records, list):
        preferred = {
            "graph_visibility_edges_gate": "optix_visibility_anyhit",
        }.get(path_name)
        for record in records:
            if isinstance(record, dict) and record.get("label") == preferred:
                return f"records.{preferred}.sec", _positive_number(record.get("sec"))
        timed = [
            _positive_number(record.get("sec"))
            for record in records
            if isinstance(record, dict) and str(record.get("label", "")).startswith("optix")
        ]
        timed = [item for item in timed if item is not None]
        if timed:
            return "records.optix*.sec.max", max(timed)

    phases = artifact.get("phases")
    if isinstance(phases, dict) and "optix_candidate_discovery_sec" in phases:
        return "phases.optix_candidate_discovery_sec", _positive_number(
            phases.get("optix_candidate_discovery_sec")
        )

    return "unavailable", None


def _classify(rtx_sec: float | None, baseline_complete: bool, artifact_status: str, baselines: list[dict[str, Any]]) -> dict[str, Any]:
    valid_times = [item for item in baselines if item["phase_sec"] is not None]
    missing_times = [item for item in baselines if item["phase_sec"] is None]

    if artifact_status != "ok" or not baseline_complete:
        return {
            "recommendation": "not_ready",
            "reason": "RTX artifact or same-semantics baseline set is not complete.",
            "fastest_baseline": None,
            "fastest_baseline_sec": None,
            "fastest_ratio_baseline_over_rtx": None,
            "warnings": [],
        }
    if rtx_sec is None:
        return {
            "recommendation": NEEDS_TIMING,
            "reason": "Final A5000 artifact has no positive comparable query/native phase.",
            "fastest_baseline": None,
            "fastest_baseline_sec": None,
            "fastest_ratio_baseline_over_rtx": None,
            "warnings": [],
        }
    if not valid_times:
        return {
            "recommendation": NEEDS_TIMING,
            "reason": "No non-OptiX same-semantics baseline exposes a positive comparable phase.",
            "fastest_baseline": None,
            "fastest_baseline_sec": None,
            "fastest_ratio_baseline_over_rtx": None,
            "warnings": [f"{item['baseline']} lacks comparable timing" for item in missing_times],
        }

    fastest = min(valid_times, key=lambda item: float(item["phase_sec"]))
    fastest_sec = float(fastest["phase_sec"])
    ratio = fastest_sec / rtx_sec
    warnings: list[str] = []
    if rtx_sec < 0.01:
        warnings.append("RTX phase is shorter than 10 ms; public wording needs larger-scale repeat evidence.")
    if missing_times:
        warnings.extend(f"{item['baseline']} lacks comparable timing" for item in missing_times)

    if ratio >= 1.20:
        recommendation = RTX_CANDIDATE if not missing_times else INTERNAL_ONLY
        reason = (
            "RTX query/native phase is at least 20% faster than every timed non-OptiX same-semantics baseline; "
            "separate 2-AI review is still required."
            if not missing_times
            else "RTX is faster than timed baselines, but at least one required baseline lacks comparable timing."
        )
    elif ratio >= 1.0:
        recommendation = INTERNAL_ONLY
        reason = "RTX is not slower than the fastest baseline, but the margin is below the 20% candidate threshold."
    else:
        recommendation = REJECT
        reason = "RTX is slower than the fastest non-OptiX same-semantics baseline in current final A5000 evidence."

    return {
        "recommendation": recommendation,
        "reason": reason,
        "fastest_baseline": fastest["baseline"],
        "fastest_baseline_sec": fastest_sec,
        "fastest_ratio_baseline_over_rtx": ratio,
        "warnings": warnings,
    }


def _baseline_index() -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (str(row["app"]), str(row["path_name"])): row
        for row in build_package()["rows"]
    }


def build_audit(summary_path: Path = SUMMARY, bundle_path: Path = BUNDLE) -> dict[str, Any]:
    summary = _load_json(summary_path)
    baseline_by_key = _baseline_index()
    rows: list[dict[str, Any]] = []

    for source_row in summary["results"]:
        app = str(source_row["app"])
        path_name = str(source_row["path_name"])
        artifact_rel = _artifact_path(source_row)
        artifact = _load_bundle_json(bundle_path, artifact_rel)
        rtx_phase_key, rtx_sec = _rtx_phase_seconds(app, path_name, artifact)
        baseline_row = baseline_by_key[(app, path_name)]
        baselines = _baseline_rows(baseline_row)
        decision = _classify(
            rtx_sec,
            bool(baseline_row.get("baseline_complete_for_speedup_review")),
            str(source_row.get("result", {}).get("status")),
            baselines,
        )
        public_wording = rt.rtx_public_wording_status(app)
        rows.append(
            {
                "app": app,
                "path_name": path_name,
                "claim_scope": source_row.get("claim_scope"),
                "non_claim": source_row.get("non_claim"),
                "artifact_path": artifact_rel,
                "rtx_phase_key": rtx_phase_key,
                "rtx_native_or_query_phase_sec": rtx_sec,
                "rtx_artifact_status": source_row.get("result", {}).get("status"),
                "baseline_status": baseline_row.get("baseline_status"),
                "baseline_complete_for_speedup_review": baseline_row.get("baseline_complete_for_speedup_review"),
                "public_speedup_claim_authorized": False,
                "current_public_wording_status": public_wording.status,
                "current_public_wording_boundary": public_wording.boundary,
                "recommendation": decision["recommendation"],
                "reason": decision["reason"],
                "fastest_baseline": decision["fastest_baseline"],
                "fastest_baseline_sec": decision["fastest_baseline_sec"],
                "fastest_ratio_baseline_over_rtx": decision["fastest_ratio_baseline_over_rtx"],
                "warnings": decision["warnings"],
                "timed_non_optix_baselines": [item for item in baselines if item["phase_sec"] is not None],
                "untimed_non_optix_baselines": [item for item in baselines if item["phase_sec"] is None],
            }
        )

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["recommendation"]] = counts.get(row["recommendation"], 0) + 1

    return {
        "goal": GOAL,
        "date": DATE,
        "summary_path": str(summary_path.relative_to(ROOT)),
        "bundle_path": str(bundle_path.relative_to(ROOT)),
        "source_commit": summary.get("git_head") or summary.get("source_commit"),
        "source_is_final_a5000_v2": summary.get("status") == "ok"
        and summary.get("failed_count") == 0
        and summary.get("entry_count") == 17
        and summary.get("dry_run") is False
        and "NVIDIA RTX A5000" in str(summary.get("nvidia_smi", "")),
        "row_count": len(rows),
        "recommendation_counts": counts,
        "current_public_wording_source": "rtdsl.rtx_public_wording_matrix()",
        "candidate_count": counts.get(RTX_CANDIDATE, 0),
        "internal_only_count": counts.get(INTERNAL_ONLY, 0),
        "reject_count": counts.get(REJECT, 0),
        "needs_timing_repair_count": counts.get(NEEDS_TIMING, 0),
        "public_speedup_claim_authorized_count": 0,
        "rows": rows,
        "boundary": (
            "Goal1005 classifies speedup-claim candidates from the final Goal1004 RTX A5000 v2 artifacts. "
            "It does not authorize public speedup claims; it only identifies rows that may deserve later "
            "2-AI public-claim review or rows that should be rejected/kept internal under current evidence."
        ),
    }


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.6f}"
    if value is None:
        return ""
    return str(value)


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1005 Post-A5000 Speedup Candidate Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- source final A5000 v2 evidence: `{payload['source_is_final_a5000_v2']}`",
        f"- rows audited: `{payload['row_count']}`",
        f"- candidate rows for later 2-AI public-claim review: `{payload['candidate_count']}`",
        f"- internal-only rows: `{payload['internal_only_count']}`",
        f"- rejected current public speedup rows: `{payload['reject_count']}`",
        f"- public speedup claims authorized here: `{payload['public_speedup_claim_authorized_count']}`",
        f"- recommendation counts: `{payload['recommendation_counts']}`",
        "",
        "## App/Path Decisions",
        "",
        "| App | Path | RTX phase key | RTX phase (s) | Fastest non-OptiX baseline | Ratio | Recommendation | Current public wording |",
        "|---|---|---|---:|---|---:|---|---|",
    ]
    for row in payload["rows"]:
        baseline = row["fastest_baseline"] or ""
        baseline_sec = row["fastest_baseline_sec"]
        baseline_text = f"`{baseline}` {_fmt(baseline_sec)}" if baseline else ""
        lines.append(
            f"| `{row['app']}` | `{row['path_name']}` | `{row['rtx_phase_key']}` | "
            f"{_fmt(row['rtx_native_or_query_phase_sec'])} | {baseline_text} | "
            f"{_fmt(row['fastest_ratio_baseline_over_rtx'])} | `{row['recommendation']}` | "
            f"`{row['current_public_wording_status']}` |"
        )
    lines.extend(
        [
            "",
            "## Current Public Wording Source-Of-Truth",
            "",
            "Release-facing wording must follow `rtdsl.rtx_public_wording_matrix()` rather than this candidate audit alone.",
            "",
            "## Boundary",
            "",
            payload["boundary"],
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit final A5000 artifacts against same-semantics baselines.")
    parser.add_argument("--summary", default=str(SUMMARY))
    parser.add_argument("--bundle", default=str(BUNDLE))
    parser.add_argument("--output-json", default="docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.json")
    parser.add_argument("--output-md", default="docs/reports/goal1005_post_a5000_speedup_candidate_audit_2026-04-26.md")
    args = parser.parse_args()
    payload = build_audit(Path(args.summary), Path(args.bundle))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md = to_markdown(payload)
    Path(args.output_md).write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0 if payload["source_is_final_a5000_v2"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
