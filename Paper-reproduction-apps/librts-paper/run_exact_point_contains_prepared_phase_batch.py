from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_exact_point_contains_batch_gate import CASE_MEMBERS, _resolve_member, _sha256
from run_exact_point_contains_prepared_phase_gate import run_gate


DTL_MEMBER = (
    "PPoPPAE/datasets/polygons/dtl_cnty.wkt",
    "PPoPPAE/datasets/queries/point-contains_queries_100000/dtl_cnty.wkt",
)


CASE_MANIFESTS = {"dtl_cnty": "dtl", **{case_id: "remaining" for case_id in CASE_MEMBERS}}


def run_batch(
    *,
    author_binary: Path,
    ae_root: Path,
    archive: dict[str, object],
    extraction_results: dict[str, dict[str, object]],
    output_dir: Path,
    serialize_root: Path,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    serialize_root.mkdir(parents=True, exist_ok=True)
    members = {"dtl_cnty": DTL_MEMBER, **CASE_MEMBERS}
    cases: dict[str, dict[str, object]] = {}
    for case_id, (geometry_member, query_member) in members.items():
        manifest_key = CASE_MANIFESTS[case_id]
        extraction = extraction_results[manifest_key]
        geometry = _resolve_member(extraction=extraction, member=geometry_member)
        query = _resolve_member(extraction=extraction, member=query_member)
        result = run_gate(
            author_binary=author_binary,
            ae_root=ae_root,
            geometry_path=geometry,
            query_path=query,
            serialize_dir=serialize_root / case_id,
            archive_result=archive,
            extraction_result=extraction,
        )
        result["case_id"] = case_id
        result["extraction_manifest"] = manifest_key
        result_path = output_dir / f"{case_id}.json"
        result_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
        cases[case_id] = result

    matched_count = sum(bool(item["matched"]) for item in cases.values())
    matched = matched_count == len(cases)
    return {
        "schema": "rtdl.paper_reproduction.librts.exact_point_contains_prepared_phase_batch.v1",
        "status": (
            "exact_input_point_contains_prepared_phase_batch_matched"
            if matched
            else "exact_input_point_contains_prepared_phase_batch_incomplete_or_mismatched"
        ),
        "matched": matched,
        "case_count": len(cases),
        "matched_case_count": matched_count,
        "same_files_passed_to_author_and_rtdl": True,
        "phase_boundary": {
            "prepared_query_phase_comparison_candidate": True,
            "performance_ratio_authorized": False,
        },
        "claim_boundary": {
            "exact_archive_and_extracted_input_identity_used": True,
            "same_input_result_count_agreement": matched,
            "pointwise_containment_equivalence_claimed": False,
            "figure6_reproduced": False,
            "performance_ratio_authorized": False,
            "complete_paper_reproduction_claimed": False,
            "embree_in_scope": False,
        },
        "cases": cases,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--author-binary", type=Path, required=True)
    parser.add_argument("--ae-root", type=Path, required=True)
    parser.add_argument("--archive-result", type=Path, required=True)
    parser.add_argument("--dtl-extraction-result", type=Path, required=True)
    parser.add_argument("--remaining-extraction-result", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--serialize-root", type=Path, required=True)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.serialize_root.mkdir(parents=True, exist_ok=True)
    payload = run_batch(
        author_binary=args.author_binary.resolve(),
        ae_root=args.ae_root.resolve(),
        archive=json.loads(args.archive_result.read_text(encoding="utf-8")),
        extraction_results={
            "dtl": json.loads(args.dtl_extraction_result.read_text(encoding="utf-8")),
            "remaining": json.loads(args.remaining_extraction_result.read_text(encoding="utf-8")),
        },
        output_dir=args.output_dir.resolve(),
        serialize_root=args.serialize_root.resolve(),
    )
    (args.output_dir / "batch_summary.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["matched"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
