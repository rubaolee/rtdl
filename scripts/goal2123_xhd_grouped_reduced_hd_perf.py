from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_hausdorff_v2_function as hd


DEFAULT_SIZES = (4096, 8192, 32768, 65536, 131072, 262144, 524288)
DEFAULT_GROUPS = {
    4096: 64,
    8192: 128,
    32768: 256,
    65536: 256,
    131072: 512,
    262144: 1024,
    524288: 2048,
    1048576: 4096,
}


def _run_cupy(points_a, points_b, *, warmup: int) -> dict[str, object]:
    start = time.perf_counter()
    result = hd.hausdorff_distance_2d(points_a, points_b, method="cupy_rawkernel", warmup=warmup)
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
    }


def _run_grouped(points_a, points_b, *, group_size: int, reduced: bool) -> dict[str, object]:
    start = time.perf_counter()
    if reduced:
        result = hd.hausdorff_distance_2d_rt_grouped_reduced_nearest_witness(
            points_a,
            points_b,
            seed_with_threshold=False,
            target_points_per_group=group_size,
        )
    else:
        result = hd.hausdorff_distance_2d_rt_grouped_nearest_witness(
            points_a,
            points_b,
            seed_with_threshold=False,
            target_points_per_group=group_size,
        )
    return {
        "ok": True,
        "elapsed_sec": time.perf_counter() - start,
        "distance": result.distance,
        "direction": result.direction,
        "source_index": result.source_index,
        "target_index": result.target_index,
        "method": result.method,
        "target_points_per_group": group_size,
    }


def _safe_call(name: str, fn):
    try:
        return fn()
    except Exception as exc:  # pragma: no cover - perf artifact path
        return {"ok": False, "method": name, "error": repr(exc)}


def run(args: argparse.Namespace) -> dict[str, object]:
    rows = []
    sizes = tuple(args.sizes or DEFAULT_SIZES)
    for n in sizes:
        group_size = int(args.group_size or DEFAULT_GROUPS.get(n, max(64, n // 256)))
        print(f"[goal2123] size={n} group={group_size} generate start", flush=True)
        points_a = hd.make_demo_points(n, seed=args.seed_a)
        points_b = hd.make_demo_points(n, seed=args.seed_b, offset=(args.offset_x, args.offset_y))

        print(f"[goal2123] size={n} cupy baseline start", flush=True)
        cupy = _safe_call("cupy_rawkernel", lambda: _run_cupy(points_a, points_b, warmup=args.warmup))
        print(f"[goal2123] size={n} cupy done ok={cupy.get('ok')} sec={cupy.get('elapsed_sec')}", flush=True)

        grouped = None
        if args.include_row_materialized:
            print(f"[goal2123] size={n} row-materialized grouped RTDL start", flush=True)
            grouped = _safe_call(
                "rtdl_rt_grouped_nearest_witness",
                lambda: _run_grouped(points_a, points_b, group_size=group_size, reduced=False),
            )
            print(
                f"[goal2123] size={n} row-materialized done ok={grouped.get('ok')} sec={grouped.get('elapsed_sec')}",
                flush=True,
            )

        print(f"[goal2123] size={n} reduced grouped RTDL start", flush=True)
        reduced = _safe_call(
            "rtdl_rt_grouped_reduced_nearest_witness",
            lambda: _run_grouped(points_a, points_b, group_size=group_size, reduced=True),
        )
        print(f"[goal2123] size={n} reduced done ok={reduced.get('ok')} sec={reduced.get('elapsed_sec')}", flush=True)

        row = {
            "n": n,
            "target_points_per_group": group_size,
            "cupy_rawkernel": cupy,
            "rtdl_rt_grouped_reduced_nearest_witness": reduced,
        }
        if grouped is not None:
            row["rtdl_rt_grouped_nearest_witness"] = grouped
        if cupy.get("ok") and reduced.get("ok"):
            row["matches_cupy"] = math.isclose(
                float(cupy["distance"]),
                float(reduced["distance"]),
                rel_tol=args.tolerance,
                abs_tol=args.tolerance,
            )
            row["reduced_vs_cupy_ratio"] = float(reduced["elapsed_sec"]) / float(cupy["elapsed_sec"])
        if grouped and grouped.get("ok") and reduced.get("ok"):
            row["reduced_vs_row_materialized_ratio"] = float(reduced["elapsed_sec"]) / float(grouped["elapsed_sec"])
        rows.append(row)
    return {
        "goal": "goal2123_xhd_grouped_reduced_hd_perf",
        "commit": args.commit_label,
        "gpu": os.popen("nvidia-smi --query-gpu=name,driver_version --format=csv,noheader 2>/dev/null | head -1").read().strip(),
        "sizes": list(sizes),
        "rows": rows,
        "claim_boundary": {
            "same_xhd_paper_datasets": False,
            "synthetic_large_scale_speedup_authorized": False,
            "release_speedup_claim_authorized": False,
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Goal2123 grouped RTDL/OptiX Hausdorff reduction perf sweep.")
    parser.add_argument("--sizes", type=int, action="append")
    parser.add_argument("--group-size", type=int)
    parser.add_argument("--seed-a", type=int, default=11)
    parser.add_argument("--seed-b", type=int, default=29)
    parser.add_argument("--offset-x", type=float, default=0.08)
    parser.add_argument("--offset-y", type=float, default=-0.06)
    parser.add_argument("--warmup", type=int, default=1)
    parser.add_argument("--tolerance", type=float, default=1e-6)
    parser.add_argument("--include-row-materialized", action="store_true")
    parser.add_argument("--commit-label", default="")
    parser.add_argument("--json-out", type=Path, required=True)
    args = parser.parse_args(argv)

    payload = run(args)
    rendered = json.dumps(payload, indent=2, sort_keys=True)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(rendered + "\n", encoding="utf-8")
    print(rendered, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
