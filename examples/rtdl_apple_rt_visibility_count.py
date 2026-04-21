#!/usr/bin/env python3
from __future__ import annotations

import json

import rtdsl as rt


def main() -> int:
    triangles = (
        rt.Triangle(id=0, x0=1.0, y0=-0.5, x1=1.8, y1=-0.5, x2=1.8, y2=0.5),
        rt.Triangle(id=1, x0=1.0, y0=-0.5, x1=1.8, y1=0.5, x2=1.0, y2=0.5),
        rt.Triangle(id=2, x0=1.0, y0=2.0, x1=1.8, y1=2.0, x2=1.8, y2=2.8),
        rt.Triangle(id=3, x0=1.0, y0=2.0, x1=1.8, y1=2.8, x2=1.0, y2=2.8),
    )
    rays = (
        rt.Ray2D(id=0, ox=0.0, oy=0.0, dx=3.0, dy=0.0, tmax=1.0),
        rt.Ray2D(id=1, ox=0.0, oy=2.4, dx=3.0, dy=0.0, tmax=1.0),
        rt.Ray2D(id=2, ox=0.0, oy=4.0, dx=3.0, dy=0.0, tmax=1.0),
        rt.Ray2D(id=3, ox=0.0, oy=-2.0, dx=3.0, dy=0.0, tmax=1.0),
    )

    try:
        packed_rays = rt.prepare_apple_rt_rays_2d(rays)
        with rt.prepare_apple_rt_ray_triangle_any_hit_2d(triangles) as prepared:
            blocked_count, profile = prepared.count_profile_packed(packed_rays)
    except Exception as exc:
        print(json.dumps({"status": "skipped", "reason": f"Apple RT unavailable: {exc}"}, indent=2))
        return 0

    print(
        json.dumps(
            {
                "status": "ok",
                "input": {"ray_count": len(rays), "triangle_count": len(triangles)},
                "output": {"blocked_ray_count": blocked_count, "clear_ray_count": len(rays) - blocked_count},
                "profile": {
                    "native_total_seconds": profile["total_seconds"],
                    "dispatch_wait_seconds": profile["dispatch_wait_seconds"],
                    "hit_count": profile["hit_count"],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
