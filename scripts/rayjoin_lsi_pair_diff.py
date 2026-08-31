from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Iterable


INT64_MIN = -(1 << 63)
INT64_MAX = (1 << 63) - 1
SCALING_BOUNDING_BOX_MARGIN = 1.0


def _read_author_pairs(path: Path) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        base_id, query_id = (int(value) for value in line.split())
        pairs.add((base_id, query_id))
    return pairs


def _read_rtdl_pairs_as_author_pairs(path: Path) -> set[tuple[int, int]]:
    pairs: set[tuple[int, int]] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        query_id, base_id = (int(value) for value in line.split())
        pairs.add((base_id - 1, query_id - 1))
    return pairs


def _author_scaling(base, query):
    all_points = [point for dataset in (base, query) for chain in dataset.chains for point in chain.points]
    min_x = min(point.x for point in all_points)
    max_x = max(point.x for point in all_points)
    min_y = min(point.y for point in all_points)
    max_y = max(point.y for point in all_points)

    internal_max = INT64_MAX >> 17
    internal_min = INT64_MIN >> 17
    internal_range = internal_max - internal_min
    margin = SCALING_BOUNDING_BOX_MARGIN
    max_x_margin = max_x + margin
    min_x_margin = min_x - margin
    max_y_margin = max_y + margin
    min_y_margin = min_y - margin

    rx = internal_range / (max_x_margin - min_x_margin)
    ry = internal_range / (max_y_margin - min_y_margin)
    rrx = 1.0 / rx
    rry = 1.0 / ry
    deltax = 0.5 * ((internal_max + internal_min) - (max_x_margin + min_x_margin) * rx)
    deltay = 0.5 * ((internal_max + internal_min) - (max_y_margin + min_y_margin) * ry)
    ddeltax = 0.5 * ((max_x_margin + min_x_margin) - (internal_max + internal_min) * rrx)
    ddeltay = 0.5 * ((max_y_margin + min_y_margin) - (internal_max + internal_min) * rry)

    def fma(a: float, b: float, c: float) -> float:
        if hasattr(math, "fma"):
            return math.fma(a, b, c)
        return a * b + c

    def scale(x: float, y: float) -> tuple[int, int]:
        return int(fma(x, rx, deltax)), int(fma(y, ry, deltay))

    def unscale(x: int, y: int) -> tuple[float, float]:
        return x * rrx + ddeltax, y * rry + ddeltay

    return {
        "bbox": (min_x, min_y, max_x, max_y),
        "scaled_bbox": (
            int(min_x * rx + deltax),
            int(min_y * ry + deltay),
            int(max_x * rx + deltax),
            int(max_y * ry + deltay),
        ),
        "scale": scale,
        "unscale": unscale,
    }


def _line(segment: tuple[int, int, int, int]) -> tuple[int, int, int]:
    x0, y0, x1, y1 = segment
    a = y0 - y1
    b = x1 - x0
    c = -x0 * a - y0 * b
    if b < 0:
        return -a, -b, -c
    return a, b, c


def _eval(line: tuple[int, int, int], point: tuple[int, int]) -> int:
    a, b, c = line
    x, y = point
    return x * a + y * b + c


def _oriented_for_ray(segment: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = segment
    if x0 == x1:
        if y0 > y1:
            return x1, y1, x0, y0
    elif x0 > x1:
        return x1, y1, x0, y0
    return segment


def _rayjoin_predicate_detail(
    query_segment: tuple[int, int, int, int],
    base_segment: tuple[int, int, int, int],
) -> tuple[bool, dict[str, int | str | tuple[int, int, int]]]:
    query_line = _line(query_segment)
    base_line = _line(base_segment)
    query_p1 = (query_segment[0], query_segment[1])
    query_p2 = (query_segment[2], query_segment[3])
    base_p1 = (base_segment[0], base_segment[1])
    base_p2 = (base_segment[2], base_segment[3])

    base_p1_against_query = _eval(query_line, base_p1)
    base_p2_against_query = _eval(query_line, base_p2)
    query_p1_against_base = _eval(base_line, query_p1)
    query_p2_against_base = _eval(base_line, query_p2)
    detail: dict[str, int | str | tuple[int, int, int]] = {
        "query_line": query_line,
        "base_line": base_line,
        "base_p1_against_query_raw": base_p1_against_query,
        "base_p2_against_query_raw": base_p2_against_query,
        "query_p1_against_base_raw": query_p1_against_base,
        "query_p2_against_base_raw": query_p2_against_base,
    }

    if query_p1_against_base == 0:
        query_p1_against_base = -base_line[0]
    if query_p1_against_base == 0:
        query_p1_against_base = -base_line[1]
    if query_p1_against_base == 0:
        detail["stage"] = "query_p1_zero"
        return False, detail

    if query_p2_against_base == 0:
        query_p2_against_base = -base_line[0]
    if query_p2_against_base == 0:
        query_p2_against_base = -base_line[1]
    if query_p2_against_base == 0:
        detail["stage"] = "query_p2_zero"
        return False, detail

    detail["query_p1_against_base_tie"] = query_p1_against_base
    detail["query_p2_against_base_tie"] = query_p2_against_base
    if (
        (query_p1_against_base > 0 and query_p2_against_base > 0)
        or (query_p1_against_base < 0 and query_p2_against_base < 0)
    ):
        detail["stage"] = "query_same_side"
        return False, detail

    if base_p1_against_query == 0:
        base_p1_against_query = query_line[0]
    if base_p1_against_query == 0:
        base_p1_against_query = query_line[1]
    if base_p1_against_query == 0:
        detail["stage"] = "base_p1_zero"
        return False, detail

    if base_p2_against_query == 0:
        base_p2_against_query = query_line[0]
    if base_p2_against_query == 0:
        base_p2_against_query = query_line[1]
    if base_p2_against_query == 0:
        detail["stage"] = "base_p2_zero"
        return False, detail

    detail["base_p1_against_query_tie"] = base_p1_against_query
    detail["base_p2_against_query_tie"] = base_p2_against_query
    if (
        (base_p1_against_query > 0 and base_p2_against_query > 0)
        or (base_p1_against_query < 0 and base_p2_against_query < 0)
    ):
        detail["stage"] = "base_same_side"
        return False, detail

    if (query_p1 == base_p1 and query_p2 == base_p2) or (query_p1 == base_p2 and query_p2 == base_p1):
        detail["stage"] = "same_segment"
        return False, detail

    detail["stage"] = "hit"
    return True, detail


def _scaled_segment(segment: dict[str, float | int], scale) -> tuple[int, int, int, int]:
    x0, y0 = scale(float(segment["x0"]), float(segment["y0"]))
    x1, y1 = scale(float(segment["x1"]), float(segment["y1"]))
    return x0, y0, x1, y1


def _describe_pairs(
    pairs: Iterable[tuple[int, int]],
    *,
    base_segments,
    query_segments,
    scale,
    unscale,
    label: str,
    limit: int,
) -> None:
    for base_id, query_id in list(pairs)[:limit]:
        base = base_segments[base_id]
        query = query_segments[query_id]
        base_scaled = _scaled_segment(base, scale)
        query_scaled = _scaled_segment(query, scale)
        query_oriented = _oriented_for_ray(query_scaled)
        hit, detail = _rayjoin_predicate_detail(query_scaled, base_scaled)
        oriented_hit, oriented_detail = _rayjoin_predicate_detail(query_oriented, base_scaled)
        print()
        print(f"{label} base_eid={base_id} query_eid={query_id}")
        print(f"  base_chain={base['chain_id']} query_chain={query['chain_id']}")
        print(f"  base_raw=({base['x0']}, {base['y0']}) -> ({base['x1']}, {base['y1']})")
        print(f"  query_raw=({query['x0']}, {query['y0']}) -> ({query['x1']}, {query['y1']})")
        print(f"  base_scaled={base_scaled}")
        print(f"  query_scaled={query_scaled}")
        print(f"  query_oriented_for_ray={query_oriented}")
        print(f"  base_unscaled={unscale(base_scaled[0], base_scaled[1])} -> {unscale(base_scaled[2], base_scaled[3])}")
        print(f"  query_unscaled={unscale(query_scaled[0], query_scaled[1])} -> {unscale(query_scaled[2], query_scaled[3])}")
        print(f"  predicate_file_order={hit} {detail}")
        print(f"  predicate_ray_oriented_query={oriented_hit} {oriented_detail}")


def _summarize_pair_predicates(
    pairs: Iterable[tuple[int, int]],
    *,
    base_segments,
    query_segments,
    scale,
) -> dict[str, int]:
    stats = {
        "pairs": 0,
        "base_p1_on_query_raw": 0,
        "base_p2_on_query_raw": 0,
        "query_p1_on_base_raw": 0,
        "query_p2_on_base_raw": 0,
        "base_endpoint_on_query_raw": 0,
        "query_endpoint_on_base_raw": 0,
        "predicate_file_order_hit": 0,
    }
    for base_id, query_id in pairs:
        base_scaled = _scaled_segment(base_segments[base_id], scale)
        query_scaled = _scaled_segment(query_segments[query_id], scale)
        hit, detail = _rayjoin_predicate_detail(query_scaled, base_scaled)
        stats["pairs"] += 1
        base_endpoint = False
        query_endpoint = False
        if detail["base_p1_against_query_raw"] == 0:
            stats["base_p1_on_query_raw"] += 1
            base_endpoint = True
        if detail["base_p2_against_query_raw"] == 0:
            stats["base_p2_on_query_raw"] += 1
            base_endpoint = True
        if detail["query_p1_against_base_raw"] == 0:
            stats["query_p1_on_base_raw"] += 1
            query_endpoint = True
        if detail["query_p2_against_base_raw"] == 0:
            stats["query_p2_on_base_raw"] += 1
            query_endpoint = True
        if base_endpoint:
            stats["base_endpoint_on_query_raw"] += 1
        if query_endpoint:
            stats["query_endpoint_on_base_raw"] += 1
        if hit:
            stats["predicate_file_order_hit"] += 1
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Diff RayJoin author LSI pairs against RTDL dumped LSI pairs.")
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--author-pairs", required=True, type=Path)
    parser.add_argument("--rtdl-pairs", required=True, type=Path)
    parser.add_argument("--limit", default=20, type=int)
    parser.add_argument("--scan-author-stats", action="store_true")
    args = parser.parse_args()

    import rtdsl as rt

    author_pairs = _read_author_pairs(args.author_pairs)
    rtdl_pairs = _read_rtdl_pairs_as_author_pairs(args.rtdl_pairs)
    extras = sorted(rtdl_pairs - author_pairs)
    missing = sorted(author_pairs - rtdl_pairs)
    print(f"author={len(author_pairs)} rtdl={len(rtdl_pairs)} extra={len(extras)} missing={len(missing)}")
    print(f"extra_first={extras[:args.limit]}")
    print(f"missing_first={missing[:args.limit]}")

    if not extras and not missing:
        return

    base = rt.load_cdb(args.dataset_root / "point_cdb/dtl_cnty/dtl_cnty_Point.cdb")
    query = rt.load_cdb(args.dataset_root / "point_cdb/USAZIPCodeArea/USAZIPCodeArea_Point.cdb")
    base_segments = rt.chains_to_segments(base)
    query_segments = rt.chains_to_segments(query)
    scaling = _author_scaling(base, query)
    print(f"bbox={scaling['bbox']}")
    print(f"scaled_bbox={scaling['scaled_bbox']}")
    print(
        "extra_predicate_stats="
        f"{_summarize_pair_predicates(extras, base_segments=base_segments, query_segments=query_segments, scale=scaling['scale'])}"
    )
    if args.scan_author_stats:
        print(
            "author_predicate_stats="
            f"{_summarize_pair_predicates(sorted(author_pairs), base_segments=base_segments, query_segments=query_segments, scale=scaling['scale'])}"
        )
    _describe_pairs(
        extras,
        base_segments=base_segments,
        query_segments=query_segments,
        scale=scaling["scale"],
        unscale=scaling["unscale"],
        label="extra",
        limit=args.limit,
    )
    _describe_pairs(
        missing,
        base_segments=base_segments,
        query_segments=query_segments,
        scale=scaling["scale"],
        unscale=scaling["unscale"],
        label="missing",
        limit=args.limit,
    )


if __name__ == "__main__":
    main()
