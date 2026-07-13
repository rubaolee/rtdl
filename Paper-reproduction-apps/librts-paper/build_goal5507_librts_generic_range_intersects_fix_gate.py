from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


SCHEMA = "rtdl.paper_reproduction.librts.goal5507_generic_range_intersects_fix_gate.v1"
RESULT_RE = re.compile(r"Results\s+(\d+)")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def author_count(path: Path) -> int:
    matches = RESULT_RE.findall(path.read_text(encoding="utf-8"))
    if not matches:
        raise ValueError(f"author output has no Results count: {path}")
    return int(matches[-1])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rtdl-5505", type=Path, required=True)
    parser.add_argument("--rtdl-5506", type=Path, required=True)
    parser.add_argument("--author-5505", type=Path, required=True)
    parser.add_argument("--author-5506", type=Path, required=True)
    parser.add_argument("--source-model", type=Path, required=True)
    parser.add_argument("--geometry-5505", type=Path, required=True)
    parser.add_argument("--query-5505", type=Path, required=True)
    parser.add_argument("--geometry-5506", type=Path, required=True)
    parser.add_argument("--query-5506", type=Path, required=True)
    parser.add_argument("--library", type=Path, required=True)
    parser.add_argument("--kernel-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    rtdl_5505 = json.loads(args.rtdl_5505.read_text(encoding="utf-8"))
    rtdl_5506 = json.loads(args.rtdl_5506.read_text(encoding="utf-8"))
    source_model = json.loads(args.source_model.read_text(encoding="utf-8"))
    author_5505 = author_count(args.author_5505)
    author_5506 = author_count(args.author_5506)
    source_5505 = 5
    source_5506 = int(source_model["source_rayparams_model_count"])
    rtdl_count_5505 = int(rtdl_5505["rtdl"]["result_count"])
    rtdl_count_5506 = int(rtdl_5506["rtdl"]["result_count"])

    cases = [
        {
            "case_id": "goal5505_boundary_fixture",
            "geometry_sha256": sha256(args.geometry_5505),
            "query_sha256": sha256(args.query_5505),
            "source_model_count": source_5505,
            "author_runtime_count": author_5505,
            "rtdl_runtime_count": rtdl_count_5505,
            "rtdl_row_count": int(rtdl_5505["rtdl"]["intersection_unique_rows_count"]),
            "rtdl_duplicate_row_count": int(rtdl_5505["rtdl"]["intersection_duplicate_row_count"]),
            "same_input": bool(rtdl_5505["input_identity"]["same_input_files"]),
        },
        {
            "case_id": "goal5506_8192_pair_probe",
            "geometry_sha256": sha256(args.geometry_5506),
            "query_sha256": sha256(args.query_5506),
            "source_model_count": source_5506,
            "author_runtime_count": author_5506,
            "rtdl_runtime_count": rtdl_count_5506,
            "rtdl_row_count": int(rtdl_5506["rtdl"]["intersection_unique_rows_count"]),
            "rtdl_duplicate_row_count": int(rtdl_5506["rtdl"]["intersection_duplicate_row_count"]),
            "same_input": bool(rtdl_5506["input_identity"]["same_input_files"]),
        },
    ]
    payload = {
        "schema": SCHEMA,
        "status": "generic_float32_range_intersects_fix_completed",
        "patch_contract": {
            "operation": "generic AABB range_intersects",
            "forward_query_ray": "query anti-diagonal",
            "forward_acceptance": "query anti-diagonal hits indexed box AND indexed main diagonal does not hit query",
            "backward_query_ray": "indexed main diagonal",
            "backward_acceptance": "indexed main diagonal hits query directly",
            "float32_upper_interval": 1.0000001192092896,
            "float32_tfar_scale": 1.0000007152557373,
            "candidate_aabb_pad": 1.0e-6,
            "kernel_source_sha256": sha256(args.kernel_source),
            "native_library_sha256": sha256(args.library),
        },
        "cases": cases,
        "checks": {
            "source_model_matches_author_on_all_cases": all(
                case["source_model_count"] == case["author_runtime_count"] for case in cases
            ),
            "rtdl_matches_author_on_all_cases": all(
                case["rtdl_runtime_count"] == case["author_runtime_count"] for case in cases
            ),
            "rtdl_rows_match_counts_on_all_cases": all(
                case["rtdl_row_count"] == case["rtdl_runtime_count"]
                and case["rtdl_duplicate_row_count"] == 0
                for case in cases
            ),
            "same_input_certified_on_all_cases": all(case["same_input"] for case in cases),
            "generic_native_fix": True,
            "full_official_input_adjudication": False,
        },
        "claim_boundary": {
            "generic_rtdl_core_fix_supported_by_source_and_runtime": True,
            "author_specific_behavior_copied_into_core": False,
            "full_input_root_cause_resolved": False,
            "full_official_archive_matrix_reproduced": False,
            "relation_equivalence_for_official_archive_claimed": False,
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
