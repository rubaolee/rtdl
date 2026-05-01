#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DATE = "2026-04-30"
GOAL = "Goal1198 same-scale public wording audit"
DEFAULT_ARTIFACT_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal1194_live_pod_2026-04-30"
    / "final_recovery2"
    / "docs"
    / "reports"
    / "goal1192_public_wording_evidence_batch"
)
DEFAULT_OUTPUT_JSON = ROOT / "docs" / "reports" / "goal1198_same_scale_public_wording_audit_2026-04-30.json"
DEFAULT_OUTPUT_MD = ROOT / "docs" / "reports" / "goal1198_same_scale_public_wording_audit_2026-04-30.md"

PAIRS: tuple[tuple[str, str, str], ...] = (
    ("database_analytics", "database_compact_summary_embree.json", "database_compact_summary_optix.json"),
    ("graph_analytics", "graph_visibility_edges_embree.json", "graph_visibility_edges_optix.json"),
    ("road_hazard_screening", "road_hazard_native_summary_embree.json", "road_hazard_native_summary_optix.json"),
    ("polygon_pair_overlap_area_rows", "polygon_pair_candidate_discovery_embree.json", "polygon_pair_candidate_discovery_optix.json"),
    ("polygon_set_jaccard", "polygon_jaccard_safe_chunk_embree.json", "polygon_jaccard_safe_chunk_optix.json"),
    ("hausdorff_distance", "hausdorff_threshold_prepared_embree.json", "hausdorff_threshold_prepared_optix.json"),
)


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_copies(data: dict[str, Any]) -> int | None:
    candidates = [
        data.get("copies"),
        (data.get("parameters") or {}).get("copies") if isinstance(data.get("parameters"), dict) else None,
        (data.get("scenario") or {}).get("copies") if isinstance(data.get("scenario"), dict) else None,
    ]
    for value in candidates:
        if isinstance(value, int):
            return value
        if isinstance(value, float) and value.is_integer():
            return int(value)
    return None


def _phase_ratio(app: str, embree: dict[str, Any], optix: dict[str, Any]) -> float | None:
    if app == "road_hazard_screening":
        e = embree.get("run_phases", {}).get("query_and_materialize_sec")
        o = optix.get("timings_sec", {}).get("optix_query_sec", {}).get("median_sec")
    elif app == "hausdorff_distance":
        e = embree.get("run_phases", {}).get("native_directed_summary_sec")
        o = optix.get("scenario", {}).get("timings_sec", {}).get("optix_query_sec", {}).get("median_sec")
    elif app in {"polygon_pair_overlap_area_rows", "polygon_set_jaccard"}:
        e = embree.get("run_phases", {}).get("rt_candidate_discovery_sec")
        o = optix.get("phases", {}).get("optix_candidate_discovery_sec")
    elif app == "graph_analytics":
        e = embree.get("graph_phase_totals_sec", {}).get("query_visibility_pair_rows_sec")
        o = optix.get("records_by_label", {}).get("optix_visibility_anyhit", {}).get("sec")
    elif app == "database_analytics":
        results_e = embree.get("results") or []
        results_o = optix.get("results") or []
        e = results_e[0].get("prepared_session_warm_query_sec", {}).get("median_sec") if results_e else None
        o = results_o[0].get("prepared_session_warm_query_sec", {}).get("median_sec") if results_o else None
    else:
        return None
    if not isinstance(e, (int, float)) or not isinstance(o, (int, float)) or float(o) <= 0:
        return None
    return float(e) / float(o)


def build_audit(artifact_dir: Path = DEFAULT_ARTIFACT_DIR) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    for app, embree_name, optix_name in PAIRS:
        embree_path = artifact_dir / embree_name
        optix_path = artifact_dir / optix_name
        embree = _load(embree_path)
        optix = _load(optix_path)
        embree_copies = _extract_copies(embree)
        optix_copies = _extract_copies(optix)
        same_scale = embree_copies is not None and embree_copies == optix_copies
        ratio = _phase_ratio(app, embree, optix)
        optix_faster = bool(ratio is not None and ratio > 1.0)
        public_ratio_safe = bool(same_scale and optix_faster)
        if optix_faster and not same_scale:
            blockers.append(f"{app} has OptiX-faster ratio but not same-scale artifacts")
        rows.append(
            {
                "app": app,
                "embree_artifact": embree_name,
                "optix_artifact": optix_name,
                "embree_copies": embree_copies,
                "optix_copies": optix_copies,
                "same_scale": same_scale,
                "raw_ratio_embree_over_optix": ratio,
                "optix_faster": optix_faster,
                "public_ratio_safe": public_ratio_safe,
            }
        )
    safe = [row["app"] for row in rows if row["public_ratio_safe"]]
    unsafe = [row["app"] for row in rows if not row["public_ratio_safe"]]
    return {
        "goal": GOAL,
        "date": DATE,
        "valid": not blockers,
        "artifact_dir": str(artifact_dir.relative_to(ROOT)),
        "safe_positive_public_ratio_apps": safe,
        "unsafe_or_blocked_ratio_apps": unsafe,
        "rows": rows,
        "blockers": blockers,
        "supersedes": "Goal1196 Hausdorff positive wording proposal is unsafe because the accepted artifacts are not same-scale.",
        "boundary": (
            "Goal1198 audits whether accepted evidence can support public positive ratio wording. "
            "It does not authorize public docs, release, or speedup claims by itself."
        ),
    }


def to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Goal1198 Same-Scale Public Wording Audit",
        "",
        f"Date: {payload['date']}",
        "",
        payload["boundary"],
        "",
        "## Summary",
        "",
        f"- valid: `{payload['valid']}`",
        f"- supersedes: {payload['supersedes']}",
        f"- safe positive public ratio apps: `{', '.join(payload['safe_positive_public_ratio_apps'])}`",
        f"- unsafe or blocked ratio apps: `{', '.join(payload['unsafe_or_blocked_ratio_apps'])}`",
        "",
        "## Rows",
        "",
        "| App | Embree copies | OptiX copies | Same scale | Ratio | OptiX faster | Public ratio safe |",
        "| --- | ---: | ---: | --- | ---: | --- | --- |",
    ]
    for row in payload["rows"]:
        ratio = row["raw_ratio_embree_over_optix"]
        ratio_text = "n/a" if ratio is None else f"{ratio:.6f}"
        lines.append(
            f"| `{row['app']}` | `{row['embree_copies']}` | `{row['optix_copies']}` | "
            f"`{row['same_scale']}` | `{ratio_text}` | `{row['optix_faster']}` | `{row['public_ratio_safe']}` |"
        )
    if payload["blockers"]:
        lines.extend(["", "## Blockers", ""])
        lines.extend(f"- {blocker}" for blocker in payload["blockers"])
    lines.extend(
        [
            "",
            "## Conclusion",
            "",
            "Only same-scale, OptiX-faster rows may proceed to positive public wording review. "
            "In the current evidence, that leaves `road_hazard_screening` only. "
            "`hausdorff_distance` remains technically evidence-ready for RT traversal, but its "
            "positive ratio wording must be blocked until same-scale or explicitly normalized "
            "evidence is collected and reviewed.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit same-scale public wording evidence.")
    parser.add_argument("--artifact-dir", default=str(DEFAULT_ARTIFACT_DIR))
    parser.add_argument("--output-json", default=str(DEFAULT_OUTPUT_JSON))
    parser.add_argument("--output-md", default=str(DEFAULT_OUTPUT_MD))
    args = parser.parse_args()
    payload = build_audit(Path(args.artifact_dir))
    Path(args.output_json).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    Path(args.output_md).write_text(to_markdown(payload) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "valid": payload["valid"],
                "safe_positive_public_ratio_apps": payload["safe_positive_public_ratio_apps"],
                "blockers": payload["blockers"],
            },
            sort_keys=True,
        )
    )
    return 0 if payload["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
