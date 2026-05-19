from __future__ import annotations

import argparse
import json
import pathlib
import sys
import time


ROOT = next(parent for parent in pathlib.Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples.v2_0.research_benchmarks.rt_dbscan.rtdl_rt_dbscan_benchmark_app import (  # noqa: E402
    run_rt_dbscan_benchmark,
)


DEFAULT_MODES = (
    "partner_cupy_grid_components_3d",
    "optix_core_flags_cupy_grid_components_3d",
)


def run_repeat_probe(
    *,
    dataset: str,
    point_count: int,
    repeat_count: int,
    modes: tuple[str, ...],
) -> dict[str, object]:
    if repeat_count < 1:
        raise ValueError("repeat_count must be positive")
    rows: list[dict[str, object]] = []
    signatures: dict[str, object] = {}
    for mode in modes:
        for repeat_index in range(repeat_count):
            outer_start = time.perf_counter()
            result = run_rt_dbscan_benchmark(
                mode=mode,
                dataset=dataset,
                point_count=point_count,
                radius=None,
                min_neighbors=None,
                seed=20260519,
                partner="cupy",
                include_rows=False,
                validate=False,
            )
            outer_elapsed = time.perf_counter() - outer_start
            signatures.setdefault(mode, result["signature"])
            metadata = result.get("metadata", {})
            rows.append(
                {
                    "mode": mode,
                    "repeat_index": repeat_index + 1,
                    "outer_elapsed_sec": outer_elapsed,
                    "app_elapsed_sec": result["elapsed_sec"],
                    "optix_core_flag_sec": metadata.get("optix_core_flag_sec"),
                    "cupy_component_continuation_sec": metadata.get("cupy_component_continuation_sec"),
                    "rt_core_accelerated": result["claim_boundary"]["rt_core_accelerated"],
                    "materializes_neighbor_rows": metadata.get("materializes_neighbor_rows"),
                    "signature": result["signature"],
                }
            )
    return {
        "app": "rt_dbscan_repeat_probe",
        "dataset": dataset,
        "point_count": point_count,
        "repeat_count": repeat_count,
        "modes": list(modes),
        "rows": rows,
        "signatures_match": len({json.dumps(value, sort_keys=True) for value in signatures.values()}) == 1,
        "claim_boundary": {
            "paper_dataset_reproduction": False,
            "paper_speedup_claim_authorized": False,
            "broad_rt_core_speedup_claim_authorized": False,
            "steady_state_probe_only": True,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Repeat probe for RT-DBSCAN bridge warm/steady-state behavior.")
    parser.add_argument("--dataset", default="clustered3d", choices=("clustered3d", "road3d", "ngsim_dense"))
    parser.add_argument("--point-count", type=int, default=4096)
    parser.add_argument("--repeat-count", type=int, default=4)
    parser.add_argument("--mode", action="append", choices=DEFAULT_MODES, dest="modes")
    args = parser.parse_args(argv)
    modes = tuple(args.modes) if args.modes else DEFAULT_MODES
    print(
        json.dumps(
            run_repeat_probe(
                dataset=args.dataset,
                point_count=args.point_count,
                repeat_count=args.repeat_count,
                modes=modes,
            ),
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
