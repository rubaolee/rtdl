from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import rtdsl as rt


EXPECTED_COUNTS = [2, 1, 0, 1, 0]


def run_rtdl_sequence(*, backend: str) -> dict[str, object]:
    query = ((0.25, 0.25, 0.75, 0.75),)
    index = rt.prepare_mutable_aabb_index_2d(
        ((0.0, 0.0, 1.0, 1.0), (0.5, 0.5, 1.5, 1.5)),
        indexed_ids=(0, 1),
        backend=backend,
    )
    counts: list[int] = []
    mutation_results: list[dict[str, object]] = []

    def capture() -> None:
        counts.append(len(index.intersection_rows(query, query_ids=(0,), row_capacity=8)))

    try:
        capture()
        mutation_results.append(index.update(((1, (5.0, 5.0, 6.0, 6.0)),)))
        capture()
        mutation_results.append(index.delete((0,)))
        capture()
        insert_result = index.insert(((0.4, 0.4, 0.6, 0.6),))
        mutation_results.append(insert_result)
        inserted_ids = list(insert_result["inserted_ids"])
        capture()
        mutation_results.append(index.clear())
        capture()
        return {
            "backend": backend,
            "counts": counts,
            "expected": EXPECTED_COUNTS,
            "inserted_ids": inserted_ids,
            "metadata": index.metadata(),
            "mutation_execution_models": [
                str(result["mutation_execution_model"]) for result in mutation_results
            ],
            "matched": counts == EXPECTED_COUNTS and inserted_ids == [2],
        }
    finally:
        index.close()


def load_author_probe(path: Path) -> dict[str, object]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    candidates = [line for line in lines if line.startswith("{") and line.endswith("}")]
    if not candidates:
        raise ValueError("author probe output contains no JSON object")
    payload = json.loads(candidates[-1])
    if payload.get("schema") != "librts.author_mutation_probe.v1":
        raise ValueError("unexpected author mutation probe schema")
    return payload


def run_gate(*, author_probe_output: Path, backend: str) -> dict[str, object]:
    author = load_author_probe(author_probe_output)
    rtdl = run_rtdl_sequence(backend=backend)
    matched = bool(
        author.get("matched")
        and rtdl["matched"]
        and author.get("counts") == rtdl["counts"] == EXPECTED_COUNTS
        and author.get("implicit_inserted_id") == rtdl["inserted_ids"][0] == 2
    )
    return {
        "schema": "librts.same_input_mutation_gate.v1",
        "status": "matched" if matched else "mismatch",
        "matched": matched,
        "environment": {
            "host": platform.node(),
            "platform": platform.platform(),
        },
        "operation_sequence": [
            "insert_initial",
            "query",
            "update_id_1",
            "query",
            "delete_id_0",
            "query",
            "insert_auto_id_2",
            "query",
            "clear",
            "query",
        ],
        "author": author,
        "rtdl": rtdl,
        "comparison": {
            "same_geometry_and_query_sequence": True,
            "same_implicit_id_sequence": True,
            "same_result_counts": author.get("counts") == rtdl["counts"],
            "counts": EXPECTED_COUNTS,
        },
        "execution_model_difference": {
            "author": "native_incremental_gas_ias_update",
            "rtdl": (
                "native_sparse_slot_refit_for_update__"
                "atomic_snapshot_rebuild_for_insert_delete_clear"
                if backend == "optix"
                else "atomic_snapshot_rebuild"
            ),
            "performance_comparison_authorized": False,
        },
        "claim_boundary": {
            "bounded_same_input_mutation_semantics_claimed": matched,
            "native_incremental_rtdl_update_claimed": backend == "optix" and matched,
            "native_incremental_rtdl_insert_delete_claimed": False,
            "mutation_performance_parity_claimed": False,
            "paper_figure_reproduction_claimed": False,
            "full_paper_reproduction_claimed": False,
            "embree_used": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="LibRTS same-input mutation gate")
    parser.add_argument("--author-probe-output", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--backend", choices=("cpu", "optix"), default="optix")
    args = parser.parse_args()
    payload = run_gate(author_probe_output=args.author_probe_output, backend=args.backend)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
