#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

M7_PACKET = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_m7_row_classification_packet_2026-06-20.json"
APP_CLASSIFICATION = ROOT / "docs" / "rebuild" / "v3" / "v3_benchmark_app_classification_2026-06-20.json"
NEXT_ENGINE_WORK_QUEUE = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_next_generic_engine_work_queue_2026-06-21.json"
)
AGGREGATE_RELEASE_CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "codex_phoenix_v3_aggregate_release_readiness_2ai_consensus_2026-06-21.md"
)

EXPECTED_MISSING_CAPABILITY_FUTURE_WORK_MAP = {
    "aggregate_frontier": {
        "future_research_work_id": "barnes_hut_vector_accumulation_frontier_shape",
        "queue_generic_capability": "vector_accumulation",
        "mapping_reason": (
            "The packet-level Barnes-Hut family is aggregate_frontier; the closed queue records "
            "the refined vector_accumulation reopen shape for the same missing capability area."
        ),
    },
    "point_location_topology_stream": {
        "future_research_work_id": "spatial_rayjoin_topology_stream_author_gap",
        "queue_generic_capability": "point_location_topology_stream",
        "mapping_reason": (
            "The packet-level Spatial RayJoin topology-stream family is directly represented "
            "by the closed future-research queue item."
        ),
    },
}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _candidate_row_ids(item: dict[str, Any]) -> list[str]:
    explicit = item.get("candidate_row_ids")
    if isinstance(explicit, list):
        return [str(row_id).strip() for row_id in explicit if str(row_id).strip()]
    if isinstance(explicit, str) and explicit.strip():
        return [part.strip() for part in explicit.split(";") if part.strip()]

    row_id = item.get("candidate_row_id")
    if isinstance(row_id, str) and ";" in row_id:
        return [part.strip() for part in row_id.split(";") if part.strip()]
    if row_id:
        return [str(row_id).strip()]
    return []


def _m7_rows_by_capability(packet: dict[str, Any]) -> dict[str, list[str]]:
    rows_by_capability: dict[str, list[str]] = {}

    for row in packet.get("row_classifications", []):
        if row.get("m7_classification") != "m7_qualified_release_row":
            continue
        if row.get("row_scoped_public_speedup_claim_authorized") is not True:
            continue
        capability = row.get("generic_capability")
        if not capability:
            continue
        rows_by_capability.setdefault(str(capability), []).extend(_candidate_row_ids(row))

    for packet_row in packet.get("post_classification_final_review_packets", []):
        if packet_row.get("classification_m7_contribution", 0) <= 0:
            continue
        if packet_row.get("row_scoped_public_speedup_claim_authorized") is not True:
            continue
        capability = packet_row.get("generic_capability")
        if not capability:
            continue
        rows_by_capability.setdefault(str(capability), []).extend(_candidate_row_ids(packet_row))

    return {
        capability: sorted(dict.fromkeys(row_ids))
        for capability, row_ids in sorted(rows_by_capability.items())
    }


def _app_m7_rows(app_classification: dict[str, Any]) -> dict[str, list[str]]:
    rows_by_app: dict[str, list[str]] = {}
    for app_name, app in app_classification.get("apps", {}).items():
        row_ids = []
        if app.get("m7_row_id"):
            row_ids.append(str(app["m7_row_id"]))
        if app.get("m7_row_ids"):
            row_ids.extend(str(row_id) for row_id in app["m7_row_ids"])
        row_ids = sorted(dict.fromkeys(row_ids))
        if row_ids:
            rows_by_app[str(app_name)] = row_ids
    return dict(sorted(rows_by_app.items()))


def _supplemental_m7_rows_from_queue(
    next_queue: dict[str, Any], rows_by_capability: dict[str, list[str]]
) -> list[dict[str, Any]]:
    existing_row_ids = {
        row_id
        for row_ids in rows_by_capability.values()
        for row_id in row_ids
    }
    supplemental_rows: list[dict[str, Any]] = []
    for item in next_queue.get("closed_generic_engine_work", []):
        if int(item.get("m7_rows_added", 0)) <= 0:
            continue
        capability = item.get("generic_capability")
        if not capability:
            continue
        for row_id in _candidate_row_ids(item):
            if row_id in existing_row_ids:
                continue
            supplemental_rows.append(
                {
                    "row_id": row_id,
                    "generic_capability": str(capability),
                    "source_work_id": item.get("id"),
                    "closed_by_consensus": item.get("closed_by_consensus"),
                }
            )
            existing_row_ids.add(row_id)
    return supplemental_rows


def _as_path_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value:
        return [str(value)]
    return []


def _all_paths_exist(paths: list[str]) -> bool:
    if not paths:
        return False
    return all((ROOT / path).exists() for path in paths)


def _surface_row_record(
    *,
    row_id: str,
    capability: str,
    source_kind: str,
    source: dict[str, Any],
    evidence_paths: list[str],
    review_paths: list[str],
    consensus_paths: list[str],
) -> dict[str, Any]:
    release_authorized = bool(source.get("release_authorized", False))
    public_speedup_claim_authorized = bool(source.get("public_speedup_claim_authorized", False))
    broad_speedup_claim_authorized = bool(source.get("broad_v3_faster_than_v2_claim_authorized", False))
    return {
        "row_id": row_id,
        "generic_capability": capability,
        "source_kind": source_kind,
        "evidence_paths": evidence_paths,
        "review_paths": review_paths,
        "consensus_paths": consensus_paths,
        "evidence_paths_exist": _all_paths_exist(evidence_paths),
        "review_paths_exist": _all_paths_exist(review_paths),
        "consensus_paths_exist": _all_paths_exist(consensus_paths),
        "release_authorized": release_authorized,
        "public_speedup_claim_authorized": public_speedup_claim_authorized,
        "broad_v3_faster_than_v2_claim_authorized": broad_speedup_claim_authorized,
        "unsupported_claims_blocked": not (
            release_authorized
            or public_speedup_claim_authorized
            or broad_speedup_claim_authorized
        ),
    }


def _surface_row_integrity_manifest(packet: dict[str, Any], next_queue: dict[str, Any]) -> list[dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}

    for row in packet.get("row_classifications", []):
        if row.get("m7_classification") != "m7_qualified_release_row":
            continue
        if row.get("row_scoped_public_speedup_claim_authorized") is not True:
            continue
        capability = str(row.get("generic_capability", ""))
        for row_id in _candidate_row_ids(row):
            rows_by_id[row_id] = _surface_row_record(
                row_id=row_id,
                capability=capability,
                source_kind="base_m7_packet_row",
                source=row,
                evidence_paths=_as_path_list(row.get("evidence_basis")),
                review_paths=_as_path_list(row.get("external_review")),
                consensus_paths=_as_path_list(row.get("codex_consensus")),
            )

    for item in packet.get("post_classification_final_review_packets", []):
        if item.get("classification_m7_contribution", 0) <= 0:
            continue
        if item.get("row_scoped_public_speedup_claim_authorized") is not True:
            continue
        capability = str(item.get("generic_capability", ""))
        for row_id in _candidate_row_ids(item):
            rows_by_id[row_id] = _surface_row_record(
                row_id=row_id,
                capability=capability,
                source_kind="post_classification_final_review_packet",
                source=item,
                evidence_paths=_as_path_list(item.get("packet")),
                review_paths=_as_path_list(item.get("external_review")),
                consensus_paths=_as_path_list(item.get("codex_consensus")),
            )

    for item in next_queue.get("closed_generic_engine_work", []):
        if int(item.get("m7_rows_added", 0)) <= 0:
            continue
        capability = str(item.get("generic_capability", ""))
        for row_id in _candidate_row_ids(item):
            if row_id in rows_by_id:
                continue
            rows_by_id[row_id] = _surface_row_record(
                row_id=row_id,
                capability=capability,
                source_kind="closed_generic_engine_work_supplemental_row",
                source=item,
                evidence_paths=_as_path_list(item.get("closed_by_packet")),
                review_paths=_as_path_list(item.get("closed_by_external_review")),
                consensus_paths=_as_path_list(item.get("closed_by_consensus")),
            )

    return [rows_by_id[row_id] for row_id in sorted(rows_by_id)]


def _missing_capability_future_work_map(
    missing_capabilities: list[str], future_work: list[dict[str, Any]]
) -> dict[str, dict[str, str]]:
    queue_by_id = {str(item.get("id")): item for item in future_work if item.get("id")}
    result: dict[str, dict[str, str]] = {}
    for capability in missing_capabilities:
        expected = EXPECTED_MISSING_CAPABILITY_FUTURE_WORK_MAP.get(capability)
        if not expected:
            continue
        queue_item = queue_by_id.get(expected["future_research_work_id"], {})
        result[capability] = {
            "future_research_work_id": expected["future_research_work_id"],
            "queue_generic_capability": str(queue_item.get("generic_capability", "")),
            "expected_queue_generic_capability": expected["queue_generic_capability"],
            "mapping_reason": expected["mapping_reason"],
        }
    return result


def build_payload() -> dict[str, Any]:
    required_paths = {
        "m7_packet": M7_PACKET,
        "app_classification": APP_CLASSIFICATION,
        "next_engine_work_queue": NEXT_ENGINE_WORK_QUEUE,
        "aggregate_release_consensus": AGGREGATE_RELEASE_CONSENSUS,
    }
    checks = {f"{name}_exists": path.exists() for name, path in required_paths.items()}
    evidence: dict[str, Any] = {}

    if not all(checks.values()):
        failed_checks = [name for name, passed in checks.items() if not passed]
        return {
            "tool": "v3_phoenix_release_surface_breadth_gate",
            "gate": "phoenix_v3_major_release_surface_breadth",
            "status": "fail",
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "broad_v3_faster_than_v2_claim_authorized": False,
            "failed_checks": failed_checks,
            "checks": checks,
            "evidence": evidence,
            "decision_audit": _decision_audit(),
        }

    packet = _load_json(M7_PACKET)
    app_classification = _load_json(APP_CLASSIFICATION)
    next_queue = _load_json(NEXT_ENGINE_WORK_QUEUE)
    aggregate_consensus = _read_text(AGGREGATE_RELEASE_CONSENSUS)

    summary = packet.get("summary", {})
    planned_capabilities = sorted(
        str(item.get("generic_capability"))
        for item in packet.get("capability_summaries", [])
        if item.get("generic_capability")
    )
    rows_by_capability = _m7_rows_by_capability(packet)
    base_m7_row_count = sum(len(rows) for rows in rows_by_capability.values())
    supplemental_m7_rows = _supplemental_m7_rows_from_queue(next_queue, rows_by_capability)
    for row in supplemental_m7_rows:
        rows_by_capability.setdefault(row["generic_capability"], []).append(row["row_id"])
    rows_by_capability = {
        capability: sorted(dict.fromkeys(row_ids))
        for capability, row_ids in sorted(rows_by_capability.items())
    }
    m7_capabilities = sorted(rows_by_capability)
    missing_capabilities = sorted(set(planned_capabilities) - set(m7_capabilities))

    total_m7_rows = sum(len(rows) for rows in rows_by_capability.values())
    minimum_capability_families = int(summary.get("capability_count", len(planned_capabilities)))
    current_capability_families = len(m7_capabilities)
    future_work = next_queue.get("future_generic_engine_work", [])
    pending_external_review_candidates = next_queue.get("pending_external_review_candidates", [])
    accepted_with_boundary_candidates = next_queue.get("accepted_with_boundary_candidates", [])
    future_work_ids = [str(item.get("id")) for item in future_work if item.get("id")]
    future_work_capabilities = sorted(
        str(item.get("generic_capability"))
        for item in future_work
        if item.get("generic_capability")
    )
    missing_future_work_map = _missing_capability_future_work_map(missing_capabilities, future_work)
    app_rows_by_app = _app_m7_rows(app_classification)
    app_boundary_rows = [str(row_id) for row_id in app_classification.get("m7_row_ids", [])]
    attributed_app_boundary_rows = sorted(
        dict.fromkeys(row_id for rows in app_rows_by_app.values() for row_id in rows)
    )
    unattributed_app_boundary_rows = sorted(set(app_boundary_rows) - set(attributed_app_boundary_rows))
    surface_row_integrity = _surface_row_integrity_manifest(packet, next_queue)
    surface_row_ids = [row["row_id"] for row in surface_row_integrity]
    all_surface_row_flags_blocked = all(row["unsupported_claims_blocked"] for row in surface_row_integrity)
    all_surface_row_paths_exist = all(
        row["evidence_paths_exist"] and row["review_paths_exist"] and row["consensus_paths_exist"]
        for row in surface_row_integrity
    )
    all_surface_rows_generic_capability_rows = all(
        row["generic_capability"] in planned_capabilities for row in surface_row_integrity
    )

    checks.update(
        {
            "m7_packet_status_not_release": packet.get("status") == "m7_classification_packet_not_release",
            "m7_packet_release_false": packet.get("release_authorized") is False,
            "m7_packet_broad_speed_false": packet.get("broad_v3_faster_than_v2_claim_authorized") is False,
            "m7_packet_base_rows_still_twelve": packet.get("phoenix_m7_qualified_release_rows") == 12,
            "m7_packet_rows_extracted_as_twelve": base_m7_row_count == 12,
            "queue_supplemental_m7_rows_are_one": len(supplemental_m7_rows) == 1,
            "queue_current_rows_match_surface_rows": next_queue.get("current_m7_qualified_release_rows")
            == total_m7_rows
            == 13,
            "planned_capability_floor_is_nine": minimum_capability_families == 9,
            "current_capability_coverage_is_nine_of_nine": current_capability_families == 9,
            "missing_packet_capabilities_are_closed": missing_capabilities == [],
            "missing_capability_future_work_map_is_empty": missing_future_work_map == {},
            "missing_capability_future_work_map_matches_queue": all(
                item.get("queue_generic_capability") == item.get("expected_queue_generic_capability")
                for item in missing_future_work_map.values()
            ),
            "route_map_m7_rows_are_five": summary.get("route_map_m7_qualified_release_rows") == 5,
            "supplemental_m7_rows_are_seven": summary.get("supplemental_m7_qualified_release_rows") == 7,
            "app_boundary_snapshot_is_eight_rows": app_classification.get("phoenix_m7_qualified_release_rows") == 8,
            "app_boundary_release_false": app_classification.get("v3_release_authorized") is False,
            "app_boundary_all_rows_attributed_to_named_apps": len(attributed_app_boundary_rows)
            == app_classification.get("phoenix_m7_qualified_release_rows")
            and set(attributed_app_boundary_rows) == set(app_boundary_rows),
            "app_boundary_has_no_unattributed_m7_rows": unattributed_app_boundary_rows == [],
            "next_engine_queue_closed_not_release": next_queue.get("status")
            == "generic_engine_work_queue_closed_not_release",
            "existing_evidence_promotable_now_false": next_queue.get("existing_evidence_promotable_now") is False,
            "pending_external_review_candidates_not_promotable_now": all(
                item.get("m7_rows_added_now") == 0
                and item.get("release_authorized") is False
                and item.get("public_speedup_claim_authorized") is False
                for item in pending_external_review_candidates
            ),
            "accepted_with_boundary_candidates_not_promotable_now": all(
                item.get("m7_rows_added_now") == 0
                and item.get("release_authorized") is False
                and item.get("public_speedup_claim_authorized") is False
                for item in accepted_with_boundary_candidates
            ),
            "active_generic_engine_queue_empty": next_queue.get("queue") == [],
            "future_research_records_do_not_include_resolved_spatial_gap": set(future_work_ids)
            == {"barnes_hut_vector_accumulation_frontier_shape"},
            "aggregate_release_consensus_blocks_release": "aggregate_release_readiness_consensus_blocks_release"
            in aggregate_consensus,
            "surface_row_integrity_manifest_has_thirteen_rows": len(surface_row_integrity) == 13,
            "surface_row_integrity_manifest_rows_are_unique": len(surface_row_ids) == len(set(surface_row_ids)),
            "surface_row_integrity_manifest_matches_current_surface_rows": set(surface_row_ids)
            == {row_id for row_ids in rows_by_capability.values() for row_id in row_ids},
            "surface_row_integrity_paths_exist": all_surface_row_paths_exist,
            "surface_row_integrity_flags_block_unsupported_claims": all_surface_row_flags_blocked,
            "surface_row_integrity_rows_are_generic_capability_rows": all_surface_rows_generic_capability_rows,
        }
    )

    evidence.update(
        {
            "planned_capability_families": planned_capabilities,
            "minimum_m7_capability_families_for_major_release": minimum_capability_families,
            "m7_capability_families": m7_capabilities,
            "m7_capability_family_count": current_capability_families,
            "missing_m7_capability_families": missing_capabilities,
            "missing_capability_future_work_map": missing_future_work_map,
            "m7_rows_by_capability": rows_by_capability,
            "surface_row_integrity": surface_row_integrity,
            "surface_row_integrity_row_count": len(surface_row_integrity),
            "surface_row_integrity_all_paths_exist": all_surface_row_paths_exist,
            "surface_row_integrity_all_flags_block_unsupported_claims": all_surface_row_flags_blocked,
            "surface_row_integrity_all_rows_are_generic_capability_rows": all_surface_rows_generic_capability_rows,
            "m7_row_count_by_capability": dict(
                sorted(Counter({capability: len(rows) for capability, rows in rows_by_capability.items()}).items())
            ),
            "total_m7_row_count": total_m7_rows,
            "base_m7_packet_row_count": base_m7_row_count,
            "supplemental_m7_rows_from_current_queue": supplemental_m7_rows,
            "supplemental_m7_row_count_from_current_queue": len(supplemental_m7_rows),
            "route_map_m7_qualified_release_rows": summary.get("route_map_m7_qualified_release_rows"),
            "supplemental_m7_qualified_release_rows": summary.get("supplemental_m7_qualified_release_rows"),
            "app_boundary_m7_rows": app_classification.get("phoenix_m7_qualified_release_rows"),
            "app_boundary_m7_row_ids": app_boundary_rows,
            "apps_with_m7_rows": app_rows_by_app,
            "apps_with_m7_row_count": len(attributed_app_boundary_rows),
            "unattributed_app_boundary_m7_rows": unattributed_app_boundary_rows,
            "unattributed_app_boundary_m7_row_count": len(unattributed_app_boundary_rows),
            "next_engine_queue_status": next_queue.get("status"),
            "active_generic_engine_queue_ids": [item.get("id") for item in next_queue.get("queue", [])],
            "pending_external_review_candidate_ids": [
                item.get("id") for item in pending_external_review_candidates
            ],
            "pending_external_review_candidate_count": len(pending_external_review_candidates),
            "accepted_with_boundary_candidate_ids": [
                item.get("id") for item in accepted_with_boundary_candidates
            ],
            "accepted_with_boundary_candidate_count": len(accepted_with_boundary_candidates),
            "existing_evidence_promotable_now": next_queue.get("existing_evidence_promotable_now"),
            "future_research_work_ids": future_work_ids,
            "future_research_capabilities": future_work_capabilities,
            "capability_scope_note": (
                "aggregate_frontier/vector_accumulation is now covered by the amended Barnes-Hut "
                "Numba CUDA partner M7 row. Spatial topology-stream is now covered only by the "
                "default-path guarded squared-boundary row; it still does not authorize release."
            ),
        }
    )

    failed_checks = [name for name, passed in checks.items() if not passed]
    structural_pass = not failed_checks
    if not structural_pass:
        status = "fail"
    else:
        status = "surface_breadth_passed_not_release"

    blocking_reasons = []
    if structural_pass:
        blocking_reasons = [
            "release_authorization_false",
            "updated_thirteen_row_release_readiness_consensus_required",
        ]

    return {
        "tool": "v3_phoenix_release_surface_breadth_gate",
        "gate": "phoenix_v3_major_release_surface_breadth",
        "status": status,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "blocking_reasons": blocking_reasons,
        "failed_checks": failed_checks,
        "checks": checks,
        "evidence": evidence,
        "required_next_actions": [
            "Do not publish Phoenix V3 as a major release from the current thirteen-row surface until an aggregate 2-AI release-readiness consensus explicitly authorizes it.",
            "Seek fresh aggregate release-readiness review against the 13-row, 9-capability surface.",
            "Do not turn the Spatial row into RTDL-beats-RayJoin, public speedup, true-zero-copy, or broad V3-over-V2 wording.",
        ],
        "decision_audit": _decision_audit(),
    }


def _decision_audit() -> dict[str, str]:
    return {
        "decision": "Update the Phoenix V3 release-surface breadth gate to count 12 base packet rows plus 1 reviewed Spatial supplemental row, while keeping release blocked.",
        "was_i_foolish": "No. This removes a stale missing-capability blocker after default-path Spatial review, but it still refuses to treat breadth coverage as release authorization.",
        "foolish_actions": "The foolish action would be to treat thirteen row-scoped/supplemental wins, a closed active engine queue, or passing docs tests as enough for a V3 major release.",
        "other_path": "Keep the old twelve-row breadth blocker. That would hide the accepted Spatial default-path row and mislead future agents about the current surface.",
        "different_path_now": "Use this gate to show breadth is now 13 rows across 9 capability families, then require fresh aggregate 2-AI release-readiness review before release wording.",
    }


def render_markdown(payload: dict[str, Any]) -> str:
    evidence = payload.get("evidence", {})
    lines = [
        "# Phoenix V3 Release Surface Breadth Gate",
        "",
        f"Status: `{payload.get('status')}`",
        f"Release authorized: `{str(payload.get('release_authorized')).lower()}`",
        f"Public speedup claim authorized: `{str(payload.get('public_speedup_claim_authorized')).lower()}`",
        f"Broad V3-over-V2 speedup claim authorized: `{str(payload.get('broad_v3_faster_than_v2_claim_authorized')).lower()}`",
        "",
        "## Current Surface",
        "",
        f"- M7 row count: `{evidence.get('total_m7_row_count')}`",
        (
            "- M7 capability family coverage: "
            f"`{evidence.get('m7_capability_family_count')}` / "
            f"`{evidence.get('minimum_m7_capability_families_for_major_release')}`"
        ),
        f"- Missing M7 capability families: `{', '.join(evidence.get('missing_m7_capability_families', []))}`",
        f"- Route-map M7 rows: `{evidence.get('route_map_m7_qualified_release_rows')}`",
        f"- Supplemental M7 rows: `{evidence.get('supplemental_m7_qualified_release_rows')}`",
        f"- App-boundary attributed rows: `{evidence.get('apps_with_m7_row_count')}` / `{evidence.get('app_boundary_m7_rows')}`",
        f"- Unattributed app-boundary rows: `{evidence.get('unattributed_app_boundary_m7_row_count')}`",
        f"- Existing evidence promotable now: `{str(evidence.get('existing_evidence_promotable_now')).lower()}`",
        f"- Pending external-review candidates: `{evidence.get('pending_external_review_candidate_count')}`",
        f"- Accepted-with-boundary candidates: `{evidence.get('accepted_with_boundary_candidate_count')}`",
        f"- Surface row integrity rows: `{evidence.get('surface_row_integrity_row_count')}`",
        f"- Surface row paths all exist: `{str(evidence.get('surface_row_integrity_all_paths_exist')).lower()}`",
        (
            "- Surface row unsupported-claim flags blocked: "
            f"`{str(evidence.get('surface_row_integrity_all_flags_block_unsupported_claims')).lower()}`"
        ),
        (
            "- Surface rows are generic capability rows: "
            f"`{str(evidence.get('surface_row_integrity_all_rows_are_generic_capability_rows')).lower()}`"
        ),
        "",
        "## Missing Capability Future-Work Map",
        "",
        "| Missing planned capability | Future work ID | Queue capability |",
        "| --- | --- | --- |",
    ]
    for capability, item in evidence.get("missing_capability_future_work_map", {}).items():
        lines.append(
            f"| `{capability}` | `{item.get('future_research_work_id')}` | `{item.get('queue_generic_capability')}` |"
        )

    lines.extend(
        [
            "",
            "## M7 Rows By Capability",
            "",
            "| Capability | Rows |",
            "| --- | ---: |",
        ]
    )
    for capability, rows in evidence.get("m7_rows_by_capability", {}).items():
        lines.append(f"| `{capability}` | {len(rows)} |")

    lines.extend(
        [
            "",
            "## Blocking Reasons",
            "",
        ]
    )
    lines.extend(f"- `{reason}`" for reason in payload.get("blocking_reasons", []))

    lines.extend(
        [
            "",
            "## Required Next Actions",
            "",
        ]
    )
    lines.extend(f"- {action}" for action in payload.get("required_next_actions", []))

    audit = payload.get("decision_audit", {})
    lines.extend(
        [
            "",
            "## Goal-Level Decision Self-Audit",
            "",
            f"- Decision: {audit.get('decision')}",
            f"- Was I foolish? {audit.get('was_i_foolish')}",
            f"- Foolish actions: {audit.get('foolish_actions')}",
            f"- Other path: {audit.get('other_path')}",
            f"- Different path now: {audit.get('different_path_now')}",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phoenix V3 release-surface breadth gate.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(text)
    return 2 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
