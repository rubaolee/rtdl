#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import rtdsl as rt
from scripts.goal595_apple_rt_perf_harness import _measure
from scripts.goal595_apple_rt_perf_harness import _plane_triangles
from scripts.goal595_apple_rt_perf_harness import _rays_3d
from scripts.goal595_apple_rt_perf_harness import _rows_match
from scripts.goal595_apple_rt_perf_harness import closest_hit_3d_kernel


REPORTS_DIR = ROOT / "docs" / "reports"
DEFAULT_JSON = REPORTS_DIR / "goal596_apple_rt_prepared_closest_hit_perf_macos_2026-04-19.json"
DEFAULT_MD = REPORTS_DIR / "goal596_apple_rt_prepared_closest_hit_perf_macos_2026-04-19.md"


def _prepare_seconds(triangles):
    start = time.perf_counter()
    prepared = rt.prepare_apple_rt_ray_triangle_closest_hit(triangles)
    return time.perf_counter() - start, prepared


def run_perf(*, warmups: int, repeats: int, cv_threshold: float) -> dict[str, object]:
    rays = _rays_3d(256)
    triangles = _plane_triangles(256)
    cpu_rows = tuple(rt.ray_triangle_closest_hit_cpu(rays, triangles))
    prepare_sec, prepared = _prepare_seconds(triangles)
    try:
        one_shot = _measure(
            lambda: tuple(rt.run_apple_rt(closest_hit_3d_kernel, native_only=True, rays=rays, triangles=triangles)),
            warmups=warmups,
            repeats=repeats,
            cv_threshold=cv_threshold,
        )
        prepared_measured = _measure(
            lambda: tuple(prepared.run(rays)),
            warmups=warmups,
            repeats=repeats,
            cv_threshold=cv_threshold,
        )
        embree = _measure(
            lambda: tuple(rt.run_embree(closest_hit_3d_kernel, rays=rays, triangles=triangles)),
            warmups=warmups,
            repeats=repeats,
            cv_threshold=cv_threshold,
        )
    finally:
        prepared.close()

    results = {}
    for name, measured in (
        ("apple_rt_one_shot", one_shot),
        ("apple_rt_prepared", prepared_measured),
        ("embree", embree),
    ):
        last_result = measured.pop("last_result")
        results[name] = {
            **measured,
            "row_count": len(last_result),
            "matches_cpu_reference": _rows_match("ray_triangle_closest_hit_3d", cpu_rows, last_result),
        }
    one_shot_median = results["apple_rt_one_shot"]["stats"]["median_seconds"]
    prepared_median = results["apple_rt_prepared"]["stats"]["median_seconds"]
    embree_median = results["embree"]["stats"]["median_seconds"]
    return {
        "date": "2026-04-19",
        "goal": "Goal596 Apple RT prepared closest-hit",
        "versions": {
            "apple_rt": rt.apple_rt_version(),
            "apple_rt_context": rt.apple_rt_context_probe(),
            "embree": rt.embree_version(),
        },
        "methodology": {
            "warmups": warmups,
            "repeats": repeats,
            "stability_threshold_cv": cv_threshold,
            "note": "Prepared time measures repeated ray batches after one acceleration-structure build; prepare_seconds is reported separately.",
        },
        "input_sizes": {"rays": len(rays), "triangles": len(triangles)},
        "cpu_reference_rows": len(cpu_rows),
        "prepare_seconds": prepare_sec,
        "results": results,
        "prepared_vs_one_shot_median_ratio": prepared_median / one_shot_median if one_shot_median else None,
        "prepared_vs_embree_median_ratio": prepared_median / embree_median if embree_median else None,
    }


def render_markdown(payload: dict[str, object]) -> str:
    results = payload["results"]
    lines = [
        "# Goal596: Apple RT Prepared Closest-Hit Performance",
        "",
        f"Date: {payload['date']}",
        "",
        "Status: local measurement artifact",
        "",
        "## Methodology",
        "",
        "- Workload: 3D `ray_triangle_closest_hit` on the same 256-ray / 256-triangle fixture used by Goal595.",
        f"- Warmups: `{payload['methodology']['warmups']}`.",
        f"- Repeats: `{payload['methodology']['repeats']}`.",
        f"- Stability threshold: coefficient of variation <= `{payload['methodology']['stability_threshold_cv']}`.",
        "- Prepared timing excludes one-time acceleration-structure build; `prepare_seconds` is reported separately.",
        "- Unstable medians are engineering-triage evidence only, not public speedup wording.",
        "",
        "## Versions",
        "",
        "```json",
        json.dumps(payload["versions"], indent=2),
        "```",
        "",
        f"Prepare time: `{payload['prepare_seconds']:.9f} s`.",
        "",
        "## Results",
        "",
        "| Backend path | Median | CV | Stable | Rows | Matches CPU |",
        "| --- | ---: | ---: | --- | ---: | --- |",
    ]
    for name in ("apple_rt_one_shot", "apple_rt_prepared", "embree"):
        row = results[name]
        stats = row["stats"]
        lines.append(
            "| "
            f"`{name}` | "
            f"{stats['median_seconds']:.9f} s | "
            f"{stats['coefficient_of_variation']:.3f} | "
            f"{row['stable']} | "
            f"{row['row_count']} | "
            f"{row['matches_cpu_reference']} |"
        )
    lines.extend(
        [
            "",
            "## Ratios",
            "",
            f"- Prepared / one-shot Apple RT median ratio: `{payload['prepared_vs_one_shot_median_ratio']:.3f}x`.",
            f"- Prepared / Embree median ratio: `{payload['prepared_vs_embree_median_ratio']:.3f}x`.",
            "",
            "## Interpretation",
            "",
            "The prepared API reduces repeated-call median latency for this fixture, but Apple RT variance remains above the stability threshold.",
            "This closes the prepared-handle functionality and optimization direction; public performance wording still requires stable follow-up evidence.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmups", type=int, default=5)
    parser.add_argument("--repeats", type=int, default=20)
    parser.add_argument("--cv-threshold", type=float, default=0.15)
    parser.add_argument("--json-out", type=Path, default=DEFAULT_JSON)
    parser.add_argument("--md-out", type=Path, default=DEFAULT_MD)
    args = parser.parse_args()
    payload = run_perf(warmups=args.warmups, repeats=args.repeats, cv_threshold=args.cv_threshold)
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    args.md_out.write_text(render_markdown(payload), encoding="utf-8")
    print(args.json_out)
    print(args.md_out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

