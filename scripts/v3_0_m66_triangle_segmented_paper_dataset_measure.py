from __future__ import annotations

import argparse
import json
import os
import platform
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run V3.0 M66 Triangle segmented RT-2A1 paper-dataset evidence."
    )
    parser.add_argument(
        "--input",
        action="append",
        nargs=3,
        metavar=("NAME", "EDGE_FILE", "EXPECTED_TRIANGLES"),
        required=True,
    )
    parser.add_argument("--warmup", type=int, default=0)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--segment-max-two-hop-rows", type=int, default=5_000_000)
    parser.add_argument("--hardware", default=None)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("build/goal4462_v3_0_m66_triangle_segmented_paper_dataset_evidence.json"),
    )
    args = parser.parse_args()

    if args.warmup < 0:
        raise ValueError("--warmup must be non-negative")
    if args.repeat < 1:
        raise ValueError("--repeat must be at least 1")
    if args.segment_max_two_hop_rows < 1:
        raise ValueError("--segment-max-two-hop-rows must be at least 1")

    from examples.current.research_benchmarks.triangle_counting import (
        rtdl_triangle_counting_benchmark_app as app,
    )

    rows = []
    for name, edge_file_text, expected_text in args.input:
        edge_file = Path(edge_file_text)
        expected = int(expected_text)
        if not edge_file.exists():
            raise FileNotFoundError(edge_file)
        payload = app.run_app(
            "rt_graph_2a1_segmented_generic_rt",
            edge_file=str(edge_file),
            edge_format="binary",
            backend="optix",
            detail="summary",
            partner="cupy",
            warmup=args.warmup,
            repeat=args.repeat,
            segment_max_two_hop_rows=args.segment_max_two_hop_rows,
        )
        row = _compact_row(
            payload,
            name=name,
            edge_file=edge_file,
            expected_triangle_count=expected,
        )
        if not row["triangle_count_matches_expected"]:
            raise RuntimeError(
                f"{name}: segmented RT-2A1 result mismatch; "
                f"expected {expected}, observed {row['observed_triangle_count']}"
            )
        rows.append(row)

    evidence = {
        "goal": 4462,
        "milestone": "v3_0_m66",
        "implementation": "segmented_2a1_cupy_paper_dataset",
        "status": "segmented_rt_2a1_paper_dataset_validation",
        "parameters": {
            "warmup": args.warmup,
            "repeat": args.repeat,
            "segment_max_two_hop_rows": args.segment_max_two_hop_rows,
            "hardware": args.hardware or _hardware_label(),
        },
        "rows": rows,
        "comparison": {
            "datasets": tuple(row["dataset"] for row in rows),
            "all_triangle_counts_match_expected": all(row["triangle_count_matches_expected"] for row in rows),
            "global_two_hop_summary_materialized": any(
                row["global_two_hop_summary_materialized"] for row in rows
            ),
            "previous_goal2593_blocker_addressed_for": tuple(
                row["dataset"] for row in rows if row["triangle_count_matches_expected"]
            ),
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
            "paper_dataset_speedup_claim_authorized": False,
            "whole_app_speedup_claim_authorized": False,
            "public_speedup_claim_authorized": False,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"comparison": evidence["comparison"], "rows": rows}, indent=2, sort_keys=True))
    print(f"wrote {args.output}")
    return 0


def _compact_row(
    payload: dict[str, object],
    *,
    name: str,
    edge_file: Path,
    expected_triangle_count: int,
) -> dict[str, object]:
    timing = dict(payload["timing_ms"])
    observed = int(payload["generic_rt_weighted_triangle_count"])
    return {
        "dataset": name,
        "edge_file": str(edge_file),
        "edge_count": edge_file.stat().st_size // 8,
        "expected_triangle_count": int(expected_triangle_count),
        "observed_triangle_count": observed,
        "triangle_count_matches_expected": observed == int(expected_triangle_count),
        "mode": payload["mode"],
        "partner": payload["partner"],
        "backend": payload["backend"],
        "rt_core_accelerated": payload["rt_core_accelerated"],
        "primitive_count": payload["primitive_count"],
        "ray_count": payload["ray_count"],
        "global_two_hop_summary_materialized": bool(
            payload["primitive_layout"]["global_two_hop_summary_materialized"]
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
            "query_repeat": timing.get("query_repeat"),
            "query_warmup": timing.get("query_warmup"),
            "total": timing.get("total"),
        },
    }


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
