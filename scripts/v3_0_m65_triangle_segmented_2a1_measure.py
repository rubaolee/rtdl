from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M65 triangle-counting segmented RT-2A1 CuPy/OptiX evidence."
    )
    parser.add_argument("--cliques", type=int, default=200000)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--repeat", type=int, default=3)
    parser.add_argument("--segment-max-two-hop-rows", type=int, default=200000)
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--edge-file",
        type=Path,
        default=Path("build/goal4461_m65_triangle_k4_cliques.edge"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4461_v3_0_m65_triangle_segmented_2a1_evidence.json"),
    )
    args = parser.parse_args()

    if args.cliques < 1:
        raise ValueError("--cliques must be at least 1")
    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.repeat < 1:
        raise ValueError("--repeat must be at least 1")
    if args.segment_max_two_hop_rows < 1:
        raise ValueError("--segment-max-two-hop-rows must be at least 1")

    from examples.benchmark_apps.triangle_counting import (
        rtdl_triangle_counting_benchmark_app as app,
    )
    from examples.benchmark_apps.triangle_counting.rt_graph_contract import (
        write_binary_edges,
    )

    args.edge_file.parent.mkdir(parents=True, exist_ok=True)
    write_binary_edges(args.edge_file, _k4_clique_edges(args.cliques))
    payload = app.run_app(
        "rt_graph_2a1_segmented_generic_rt",
        edge_file=str(args.edge_file),
        edge_format="binary",
        backend="optix",
        detail="summary",
        partner="cupy",
        warmup=args.warmup,
        repeat=args.repeat,
        segment_max_two_hop_rows=args.segment_max_two_hop_rows,
    )
    expected_triangle_count = args.cliques * 4
    observed_triangle_count = int(payload["generic_rt_weighted_triangle_count"])
    if observed_triangle_count != expected_triangle_count:
        raise RuntimeError(
            "M65 segmented RT-2A1 route failed generated K4 oracle: "
            f"expected {expected_triangle_count}, observed {observed_triangle_count}"
        )

    evidence = {
        "goal": 4461,
        "milestone": "v3_0_m65",
        "implementation": "segmented_2a1_cupy_directed_csr",
        "status": "segmented_rt_2a1_avoids_global_two_hop_summary_materialization",
        "parameters": {
            "cliques": args.cliques,
            "edge_count": args.cliques * 6,
            "expected_triangle_count": expected_triangle_count,
            "warmup": args.warmup,
            "repeat": args.repeat,
            "segment_max_two_hop_rows": args.segment_max_two_hop_rows,
            "edge_file": str(args.edge_file),
            "hardware": args.hardware or _hardware_label(),
        },
        "row": _compact_row(payload, expected_triangle_count=expected_triangle_count),
        "comparison": {
            "triangle_count_matches_oracle": observed_triangle_count == expected_triangle_count,
            "global_two_hop_summary_materialized": bool(
                payload["primitive_layout"]["global_two_hop_summary_materialized"]
            ),
            "segment_count": int(payload["segmentation"]["segment_count"]),
            "max_segment_two_hop_rows": int(payload["segmentation"]["max_segment_two_hop_rows"]),
            "total_two_hop_rows": int(payload["segmentation"]["total_two_hop_rows"]),
            "rt_core_accelerated": bool(payload["rt_core_accelerated"]),
            "public_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
        },
        "claim_boundary": {
            "engine_contract": "generic prepared triangle scene plus generic ray/triangle weighted any-hit sum",
            "partner_role": "CuPy app partner builds directed CSR and segmented duplicate two-hop ray batches",
            "native_engine_customization": False,
            "app_specific_native_engine_logic_allowed": False,
            "automatic_partner_selection_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": evidence["comparison"], "row": evidence["row"]}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _compact_row(payload: dict[str, object], *, expected_triangle_count: int) -> dict[str, object]:
    timing = dict(payload["timing_ms"])
    return {
        "mode": payload["mode"],
        "partner": payload["partner"],
        "backend": payload["backend"],
        "rt_core_accelerated": payload["rt_core_accelerated"],
        "primitive_count": payload["primitive_count"],
        "ray_count": payload["ray_count"],
        "expected_triangle_count": expected_triangle_count,
        "observed_triangle_count": int(payload["generic_rt_weighted_triangle_count"]),
        "triangle_count_matches_generated_oracle": (
            int(payload["generic_rt_weighted_triangle_count"]) == expected_triangle_count
        ),
        "segmentation": payload["segmentation"],
        "partner_timing_ms": payload["partner_timing_ms"],
        "timing_ms": {
            "build_contract": timing.get("build_contract"),
            "build_geometry": timing.get("build_geometry"),
            "prepare_scene_ms": timing.get("prepare_scene_ms"),
            "segment_ray_build_median_ms": timing.get("segment_ray_build_median_ms"),
            "query_median_ms": timing.get("query_median_ms"),
            "query_min_ms": timing.get("query_min_ms"),
            "query_max_ms": timing.get("query_max_ms"),
            "total": timing.get("total"),
        },
    }


def _k4_clique_edges(clique_count: int) -> tuple[tuple[int, int], ...]:
    edges: list[tuple[int, int]] = []
    for index in range(int(clique_count)):
        base = index * 4
        edges.extend(
            (
                (base + 0, base + 1),
                (base + 0, base + 2),
                (base + 0, base + 3),
                (base + 1, base + 2),
                (base + 1, base + 3),
                (base + 2, base + 3),
            )
        )
    return tuple(edges)


def _hardware_label() -> str:
    try:
        import subprocess

        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name", "--format=csv,noheader"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
        gpu = result.stdout.strip().splitlines()[0] if result.stdout.strip() else "unknown_gpu"
    except Exception:
        gpu = "unknown_gpu"
    return f"{platform.platform()} | {gpu} | CUDA_HOME={os.environ.get('CUDA_HOME') or 'unset'}"


if __name__ == "__main__":
    raise SystemExit(main())
