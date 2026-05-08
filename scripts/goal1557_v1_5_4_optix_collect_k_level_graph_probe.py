"""Probe CUDA graph replay for the real collect-k compact-level kernel chain.

This is a diagnostic bridge between the synthetic Goal 1555 graph replay probe
and a future production collect-k graph path. It uses controlled device buffers
and the actual four-kernel compact-level sequence, but it does not alter normal
COLLECT_K_BOUNDED execution.
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
    lib.rtdl_optix_collect_k_level_graph_replay_probe.argtypes = [
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_uint64),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_optix_collect_k_level_graph_replay_probe.restype = ctypes.c_int
    return lib


def run_case(
    library: Path,
    *,
    repeats: int,
    pair_count: int,
    segment_capacity: int,
) -> dict[str, Any]:
    direct_ms = ctypes.c_double()
    graph_ms = ctypes.c_double()
    first_pair_count = ctypes.c_uint64()
    error = ctypes.create_string_buffer(4096)

    lib = _load_library(library)
    rc = lib.rtdl_optix_collect_k_level_graph_replay_probe(
        repeats,
        pair_count,
        segment_capacity,
        ctypes.byref(direct_ms),
        ctypes.byref(graph_ms),
        ctypes.byref(first_pair_count),
        error,
        ctypes.sizeof(error),
    )
    if rc != 0:
        message = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_optix_collect_k_level_graph_replay_probe failed: {message}")

    speedup = direct_ms.value / graph_ms.value if graph_ms.value > 0 else None
    return {
        "pair_count": pair_count,
        "segment_capacity": segment_capacity,
        "repeats": repeats,
        "direct_ms": direct_ms.value,
        "graph_ms": graph_ms.value,
        "direct_per_replay_us": direct_ms.value * 1000.0 / repeats,
        "graph_per_replay_us": graph_ms.value * 1000.0 / repeats,
        "direct_over_graph_speedup": speedup,
        "first_pair_count": first_pair_count.value,
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    cases = result["cases"]
    best = max(
        cases,
        key=lambda case: case["direct_over_graph_speedup"] or float("-inf"),
    )
    best_speedup = best["direct_over_graph_speedup"]
    best_speedup_text = "n/a" if best_speedup is None else f"{best_speedup:.3f}x"
    verdict = (
        "The real collect-k compact-level kernel chain is graph-replayable in this diagnostic probe."
    )
    path.write_text(
        "\n".join(
            [
                "# Goal 1557 COLLECT_K Level Graph Replay Probe",
                "",
                "## Verdict",
                "",
                verdict,
                "",
                "## Scope",
                "",
                "- Probe: actual four-kernel collect-k compact-level sequence.",
                "- Sequence: materialize, mark, device-prefix, compact.",
                f"- Library: `{result['library']}`",
                f"- Repeats: `{result['repeats']}`",
                "",
                "## Result",
                "",
                "| pairs | segment capacity | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph | first pair count |",
                "|---:|---:|---:|---:|---:|---:|---:|---:|",
                *[
                    "| {pair_count} | {segment_capacity} | {direct_ms:.6f} | {graph_ms:.6f} | "
                    "{direct_per_replay_us:.6f} | {graph_per_replay_us:.6f} | {speedup} | {first_pair_count} |".format(
                        speedup=(
                            "n/a"
                            if case["direct_over_graph_speedup"] is None
                            else f"{case['direct_over_graph_speedup']:.3f}x"
                        ),
                        **case,
                    )
                    for case in cases
                ],
                "",
                f"Best direct-over-graph speedup: `{best_speedup_text}`.",
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
    parser.add_argument("--repeats", type=int, default=5000)
    parser.add_argument("--pair-counts", nargs="+", type=int, default=[1, 4, 16])
    parser.add_argument("--segment-capacity", type=int, default=2048)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
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
        "probe": "goal1557_v1_5_4_optix_collect_k_level_graph_probe",
        "claim_boundary": (
            "Diagnostic collect-k compact-level graph replay only; not a production "
            "COLLECT_K_BOUNDED optimization and not a public speedup claim."
        ),
        "library": str(args.library),
        "repeats": args.repeats,
        "cases": cases,
    }

    text = json.dumps(result, indent=2, sort_keys=True)
    print(text)
    if args.json_out:
        args.json_out.write_text(text + "\n", encoding="utf-8")
    if args.md_out:
        write_markdown(args.md_out, result)


if __name__ == "__main__":
    main()
