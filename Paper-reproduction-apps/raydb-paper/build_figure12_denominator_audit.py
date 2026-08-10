from __future__ import annotations

import argparse
import json
import re
import statistics
from pathlib import Path
from typing import Sequence


QUERY_IDS = (
    "q11", "q12", "q13", "q21", "q22", "q23", "q31",
    "q32", "q33", "q34", "q41", "q42", "q43",
)
AUTHOR_TIME_PATTERNS = {
    "build_bvh_ms": re.compile(r"^\[Time\] Build BVH: ([0-9.eE+-]+) ms$", re.MULTILINE),
    "launch_prepare_included_ms": re.compile(
        r"^\[Time\] Launch\(Prepare included\): ([0-9.eE+-]+) ms$", re.MULTILINE
    ),
    "launch_ms": re.compile(r"^\[Time\] Launch: ([0-9.eE+-]+) ms$", re.MULTILINE),
}


def _load(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_author_times(raw_stdout: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for key, pattern in AUTHOR_TIME_PATTERNS.items():
        matches = pattern.findall(raw_stdout)
        if len(matches) != 1:
            raise ValueError(f"expected exactly one {key} timing, found {len(matches)}")
        result[key] = float(matches[0])
    return result


def build_audit(
    author_dir: Path,
    rtdl_dir: Path,
    correctness_matrix: dict[str, object],
) -> dict[str, object]:
    if not bool(correctness_matrix.get("all_13_queries_passed")):
        raise ValueError("phase audit requires the passed 13-query correctness matrix")
    cases = []
    for query_id in QUERY_IDS:
        author = _load(author_dir / f"{query_id}.json")
        rtdl = _load(rtdl_dir / f"{query_id}.json")
        if author.get("query_id") != query_id or rtdl.get("query_id") != query_id:
            raise ValueError(f"query identity mismatch for {query_id}")
        if not bool(author.get("author_matches_cpu_oracle")):
            raise ValueError(f"author correctness gate did not pass for {query_id}")
        if not bool(rtdl.get("rtdl_matches_oracle")) or not bool(rtdl.get("author_matches_rtdl")):
            raise ValueError(f"RTDL correctness gate did not pass for {query_id}")
        same_hashes = all(
            author[field] == rtdl[field]
            for field in ("data_sha256", "predicate_sha256", "expected_rows_sha256")
        )
        if not same_hashes:
            raise ValueError(f"packet hash mismatch for {query_id}")
        author_times = parse_author_times(str(author["raw_stdout"]))
        rtdl_times = rtdl["phase_timing_seconds"]
        cases.append(
            {
                "query_id": query_id,
                "same_packet_hashes": True,
                "complete_group_rows_equal": True,
                "author": author_times,
                "rtdl": {
                    "prepare_build_ms": float(rtdl_times["prepare_build"]) * 1000.0,
                    "primitive_payload_prepare_ms": float(
                        rtdl_times["primitive_payload_prepare"]
                    ) * 1000.0,
                    "query_pack_ms": float(rtdl_times["query_pack"]) * 1000.0,
                    "traversal_and_result_download_ms": float(rtdl_times["traversal"]) * 1000.0,
                    "prepared_route_total_ms": float(rtdl_times["prepared_route_total"]) * 1000.0,
                    "app_lowering_ms": float(rtdl_times["app_lowering"]) * 1000.0,
                    "host_pack_triangles_and_rays_ms": float(
                        rtdl_times["host_pack_triangles_and_rays"]
                    ) * 1000.0,
                },
                "ratio_authorized": False,
                "reason_ratio_not_authorized": (
                    "author Launch is optixLaunch plus synchronize; current RTDL traversal also "
                    "includes device-to-host downloads of grouped outputs and hit count"
                ),
            }
        )

    def median(path: tuple[str, ...]) -> float:
        values = []
        for case in cases:
            current: object = case
            for key in path:
                current = current[key]  # type: ignore[index]
            values.append(float(current))
        return statistics.median(values)

    return {
        "schema": "rtdl.paper_reproduction.raydb.figure12_denominator_audit.v1",
        "host": correctness_matrix["host"],
        "gpu": correctness_matrix["gpu"],
        "input_identity_level": correctness_matrix["input_identity_level"],
        "query_count": len(cases),
        "all_correctness_gates_passed": True,
        "phase_contracts": {
            "paper_figure12": (
                "paper reports a loaded-to-GPU boundary through result calculation on RTX 4090; "
                "the modified Crystal baseline and its raw Figure-12 records are not in the author artifact"
            ),
            "author_build_bvh": "OptiX acceleration build plus synchronization; reported separately",
            "author_launch_prepare_included": (
                "predicate remap, output allocation/reset, ray-origin-z construction/upload, "
                "parameter upload, optixLaunch, and synchronization; excludes result download"
            ),
            "author_launch": "optixLaunch plus synchronization only; excludes result download",
            "rtdl_traversal_and_result_download": (
                "optixLaunch plus synchronization followed by grouped-output and hit-count device-to-host downloads"
            ),
            "crystal_upstream_q11_time_query": (
                "CUDA event from before result allocation/reset through query kernel completion; "
                "excludes result download"
            ),
        },
        "summary_medians_ms": {
            "author_build_bvh": median(("author", "build_bvh_ms")),
            "author_launch_prepare_included": median(("author", "launch_prepare_included_ms")),
            "author_launch": median(("author", "launch_ms")),
            "rtdl_prepare_build": median(("rtdl", "prepare_build_ms")),
            "rtdl_traversal_and_result_download": median(
                ("rtdl", "traversal_and_result_download_ms")
            ),
        },
        "cases": cases,
        "crystal_baseline_audit": {
            "upstream_repository": "https://github.com/anilshanbhag/crystal",
            "upstream_commit": "f2179e607eb923f2053a706c1e30aa2b6161b9db",
            "paper_modified_crystal_source_available": False,
            "paper_modified_crystal_raw_figure12_records_available": False,
            "upstream_crystal_sf1_lineorder_rows": 6_001_171,
            "current_raydb_level_b_sf1_lineorder_rows": 6_001_215,
            "sf1_row_count_difference": 44,
            "upstream_crystal_sf20_lineorder_rows": 119_994_746,
            "raydb_author_script_sf20_lineorder_rows": 119_994_608,
            "sf20_row_count_difference": 138,
            "same_input_crystal_raydb_rtdl_gate_complete": False,
            "figure12_crystal_baseline_reproduced": False,
        },
        "decision": {
            "phase_denominator_aligned": False,
            "performance_ratio_authorized": False,
            "next_action": (
                "construct a same-generator q11 Crystal/RayDB/RTDL gate and add an RTDL phase "
                "that separates launch from result download before any timing ratio"
            ),
        },
        "claim_boundary": {
            "figure12_reproduced": False,
            "crystal_baseline_reproduced": False,
            "paper_performance_claimed": False,
            "author_vs_rtdl_ratio_claimed": False,
            "similar_raw_milliseconds_imply_aligned_denominator": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit RayDB Figure-12 timing denominators")
    parser.add_argument("--author-dir", type=Path, required=True)
    parser.add_argument("--rtdl-dir", type=Path, required=True)
    parser.add_argument("--correctness-matrix", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args(argv)
    result = build_audit(args.author_dir, args.rtdl_dir, _load(args.correctness_matrix))
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result["decision"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
