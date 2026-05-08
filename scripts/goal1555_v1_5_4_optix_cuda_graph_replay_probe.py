"""Measure CUDA graph replay overhead for a tiny OptiX-native driver workload.

This is a feasibility probe only. It compares repeated direct CUDA driver calls
against repeated CUDA graph launches for the same captured memset command. It
does not measure COLLECT_K_BOUNDED and does not authorize a collect-k speedup
claim by itself.
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
    lib.rtdl_optix_cuda_graph_replay_probe.argtypes = [
        ctypes.c_size_t,
        ctypes.c_size_t,
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_double),
        ctypes.POINTER(ctypes.c_uint32),
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    lib.rtdl_optix_cuda_graph_replay_probe.restype = ctypes.c_int
    return lib


def run_probe(library: Path, repeats: int, commands_per_replay: int) -> dict[str, Any]:
    direct_ms = ctypes.c_double()
    graph_ms = ctypes.c_double()
    final_value = ctypes.c_uint32()
    error = ctypes.create_string_buffer(4096)

    lib = _load_library(library)
    rc = lib.rtdl_optix_cuda_graph_replay_probe(
        repeats,
        commands_per_replay,
        ctypes.byref(direct_ms),
        ctypes.byref(graph_ms),
        ctypes.byref(final_value),
        error,
        ctypes.sizeof(error),
    )
    if rc != 0:
        message = error.value.decode("utf-8", errors="replace")
        raise RuntimeError(f"rtdl_optix_cuda_graph_replay_probe failed: {message}")

    graph_value = graph_ms.value
    speedup = direct_ms.value / graph_value if graph_value > 0 else None
    return {
        "probe": "goal1555_v1_5_4_optix_cuda_graph_replay_probe",
        "claim_boundary": (
            "CUDA graph replay feasibility only; not a COLLECT_K_BOUNDED "
            "measurement and does not authorize a collect-k speedup claim."
        ),
        "library": str(library),
        "repeats": repeats,
        "commands_per_replay": commands_per_replay,
        "direct_ms": direct_ms.value,
        "graph_ms": graph_ms.value,
        "direct_per_replay_us": (direct_ms.value * 1000.0) / repeats,
        "graph_per_replay_us": (graph_ms.value * 1000.0) / repeats,
        "direct_per_command_us": (direct_ms.value * 1000.0) / (repeats * commands_per_replay),
        "graph_per_command_us": (graph_ms.value * 1000.0) / (repeats * commands_per_replay),
        "direct_over_graph_speedup": speedup,
        "final_value_hex": f"0x{final_value.value:08x}",
    }


def write_markdown(path: Path, result: dict[str, Any]) -> None:
    cases = result["cases"]
    best = max(
        cases,
        key=lambda case: case["direct_over_graph_speedup"] or float("-inf"),
    )
    best_speedup = best["direct_over_graph_speedup"]
    speedup_text = "n/a" if best_speedup is None else f"{best_speedup:.3f}x"
    verdict = (
        "CUDA graph replay is promising only for batched command replay in this probe."
        if best_speedup is not None and best_speedup > 1.0
        else "CUDA graph replay did not beat direct driver calls in this probe."
    )
    path.write_text(
        "\n".join(
            [
                "# Goal 1555 CUDA Graph Replay Feasibility Probe",
                "",
                "## Verdict",
                "",
                verdict,
                "",
                "## Scope",
                "",
                "- Probe: repeated CUDA driver memset calls versus replaying a captured CUDA graph.",
                f"- Library: `{result['library']}`",
                f"- Repeats: `{result['repeats']}`",
                "",
                "## Result",
                "",
                "| commands per replay | direct ms | graph ms | direct us/replay | graph us/replay | direct/graph |",
                "|---:|---:|---:|---:|---:|---:|",
                *[
                    "| {commands_per_replay} | {direct_ms:.6f} | {graph_ms:.6f} | "
                    "{direct_per_replay_us:.6f} | {graph_per_replay_us:.6f} | {speedup} |".format(
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
                f"Best direct-over-graph speedup: `{speedup_text}` at `{best['commands_per_replay']}` commands per replay.",
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
    parser.add_argument("--repeats", type=int, default=20000)
    parser.add_argument(
        "--commands-per-replay",
        type=int,
        nargs="+",
        default=[1, 4, 8, 16],
    )
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--md-out", type=Path)
    args = parser.parse_args()

    cases = [
        run_probe(args.library, args.repeats, commands)
        for commands in args.commands_per_replay
    ]
    result = {
        "probe": "goal1555_v1_5_4_optix_cuda_graph_replay_probe",
        "claim_boundary": (
            "CUDA graph replay feasibility only; not a COLLECT_K_BOUNDED "
            "measurement and does not authorize a collect-k speedup claim."
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
