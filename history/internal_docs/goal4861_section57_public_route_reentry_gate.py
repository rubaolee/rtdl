from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INTERNAL = ROOT / "history" / "internal_docs"


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _extract_author_pip_diag(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8", errors="replace")
    match = re.search(
        r"AUTHORPATCH_PIP_DIAG\s+query_points=(\d+)\s+positive_count=(\d+)\s+"
        r"closest_eids_fnv64=(\d+)\s+dontknow_value=(\d+)",
        text,
    )
    if not match:
        raise RuntimeError(f"AUTHORPATCH_PIP_DIAG line not found in {path}")
    return {
        "query_points": int(match.group(1)),
        "positive_count": int(match.group(2)),
        "closest_eids_fnv64": int(match.group(3)),
        "dontknow_value": int(match.group(4)),
    }


def main() -> None:
    county_lsi = _load_json(INTERNAL / "goal4860_county_zipcode_lsi_row_gate_summary.json")
    au_lsi = _load_json(INTERNAL / "goal4860_au_lsi_row_gate_summary.json")
    county_pip = _load_json(
        INTERNAL / "goal4856_section53_pip_consistency" / "county_zipcode_rtdl_raw.json"
    )
    author_pip = _extract_author_pip_diag(
        INTERNAL / "goal4856_section53_pip_consistency" / "county_zipcode_author_diag.stderr"
    )

    init_text = (ROOT / "src" / "rtdsl" / "__init__.py").read_text(encoding="utf-8")
    optix_text = (ROOT / "src" / "rtdsl" / "optix_runtime.py").read_text(encoding="utf-8")
    public_exports = {
        "prepare_planar_map_lsi_2d_optix": "prepare_planar_map_lsi_2d_optix" in init_text,
        "prepare_planar_map_point_location_2d_optix": "prepare_planar_map_point_location_2d_optix" in init_text,
        "assemble_output_chains": "assemble_output_chains" in init_text,
        "write_output_chains": "write_output_chains" in init_text,
    }

    county_first_row_keys = sorted((county_lsi.get("first_rows") or [{}])[0].keys())
    lsi_scaled_fields = [
        "intersection_scaled_x",
        "intersection_scaled_y",
        "intersection_scaled_x_rational",
        "intersection_scaled_y_rational",
    ]
    has_scaled_or_rational_lsi_rows = any(field in county_first_row_keys for field in lsi_scaled_fields)

    lsi_count_ok = (
        county_lsi["planar_map_lsi_count"] == county_lsi["planar_map_lsi_row_count"] == county_lsi["expected"]
        and au_lsi["planar_map_lsi_count"] == au_lsi["planar_map_lsi_row_count"] == au_lsi["expected"]
    )
    pip_count_ok = (
        int(county_pip["total_points"]) == author_pip["query_points"]
        and int(county_pip["segment_found_count"]) == author_pip["positive_count"]
    )
    pip_hash_ok = int(county_pip["segment_hash_minus1_fnv64"]) == author_pip["closest_eids_fnv64"]

    output_chain_public_surface_ok = bool(public_exports["assemble_output_chains"] or public_exports["write_output_chains"])
    preferred_route_can_claim_byte_equal = bool(
        lsi_count_ok
        and pip_count_ok
        and pip_hash_ok
        and output_chain_public_surface_ok
        and has_scaled_or_rational_lsi_rows
    )

    if preferred_route_can_claim_byte_equal:
        preferred_route_status = "ready_for_public_app_layer_overlay_byte_compare"
        exit_label = "ready_to_execute_section57_public_generic_route_byte_compare"
    else:
        preferred_route_status = "blocked_after_public_lsi_and_pip"
        exit_label = "blocked_by_output_chain_app_logic_gap"

    summary = {
        "schema": "rtdl.goal4861.section57_public_route_reentry_gate.v1",
        "route_label": "generic_public_primitives_plus_app_layer",
        "claim_boundary": {
            "section52_lsi_rows": True,
            "section53_pip_consistency_for_county_zipcode": True,
            "section57_overlay_correctness": False,
            "section57_performance": False,
            "bundled_helper_route": False,
        },
        "lsi_stage": {
            "county_zipcode": {
                "expected": county_lsi["expected"],
                "count": county_lsi["planar_map_lsi_count"],
                "rows": county_lsi["planar_map_lsi_row_count"],
                "pass": county_lsi["rows_equal_expected"] and county_lsi["rows_equal_count"],
            },
            "australia_representative": {
                "expected": au_lsi["expected"],
                "count": au_lsi["planar_map_lsi_count"],
                "rows": au_lsi["planar_map_lsi_row_count"],
                "pass": au_lsi["rows_equal_expected"] and au_lsi["rows_equal_count"],
            },
            "first_row_keys": county_first_row_keys,
            "has_scaled_or_rational_row_fields": has_scaled_or_rational_lsi_rows,
            "pass": lsi_count_ok,
        },
        "pip_stage": {
            "county_zipcode": {
                "author_query_points": author_pip["query_points"],
                "rtdl_total_points": county_pip["total_points"],
                "author_positive_count": author_pip["positive_count"],
                "rtdl_segment_found_count": county_pip["segment_found_count"],
                "author_closest_eids_fnv64": author_pip["closest_eids_fnv64"],
                "rtdl_segment_hash_minus1_fnv64": county_pip["segment_hash_minus1_fnv64"],
                "count_match": pip_count_ok,
                "hash_match": pip_hash_ok,
            },
            "pass": pip_count_ok and pip_hash_ok,
        },
        "public_surface": {
            "exports": public_exports,
            "optix_runtime_has_private_rayjoin_overlay_import": "import rtdsl.rayjoin_overlay" in optix_text
            or "from .rayjoin_overlay" in optix_text,
            "public_lsi_and_pip_available": public_exports["prepare_planar_map_lsi_2d_optix"]
            and public_exports["prepare_planar_map_point_location_2d_optix"],
            "public_output_chain_assembler_available": output_chain_public_surface_ok,
        },
        "blocker_analysis": {
            "preferred_route_status": preferred_route_status,
            "exit_label": exit_label,
            "reason": (
                "Public LSI rows and County x Zipcode PIP consistency are available, "
                "but the public user surface does not expose an output-chain assembler "
                "and the public LSI row surface does not expose scaled/rational "
                "intersection coordinates needed for an author-compatible byte-equality "
                "output-chain implementation."
            ),
        },
        "allowed_next_step": {
            "fallback_bundled_helper_compare": True,
            "fallback_label_required": "bounded_bundled_helper_reproduction",
            "must_not_claim": [
                "generic public-language Section 5.7 reproduction",
                "Section 5.7 performance",
                "full 8/8 paper reproduction",
            ],
        },
    }
    out = INTERNAL / "goal4861_section57_public_route_reentry_gate_summary.json"
    out.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
