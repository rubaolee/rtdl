"""Probe CUDA graph executable kernel-node updates for collect-k level replay.

This diagnostic captures the real four-kernel COLLECT_K_BOUNDED compact-level
sequence with one topology, updates the executable kernel-node parameters to a
target topology, then compares updated graph replay against direct launches for
that target. It does not change the production collect-k runtime path.
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
    lib.rtdl_optix_collect_k_level_graph_update_probe.argtypes = [
        ctypes.c_size_t,
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
    lib.rtdl_optix_collect_k_level_graph_update_probe.restype = ctypes.c_int
    return lib


def run_case(
    library: Path,
    *,
    repeats: int,
    initial_pair_count: int,
    target_pair_count: int,
    segment_capacity: int,
) -> dict[str, Any]:
    direct_ms = ctypes.c_double()
    graph_update_ms = ctypes.c_double()
    first_pair_count = ctypes.c_uint64()
    kernel_node_count = ctypes.c_uint64()
    error = ctypes.create_string_buffer(4096)

    lib = _load_library(library)
    rc = lib.rtdl_optix_collect_k_level_graph_update_probe(
        repeats,
        initial_pair_count,
        target_pair_count,
        segment_capacity,
        ctypes.byref(direct_ms),
        ctypes.byref(graph_update_ms),
        ctypes.byref(first_pair_count),
        ctypes.byref(kernel_node_count),
        error,
        ctypes.sizeof(error),
    )
    if rc != 0:
        message = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_optix_collect_k_level_graph_update_probe failed: {message}")

    speedup = direct_ms.value / graph_update_ms.value if graph_update_ms.value > 0 else None
    return {
        "initial_pair_count": initial_pair_count,
        "target_pair_count": target_pair_count,
        "segment_capacity": segment_capacity,
        "repeats": repeats,
        "direct_ms": direct_ms.value,
        "graph_update_ms": graph_update_ms.value,
        "direct_per_replay_us": direct_ms.value * 1000.0 / repeats,
        "graph_update_per_replay_us": graph_update_ms.value * 1000.0 / repeats,
        "direct_over_graph_update_speedup": speedup,
        "first_pair_count": first_pair_count.value,
        "kernel_node_count": kernel_node_count.value,
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    cases = result["cases"]
    best = max(
        cases,
        key=lambda case: case["direct_over_graph_update_speedup"] or float("-inf"),
    )
    best_speedup = best["direct_over_graph_update_speedup"]
    best_speedup_text = "n/a" if best_speedup is None else f"{best_speedup:.3f}x"
    path.write_text(
        "\n".join(
            [
                "# Goal 1559 COLLECT_K Level Graph Update Probe",
                "",
                "## Verdict",
                "",
                "CUDA graph executable kernel-node parameter update completed for the real collect-k compact-level sequence in this diagnostic probe.",
                "",
                "## Scope",
                "",
                "- Probe: capture one collect-k compact-level graph, update kernel node parameters, replay target topology.",
                "- Sequence: materialize, mark, device-prefix, compact.",
                f"- Library: `{result['library']}`",
                f"- Repeats: `{result['repeats']}`",
                "",
                "## Result",
                "",
                "| initial pairs | target pairs | segment capacity | direct ms | graph-update ms | direct us/replay | graph-update us/replay | direct/graph-update | nodes | first pair count |",
                "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
                *[
                    "| {initial_pair_count} | {target_pair_count} | {segment_capacity} | "
                    "{direct_ms:.6f} | {graph_update_ms:.6f} | {direct_per_replay_us:.6f} | "
                    "{graph_update_per_replay_us:.6f} | {speedup} | {kernel_node_count} | {first_pair_count} |".format(
                        speedup=(
                            "n/a"
                            if case["direct_over_graph_update_speedup"] is None
                            else f"{case['direct_over_graph_update_speedup']:.3f}x"
                        ),
                        **case,
                    )
                    for case in cases
                ],
                "",
                f"Best direct-over-updated-graph speedup: `{best_speedup_text}`.",
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
    parser.add_argument("--initial-pair-count", type=int, default=1)
    parser.add_argument("--target-pair-counts", nargs="+", type=int, default=[4, 16])
    parser.add_argument("--segment-capacity", type=int, default=2048)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    cases = [
        run_case(
            args.library,
            repeats=args.repeats,
            initial_pair_count=args.initial_pair_count,
            target_pair_count=target_pair_count,
            segment_capacity=args.segment_capacity,
        )
        for target_pair_count in args.target_pair_counts
    ]
    result: dict[str, Any] = {
        "probe": "goal1559_v1_5_4_optix_collect_k_level_graph_update_probe",
        "claim_boundary": (
            "Diagnostic collect-k graph executable parameter update only; not a production "
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
