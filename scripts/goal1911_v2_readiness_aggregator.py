#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import pathlib
from typing import Iterable


REQUIRED_POD_ARTIFACTS = (
    "docs/reports/goal1903_fixed_radius_batch_pod.json",
    "docs/reports/goal1903_segment_polygon_batch_pod_512.json",
    "docs/reports/goal1903_segment_polygon_batch_pod_2048.json",
    "docs/reports/goal1889_road_hazard_prepared_reuse_pod_512.json",
    "docs/reports/goal1889_road_hazard_prepared_reuse_pod_2048.json",
    "docs/reports/goal1903_v2_partner_pod_batch_summary.json",
)

GOAL1905_ACCEPTANCE = "docs/reports/goal1905_v2_partner_pod_batch_acceptance.json"
GOAL1916_MANIFEST = "docs/reports/goal1916_v2_post_pod_artifact_manifest.json"
POST_POD_REVIEW_CANDIDATES = (
    "docs/reviews/goal1912_claude_review_goal1903_post_pod_artifacts_2026-05-13.md",
    "docs/reviews/goal1912_gemini_review_goal1903_post_pod_artifacts_2026-05-13.md",
)
POST_POD_DECISIVE_REVIEW_CANDIDATES = (
    "docs/reviews/goal1912_claude_review_goal1903_post_pod_artifacts_2026-05-13.md",
)

SUPPORTING_REQUIRED = (
    "docs/reports/goal1899_v2_strict_birth_gate_current_board_2026-05-13.md",
    "docs/reports/goal1900_partner_acceleration_boundary_doc_2026-05-13.md",
    "docs/reports/goal1902_v2_source_tree_only_release_exception_proposal_2026-05-13.md",
    "docs/reports/goal1903_v2_partner_pod_batch_packet_2026-05-13.md",
    "docs/reviews/goal1904_gemini_review_goal1903_batch_packet_2026-05-13.md",
    "docs/reports/goal1905_v2_partner_pod_batch_acceptance_2026-05-13.md",
    "docs/reports/goal1906_public_v2_claim_boundary_scan_2026-05-13.md",
    "docs/reviews/goal1907_gemini_review_v2_boundary_and_source_tree_2026-05-13.md",
    "docs/reports/goal1908_v2_local_preflight_2026-05-13.md",
    "docs/reports/goal1909_v2_release_packet_skeleton_2026-05-13.md",
    "docs/reviews/goal1910_gemini_review_v2_release_skeleton_2026-05-13.md",
    "docs/handoff/GOAL1912_POST_POD_EXTERNAL_REVIEW_TEMPLATE_2026-05-13.md",
    "docs/reports/goal1912_post_pod_external_review_template_2026-05-13.md",
    "scripts/goal1913_v2_pod_session_runbook.sh",
    "docs/reports/goal1913_v2_pod_session_runbook_2026-05-13.md",
    "docs/reports/goal1914_v2_pod_artifact_provenance_hardening_2026-05-13.md",
    "docs/reviews/goal1915_gemini_review_goal1914_pod_provenance_2026-05-13.md",
    "scripts/goal1916_v2_post_pod_artifact_manifest.py",
    "docs/reports/goal1916_v2_post_pod_artifact_manifest_2026-05-13.md",
    "docs/reviews/goal1917_gemini_review_goal1916_post_pod_manifest_2026-05-13.md",
    "docs/reports/goal1918_fixed_radius_reference_oom_guard_2026-05-13.md",
    "docs/reports/goal1919_post_pod_evidence_integration_2026-05-13.md",
    "docs/reviews/goal1920_gemini_followup_goal1912_post_pod_review_correction_2026-05-13.md",
    "docs/reports/goal1921_v2_post_pod_performance_report_2026-05-13.md",
)


def _exists(root: pathlib.Path, path_text: str) -> bool:
    return (root / path_text).exists()


def _read_json_if_exists(root: pathlib.Path, path_text: str) -> dict | None:
    path = root / path_text
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def aggregate(root: pathlib.Path) -> dict[str, object]:
    missing_supporting = [path for path in SUPPORTING_REQUIRED if not _exists(root, path)]
    missing_pod = [path for path in REQUIRED_POD_ARTIFACTS if not _exists(root, path)]
    acceptance = _read_json_if_exists(root, GOAL1905_ACCEPTANCE)
    acceptance_status = acceptance.get("status") if acceptance else "not-run"
    manifest = _read_json_if_exists(root, GOAL1916_MANIFEST)
    manifest_status = manifest.get("status") if manifest else "not-run"
    post_pod_reviews = [path for path in POST_POD_REVIEW_CANDIDATES if _exists(root, path)]
    decisive_post_pod_reviews = [
        path for path in POST_POD_DECISIVE_REVIEW_CANDIDATES if _exists(root, path)
    ]
    local_preflight = _read_json_if_exists(root, "scratch/goal1908_final_preflight_post_commit.json")
    if local_preflight is None:
        local_preflight = _read_json_if_exists(root, "scratch/goal1908_final_preflight.json")
    local_preflight_status = local_preflight.get("status") if local_preflight else "not-run"

    blockers = []
    if missing_supporting:
        blockers.append("supporting gate files missing")
    if missing_pod:
        blockers.append("RTX pod batch artifacts missing")
    if acceptance_status != "pass":
        blockers.append("strict Goal1905 post-pod acceptance not passed on pod artifacts")
    if manifest_status != "pass":
        blockers.append("Goal1916 post-pod artifact manifest not passed on pod artifacts")
    if not decisive_post_pod_reviews:
        blockers.append("fresh Claude or Pro-class review of actual pod artifacts missing")
    blockers.append("final source-tree-only or packaging decision lacks 3-AI release consensus")
    blockers.append("final v2.0 release consensus missing")
    blockers.append("explicit user-requested release action missing")
    pod_evidence_collected = (
        not missing_pod
        and acceptance_status == "pass"
        and manifest_status == "pass"
    )

    return {
        "goal": "Goal1911",
        "status": "blocked",
        "local_preflight_status": local_preflight_status,
        "goal1905_acceptance_status": acceptance_status,
        "goal1916_manifest_status": manifest_status,
        "post_pod_review_files": post_pod_reviews,
        "decisive_post_pod_review_files": decisive_post_pod_reviews,
        "missing_supporting_files": missing_supporting,
        "missing_pod_artifacts": missing_pod,
        "blockers": blockers,
        "next_hardware_command": (
            "OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch "
            "OPTIX_PREFIX=/root/vendor/optix-sdk "
            "bash scripts/goal1903_v2_partner_pod_batch_runner.sh"
        ),
        "post_pod_acceptance_command": "PYTHONPATH=src:. python3 scripts/goal1905_v2_partner_pod_batch_acceptance.py",
        "post_pod_manifest_command": "PYTHONPATH=src:. python3 scripts/goal1916_v2_post_pod_artifact_manifest.py",
        "pod_session_runbook_command": (
            "OUT_DIR=docs/reports/goal1903_v2_partner_pod_batch "
            "OPTIX_PREFIX=/root/vendor/optix-sdk "
            "bash scripts/goal1913_v2_pod_session_runbook.sh"
        ),
        "claim_boundary": {
            "v2_0_release_authorized": False,
            "pod_evidence_collected": pod_evidence_collected,
            "package_install_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "arbitrary_partner_program_acceleration_authorized": False,
        },
    }


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Aggregate current v2.0 readiness blockers.")
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="docs/reports/goal1911_v2_readiness_aggregator.json")
    args = parser.parse_args(list(argv) if argv is not None else None)

    root = pathlib.Path(args.root)
    payload = aggregate(root)
    output = root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
