from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt
from examples.reference.rtdl_knn_rows_reference import knn_rows_reference
from examples.reference.rtdl_knn_rows_reference import make_knn_rows_authored_case


def run_case(backend: str) -> dict[str, object]:
    case = make_knn_rows_authored_case()
    if backend == "cpu_python_reference":
        rows = rt.run_cpu_python_reference(knn_rows_reference, **case)
    elif backend == "cpu":
        rows = rt.run_cpu(knn_rows_reference, **case)
    elif backend == "embree":
        rows = rt.run_embree(knn_rows_reference, **case)
    else:
        raise ValueError(f"unsupported backend `{backend}`")

    grouped: dict[int, list[dict[str, object]]] = {}
    for row in rows:
        grouped.setdefault(int(row["query_id"]), []).append(
            {
                "neighbor_id": int(row["neighbor_id"]),
                "neighbor_rank": int(row["neighbor_rank"]),
                "distance": float(row["distance"]),
            }
        )

    return {
        "app": "knn_rows",
        "backend": backend,
        "k": 3,
        "query_count": len(case["query_points"]),
        "search_count": len(case["search_points"]),
        "rows": rows,
        "neighbors_by_query": grouped,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Release-facing k-nearest-neighbor example for the v0.4 nearest-neighbor line."
    )
    parser.add_argument(
        "--backend",
        choices=("cpu_python_reference", "cpu", "embree"),
        default="cpu_python_reference",
    )
    args = parser.parse_args(argv)
    print(json.dumps(run_case(args.backend), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
