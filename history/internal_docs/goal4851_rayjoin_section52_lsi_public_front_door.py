#!/usr/bin/env python3
"""Section 5.2 LSI count through the public planar-map RTDL front door."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rtdsl import load_cdb, prepare_planar_map_lsi_2d_optix


def _timed(func):
    start = time.perf_counter()
    value = func()
    return value, time.perf_counter() - start


def _reject_bundled_helper_import() -> None:
    if "rtdsl.rayjoin_overlay" in sys.modules:
        raise RuntimeError("rtdsl.rayjoin_overlay was imported; this script must use the public LSI front door")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--poly1", required=True, help="AuthorPatch -poly1/base CDB path")
    parser.add_argument("--poly2", required=True, help="AuthorPatch -poly2/query CDB path")
    parser.add_argument("--expected-count", type=int, default=None)
    parser.add_argument(
        "--expected-count-provenance",
        default="unspecified",
        help=(
            "Where --expected-count came from, for example "
            "authorpatch_independent_run, rtdl_bundled_helper_prior_run, "
            "or restored_same_source_prior_count"
        ),
    )
    parser.add_argument("--label", default="unnamed")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    _reject_bundled_helper_import()

    poly1 = Path(args.poly1)
    poly2 = Path(args.poly2)
    base, load_base_sec = _timed(lambda: load_cdb(poly1))
    query, load_query_sec = _timed(lambda: load_cdb(poly2))

    prepare_start = time.perf_counter()
    with prepare_planar_map_lsi_2d_optix(base) as prepared:
        prepare_sec = time.perf_counter() - prepare_start
        result, count_sec = _timed(lambda: prepared.count_with_metadata(query))

    _reject_bundled_helper_import()

    count = int(result["count"])
    matched = args.expected_count is None or count == args.expected_count
    summary = {
        "schema": "rtdl.goal4851.section52_lsi_public_front_door.v1",
        "label": args.label,
        "poly1": str(poly1),
        "poly2": str(poly2),
        "authorpatch_command_shape": "query_exec -poly1 poly1 -poly2 poly2 -query=lsi",
        "rtdl_public_api": "prepare_planar_map_lsi_2d_optix",
        "count": count,
        "expected_count": args.expected_count,
        "expected_count_provenance": args.expected_count_provenance,
        "matched_expected": matched,
        "front_door_result": result,
        "timings_sec": {
            "load_poly1": load_base_sec,
            "load_poly2": load_query_sec,
            "prepare": prepare_sec,
            "count": count_sec,
            "total_observed": load_base_sec + load_query_sec + prepare_sec + count_sec,
        },
        "claim_boundary": {
            "section52_lsi_count_only": True,
            "public_generic_rtdl_primitive": True,
            "bundled_rayjoin_helper_used": False,
            "full_overlay_claim": False,
            "all_eight_exact_paper_pairs_claim": False,
            "broad_speedup_claim": False,
        },
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0 if matched else 2


if __name__ == "__main__":
    raise SystemExit(main())
