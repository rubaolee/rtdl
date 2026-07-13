#!/usr/bin/env python3
"""Section 5.2 LSI count using public generic RTDL prepared primitives.

This is intentionally not a RayJoin overlay helper.  It does not import
``rtdsl.rayjoin_overlay`` and does not assemble polygon-overlay output chains.
It reproduces the Section 5.2 LSI count contract:

    AuthorPatch: query_exec -poly1 A -poly2 B -query=lsi
    RTDL route:  build/right index = A, query/left set = B
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rtdsl import chains_to_rayjoin_cdb_segments, load_cdb
from rtdsl.optix_runtime import (
    prepare_segment_pair_intersection_optix,
    prepare_segment_pair_left_set_optix,
)


def _timed(label: str, func):
    start = time.perf_counter()
    value = func()
    return value, time.perf_counter() - start


def _result_count(result) -> int:
    if isinstance(result, dict):
        return int(result["count"])
    return int(result)


def _reject_bundled_helper_import() -> None:
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("rtdsl.rayjoin_overlay was imported; this goal forbids bundled RayJoin helpers")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poly1", required=True, help="AuthorPatch -poly1/base CDB path")
    parser.add_argument("--poly2", required=True, help="AuthorPatch -poly2/query CDB path")
    parser.add_argument("--expected-count", type=int, default=None)
    parser.add_argument("--label", default="unnamed")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    # Fail early if the forbidden module is already imported by sitecustomize or
    # surrounding harness code.  The normal path below never imports it.
    _reject_bundled_helper_import()

    poly1 = Path(args.poly1)
    poly2 = Path(args.poly2)

    base, load_base_sec = _timed("load_poly1", lambda: load_cdb(poly1))
    query, load_query_sec = _timed("load_poly2", lambda: load_cdb(poly2))
    base_segments, base_segments_sec = _timed(
        "segments_poly1",
        lambda: chains_to_rayjoin_cdb_segments(base),
    )
    query_segments, query_segments_sec = _timed(
        "segments_poly2",
        lambda: chains_to_rayjoin_cdb_segments(query),
    )

    prepare_start = time.perf_counter()
    with prepare_segment_pair_intersection_optix(base_segments) as base_index:
        with prepare_segment_pair_left_set_optix(query_segments) as query_left:
            prepare_sec = time.perf_counter() - prepare_start
            count_result, count_sec = _timed(
                "count_prepared_left_exact_intersections",
                lambda: base_index.count_prepared_left_exact_intersections(query_left),
            )

    count = _result_count(count_result)
    matched = args.expected_count is None or count == args.expected_count

    # Check after the run too: this catches accidental imports added later.
    _reject_bundled_helper_import()

    summary = {
        "schema": "rtdl.goal4850.section52_lsi_public_generic_primitives.v1",
        "label": args.label,
        "authorpatch_command_shape": "query_exec -poly1 poly1 -poly2 poly2 -query=lsi",
        "rtdl_direction_contract": {
            "base_right_index": "poly1",
            "query_left_set": "poly2",
        },
        "poly1": str(poly1),
        "poly2": str(poly2),
        "base_segment_count": len(base_segments),
        "query_segment_count": len(query_segments),
        "count": count,
        "expected_count": args.expected_count,
        "matched_expected": matched,
        "raw_count_result": count_result,
        "timings_sec": {
            "load_poly1": load_base_sec,
            "load_poly2": load_query_sec,
            "segments_poly1": base_segments_sec,
            "segments_poly2": query_segments_sec,
            "prepare_both": prepare_sec,
            "count": count_sec,
            "total_observed": load_base_sec
            + load_query_sec
            + base_segments_sec
            + query_segments_sec
            + prepare_sec
            + count_sec,
        },
        "imports": {
            "rtdsl_top_level": ["load_cdb", "chains_to_rayjoin_cdb_segments"],
            "rtdsl.optix_runtime": [
                "prepare_segment_pair_intersection_optix",
                "prepare_segment_pair_left_set_optix",
            ],
            "forbidden_module_imported": "rtdsl.rayjoin_overlay" in sys.modules,
        },
        "claim_boundary": {
            "section52_lsi_count_only": True,
            "full_section57_overlay_claim": False,
            "all_eight_exact_paper_pairs_claim": False,
            "bundled_rayjoin_helper_used": False,
            "numba_hot_path_required": False,
            "public_generic_rtdl_primitives": True,
        },
    }

    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if matched else 2


if __name__ == "__main__":
    raise SystemExit(main())
