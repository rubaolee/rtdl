from __future__ import annotations

import argparse
import json
import time
from decimal import Decimal, getcontext
from pathlib import Path

getcontext().prec = 80

INTERNAL_MAX = (1 << 46) - 1
INTERNAL_MIN = -(1 << 46)
MARGIN = Decimal(1)


def _scale_params(bounds: list[float]) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    min_x, max_x, min_y, max_y = [Decimal(str(v)) for v in bounds]
    box_min_x = min_x - MARGIN
    box_max_x = max_x + MARGIN
    box_min_y = min_y - MARGIN
    box_max_y = max_y + MARGIN
    internal_range = Decimal(INTERNAL_MAX - INTERNAL_MIN)
    rx = internal_range / (box_max_x - box_min_x)
    ry = internal_range / (box_max_y - box_min_y)
    deltax = (Decimal(INTERNAL_MAX + INTERNAL_MIN) - (box_max_x + box_min_x) * rx) / 2
    deltay = (Decimal(INTERNAL_MAX + INTERNAL_MIN) - (box_max_y + box_min_y) * ry) / 2
    return rx, ry, deltax, deltay


def _scale_decimal(value: str, ratio: Decimal, delta: Decimal) -> int:
    return int(Decimal(value) * ratio + delta)


def _candidate(segment_id: int, header: str, p1: str, p2: str, point_sx: int, point_sy: int, query_map_id: int, rx: Decimal, ry: Decimal, dx: Decimal, dy: Decimal):
    h = header.split()
    left = int(h[4])
    right = int(h[5])
    x0, y0 = p1.split()
    x1, y1 = p2.split()
    sx0 = _scale_decimal(x0, rx, dx)
    sx1 = _scale_decimal(x1, rx, dx)
    sy0 = _scale_decimal(y0, ry, dy)
    sy1 = _scale_decimal(y1, ry, dy)
    a = sy0 - sy1
    b = sx1 - sx0
    c = -(sx0 * a) - (sy0 * b)
    if b < 0:
        a = -a
        b = -b
        c = -c
    lo = min(sx0, sx1)
    hi = max(sx0, sx1)
    excluded_endpoint = lo if query_map_id == 0 else hi
    if not (lo <= point_sx <= hi):
        return None
    if b == 0:
        return None
    xsect_y = Decimal(-(a * point_sx) - c) / Decimal(b)
    diff = Decimal(point_sy) - xsect_y
    sos_diff = diff
    if sos_diff == 0:
        sos_diff = Decimal(-a if query_map_id == 0 else a)
    if sos_diff == 0:
        sos_diff = Decimal(-b if query_map_id == 0 else b)
    endpoint = point_sx == excluded_endpoint
    skip_above = sos_diff > 0
    accepted = (not endpoint) and (not skip_above)
    slope = Decimal(a) / Decimal(b)
    face = right if sx0 < sx1 else left
    return {
        "segment_id": segment_id,
        "header": header.strip(),
        "x0": x0,
        "y0": y0,
        "x1": x1,
        "y1": y1,
        "left": left,
        "right": right,
        "sx0": sx0,
        "sx1": sx1,
        "sy0": sy0,
        "sy1": sy1,
        "face": face,
        "endpoint": endpoint,
        "xsect_y": str(xsect_y),
        "diff": str(diff),
        "sos_diff": str(sos_diff),
        "skip_above": skip_above,
        "accepted": accepted,
        "slope": str(slope),
    }


def _best_key(candidate: dict[str, object], query_map_id: int):
    xsect_y = Decimal(str(candidate["xsect_y"]))
    slope = Decimal(str(candidate["slope"]))
    return (xsect_y, -slope if query_map_id == 0 else slope, int(candidate["segment_id"]))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--segments", required=True)
    parser.add_argument("--bounds-json", required=True, help="JSON file containing a scale_bounds array")
    parser.add_argument("--point-x", required=True)
    parser.add_argument("--point-y", required=True)
    parser.add_argument("--query-map-id", type=int, choices=[0, 1], required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--top", type=int, default=20)
    args = parser.parse_args()

    with open(args.bounds_json, "r", encoding="utf-8") as f:
        bounds_container = json.load(f)
    bounds = bounds_container["scale_bounds"] if isinstance(bounds_container, dict) else bounds_container
    rx, ry, dx, dy = _scale_params(bounds)
    point_sx = _scale_decimal(args.point_x, rx, dx)
    point_sy = _scale_decimal(args.point_y, ry, dy)

    start = time.perf_counter()
    covering = []
    accepted = []
    with Path(args.segments).open("r", encoding="utf-8", errors="replace") as f:
        segment_id = 0
        for header in f:
            segment_id += 1
            p1 = next(f).strip()
            p2 = next(f).strip()
            row = _candidate(segment_id, header, p1, p2, point_sx, point_sy, args.query_map_id, rx, ry, dx, dy)
            if row is None:
                continue
            covering.append(row)
            if row["accepted"]:
                accepted.append(row)

    accepted_sorted = sorted(accepted, key=lambda row: _best_key(row, args.query_map_id))
    summary = {
        "segments": args.segments,
        "point_x": args.point_x,
        "point_y": args.point_y,
        "point_sx": point_sx,
        "point_sy": point_sy,
        "query_map_id": args.query_map_id,
        "elapsed_sec": time.perf_counter() - start,
        "covering_count": len(covering),
        "accepted_count": len(accepted),
        "best": accepted_sorted[0] if accepted_sorted else None,
        "accepted_top": accepted_sorted[: args.top],
    }
    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, sort_keys=True)
        f.write("\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "accepted_top"}, indent=2, sort_keys=True))
    return 0 if accepted_sorted else 1


if __name__ == "__main__":
    raise SystemExit(main())
