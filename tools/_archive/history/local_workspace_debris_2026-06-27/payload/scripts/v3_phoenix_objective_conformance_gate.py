#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    import v3_phoenix_release_surface_breadth_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_phoenix_release_surface_breadth_gate

try:
    import v3_release_wording_gate
except ModuleNotFoundError:  # pragma: no cover - exercised by unittest import path.
    from scripts import v3_release_wording_gate


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON_OUT = (
    ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_objective_conformance_gate_2026-06-22.json"
)

OBJECTIVE_CAPABILITY_REQUIREMENTS = {
    "raydb_grouped_reduction": {
        "capability": "grouped_reduction",
        "min_rows": 3,
        "objective": "RayDB-style grouped reductions must be represented by reusable grouped-reduction rows.",
    },
    "rtdbscan_component_union": {
        "capability": "component_union",
        "min_rows": 1,
        "objective": "RTDBSCAN must expose the reusable component-union capability, not only an app demo.",
    },
    "spatial_rayjoin_topology_stream": {
        "capability": "point_location_topology_stream",
        "min_rows": 1,
        "objective": "Spatial RayJoin must close the topology-stream route at current default-path scope.",
    },
    "triangle_prepared_graph": {
        "capability": "prepared_graph_chunk",
        "min_rows": 1,
        "objective": "Triangle counting must be represented by the prepared-graph chunk executor route.",
    },
    "rtnn_ranked_summary": {
        "capability": "ranked_summary",
        "min_rows": 1,
        "objective": "RTNN must expose ranked-summary evidence through the prepared NPZ/CUBIN route.",
    },
}

ADDITIONAL_CURRENT_CAPABILITIES = (
    "aabb_candidate_stream",
    "aggregate_frontier",
    "collision_flag_stream",
    "threshold_summary",
)

REQUIRED_FALSE_CLAIM_FLAGS = (
    "release_authorized",
    "public_speedup_claim_authorized",
    "broad_v3_faster_than_v2_claim_authorized",
    "package_install_claim_authorized",
    "multi_gpu_performance_portability_claim_authorized",
    "secondary_rt_performance_confirmation_authorized",
)


def _objective_coverage(rows_by_capability: dict[str, list[str]]) -> dict[str, dict[str, Any]]:
    coverage: dict[str, dict[str, Any]] = {}
    for objective_id, requirement in OBJECTIVE_CAPABILITY_REQUIREMENTS.items():
        capability = str(requirement["capability"])
        rows = sorted(rows_by_capability.get(capability, []))
        min_rows = int(requirement["min_rows"])
        coverage[objective_id] = {
            "objective": requirement["objective"],
            "capability": capability,
            "min_rows": min_rows,
            "row_count": len(rows),
            "row_ids": rows,
            "covered": len(rows) >= min_rows,
        }
    return coverage


def _claim_flags_all_false(claim_flags: dict[str, Any]) -> bool:
    return all(claim_flags.get(flag) is False for flag in REQUIRED_FALSE_CLAIM_FLAGS)


def build_payload() -> dict[str, Any]:
    surface_payload = v3_phoenix_release_surface_breadth_gate.build_payload()
    wording_payload = v3_release_wording_gate.build_payload()

    surface_evidence = surface_payload.get("evidence", {})
    rows_by_capability = surface_evidence.get("m7_rows_by_capability", {})
    objective_coverage = _objective_coverage(rows_by_capability)
    covered_objectives = [
        objective_id for objective_id, item in objective_coverage.items() if item.get("covered") is True
    ]
    claim_flags = wording_payload.get("claim_flags_required_false", {})

    checks = {
        "release_surface_gate_passed_not_release": (
            surface_payload.get("status") == "surface_breadth_passed_not_release"
        ),
        "release_surface_has_13_rows": surface_evidence.get("total_m7_row_count") == 13,
        "release_surface_has_9_capabilities": surface_evidence.get("m7_capability_family_count") == 9,
        "release_surface_missing_capabilities_none": (
            surface_evidence.get("missing_m7_capability_families") == []
        ),
        "objective_required_capabilities_all_covered": len(covered_objectives)
        == len(OBJECTIVE_CAPABILITY_REQUIREMENTS),
        "surface_rows_all_generic": (
            surface_evidence.get("surface_row_integrity_all_rows_are_generic_capability_rows") is True
        ),
        "surface_rows_all_paths_exist": surface_evidence.get("surface_row_integrity_all_paths_exist") is True,
        "surface_rows_block_unsupported_claims": (
            surface_evidence.get("surface_row_integrity_all_flags_block_unsupported_claims") is True
        ),
        "app_boundary_rows_are_attributed": (
            surface_evidence.get("unattributed_app_boundary_m7_row_count") == 0
        ),
        "wording_gate_pass": wording_payload.get("status") == "pass",
        "wording_claim_flags_required_false": _claim_flags_all_false(claim_flags),
        "no_objective_gate_or_public_speedup_authorized": (
            surface_payload.get("release_authorized") is False
            and wording_payload.get("release_authorized") is False
            and surface_payload.get("public_speedup_claim_authorized") is False
            and surface_payload.get("broad_v3_faster_than_v2_claim_authorized") is False
            and wording_payload.get("public_speedup_claim_authorized") is False
            and wording_payload.get("broad_v3_faster_than_v2_claim_authorized") is False
            and claim_flags.get("broad_v3_faster_than_v2_claim_authorized") is False
        ),
        "v4_cabi_embedding_out_of_v3_public_surface": (
            wording_payload.get("status") == "pass"
            and claim_flags.get("release_authorized") is False
            and claim_flags.get("package_install_claim_authorized") is False
        ),
        "broad_v2_speedup_claim_out": (
            claim_flags.get("broad_v3_faster_than_v2_claim_authorized") is False
        ),
    }
    for objective_id, item in objective_coverage.items():
        checks[f"objective_{objective_id}_covered"] = item.get("covered") is True

    failed_checks = [name for name, passed in checks.items() if not passed]
    status = "objective_conformance_passed_not_release" if not failed_checks else "fail"

    return {
        "tool": "v3_phoenix_objective_conformance_gate",
        "gate": "phoenix_v3_goal_conformance_contract",
        "status": status,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "broad_v3_faster_than_v2_claim_authorized": False,
        "blocking_reasons": [
            "release_authorization_false",
            "updated_thirteen_row_release_readiness_consensus_required",
        ]
        if status != "fail"
        else [],
        "failed_checks": failed_checks,
        "checks": checks,
        "evidence": {
            "objective_capability_requirements": objective_coverage,
            "objective_required_capability_coverage_count": len(covered_objectives),
            "objective_required_capability_count": len(OBJECTIVE_CAPABILITY_REQUIREMENTS),
            "objective_required_capabilities_covered": covered_objectives,
            "current_surface_total_m7_row_count": surface_evidence.get("total_m7_row_count"),
            "current_surface_capability_family_count": surface_evidence.get("m7_capability_family_count"),
            "current_surface_capability_families": surface_evidence.get("m7_capability_families", []),
            "additional_current_capabilities": list(ADDITIONAL_CURRENT_CAPABILITIES),
            "future_research_work_ids": surface_evidence.get("future_research_work_ids", []),
            "future_research_capabilities": surface_evidence.get("future_research_capabilities", []),
            "surface_row_integrity_all_rows_are_generic_capability_rows": surface_evidence.get(
                "surface_row_integrity_all_rows_are_generic_capability_rows"
            ),
            "surface_row_integrity_all_paths_exist": surface_evidence.get(
                "surface_row_integrity_all_paths_exist"
            ),
            "surface_row_integrity_all_flags_block_unsupported_claims": surface_evidence.get(
                "surface_row_integrity_all_flags_block_unsupported_claims"
            ),
            "app_boundary_note": (
                "App-boundary rows may be attributed to benchmark apps, but Phoenix V3 release scope is "
                "capability-bound and every current surface row must be a generic capability row."
            ),
            "exclusions": {
                "app_specific_native_engines": (
                    "not a release surface category; current rows are generic capability rows"
                ),
                "v4_c_abi_embedding": "out of V3 public surface by wording gate and claim-boundary scan",
                "public_sdk_packaging": "out of current V3 public claims",
                "broad_v3_over_v2_speedup_claim": "not authorized",
                "unsupported_public_wording": "blocked by final public-surface wording gate",
            },
            "wording_gate_status": wording_payload.get("status"),
            "wording_gate_violation_count": len(wording_payload.get("violations", [])),
            "claim_flags_required_false": claim_flags,
            "release_surface_breadth_status": surface_payload.get("status"),
        },
        "required_next_actions": [
            "Use this gate as a required input to Phoenix V3 release readiness.",
            "Do not treat objective conformance as a standalone release authority.",
            "Do not convert row-scoped objective coverage into broad V3-over-V2 speedup wording.",
        ],
        "decision_audit": _decision_audit(),
    }


def _decision_audit() -> dict[str, str]:
    return {
        "decision": "Add an objective conformance gate that maps Phoenix V3 goals to exact reusable capability evidence while keeping release blocked until the major performance mandate passes.",
        "was_i_foolish": "No. This fixes the risk that a broad 13-row surface can pass without explicitly proving the user-facing V3 objective coverage.",
        "foolish_actions": "The foolish action would be to keep relying on prose summaries or app labels when the release gate can demand exact capability coverage and explicit exclusions.",
        "other_path": "Only update the dossier text. That would be easier, but future agents could still drift because readiness would not enforce the mapping.",
        "different_path_now": "Make objective conformance machine-checkable, wire it into readiness, and keep release plus broad/public claim flags false until serious all-app V3-vs-V2.x evidence proves the runtime case.",
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phoenix V3 objective conformance gate.")
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--pretty", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = build_payload()
    text = json.dumps(payload, indent=2 if args.pretty else None, sort_keys=True)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    print(text)
    return 2 if payload["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
