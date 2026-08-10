from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence


QUERY_IDS = ("q11", "q12", "q13", "q21", "q22", "q23", "q31", "q32", "q33", "q34", "q41", "q42", "q43")


def consolidate(matrix_path: Path, author_dir: Path, rtdl_dir: Path) -> dict[str, object]:
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))
    packet_by_query = {packet["query_id"]: packet for packet in matrix["packets"]}
    if tuple(packet_by_query) != QUERY_IDS:
        raise ValueError("matrix packet order or membership differs from the 13-query contract")
    cases = []
    for query_id in QUERY_IDS:
        packet = packet_by_query[query_id]
        author = json.loads((author_dir / f"{query_id}.json").read_text(encoding="utf-8"))
        rtdl = json.loads((rtdl_dir / f"{query_id}.json").read_text(encoding="utf-8"))
        same_hashes = all(
            packet[field] == author[field] == rtdl[field]
            for field in ("data_sha256", "predicate_sha256", "expected_rows_sha256")
        )
        complete_rows_equal = (
            packet["expected_rows"] == author["author_rows"] == rtdl["rtdl_rows"]
        )
        passed = bool(
            same_hashes
            and complete_rows_equal
            and author["author_matches_cpu_oracle"]
            and rtdl["author_matches_oracle"]
            and rtdl["rtdl_matches_oracle"]
            and rtdl["author_matches_rtdl"]
            and rtdl["missing_rows"] == []
            and rtdl["unexpected_rows"] == []
        )
        if not passed:
            raise ValueError(f"{query_id} did not pass the complete same-input row gate")
        cases.append(
            {
                "query_id": query_id,
                "passed": passed,
                "row_count": int(packet["row_count"]),
                "output_group_row_count": len(packet["expected_rows"]),
                "same_packet_hashes": same_hashes,
                "complete_group_rows_equal": complete_rows_equal,
                "data_sha256": packet["data_sha256"],
                "predicate_sha256": packet["predicate_sha256"],
                "expected_rows_sha256": packet["expected_rows_sha256"],
                "author_line_num": int(author["author_line_num"]),
                "rtdl_triangle_count": int(rtdl["triangle_count"]),
                "rtdl_ray_count": int(rtdl["ray_grid"]["ray_count"]),
                "rtdl_native_symbol": rtdl["native_symbol"],
                "rtdl_phase_timing_seconds": rtdl["phase_timing_seconds"],
            }
        )
    return {
        "schema": "rtdl.paper_reproduction.raydb.ssb_sf1_complete_grouped_rows_matrix.v1",
        "host": "lx1",
        "gpu": "NVIDIA GeForce GTX 1070",
        "input_identity_level": "deterministic_generated_ssb_sf1_same_bytes__not_exact_paper_input",
        "dbgen_repository": matrix["dbgen_repository"],
        "dbgen_commit": matrix["dbgen_commit"],
        "table_sha256": matrix["table_sha256"],
        "query_count": len(cases),
        "passed_query_count": sum(int(case["passed"]) for case in cases),
        "failed_query_count": sum(int(not case["passed"]) for case in cases),
        "all_13_queries_passed": all(case["passed"] for case in cases),
        "comparison_contract": "same hashed packet bytes; complete canonical nonzero group tuples and integer aggregate values; independent DuckDB oracle",
        "cases": cases,
        "system_contract": {
            "app_lowering": "SSB schema/join/query encoding and author-compatible ray geometry are owned by raydb-paper",
            "rtdl_core": "generic packed/prepared 3-D ray-triangle primitive grouped i64 reduction",
            "per_ray_records_downloaded_to_host": False,
            "group_rows_downloaded_to_host": True,
        },
        "claim_boundary": {
            "ssb_sf1_query_matrix_complete_grouped_rows_claimed": True,
            "exact_paper_input_claimed": False,
            "ssb_sf10_query_matrix_claimed": False,
            "ssb_sf20_query_matrix_claimed": False,
            "figure12_reproduced": False,
            "paper_performance_claimed": False,
            "author_performance_parity_claimed": False,
            "author_algorithm_equivalence_claimed": False,
        },
        "external_review": "pending",
        "exit_label": "raydb_ssb_sf1_13_of_13_complete_grouped_rows_same_input__review_pending",
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Consolidate the RayDB 13-query SSB SF1 matrix")
    parser.add_argument("--matrix-json", type=Path, required=True)
    parser.add_argument("--author-dir", type=Path, required=True)
    parser.add_argument("--rtdl-dir", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    result = consolidate(args.matrix_json, args.author_dir, args.rtdl_dir)
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: result[key] for key in ("query_count", "passed_query_count", "failed_query_count", "all_13_queries_passed", "exit_label")}, indent=2))
    return 0 if result["all_13_queries_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
