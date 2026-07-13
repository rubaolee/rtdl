from __future__ import annotations

import argparse
import json
from pathlib import Path


CASE_DATASETS = {
    "dtl_cnty": "dtl_cnty.wkt.log",
    "USACensusBlockGroupBoundaries": "USACensusBlockGroupBoundaries.wkt.log",
    "USADetailedWaterBodies": "USADetailedWaterBodies.wkt.log",
    "parks_Europe": "parks_Europe.wkt.log",
    "lakes.bz2": "lakes.bz2.wkt.log",
    "parks.bz2": "parks.bz2.wkt.log",
}


def _load_json(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


def select_figure6_rtspatial_records(
    author_logs: dict[str, object],
) -> dict[str, dict[str, object]]:
    records = author_logs.get("records", ())
    selected: dict[str, dict[str, object]] = {}
    for record in records:
        if not isinstance(record, dict):
            continue
        if (
            record.get("paper_figure") != 6
            or record.get("category") != "point-contains_queries_100000"
            or record.get("index_type") != "rtspatial"
        ):
            continue
        dataset = str(record.get("dataset", ""))
        if dataset in CASE_DATASETS.values():
            case_id = next(
                key for key, expected in CASE_DATASETS.items() if expected == dataset
            )
            if case_id in selected:
                raise ValueError(f"duplicate Figure-6 RTSpatial record: {dataset}")
            selected[case_id] = record
    missing = set(CASE_DATASETS) - set(selected)
    if missing:
        raise ValueError(f"missing Figure-6 RTSpatial records: {sorted(missing)}")
    return selected


def _exact_cases(
    *,
    first: dict[str, object],
    remaining: dict[str, object],
) -> dict[str, dict[str, object]]:
    cases: dict[str, dict[str, object]] = {"dtl_cnty": first}
    remaining_cases = remaining.get("cases", {})
    if not isinstance(remaining_cases, dict):
        raise ValueError("remaining batch evidence has no cases object")
    for case_id in CASE_DATASETS:
        if case_id == "dtl_cnty":
            continue
        case = remaining_cases.get(case_id)
        if not isinstance(case, dict):
            raise ValueError(f"missing exact gate result: {case_id}")
        cases[case_id] = case
    return cases


def build_audit(
    *,
    author_logs: dict[str, object],
    first: dict[str, object],
    remaining: dict[str, object],
) -> dict[str, object]:
    log_records = select_figure6_rtspatial_records(author_logs)
    exact_cases = _exact_cases(first=first, remaining=remaining)
    cases: dict[str, dict[str, object]] = {}
    for case_id in CASE_DATASETS:
        exact = exact_cases[case_id]
        author = exact.get("author", {})
        if not isinstance(author, dict):
            raise ValueError(f"malformed author result: {case_id}")
        log = log_records[case_id]
        checks = {
            "exact_gate_matched": bool(exact.get("matched")),
            "geometry_count_matches_log": int(author["geometry_count"])
            == int(log["loaded_geometries"]),
            "query_count_matches_log": int(author["query_count"])
            == int(log["loaded_queries"]),
            "result_count_matches_log": int(author["result_count"])
            == int(log["result_count"]),
            "same_input_identity_used": bool(
                exact.get("input_identity", {}).get("same_files_passed_to_author_and_rtdl", False)
            ),
        }
        if not all(checks.values()):
            raise ValueError(f"Figure-6 denominator check failed for {case_id}: {checks}")
        cases[case_id] = {
            "case_id": case_id,
            "author_log_path": log["path"],
            "geometry_count": int(author["geometry_count"]),
            "query_count": int(author["query_count"]),
            "author_result_count": int(author["result_count"]),
            "author_loading_ms": float(log["loading_ms"]),
            "author_query_ms": float(log["query_ms"]),
            "checks": checks,
            "timing_contract": "author internal Query Time; Loading Time excluded",
        }
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_figure6_point_contains_denominator.v1",
        "status": "exact_input_figure6_point_contains_denominator_aligned__no_performance_claim",
        "case_count": len(cases),
        "all_cases_aligned": True,
        "cases": cases,
        "phase_boundary": {
            "author_metric": "author internal Query Time",
            "author_loading_excluded": True,
            "rtdl_route_wall_collected_but_not_denominator_aligned": True,
            "performance_ratio_authorized": False,
        },
        "claim_boundary": {
            "exact_input_count_matrix_audited": True,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-logs", type=Path, required=True)
    parser.add_argument("--first-result", type=Path, required=True)
    parser.add_argument("--remaining-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload = build_audit(
        author_logs=_load_json(args.author_logs),
        first=_load_json(args.first_result),
        remaining=_load_json(args.remaining_result),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
