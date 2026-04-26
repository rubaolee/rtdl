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

from scripts.goal846_active_rtx_claim_gate import build_active_claim_gate


GOAL = "Goal847 active RTX claim review package"
DATE = "2026-04-23"
GOAL762_PATH = ROOT / "docs" / "reports" / "goal762_rtx_cloud_artifact_report_rtx3090_2026-04-23.json"

FIXED_RADIUS_SCOPES = {
    "outlier_detection": {
        "claim_scope": "prepared fixed-radius scalar threshold-count traversal only",
        "non_claim": (
            "not per-point outlier labels, row-returning outputs, broad anomaly detection, "
            "or whole-app speedup"
        ),
    },
    "dbscan_clustering": {
        "claim_scope": "prepared fixed-radius scalar core-count traversal only",
        "non_claim": "not per-point core flags, cluster expansion, full DBSCAN clustering, or whole-app speedup",
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _ratio(baseline_sec: float | None, cloud_sec: float | None) -> float | None:
    if not isinstance(baseline_sec, (int, float)) or not isinstance(cloud_sec, (int, float)):
        return None
    if baseline_sec <= 0.0 or cloud_sec <= 0.0:
        return None
    return float(baseline_sec) / float(cloud_sec)


def _phase_metric_name(app: str) -> str:
    if app == "database_analytics":
        return "native_query"
    if app in {"outlier_detection", "dbscan_clustering"}:
        return "native_threshold_query"
    if app == "robot_collision_screening":
        return "native_anyhit_query"
    raise KeyError(app)


def _cloud_query_seconds(app: str, row: dict[str, Any]) -> float | None:
    value = row.get("warm_query_median_sec")
    return float(value) if isinstance(value, (int, float)) else None


def _claim_scope(app: str, row: dict[str, Any]) -> str | None:
    override = FIXED_RADIUS_SCOPES.get(app)
    if override is not None:
        return override["claim_scope"]
    value = row.get("claim_scope")
    return str(value) if value is not None else None


def _non_claim(app: str, row: dict[str, Any]) -> str | None:
    override = FIXED_RADIUS_SCOPES.get(app)
    if override is not None:
        return override["non_claim"]
    value = row.get("non_claim")
    return str(value) if value is not None else None


def _top_nonquery_phases(app: str, row: dict[str, Any]) -> list[dict[str, float]]:
    phases: list[tuple[str, float]] = []
    if app == "database_analytics":
        for key, label in (
            ("prepare_total_sec", "prepare_total_sec"),
            ("one_shot_total_sec", "one_shot_total_sec"),
            ("close_sec", "close_sec"),
        ):
            value = row.get(key)
            if isinstance(value, (int, float)):
                phases.append((label, float(value)))
        total = row.get("one_shot_total_sec")
        prepare = row.get("prepare_total_sec")
        query = row.get("warm_query_median_sec")
        close = row.get("close_sec")
        if all(isinstance(v, (int, float)) for v in (total, prepare, query, close)):
            residual = float(total) - float(prepare) - float(query) - float(close)
            if residual > 0:
                phases.append(("residual_host_overhead_sec", residual))
    elif app in {"outlier_detection", "dbscan_clustering"}:
        for key, label in (
            ("pack_points_sec", "pack_points_sec"),
            ("postprocess_median_sec", "postprocess_median_sec"),
            ("prepare_sec", "prepare_sec"),
            ("validation_median_sec", "validation_median_sec"),
        ):
            value = row.get(key)
            if isinstance(value, (int, float)):
                phases.append((label, float(value)))
        total = row.get("one_shot_total_sec")
        pack = row.get("pack_points_sec")
        prepare = row.get("prepare_sec")
        query = row.get("warm_query_median_sec")
        post = row.get("postprocess_median_sec")
        validation = row.get("validation_median_sec")
        if all(isinstance(v, (int, float)) for v in (total, pack, prepare, query, post, validation)):
            residual = float(total) - float(pack) - float(prepare) - float(query) - float(post) - float(validation)
            if residual > 0:
                phases.append(("residual_misc_sec", residual))
    elif app == "robot_collision_screening":
        for key, label in (
            ("prepare_scene_sec", "prepare_scene_sec"),
            ("prepare_rays_sec", "prepare_rays_sec"),
            ("prepare_pose_indices_sec", "prepare_pose_indices_sec"),
            ("oracle_validate_sec", "oracle_validate_sec"),
        ):
            value = row.get(key)
            if isinstance(value, (int, float)):
                phases.append((label, float(value)))
    phases.sort(key=lambda item: item[1], reverse=True)
    return [{"phase": name, "seconds": value} for name, value in phases[:4]]


def _row_note(app: str) -> str:
    if app == "database_analytics":
        return (
            "DB review stays bounded to prepared compact-summary semantics. "
            "Warm-query comparison is meaningful, but one-shot totals still include substantial non-query work. "
            "Local Goals850/851 removed grouped row materialization on compact-summary paths; a fresh RTX rerun is still required before that reduction appears in this package."
        )
    if app in {"outlier_detection", "dbscan_clustering"}:
        return (
            "Fixed-radius review stays bounded to prepared scalar-summary semantics. "
            "Optional SciPy/reference baselines remain excluded from the active mandatory gate."
        )
    if app == "robot_collision_screening":
        return (
            "Robot review is bounded to scalar colliding-pose count semantics. "
            "The structured Goal762 row exposes scene/ray/query phases, but not the full Python input phase now described separately in Goal772."
        )
    return ""


def build_review_package() -> dict[str, Any]:
    active_gate = build_active_claim_gate()
    if active_gate["status"] != "ok":
        raise RuntimeError("Goal846 active gate must be green before claim review packaging.")

    goal762 = _load_json(GOAL762_PATH)
    cloud_rows = {
        (str(row["app"]), str(row["path_name"])): row
        for row in goal762["rows"]
    }

    package_rows: list[dict[str, Any]] = []
    missing_cloud_rows: list[dict[str, str]] = []
    for gate_row in active_gate["rows"]:
        app = str(gate_row["app"])
        path_name = str(gate_row["path_name"])
        cloud = cloud_rows.get((app, path_name))
        if cloud is None:
            missing_cloud_rows.append({"app": app, "path_name": path_name})
            continue
        metric_name = _phase_metric_name(app)
        cloud_query_sec = _cloud_query_seconds(app, cloud)
        baselines: list[dict[str, Any]] = []
        for check in gate_row["blocking_checks"]:
            payload = _load_json(Path(str(check["path"])))
            baseline_phase_sec = payload["phase_seconds"].get(metric_name)
            baselines.append(
                {
                    "baseline_name": payload["baseline_name"],
                    "source_backend": payload["source_backend"],
                    "phase_metric_name": metric_name,
                    "baseline_phase_sec": baseline_phase_sec,
                    "cloud_phase_sec": cloud_query_sec,
                    "baseline_over_cloud_ratio": _ratio(baseline_phase_sec, cloud_query_sec),
                    "summary_sha256": payload.get("summary_sha256"),
                }
            )
        package_rows.append(
            {
                "app": app,
                "path_name": path_name,
                "claim_scope": _claim_scope(app, cloud),
                "non_claim": _non_claim(app, cloud),
                "cloud_query_metric_name": metric_name,
                "cloud_query_sec": cloud_query_sec,
                "cloud_artifact_status": cloud.get("artifact_status"),
                "cloud_runner_status": cloud.get("runner_status"),
                "top_nonquery_phases": _top_nonquery_phases(app, cloud),
                "baseline_comparisons": baselines,
                "review_note": _row_note(app),
            }
        )

    return {
        "goal": GOAL,
        "date": DATE,
        "repo": str(ROOT),
        "source_goal846_status": active_gate["status"],
        "source_goal762_status": goal762["status"],
        "row_count": len(package_rows),
        "missing_cloud_row_count": len(missing_cloud_rows),
        "missing_cloud_rows": missing_cloud_rows,
        "rows": package_rows,
        "boundary": (
            "This package is for internal active OptiX claim review only. It compares same-semantics native-query phases "
            "for the active mandatory baseline set and highlights remaining non-query bottlenecks. It does not authorize a public RTX speedup claim."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal847 Active RTX Claim Review Package",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- active rows: `{payload['row_count']}`",
        f"- Goal846 status: `{payload['source_goal846_status']}`",
        f"- Goal762 status: `{payload['source_goal762_status']}`",
        "",
        "## Comparable Native-Phase Table",
        "",
        "| App | Path | Cloud query metric | Cloud query (s) | Fastest baseline | Fastest ratio (baseline/cloud) | Non-claim |",
        "|---|---|---|---:|---|---:|---|",
    ]
    for row in payload["rows"]:
        best = max(
            (
                item for item in row["baseline_comparisons"]
                if isinstance(item.get("baseline_over_cloud_ratio"), (int, float))
            ),
            key=lambda item: float(item["baseline_over_cloud_ratio"]),
            default=None,
        )
        lines.append(
            f"| {row['app']} | {row['path_name']} | {row['cloud_query_metric_name']} | "
            f"{row['cloud_query_sec']:.6f} | "
            f"{'' if best is None else best['baseline_name']} | "
            f"{'' if best is None else f'{best['baseline_over_cloud_ratio']:.3f}'} | "
            f"{row['non_claim']} |"
        )
    for row in payload["rows"]:
        lines.extend(["", f"## {row['app']} / {row['path_name']}", ""])
        lines.append(f"- claim scope: `{row['claim_scope']}`")
        lines.append(f"- cloud comparable phase: `{row['cloud_query_metric_name']}` = `{row['cloud_query_sec']:.6f}s`")
        lines.append(f"- review note: {row['review_note']}")
        lines.append("")
        lines.append("| Baseline | Backend | Comparable phase (s) | Ratio baseline/cloud |")
        lines.append("|---|---|---:|---:|")
        for item in row["baseline_comparisons"]:
            phase = item["baseline_phase_sec"]
            ratio = item["baseline_over_cloud_ratio"]
            lines.append(
                f"| {item['baseline_name']} | {item['source_backend']} | "
                f"{'' if phase is None else f'{phase:.6f}'} | "
                f"{'' if ratio is None else f'{ratio:.3f}'} |"
            )
        lines.extend(["", "Top non-query phases on RTX path:"])
        for phase in row["top_nonquery_phases"]:
            lines.append(f"- `{phase['phase']}` = `{phase['seconds']:.6f}s`")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build an internal active OptiX claim-review comparison package.")
    parser.add_argument("--output-json", default="docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.json")
    parser.add_argument("--output-md", default="docs/reports/goal847_active_rtx_claim_review_package_2026-04-23.md")
    args = parser.parse_args(argv)
    payload = build_review_package()
    out_json = ROOT / args.output_json
    out_md = ROOT / args.output_md
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = to_markdown(payload)
    out_md.write_text(markdown + "\n", encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
