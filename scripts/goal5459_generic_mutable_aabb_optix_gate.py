from __future__ import annotations

import argparse
import json
import platform
from pathlib import Path

import rtdsl as rt


def run_gate(*, environment_label: str, gpu_label: str) -> dict[str, object]:
    query = ((0.25, 0.25, 0.75, 0.75),)
    index = rt.prepare_mutable_aabb_index_2d(
        ((0.0, 0.0, 1.0, 1.0), (0.5, 0.5, 1.5, 1.5)),
        indexed_ids=(10, 20),
        backend="optix",
    )
    revisions: list[dict[str, object]] = []

    def capture(label: str) -> None:
        rows = index.intersection_rows(query, query_ids=(900,), row_capacity=8)
        revisions.append(
            {
                "label": label,
                "revision": index.revision,
                "active_ids": list(index.active_ids),
                "rows": [list(row) for row in rows],
            }
        )

    capture("initial")
    index.update(((20, (5.0, 5.0, 6.0, 6.0)),))
    capture("after_update")
    index.delete((10,))
    capture("after_delete")
    index.insert(((0.4, 0.4, 0.6, 0.6),), ids=(30,))
    capture("after_insert")
    metadata_before_clear = index.metadata()
    index.clear()
    empty_count = index.count(operation="range_intersects")["counts"]["range_intersects"]
    metadata_after_clear = index.metadata()
    index.close()

    expected_rows = [
        [[900, 10], [900, 20]],
        [[900, 10]],
        [],
        [[900, 30]],
    ]
    matched = [row["rows"] for row in revisions] == expected_rows and empty_count == 0
    return {
        "schema": "rtdl.generic_mutable_aabb.optix_snapshot_rebuild_gate.v1",
        "status": "matched" if matched else "mismatch",
        "matched": matched,
        "environment": {
            "label": environment_label,
            "host": platform.node(),
            "platform": platform.platform(),
            "gpu": gpu_label,
        },
        "contract": rt.MUTABLE_AABB_INDEX_2D_CONTRACT,
        "revisions": revisions,
        "metadata_before_clear": metadata_before_clear,
        "metadata_after_clear": metadata_after_clear,
        "empty_count_after_clear": empty_count,
        "claim_boundary": {
            "generic_semantic_parity_only": True,
            "native_incremental_mutation_claimed": False,
            "performance_claimed": False,
            "paper_reproduction_claimed": False,
            "app_specific_semantics_claimed": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Goal5459 mutable AABB OptiX gate")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--environment-label", default="unspecified")
    parser.add_argument("--gpu-label", default="unspecified")
    args = parser.parse_args()
    payload = run_gate(environment_label=args.environment_label, gpu_label=args.gpu_label)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
