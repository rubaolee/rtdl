from __future__ import annotations

import json
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").is_dir())
RESULTS = ROOT / "Paper-reproduction-apps" / "librts-paper" / "results"


def _read(name: str) -> dict[str, object]:
    return json.loads((RESULTS / name).read_text(encoding="utf-8"))


def main() -> None:
    point = _read("goal5523_parks_europe_point_contains_cardinality_gate.json")
    contains = _read("goal5521_parks_bz2_range_contains_cardinality_gate.json")
    intersects = _read("goal5516_range_intersects_coverage_ledger.json")
    pip = _read("librts_goal5467_representative_same_input_pip.json")
    mutation = _read("librts_goal5462_native_sparse_refit_mutation.json")

    if point["coverage"]["matched_after_goal5523"] != 14 or point["coverage"]["remaining_not_checkpointed"] != 0:
        raise ValueError("point-contains exact count matrix is incomplete")
    if contains["coverage"]["matched_after_goal5521"] != 14 or contains["coverage"]["remaining_not_checkpointed"] != 0:
        raise ValueError("range-contains exact count matrix is incomplete")
    if intersects["status_counts"] != {"author_capacity_failure": 2, "matched": 14, "not_checkpointed": 26}:
        raise ValueError("range-intersects ledger changed")
    if not (pip["matched"] and pip["comparison"]["pair_rows_equal"] and pip["comparison"]["canonical_row_sha256_equal"]):
        raise ValueError("representative PIP relation gate is incomplete")
    if not mutation["matched"] or mutation["comparison"]["counts"] != [2, 1, 0, 1, 0]:
        raise ValueError("bounded mutation gate is incomplete")

    payload = {
        "schema": "rtdl.paper_reproduction.librts.goal5524_system_value_closeout.v1",
        "status": "librts_scoped_correctness_and_system_extraction_complete__review_pending",
        "completion_scope": {
            "librts_scoped_correctness_and_system_extraction_complete": True,
            "full_all_dataset_all_figure_paper_reproduction_complete": False,
            "performance_parity_complete": False,
            "embree_in_scope": False,
        },
        "evidence_matrix": {
            "point_contains": {
                "exact_archive_pair_count": 14,
                "exact_count_matches": 14,
                "pointwise_relation_claimed": False,
            },
            "range_contains": {
                "exact_archive_pair_count": 14,
                "exact_count_matches": 14,
                "pointwise_relation_claimed": False,
            },
            "range_intersects": {
                "exact_archive_pair_count": 42,
                "exact_count_matches": 14,
                "author_capacity_failures": 2,
                "not_checkpointed": 26,
                "complete_matrix_claimed": False,
                "pointwise_relation_claimed": False,
            },
            "pip": {
                "scope": "representative_same_input_app_instrumented_relation_gate",
                "canonical_pair_rows_matched": int(pip["comparison"]["rtdl_result_count"]),
                "pair_rows_equal": True,
                "exact_archive_pair_available": False,
            },
            "mutation": {
                "scope": "bounded_same_input_operation_sequence",
                "author_rtdl_counts": mutation["comparison"]["counts"],
                "matched": True,
            },
        },
        "system_improvements": [
            "generic Aabb2DColumns public front door",
            "generic prepared AABB count operations",
            "generic mutable AABB index with stable IDs",
            "generic native fixed-cardinality and sparse-slot refit",
            "rollback recovery and persistent fail-closed invalidation gates",
            "operation-scoped packed AABB validity semantics",
            "app-neutral prepared-column and batch reuse contracts",
        ],
        "app_owned_work": [
            "official archive provenance and extraction",
            "WKT parsing and derived cache construction",
            "paper-specific wrappers, case matrices, comparators, and tolerances",
            "author log and figure-denominator mapping",
        ],
        "stop_loss": {
            "decision": "freeze_exhaustive_range_intersects_enumeration",
            "reason": "remaining combinations repeat an already validated generic operation and produce no new system capability",
            "generic_capability_produced_by_more_matrix_rows": False,
            "unique_unresolved_semantic_question": False,
            "preserve_uncheckpointed_as_uncheckpointed": True,
            "reopen_only_if": [
                "a new semantic disagreement appears",
                "a denominator-aligned paper figure objective is explicitly authorized",
                "a new generic system capability with a non-LibRTS consumer is proposed",
            ],
        },
        "claim_boundary": {
            "full_paper_reproduction_claimed": False,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
            "author_algorithm_equivalence_claimed": False,
            "all_range_intersects_pairs_claimed": False,
            "pointwise_contains_relation_equivalence_claimed": False,
            "device_zero_copy_claimed": False,
            "embree_in_scope": False,
        },
    }
    output = RESULTS / "goal5524_librts_system_value_closeout.json"
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
