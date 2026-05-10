#!/usr/bin/env python3
"""Probe a diagnostic four-way OptiX collect-k merge block.

This is intentionally diagnostic-only. It calls a native probe that compares a
two-level binary reference merge against one four-way merge block for the same
four sorted row-width=2 input segments.
"""

from __future__ import annotations

import argparse
import ctypes
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LIBRARY = ROOT / "build" / "librtdl_optix.so"


def _load_library(path: Path) -> ctypes.CDLL:
    lib = ctypes.CDLL(str(path))
    lib.rtdl_optix_collect_k_four_way_merge_probe.argtypes = [
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_optix_collect_k_four_way_merge_probe.restype = ctypes.c_int
    return lib


def run_case(
    library: Path,
    *,
    repeats: int,
    group_count: int,
    segment_capacity: int,
) -> dict[str, Any]:
    reference_ms = ctypes.c_double()
    four_way_ms = ctypes.c_double()
    mismatch_count = ctypes.c_uint64()
    first_group_count = ctypes.c_uint64()
    error = ctypes.create_string_buffer(4096)

    lib = _load_library(library)
    rc = lib.rtdl_optix_collect_k_four_way_merge_probe(
        repeats,
        group_count,
        segment_capacity,
        ctypes.byref(reference_ms),
        ctypes.byref(four_way_ms),
        ctypes.byref(mismatch_count),
        ctypes.byref(first_group_count),
        error,
        ctypes.sizeof(error),
    )
    if rc != 0:
        message = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_optix_collect_k_four_way_merge_probe failed: {message}")

    speedup = reference_ms.value / four_way_ms.value if four_way_ms.value > 0 else None
    return {
        "group_count": group_count,
        "segment_capacity": segment_capacity,
        "repeats": repeats,
        "reference_ms": reference_ms.value,
        "four_way_ms": four_way_ms.value,
        "reference_per_replay_us": reference_ms.value * 1000.0 / repeats,
        "four_way_per_replay_us": four_way_ms.value * 1000.0 / repeats,
        "reference_over_four_way_speedup": speedup,
        "mismatch_count": mismatch_count.value,
        "first_group_count": first_group_count.value,
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    cases = result["cases"]
    path.write_text(
        "\n".join(
            [
                "# Goal1657 v1.6.x OptiX Collect-K Four-Way Merge Probe",
                "",
                "## Verdict",
                "",
                "`diagnostic_four_way_merge_probe_recorded`",
                "",
                "## Scope",
                "",
                "- Reference: two binary compact-level merge blocks over four sorted segments.",
                "- Candidate: one four-way materialize+mark block plus prefix and compact.",
                f"- Library: `{result['library']}`",
                f"- Repeats: `{result['repeats']}`",
                "",
                "## Result",
                "",
                "| groups | segment capacity | reference ms | four-way ms | reference us/replay | four-way us/replay | reference/four-way | mismatches | first group count |",
                "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
                *[
                    "| {group_count} | {segment_capacity} | {reference_ms:.6f} | {four_way_ms:.6f} | "
                    "{reference_per_replay_us:.6f} | {four_way_per_replay_us:.6f} | {speedup} | "
                    "{mismatch_count} | {first_group_count} |".format(
                        speedup=(
                            "n/a"
                            if case["reference_over_four_way_speedup"] is None
                            else f"{case['reference_over_four_way_speedup']:.3f}x"
                        ),
                        **case,
                    )
                    for case in cases
                ],
                "",
                "## Claim Boundary",
                "",
                result["claim_boundary"],
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--repeats", type=int, default=1000)
    parser.add_argument("--group-counts", nargs="+", type=int, default=[1, 4, 16])
    parser.add_argument("--segment-capacity", type=int, default=2048)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    cases = [
        run_case(
            args.library,
            repeats=args.repeats,
            group_count=group_count,
            segment_capacity=args.segment_capacity,
        )
        for group_count in args.group_counts
    ]
    result: dict[str, Any] = {
        "probe": "goal1657_v1_6_x_optix_collect_k_four_way_merge_probe",
        "claim_boundary": (
            "Diagnostic four-way collect-k merge probe only; not a production "
            "COLLECT_K_BOUNDED optimization and not a public speedup claim."
        ),
        "library": str(args.library),
        "repeats": args.repeats,
        "cases": cases,
    }

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(args.md_out, result)


if __name__ == "__main__":
    main()
