#!/usr/bin/env python3
"""Run the RTDL LSI kernel on two CDB files and emit a bounded count/hash.

This script uses released RTDL APIs (`load_cdb`, `chains_to_segments`,
`run_optix`, `run_cpu`) and an ordinary LSI kernel.  It does not modify RTDL and
does not call RayJoin overlay helpers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

import rtdsl as rt


@rt.kernel(backend="rtdl", precision="float_approx")
def lsi_reference():
    left = rt.input("left", rt.Segments, layout=rt.Segment2DLayout, role="probe")
    right = rt.input("right", rt.Segments, layout=rt.Segment2DLayout, role="build")
    candidates = rt.traverse(left, right, accel="bvh")
    hits = rt.refine(candidates, predicate=rt.segment_intersection(exact=False))
    return rt.emit(
        hits,
        fields=["left_id", "right_id", "intersection_point_x", "intersection_point_y"],
    )


def _hash_rows(rows) -> dict[str, int | str]:
    hasher = hashlib.sha256()
    count = 0
    for row in sorted((int(r["left_id"]), int(r["right_id"])) for r in rows):
        hasher.update(f"{row[0]}\t{row[1]}\n".encode("utf-8"))
        count += 1
    return {"row_count": count, "sha256": hasher.hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-cdb", required=True)
    parser.add_argument("--right-cdb", required=True)
    parser.add_argument("--backend", default="optix", choices=("cpu", "optix"))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    load_start = time.perf_counter()
    left = rt.load_cdb(args.left_cdb)
    right = rt.load_cdb(args.right_cdb)
    left_segments = tuple(rt.Segment(**{k: v for k, v in rec.items() if k in {"id", "x0", "y0", "x1", "y1"}}) for rec in rt.chains_to_segments(left))
    right_segments = tuple(rt.Segment(**{k: v for k, v in rec.items() if k in {"id", "x0", "y0", "x1", "y1"}}) for rec in rt.chains_to_segments(right))
    load_sec = time.perf_counter() - load_start

    run_start = time.perf_counter()
    if args.backend == "cpu":
        rows = rt.run_cpu(lsi_reference, left=left_segments, right=right_segments)
    else:
        rows = rt.run_optix(lsi_reference, left=left_segments, right=right_segments)
    run_sec = time.perf_counter() - run_start

    summary = {
        "left_cdb": args.left_cdb,
        "right_cdb": args.right_cdb,
        "backend": args.backend,
        "left_segment_count": len(left_segments),
        "right_segment_count": len(right_segments),
        "load_sec": load_sec,
        "run_sec": run_sec,
        "result": _hash_rows(rows),
        "claim_boundary": "RTDL LSI kernel count/hash only; no overlay/PIP/full Section 5.7 claim",
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
