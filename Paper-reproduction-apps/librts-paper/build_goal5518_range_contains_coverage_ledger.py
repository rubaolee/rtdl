from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
APP = ROOT / "Paper-reproduction-apps" / "librts-paper"
RESULTS = APP / "results"


def main() -> None:
    inventory = json.loads(
        (RESULTS / "librts_goal5492_exact_archive_operation_inventory.json").read_text(encoding="utf-8")
    )
    gate = json.loads((RESULTS / "goal5517_exact_range_contains_batch_gate.json").read_text(encoding="utf-8"))
    matched = {
        (
            case["input_identity"]["geometry_path"].split("/PPoPPAE/", 1)[1],
            case["input_identity"]["query_path"].split("/PPoPPAE/", 1)[1],
        ): case
        for case in gate["cases"]
    }
    cases = []
    for pair in inventory["inventory"]["exact_pairs"]["range_contains"]:
        key = (pair["geometry"].split("PPoPPAE/", 1)[1], pair["query"].split("PPoPPAE/", 1)[1])
        case = {
            "geometry": pair["geometry"],
            "query": pair["query"],
            "status": "matched" if key in matched else "not_checkpointed",
        }
        if key in matched:
            case["evidence_source"] = "results/goal5517_exact_range_contains_batch_gate.json"
            case["author_rtdl_count"] = matched[key]["author"]["result_count"]
        cases.append(case)
    counts = {name: sum(case["status"] == name for case in cases) for name in ("matched", "not_checkpointed")}
    if len(cases) != 14 or counts != {"matched": 4, "not_checkpointed": 10}:
        raise ValueError(f"unexpected coverage: {len(cases)} {counts}")
    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5518_range_contains_coverage_ledger.v1",
        "status": "range_contains_exact_archive_coverage_reconciled",
        "operation": "range_contains",
        "inventory_source": "results/librts_goal5492_exact_archive_operation_inventory.json",
        "exact_archive_pair_count": 14,
        "status_counts": counts,
        "cases": cases,
        "remaining_work_classification": {
            "parks_Europe_query_cardinality_variants": 4,
            "parks_bz2_query_cardinality_variants": 5,
            "large_geometry_100000_cases": 2,
            "lakes_bz2_100000_case": 1,
            "note": "All ten entries require new checkpoints; large parks/lakes cases require independent capacity handling.",
        },
        "claim_boundary": {
            "coverage_ledger_only": True,
            "complete_range_contains_matrix_claimed": False,
            "pointwise_containment_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "device_zero_copy_claimed": False,
            "author_performance_parity_claimed": False,
            "embree_in_scope": False,
        },
    }
    output = RESULTS / "goal5518_range_contains_coverage_ledger.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
