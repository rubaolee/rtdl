#!/usr/bin/env python3
"""Convert GeoJSONSeq polygon features to RayJoin/RTDL CDB rings for LSI.

This is a Goal4848 paper-reproduction utility, not RTDL runtime code.  It
intentionally emits ring chains only: enough for line-segment-intersection
queries, not enough to claim polygon-overlay topology or PIP equivalence.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable


def _iter_features(path: Path) -> Iterable[dict]:
    with path.open("r", encoding="utf-8") as handle:
        first = handle.read(1)
        handle.seek(0)
        if first == "{":
            payload = json.load(handle)
            if payload.get("type") == "FeatureCollection":
                yield from payload.get("features", ())
                return
        for line in handle:
            line = line.strip()
            if line:
                yield json.loads(line)


def _rings_from_geometry(geometry: dict) -> Iterable[list[list[float]]]:
    kind = geometry.get("type")
    coords = geometry.get("coordinates", ())
    if kind == "Polygon":
        yield from coords
    elif kind == "MultiPolygon":
        for polygon in coords:
            yield from polygon


def _closed_ring(ring: list[list[float]]) -> list[list[float]]:
    if len(ring) < 3:
        return []
    first = ring[0]
    last = ring[-1]
    if first[0] == last[0] and first[1] == last[1]:
        return ring
    return ring + [first]


def convert(input_path: Path, output_path: Path, *, max_features: int | None) -> dict[str, int | str]:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    chain_id = 0
    point_id = 0
    feature_count = 0
    ring_count = 0
    point_count = 0
    skipped_non_polygon = 0
    skipped_short_ring = 0

    with output_path.open("w", encoding="utf-8") as out:
        for feature in _iter_features(input_path):
            geometry = feature.get("geometry") or {}
            if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
                skipped_non_polygon += 1
                continue
            feature_count += 1
            face_id = feature_count
            for raw_ring in _rings_from_geometry(geometry):
                ring = _closed_ring(raw_ring)
                if len(ring) < 4:
                    skipped_short_ring += 1
                    continue
                first_point_id = point_id
                last_point_id = point_id + len(ring) - 1
                out.write(f"{chain_id} {len(ring)} {first_point_id} {last_point_id} {face_id} 0\n")
                for x, y, *_rest in ring:
                    out.write(f"{float(x):.9f} {float(y):.9f}\n")
                chain_id += 1
                point_id += len(ring)
                ring_count += 1
                point_count += len(ring)
            if max_features is not None and feature_count >= max_features:
                break

    return {
        "input_path": str(input_path),
        "output_path": str(output_path),
        "feature_count": feature_count,
        "ring_chain_count": ring_count,
        "point_count": point_count,
        "skipped_non_polygon": skipped_non_polygon,
        "skipped_short_ring": skipped_short_ring,
        "claim_boundary": "LSI ring geometry only; no overlay topology or PIP claim",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--max-features", type=int, default=None)
    args = parser.parse_args()

    summary = convert(Path(args.input), Path(args.output), max_features=args.max_features)
    Path(args.summary).write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
