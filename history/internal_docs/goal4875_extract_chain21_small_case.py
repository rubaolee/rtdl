#!/usr/bin/env python3
"""Extract a focused chain21 small case for Goal4875 overlay debugging."""

from __future__ import annotations

import json
from pathlib import Path


LEFT = Path("/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb")
RIGHT = Path("/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb")
OUT_DIR = Path("/workspace/goal4875_section57_au_representative/small_chain21")

# Zero-based right-map segment ids observed in the first-diff chain21 window:
# xsect partners plus vertex point-location witnesses around edges 540..620.
RIGHT_SEGMENTS = {
    478507, 478508, 478636, 478637, 478638, 478640, 478643,
    925309, 925337, 925338, 925339, 925341, 925356, 925358, 925359,
    925360, 925361, 925362, 925363, 925364, 925367, 925368, 925371,
    925372, 925373, 925374, 925378,
    929266, 929268, 929274, 929275, 929276, 929283, 929286, 929287,
    929290, 929291, 929292,
    930886, 930900, 930901, 930904, 930906, 930909, 930911, 930912,
}


def iter_cdb_chains(path: Path):
    point_offset = 0
    edge_offset = 0
    with path.open("r", encoding="utf-8") as handle:
        chain_index = 0
        while True:
            header = handle.readline()
            if not header:
                break
            fields = header.split()
            npoints = int(fields[1])
            points = [handle.readline() for _ in range(npoints)]
            yield {
                "chain_index": chain_index,
                "point_offset": point_offset,
                "edge_offset": edge_offset,
                "edge_end": edge_offset + max(0, npoints - 1),
                "header": header,
                "points": points,
                "npoints": npoints,
            }
            point_offset += npoints
            edge_offset += max(0, npoints - 1)
            chain_index += 1


def write_chains(path: Path, chains) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for chain in chains:
            handle.write(chain["header"])
            for point in chain["points"]:
                handle.write(point)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    left_chains = [chain for chain in iter_cdb_chains(LEFT) if chain["chain_index"] == 21]
    if len(left_chains) != 1:
        raise RuntimeError(f"expected exactly one left chain21, got {len(left_chains)}")
    right_chains = []
    for chain in iter_cdb_chains(RIGHT):
        edge_ids = set(range(chain["edge_offset"], chain["edge_end"]))
        if edge_ids & RIGHT_SEGMENTS:
            right_chains.append(chain)
    left_out = OUT_DIR / "left_chain21.cdb"
    right_out = OUT_DIR / "right_relevant_chains.cdb"
    write_chains(left_out, left_chains)
    write_chains(right_out, right_chains)
    summary = {
        "schema": "rtdl.goal4875.chain21_small_case.v1",
        "left": {
            "path": str(left_out),
            "chains": len(left_chains),
            "source_chain_indices": [chain["chain_index"] for chain in left_chains],
            "source_edge_offsets": [chain["edge_offset"] for chain in left_chains],
            "points": sum(chain["npoints"] for chain in left_chains),
        },
        "right": {
            "path": str(right_out),
            "chains": len(right_chains),
            "source_chain_indices": [chain["chain_index"] for chain in right_chains],
            "source_edge_offsets": [chain["edge_offset"] for chain in right_chains],
            "points": sum(chain["npoints"] for chain in right_chains),
        },
        "selected_right_segment_count": len(RIGHT_SEGMENTS),
    }
    (OUT_DIR / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
