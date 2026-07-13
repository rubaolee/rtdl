from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def case_id(geometry: str, query: str) -> str:
    geometry_name = Path(geometry).name.removesuffix(".wkt")
    family = Path(query).parent.name
    return f"{geometry_name}_{family}"


def main() -> None:
    inventory = json.loads(
        (RESULTS / "librts_goal5492_exact_archive_operation_inventory.json").read_text(
            encoding="utf-8"
        )
    )
    observed = {
        "parks_Europe_range-intersects_select_0.01_queries_10000": {
            "status": "matched",
            "source": "results/goal5514_exact_range_intersects_select001_resolution_gate.json",
            "count": 216977211,
        },
        "dtl_cnty_range-intersects_select_0.01_queries_10000": {
            "status": "matched",
            "source": "results/goal5514_exact_range_intersects_select001_resolution_gate.json",
            "count": 1570285,
        },
        "lakes.bz2_range-intersects_select_0.01_queries_10000": {
            "status": "matched",
            "source": "results/goal5514_exact_range_intersects_select001_resolution_gate.json",
            "count": 1113229623,
        },
        "USACensusBlockGroupBoundaries_range-intersects_select_0.01_queries_10000": {
            "status": "matched",
            "source": "results/goal5514_exact_range_intersects_select001_resolution_gate.json",
            "count": 33404355,
        },
        "USADetailedWaterBodies_range-intersects_select_0.01_queries_10000": {
            "status": "matched",
            "source": "results/goal5514_exact_range_intersects_select001_resolution_gate.json",
            "count": 55205607,
        },
        "parks.bz2_range-intersects_select_0.01_queries_10000": {
            "status": "author_capacity_failure",
            "source": "results/goal5514_parks_bz2_select001_10000.json",
        },
    }
    pairs = inventory["inventory"]["exact_pairs"]["range_intersects"]
    for pair in pairs:
        geometry, query = pair["geometry"], pair["query"]
        identifier = case_id(geometry, query)
        if identifier in observed:
            continue
        if "range-intersects_select_0.0001_queries_10000" in query:
            name = Path(geometry).name.removesuffix(".wkt")
            observed_key = f"{name}_range-intersects_select_0.0001_queries_10000"
            if observed_key in {
                "parks_Europe_range-intersects_select_0.0001_queries_10000",
                "dtl_cnty_range-intersects_select_0.0001_queries_10000",
                "USACensusBlockGroupBoundaries_range-intersects_select_0.0001_queries_10000",
                "USADetailedWaterBodies_range-intersects_select_0.0001_queries_10000",
            }:
                observed[identifier] = {
                    "status": "matched",
                    "source": "results/goal5509_exact_range_intersects_next_batch_gate.json",
                }
            elif observed_key == "lakes.bz2_range-intersects_select_0.0001_queries_10000":
                observed[identifier] = {
                    "status": "matched",
                    "source": "results/goal5512_lakes_bz2_select0001_10000.json",
                    "count": 10579596,
                }
            elif observed_key == "parks.bz2_range-intersects_select_0.0001_queries_10000":
                observed[identifier] = {
                    "status": "author_capacity_failure",
                    "source": "results/goal5512_parks_bz2_select0001_10000.json",
                }
        elif "range-intersects_select_0.001_queries_10000" in query:
            name = Path(geometry).name.removesuffix(".wkt")
            if name in {"parks_Europe", "dtl_cnty", "USACensusBlockGroupBoundaries", "USADetailedWaterBodies"}:
                observed[identifier] = {
                    "status": "matched",
                    "source": "results/goal5511_exact_range_intersects_select0001_gate.json",
                }

    cases = []
    for pair in pairs:
        geometry, query = pair["geometry"], pair["query"]
        identifier = case_id(geometry, query)
        entry = {
            "case_id": identifier,
            "geometry": geometry,
            "query": query,
            "status": observed.get(identifier, {}).get("status", "not_checkpointed"),
        }
        if identifier in observed:
            entry["evidence_source"] = observed[identifier]["source"]
            if "count" in observed[identifier]:
                entry["author_rtdl_count"] = observed[identifier]["count"]
        cases.append(entry)

    counts = {}
    for entry in cases:
        counts[entry["status"]] = counts.get(entry["status"], 0) + 1
    if len(cases) != 42 or counts.get("matched", 0) != 14 or counts.get("author_capacity_failure", 0) != 2:
        raise ValueError(f"unexpected ledger counts: {len(cases)} {counts}")
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5516_range_intersects_coverage_ledger.v1",
        "status": "range_intersects_exact_archive_coverage_reconciled",
        "inventory_source": "results/librts_goal5492_exact_archive_operation_inventory.json",
        "operation": "range_intersects",
        "exact_archive_pair_count": len(cases),
        "status_counts": counts,
        "cases": cases,
        "claim_boundary": {
            "coverage_ledger_only": True,
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "device_zero_copy_claimed": False,
            "author_performance_parity_claimed": False,
            "embree_in_scope": False,
        },
        "interpretation": "Fourteen exact same-input count matches and two author capacity failures are checkpointed across the inventory; twenty-six pairs remain not checkpointed. The ledger does not infer semantics from absent inputs or from count-only evidence.",
    }
    output = RESULTS / "goal5516_range_intersects_coverage_ledger.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
