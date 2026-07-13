#!/usr/bin/env python3
"""Goal4875 focused probe: point-location faces for map0 source chain 21.

This is a diagnostic script.  It does not import rtdsl.rayjoin_overlay; it uses
the same public point-location primitive as the public route.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

from rtdsl import prepare_planar_map_point_location_2d_optix
from rtdsl.embree_runtime import pack_rayjoin_cdb_scaled_points


PUBLIC_ROUTE = Path("/workspace/goal4875_public_primitives_au_overlay.py")
LEFT = Path("/workspace/goal4848_rep/current_osm_au/lakes_Australia_current_osm_Point.cdb")
RIGHT = Path("/workspace/goal4848_rep/current_osm_au/parks_Australia_current_osm_Point.cdb")
OUT = Path("/workspace/goal4875_section57_au_representative/chain21_vertex_probe.json")
SCALE_BOUNDS = (73.3778761, 167.9699741, -54.7704428, -9.2320578)


def load_public_route_module():
    spec = importlib.util.spec_from_file_location("goal4875_public_route", PUBLIC_ROUTE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {PUBLIC_ROUTE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_chain(path: Path, target_chain_index: int):
    point_offset = 0
    edge_offset = 0
    with path.open("r", encoding="utf-8") as handle:
        for chain_index in range(target_chain_index + 1):
            header = handle.readline()
            if not header:
                raise ValueError(f"missing chain {target_chain_index}")
            fields = header.split()
            npoints = int(fields[1])
            left_face = int(fields[4])
            right_face = int(fields[5])
            coords = []
            for _ in range(npoints):
                line = handle.readline()
                x, y = (float(value) for value in line.split()[:2])
                coords.append((x, y))
            if chain_index == target_chain_index:
                return {
                    "chain_index": chain_index,
                    "point_offset": point_offset,
                    "edge_offset": edge_offset,
                    "left_face": left_face,
                    "right_face": right_face,
                    "coords": coords,
                }
            point_offset += npoints
            edge_offset += max(0, npoints - 1)
    raise AssertionError("unreachable")


def main() -> None:
    mod = load_public_route_module()
    chain = read_chain(LEFT, 21)
    right = mod.load_dataset_arrays(RIGHT)
    rx_scale, ry_scale, deltax, deltay, *_ = mod._rayjoin_scaling_constants(SCALE_BOUNDS)
    coords = chain["coords"]
    x = np.array([p[0] for p in coords], dtype=np.float64)
    y = np.array([p[1] for p in coords], dtype=np.float64)
    sx = mod._scale_array(x, rx_scale, deltax)
    sy = mod._scale_array(y, ry_scale, deltay)
    ids = np.arange(1, len(coords) + 1, dtype=np.int64)
    packed = pack_rayjoin_cdb_scaled_points(ids=ids, x=x, y=y, sx=sx, sy=sy)
    rows = None
    with prepare_planar_map_point_location_2d_optix(
        right.cdb_segments,
        query_map_id=0,
        scale_bounds=SCALE_BOUNDS,
    ) as locator:
        rows = locator.run_raw(packed)
        columns = rows.to_numpy_columns(copy=True)
        rows.close()
    faces_by_id = {
        int(point_id): {
            "segment_id": int(segment_id),
            "face_id": int(face_id),
            "hit_t": float(hit_t),
        }
        for point_id, segment_id, face_id, hit_t in zip(
            columns["point_id"],
            columns["segment_id"],
            columns["face_id"],
            columns["hit_t"],
        )
    }
    interesting = []
    for local_point_index, (px, py) in enumerate(coords):
        global_point_index = int(chain["point_offset"]) + local_point_index
        before_edge = int(chain["edge_offset"]) + local_point_index - 1 if local_point_index > 0 else None
        after_edge = int(chain["edge_offset"]) + local_point_index if local_point_index < len(coords) - 1 else None
        if 540 <= (after_edge or -1) <= 620 or 540 <= (before_edge or -1) <= 620:
            info = faces_by_id.get(local_point_index + 1, {"segment_id": 0xFFFFFFFF, "face_id": 0, "hit_t": 0.0})
            interesting.append(
                {
                    "local_point_index": local_point_index,
                    "global_point_index": global_point_index,
                    "before_edge": before_edge,
                    "after_edge": after_edge,
                    "x": px,
                    "y": py,
                    "sx": int(sx[local_point_index]),
                    "sy": int(sy[local_point_index]),
                    **info,
                }
            )
    payload = {
        "schema": "rtdl.goal4875.chain21_vertex_probe.v1",
        "chain": {
            "chain_index": chain["chain_index"],
            "point_offset": chain["point_offset"],
            "edge_offset": chain["edge_offset"],
            "point_count": len(coords),
            "left_face": chain["left_face"],
            "right_face": chain["right_face"],
        },
        "interesting_points": interesting,
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
