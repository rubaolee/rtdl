#!/usr/bin/env python3
"""Run the v2.14 bundled RayJoin LSI helper on two CDB files.

This is intentionally not presented as a generic RTDL language primitive.  It
uses the released RayJoin CDB helper path for Section 5.2-style LSI comparison.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

from rtdsl.rayjoin_overlay import _run_lsi_rows, load_cdb_overlay_packed_inputs


def _hash_rows(rows) -> dict[str, int | str]:
    hasher = hashlib.sha256()
    left = rows["left_id"]
    right = rows["right_id"]
    for left_id, right_id in sorted(zip(left, right)):
        hasher.update(f"{int(left_id)}\t{int(right_id)}\n".encode("utf-8"))
    return {"row_count": int(len(rows)), "sha256": hasher.hexdigest()}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--left-cdb", required=True)
    parser.add_argument("--right-cdb", required=True)
    parser.add_argument("--backend", default="optix", choices=("optix",))
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    load_start = time.perf_counter()
    left_inputs = load_cdb_overlay_packed_inputs(args.left_cdb)
    right_inputs = load_cdb_overlay_packed_inputs(args.right_cdb)
    load_sec = time.perf_counter() - load_start

    run_start = time.perf_counter()
    rows, timings = _run_lsi_rows(
        args.backend,
        left_inputs.segments,
        right_inputs.segments,
        None,
        None,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
        scale_bounds=None,
    )
    run_sec = time.perf_counter() - run_start

    summary = {
        "left_cdb": args.left_cdb,
        "right_cdb": args.right_cdb,
        "backend": args.backend,
        "left_segment_count": int(left_inputs.segments.count),
        "right_segment_count": int(right_inputs.segments.count),
        "load_sec": load_sec,
        "run_sec": run_sec,
        "native_timings": timings,
        "result": _hash_rows(rows),
        "claim_boundary": (
            "v2.14 bundled RayJoin LSI helper; Section 5.2 LSI count/hash only; "
            "not generic-language proof and not overlay/PIP/full Section 5.7"
        ),
    }
    Path(args.output).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
