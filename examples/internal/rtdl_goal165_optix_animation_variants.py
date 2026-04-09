"""Goal 165: Run three spin-speed variants on OptiX and report per-frame parity.

Two tiers:
  1. Parity tier: 64x64, 4 frames, optix vs cpu_python_reference -- fast
  2. Full-res tier: 192x192, 8 frames, optix only -- visual artifact

Usage (Linux):
    cd /home/lestat/work/rtdl_python_only
    PYTHONPATH=src:. python3 examples/internal/rtdl_goal165_optix_animation_variants.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, "src")
sys.path.insert(0, ".")

from examples.visual_demo.rtdl_spinning_ball_3d_demo import render_spinning_ball_3d_frames

VARIANTS = [
    {"name": "current_spin", "spin_speed": 1.1},
    {"name": "slower_spin", "spin_speed": 0.35},
    {"name": "no_spin", "spin_speed": 0.0},
]

# Tier 1: small enough to include cpu_python_reference comparison
PARITY_PARAMS = {
    "backend": "optix",
    "compare_backend": "cpu_python_reference",
    "width": 64,
    "height": 64,
    "latitude_bands": 12,
    "longitude_bands": 24,
    "frame_count": 4,
}

# Tier 2: full-resolution animation artifact, no comparison
FULLRES_PARAMS = {
    "backend": "optix",
    "compare_backend": "none",
    "width": 192,
    "height": 192,
    "latitude_bands": 32,
    "longitude_bands": 64,
    "frame_count": 8,
}


def _parity_list(summary: dict) -> list[bool]:
    result = []
    for frame in summary["frames"]:
        cb = frame.get("compare_backend")
        if cb is None:
            result.append(False)
        else:
            result.append(bool(cb.get("matches", False)))
    return result


def run_tier(tier_name: str, params: dict, variants: list[dict]) -> dict:
    print(f"\n{'='*60}", flush=True)
    print(f"Tier: {tier_name}", flush=True)
    print(f"Params: {params}", flush=True)
    print(f"{'='*60}", flush=True)

    tier_results = {}
    all_ok = True

    for variant in variants:
        name = variant["name"]
        spin_speed = variant["spin_speed"]
        output_dir = Path(f"build/goal165_optix_variants/{tier_name}/{name}")

        print(f"\n  --- Variant: {name} (spin_speed={spin_speed}) ---", flush=True)

        summary = render_spinning_ball_3d_frames(
            spin_speed=spin_speed,
            output_dir=output_dir,
            **params,
        )

        if params.get("compare_backend") and params["compare_backend"] != "none":
            parity = _parity_list(summary)
            all_parity_ok = all(parity)
            if not all_parity_ok:
                all_ok = False
        else:
            parity = None
            all_parity_ok = None

        query_share = summary["query_share"]

        result = {
            "variant": name,
            "spin_speed": spin_speed,
            "frame_count": summary["frame_count"],
            "parity": parity,
            "all_parity_ok": all_parity_ok,
            "query_share": query_share,
            "total_query_seconds": summary["total_query_seconds"],
            "total_shading_seconds": summary["total_shading_seconds"],
            "triangle_count": summary["triangle_count"],
        }
        tier_results[name] = result

        print(f"    parity: {parity}", flush=True)
        print(f"    all_parity_ok: {all_parity_ok}", flush=True)
        print(f"    query_share: {query_share:.4f}", flush=True)
        print(f"    total_query_seconds: {summary['total_query_seconds']:.4f}", flush=True)

    return {"tier": tier_name, "params": params, "all_ok": all_ok, "variants": tier_results}


def main() -> None:
    parity_results = run_tier("parity_64x64", PARITY_PARAMS, VARIANTS)
    fullres_results = run_tier("fullres_192x192", FULLRES_PARAMS, VARIANTS)

    combined = {
        "goal": "165",
        "description": "OptiX spinning-ball 3D animation variants",
        "parity_tier": parity_results,
        "fullres_tier": fullres_results,
    }

    print("\n=== Goal 165 Combined Results ===")
    print(json.dumps(combined, indent=2, sort_keys=True))

    parity_ok = parity_results["all_ok"]
    status = "PASS" if parity_ok else "FAIL"
    print(f"\nParity tier overall status: {status}")
    sys.exit(0 if parity_ok else 1)


if __name__ == "__main__":
    main()
