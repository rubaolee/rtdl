"""Probe output-indexed merge-path fused materialize+mark for collect-k."""

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
    lib.rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe.argtypes = [
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
    lib.rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe.restype = ctypes.c_int
    return lib


def run_case(library: Path, *, repeats: int, pair_count: int, segment_capacity: int) -> dict[str, Any]:
    reference_ms = ctypes.c_double()
    fused_ms = ctypes.c_double()
    mismatch_count = ctypes.c_uint64()
    first_pair_count = ctypes.c_uint64()
    error = ctypes.create_string_buffer(4096)

    lib = _load_library(library)
    rc = lib.rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe(
        repeats,
        pair_count,
        segment_capacity,
        ctypes.byref(reference_ms),
        ctypes.byref(fused_ms),
        ctypes.byref(mismatch_count),
        ctypes.byref(first_pair_count),
        error,
        ctypes.sizeof(error),
    )
    if rc != 0:
        message = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(
            f"rtdl_optix_collect_k_output_indexed_fused_materialize_mark_probe failed: {message}"
        )

    return {
        "pair_count": pair_count,
        "segment_capacity": segment_capacity,
        "repeats": repeats,
        "reference_ms": reference_ms.value,
        "fused_ms": fused_ms.value,
        "reference_per_replay_us": reference_ms.value * 1000.0 / repeats,
        "fused_per_replay_us": fused_ms.value * 1000.0 / repeats,
        "reference_over_fused_speedup": (
            reference_ms.value / fused_ms.value if fused_ms.value > 0 else None
        ),
        "mismatch_count": mismatch_count.value,
        "first_pair_count": first_pair_count.value,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--library", type=Path, default=DEFAULT_LIBRARY)
    parser.add_argument("--repeats", type=int, default=2000)
    parser.add_argument("--pair-counts", nargs="+", type=int, default=[1, 4, 16])
    parser.add_argument("--segment-capacity", type=int, default=2048)
    parser.add_argument("--json-out", type=Path)
    args = parser.parse_args()

    cases = [
        run_case(
            args.library,
            repeats=args.repeats,
            pair_count=pair_count,
            segment_capacity=args.segment_capacity,
        )
        for pair_count in args.pair_counts
    ]
    result: dict[str, Any] = {
        "probe": "goal1567_v1_5_4_optix_collect_k_output_indexed_fused_probe",
        "claim_boundary": (
            "Diagnostic output-indexed fused materialize+mark probe only; not a "
            "production COLLECT_K_BOUNDED optimization and not a public speedup claim."
        ),
        "library": str(args.library),
        "repeats": args.repeats,
        "cases": cases,
    }
    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        args.json_out.write_text(text + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
