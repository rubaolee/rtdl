from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_exact_range_intersects_count_gate import run_gate


def run_batch(
    *,
    author_binary: Path,
    ae_root: Path,
    cases: list[dict[str, str]],
    archive_result: dict[str, object],
    extraction_result: dict[str, object],
    author_load_factor: str = "1",
) -> dict[str, object]:
    if not cases:
        raise ValueError("range-intersects batch requires at least one case")
    results: list[dict[str, object]] = []
    for case in cases:
        serialize_dir = Path(case["serialize_dir"])
        serialize_dir.mkdir(parents=True, exist_ok=True)
        try:
            result = run_gate(
                author_binary=author_binary,
                ae_root=ae_root,
                geometry_path=Path(case["geometry"]),
                query_path=Path(case["query"]),
                serialize_dir=serialize_dir,
                archive_result=archive_result,
                extraction_result=extraction_result,
                author_load_factor=author_load_factor,
            )
            result.update(
                {
                    "case_id": case.get("case_id", case.get("query", "unknown")),
                    "geometry": case.get("geometry"),
                    "query": case.get("query"),
                    "serialize_dir": str(serialize_dir),
                }
            )
            results.append(result)
        except Exception as error:
            results.append(
                {
                    "case_id": case.get("case_id", case.get("query", "unknown")),
                    "geometry": case.get("geometry"),
                    "query": case.get("query"),
                    "serialize_dir": str(serialize_dir),
                    "status": "case_execution_failed",
                    "matched": False,
                    "error_type": type(error).__name__,
                    "error": str(error),
                }
            )
    matched_count = sum(1 for result in results if result["matched"])
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_range_intersects_batch.v1",
        "status": "exact_input_range_intersects_batch_matched" if matched_count == len(results) else "exact_input_range_intersects_batch_mismatch",
        "matched": matched_count == len(results),
        "case_count": len(results),
        "matched_case_count": matched_count,
        "cases": results,
        "claim_boundary": {
            "count_level_same_input_agreement_only": matched_count == len(results),
            "complete_range_intersects_matrix_claimed": False,
            "pointwise_intersection_equivalence_claimed": False,
            "performance_ratio_authorized": False,
            "figure6_reproduced": False,
            "complete_paper_reproduction_claimed": False,
            "device_zero_copy_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--extraction-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--author-load-factor", default="1")
    args = parser.parse_args()
    payload = run_batch(
        author_binary=args.author_binary.resolve(),
        ae_root=args.ae_root.resolve(),
        cases=json.loads(args.cases.read_text(encoding="utf-8")),
        archive_result=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction_result=json.loads(args.extraction_result.read_text(encoding="utf-8")),
        author_load_factor=args.author_load_factor,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
