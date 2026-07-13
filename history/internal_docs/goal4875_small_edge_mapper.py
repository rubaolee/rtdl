#!/usr/bin/env python3
"""Map Goal4875 small-case edge ids back to original CDB segment ids.

The author debug dump reports edge ids in the extracted small CDB.  RTDL rows
report global segment ids from the original packed map in some probes.  This
utility makes that correspondence explicit so the next point-location fix can
be based on a named edge, not on a vague output-chain mismatch.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


SMALL_RIGHT = Path(
    "/workspace/goal4875_section57_au_representative/small_chain21/"
    "right_relevant_chains.cdb"
)
SMALL_SUMMARY = Path(
    "/workspace/goal4875_section57_au_representative/small_chain21/summary.json"
)
CHAIN21_PROBE = Path(
    "/workspace/goal4875_section57_au_representative/chain21_vertex_probe.json"
)
OUT = Path(
    "/workspace/goal4875_section57_au_representative/small_chain21/"
    "edge_id_map.json"
)


def iter_cdb_chain_headers(path: Path):
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
            left_face = int(fields[4])
            right_face = int(fields[5])
            for _ in range(npoints):
                handle.readline()
            yield {
                "small_chain_index": chain_index,
                "small_point_offset": point_offset,
                "small_edge_offset": edge_offset,
                "small_edge_end_exclusive": edge_offset + max(0, npoints - 1),
                "npoints": npoints,
                "left_face": left_face,
                "right_face": right_face,
            }
            point_offset += npoints
            edge_offset += max(0, npoints - 1)
            chain_index += 1


def map_edge(edge_id: int, chains: list[dict], source_edge_offsets: list[int]) -> dict:
    for idx, chain in enumerate(chains):
        start = int(chain["small_edge_offset"])
        end = int(chain["small_edge_end_exclusive"])
        if start <= edge_id < end:
            source_offset = int(source_edge_offsets[idx])
            return {
                **chain,
                "small_edge_id": edge_id,
                "edge_index_within_small_chain": edge_id - start,
                "source_edge_offset": source_offset,
                "source_global_edge_id": source_offset + (edge_id - start),
            }
    raise ValueError(f"edge id {edge_id} not present in {SMALL_RIGHT}")


def main(argv: list[str]) -> int:
    requested = [int(arg) for arg in argv[1:]]
    if not requested:
        requested = [178]
    summary = json.loads(SMALL_SUMMARY.read_text(encoding="utf-8"))
    source_offsets = [int(v) for v in summary["right"]["source_edge_offsets"]]
    chains = list(iter_cdb_chain_headers(SMALL_RIGHT))
    mapped = [map_edge(edge_id, chains, source_offsets) for edge_id in requested]

    probe_payload = json.loads(CHAIN21_PROBE.read_text(encoding="utf-8"))
    probe_points = {
        int(row["local_point_index"]): row
        for row in probe_payload.get("interesting_points", [])
    }
    payload = {
        "schema": "rtdl.goal4875.small_edge_mapper.v1",
        "small_right": str(SMALL_RIGHT),
        "source_edge_offsets": source_offsets,
        "small_chains": chains,
        "mapped_edges": mapped,
        "rtdl_chain21_probe_points": {
            str(key): probe_points[key]
            for key in sorted(probe_points)
            if 120 <= key <= 135
        },
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
