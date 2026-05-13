#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Any, Iterable


FORBID_TRUE_CLAIMS = (
    "v2_0_release_authorized",
    "whole_app_speedup_claim_authorized",
    "broad_rt_core_speedup_claim_authorized",
)

ARTIFACTS = (
    ("fixed_radius", "docs/reports/goal1903_fixed_radius_batch_pod.json"),
    ("segment_polygon_512", "docs/reports/goal1903_segment_polygon_batch_pod_512.json"),
    ("segment_polygon_2048", "docs/reports/goal1903_segment_polygon_batch_pod_2048.json"),
    ("road_hazard_512", "docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json"),
    ("road_hazard_2048", "docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json"),
    ("batch_summary", "docs/reports/goal1903_v2_partner_pod_batch_summary.json"),
)


def _load_json(path: pathlib.Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _claim_boundary(data: dict[str, Any]) -> dict[str, Any]:
    if isinstance(data.get("claim_boundary"), dict):
        return data["claim_boundary"]
    return {}


def _claims_ok(data: dict[str, Any]) -> bool:
    boundaries: list[dict[str, Any]] = []
    boundary = _claim_boundary(data)
    if boundary:
        boundaries.append(boundary)
    for result in data.get("results", []):
        if isinstance(result, dict) and isinstance(result.get("claim_boundaries"), dict):
            boundaries.append(result["claim_boundaries"])
    if not boundaries:
        return False
    return all(not boundary.get(key) for boundary in boundaries for key in FORBID_TRUE_CLAIMS)


def _partners(data: dict[str, Any]) -> list[str]:
    if isinstance(data.get("partners"), dict):
        return sorted(str(key) for key in data["partners"])
    partners = set()
    for result in data.get("results", []):
        if isinstance(result, dict) and "partner" in result:
            partners.add(str(result["partner"]))
    return sorted(partners)


def _row_count(data: dict[str, Any]) -> int | None:
    if isinstance(data.get("count"), int):
        return int(data["count"])
    if isinstance(data.get("results"), list):
        return len(data["results"])
    return None


def _entry(kind: str, artifact: str, data: dict[str, Any] | None, source_label: str | None) -> dict[str, Any]:
    if data is None:
        return {
            "kind": kind,
            "artifact": artifact,
            "exists": False,
            "review_ready": False,
            "errors": ["missing artifact"],
        }
    gpu = str(data.get("gpu", ""))
    git_commit = str(data.get("git_commit", ""))
    artifact_source = str(data.get("source_commit_label", ""))
    errors = []
    if kind != "batch_summary":
        if "RTX" not in gpu:
            errors.append("missing RTX GPU provenance")
        if not git_commit or git_commit == "unknown":
            errors.append("missing git_commit provenance")
        if source_label and artifact_source != source_label:
            errors.append("source_commit_label mismatch")
        elif not artifact_source:
            errors.append("missing source_commit_label provenance")
    if not _claims_ok(data):
        errors.append("claim boundary missing or over-authorized")
    return {
        "kind": kind,
        "artifact": artifact,
        "exists": True,
        "review_ready": not errors,
        "status": data.get("status"),
        "goal": data.get("goal"),
        "goal_extension": data.get("goal_extension"),
        "gpu": gpu,
        "git_commit": git_commit,
        "source_commit_label": artifact_source,
        "source_matches_summary": bool(source_label and artifact_source == source_label),
        "partners": _partners(data),
        "row_count_or_result_count": _row_count(data),
        "claim_boundary_ok": _claims_ok(data),
        "errors": errors,
    }


def build_manifest(root: pathlib.Path) -> dict[str, Any]:
    summary_artifact = "docs/reports/goal1903_v2_partner_pod_batch_summary.json"
    summary = _load_json(root / summary_artifact)
    source_label = summary.get("source_commit_label") if isinstance(summary, dict) else None
    entries = [
        _entry(kind, artifact, _load_json(root / artifact), source_label)
        for kind, artifact in ARTIFACTS
    ]
    missing = [entry["artifact"] for entry in entries if not entry["exists"]]
    errors = [
        f"{entry['artifact']}: {error}"
        for entry in entries
        for error in entry.get("errors", [])
    ]
    status = "pass"
    if errors:
        status = "fail"
    if missing:
        status = "blocked_missing_artifacts"
    return {
        "goal": "Goal1916",
        "status": status,
        "source_commit_label": source_label or "",
        "artifacts": entries,
        "missing_artifacts": missing,
        "errors": errors,
        "next_review_inputs": [
            "docs/reports/goal1905_v2_partner_pod_batch_acceptance.json",
            "docs/reports/goal1916_v2_post_pod_artifact_manifest.json",
            "docs/handoff/GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE_2026-05-13.md",
        ],
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build a reviewer manifest for Goal1903 post-pod artifacts.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="docs/reports/goal1916_v2_post_pod_artifact_manifest.json")
    parser.add_argument("--allow-missing", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = pathlib.Path(args.root)
    payload = build_manifest(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["status"] == "fail":
        return 1
    if payload["status"] == "blocked_missing_artifacts" and not args.allow_missing:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
