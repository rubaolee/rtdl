#!/usr/bin/env python3
"""Prepare UCI 3DRoad as an RT-DBSCAN AuthorOfficial input candidate.

This script intentionally produces a *same-source candidate*, not an exact paper
input. The RT-DBSCAN paper says 3DRoad is used as a 2D latitude/longitude
dataset, while the pinned AuthorOfficial sample reads a 3-column point stream.
The default route therefore writes longitude,latitude,0.0 rows.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def prepare_3droad(
    *,
    source: Path,
    output: Path,
    summary: Path,
    mode: str,
    limit: int | None,
) -> dict[str, object]:
    if mode not in {"paper_2d_zero_z", "source_3d_altitude"}:
        raise ValueError(f"unsupported mode: {mode}")
    if limit is not None and limit <= 0:
        raise ValueError("limit must be positive when provided")

    output.parent.mkdir(parents=True, exist_ok=True)
    summary.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    min_x = float("inf")
    max_x = float("-inf")
    min_y = float("inf")
    max_y = float("-inf")
    min_z = float("inf")
    max_z = float("-inf")

    with source.open("r", newline="", encoding="utf-8") as src, output.open(
        "w", newline="", encoding="utf-8"
    ) as out:
        reader = csv.reader(src)
        writer = csv.writer(out, lineterminator="\n")
        for row in reader:
            if limit is not None and count >= limit:
                break
            if len(row) != 4:
                raise ValueError(f"expected 4 columns at input row {count + 1}, got {len(row)}")
            _osm_id, lon_text, lat_text, alt_text = row
            lon = float(lon_text)
            lat = float(lat_text)
            alt = float(alt_text)
            if mode == "paper_2d_zero_z":
                x, y, z = lon, lat, 0.0
            else:
                x, y, z = lon, lat, alt
            writer.writerow((format(x, ".9g"), format(y, ".9g"), format(z, ".9g")))
            count += 1
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)
            min_z = min(min_z, z)
            max_z = max(max_z, z)

    payload: dict[str, object] = {
        "schema": "rtdl.paper_reproduction.rt_dbscan.uci_3droad_author_input_candidate.v1",
        "status": "same_source_candidate_not_exact_paper_input",
        "source": str(source),
        "source_sha256": _sha256(source),
        "output": str(output),
        "output_sha256": _sha256(output),
        "mode": mode,
        "limit": limit,
        "row_count": count,
        "bounds": {
            "x": [min_x, max_x],
            "y": [min_y, max_y],
            "z": [min_z, max_z],
        },
        "claim_boundary": [
            "UCI 3DRoad same-source candidate only.",
            "Not the author's packaged 3droad_full.csv.",
            "Not exact RT-DBSCAN paper input provenance.",
        ],
        "author_input_contract": "sample02-rtdbscan [inFile] [size] [eps] [minPts] [outFile]",
    }
    summary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument(
        "--mode",
        choices=("paper_2d_zero_z", "source_3d_altitude"),
        default="paper_2d_zero_z",
    )
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    payload = prepare_3droad(
        source=args.source,
        output=args.output,
        summary=args.summary,
        mode=args.mode,
        limit=args.limit,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
