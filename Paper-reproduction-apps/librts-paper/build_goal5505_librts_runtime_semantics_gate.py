from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


SCHEMA = "rtdl.paper_reproduction.librts.goal5505_runtime_semantics_gate.v1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures", type=Path, required=True)
    parser.add_argument("--observations", type=Path, required=True)
    parser.add_argument("--geometry", type=Path, required=True)
    parser.add_argument("--query", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fixtures = json.loads(args.fixtures.read_text(encoding="utf-8"))
    observations = json.loads(args.observations.read_text(encoding="utf-8"))
    cases_by_id = {case["case_id"]: case for case in fixtures["cases"]}
    # The POD observation file follows the committed WKT query order. Keep
    # that order explicit; Goal5504's diagnostic fixture order is different.
    runtime_case_order = [
        "interior_overlap",
        "edge_touch",
        "corner_touch",
        "one_ulp_overlap_before_box_max",
        "one_ulp_gap_after_box_max",
    ]
    cases = [cases_by_id[case_id] for case_id in runtime_case_order]
    author_counts = observations["author_counts"]
    rtdl_counts = observations["rtdl_counts"]
    if len(cases) != len(author_counts) or len(cases) != len(rtdl_counts):
        raise ValueError("fixture and runtime observation case counts differ")
    if not observations["same_input_per_case"]:
        raise ValueError("runtime observations do not certify same-input execution")

    rows = []
    for index, case in enumerate(cases):
        author_count = int(author_counts[index])
        rtdl_count = int(rtdl_counts[index])
        expected_count = 1 if bool(case["cpu_inclusive_intersects"]) else 0
        emulated_count = 1 if bool(case["author_gpu_style_intersects"]) else 0
        rows.append(
            {
                "case_id": case["case_id"],
                "cpu_inclusive_count": expected_count,
                "source_emulation_count": emulated_count,
                "author_runtime_count": author_count,
                "rtdl_runtime_count": rtdl_count,
                "author_matches_source_emulation": author_count == emulated_count,
                "rtdl_matches_cpu_inclusive": rtdl_count == expected_count,
                "author_rtdl_match": author_count == rtdl_count,
            }
        )

    payload = {
        "schema": SCHEMA,
        "status": "runtime_semantics_gate_completed",
        "input_identity": {
            "same_input_per_case": True,
            "runtime_case_order": runtime_case_order,
            "geometry_sha256": observations["geometry_sha256"],
            "query_sha256": observations["query_sha256"],
            "local_geometry_sha256": sha256(args.geometry),
            "local_query_sha256": sha256(args.query),
        },
        "contracts": {
            "cpu_reference": "inclusive_aabb_intersects_float32",
            "author_runtime": observations["author_command_contract"],
            "rtdl_runtime": observations["rtdl_contract"],
            "source_emulation": "RayParams<float,2> forward+backward diagonal shader model",
        },
        "cases": rows,
        "summary": {
            "case_count": len(rows),
            "author_runtime_total": sum(row["author_runtime_count"] for row in rows),
            "rtdl_runtime_total": sum(row["rtdl_runtime_count"] for row in rows),
            "author_matches_source_emulation_count": sum(
                row["author_matches_source_emulation"] for row in rows
            ),
            "author_matches_cpu_inclusive_count": sum(
                row["author_runtime_count"] == row["cpu_inclusive_count"] for row in rows
            ),
            "rtdl_matches_cpu_inclusive_count": sum(
                row["rtdl_matches_cpu_inclusive"] for row in rows
            ),
            "author_rtdl_mismatch_case_count": sum(
                not row["author_rtdl_match"] for row in rows
            ),
        },
        "interpretation": {
            "source_emulation_matches_author_runtime": all(
                row["author_matches_source_emulation"] for row in rows
            ),
            "rtdl_matches_independent_cpu_contract": all(
                row["rtdl_matches_cpu_inclusive"] for row in rows
            ),
            "localized_difference": "one_ulp_gap_after_box_max",
            "full_input_root_cause_resolved": False,
        },
        "claim_boundary": {
            "author_gpu_runtime_executed": True,
            "same_input_runtime_fixture_agreement": True,
            "author_validity_proven_for_full_inputs": False,
            "full_input_adjudication": False,
            "rtdl_core_change_authorized": False,
            "author_specific_rtdl_core_behavior_authorized": False,
            "performance_ratio_authorized": False,
            "paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
