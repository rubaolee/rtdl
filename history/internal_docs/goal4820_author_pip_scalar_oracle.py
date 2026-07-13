from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from rtdsl.datasets import CdbDataset
from rtdsl.datasets import CdbPoint
from rtdsl.datasets import load_cdb
import rtdsl.rayjoin_overlay as r


LEFT = Path("/workspace/RayJoin_fresh/test/dataset/br_county_clean_25_odyssey_final.txt")
RIGHT = Path("/workspace/RayJoin_fresh/test/dataset/br_soil_ascii_odyssey_final.txt")
OUT = Path("/workspace/rtdl_goal4820_artifacts/author_pip_scalar_oracle.json")

TARGET_RAW_INDEX = 250


@dataclass(frozen=True)
class RayjoinScale:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    rx: float
    ry: float
    rrx: float
    rry: float
    deltax: float
    deltay: float
    ddeltax: float
    ddeltay: float

    @classmethod
    def from_bounds(cls, bounds: tuple[float, float, float, float]) -> "RayjoinScale":
        min_x, max_x, min_y, max_y = bounds
        box_min_x = min_x - 1.0
        box_max_x = max_x + 1.0
        box_min_y = min_y - 1.0
        box_max_y = max_y + 1.0
        internal_max = (1 << 46) - 1
        internal_min = -(1 << 46)
        internal_range = float(internal_max - internal_min)
        rx = internal_range / (box_max_x - box_min_x)
        ry = internal_range / (box_max_y - box_min_y)
        rrx = 1.0 / rx
        rry = 1.0 / ry
        deltax = 0.5 * (float(internal_max + internal_min) - (box_max_x + box_min_x) * rx)
        deltay = 0.5 * (float(internal_max + internal_min) - (box_max_y + box_min_y) * ry)
        ddeltax = 0.5 * ((box_max_x + box_min_x) - float(internal_max + internal_min) * rrx)
        ddeltay = 0.5 * ((box_max_y + box_min_y) - float(internal_max + internal_min) * rry)
        return cls(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
            rx=rx,
            ry=ry,
            rrx=rrx,
            rry=rry,
            deltax=deltax,
            deltay=deltay,
            ddeltax=ddeltax,
            ddeltay=ddeltay,
        )

    def scale_x(self, x: float) -> int:
        return int(x * self.rx + self.deltax)

    def scale_y(self, y: float) -> int:
        return int(y * self.ry + self.deltay)

    def unscale_x(self, x: int) -> float:
        return float(x) * self.rrx + self.ddeltax

    def unscale_y(self, y: int) -> float:
        return float(y) * self.rry + self.ddeltay


def _flat_segments(dataset: CdbDataset) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    eid = 0
    point_offset = 0
    for chain_index, chain in enumerate(dataset.chains):
        for local_point_index, (start, end) in enumerate(zip(chain.points, chain.points[1:])):
            records.append(
                {
                    "eid": eid,
                    "segment_id": eid + 1,
                    "chain_index": chain_index,
                    "chain_id": chain.chain_id,
                    "local_point_index": local_point_index,
                    "point_index": point_offset + local_point_index,
                    "x0": float(start.x),
                    "y0": float(start.y),
                    "x1": float(end.x),
                    "y1": float(end.y),
                    "left_face_id": int(chain.left_face_id),
                    "right_face_id": int(chain.right_face_id),
                }
            )
            eid += 1
        point_offset += len(chain.points)
    return records


def _author_scalar_point_location(
    point: CdbPoint,
    base: CdbDataset,
    scale: RayjoinScale,
    *,
    query_map_id: int,
    tie_policy: str,
) -> dict[str, object]:
    sx = scale.scale_x(float(point.x))
    sy = scale.scale_y(float(point.y))
    best_y = None
    best = None
    skipped_equal_ties = 0
    accepted_equal_ties = 0

    for segment in _flat_segments(base):
        sx0 = scale.scale_x(float(segment["x0"]))
        sy0 = scale.scale_y(float(segment["y0"]))
        sx1 = scale.scale_x(float(segment["x1"]))
        sy1 = scale.scale_y(float(segment["y1"]))
        x_min = min(sx0, sx1)
        x_max = max(sx0, sx1)
        excluded_x = x_min if query_map_id == 0 else x_max
        if sx < x_min or sx > x_max or sx == excluded_x:
            continue

        a = sy0 - sy1
        b = sx1 - sx0
        c = -(sx0 * a) - (sy0 * b)
        if b < 0:
            a = -a
            b = -b
            c = -c
        if b == 0:
            continue

        xsect_y = float((-(a * sx) - c) / b)
        diff_y = float(sy) - xsect_y
        if diff_y == 0.0:
            diff_y = -float(a) if query_map_id == 0 else float(a)
        if diff_y == 0.0:
            diff_y = -float(b) if query_map_id == 0 else float(b)
        if diff_y > 0.0:
            continue

        slope = float(a) / float(b)
        if best_y is not None:
            if xsect_y > best_y:
                continue
            if xsect_y == best_y:
                best_slope = float(best["slope"])
                if tie_policy == "author_reply":
                    better = slope > best_slope if query_map_id == 0 else slope < best_slope
                    if not better:
                        skipped_equal_ties += 1
                        continue
                elif tie_policy == "author_source_literal":
                    current_slope_gt = slope > best_slope
                    if (query_map_id != 0 and not current_slope_gt) or (
                        current_slope_gt and query_map_id == 0
                    ):
                        skipped_equal_ties += 1
                        continue
                else:
                    raise ValueError(f"unknown tie policy: {tie_policy}")
                accepted_equal_ties += 1

        face_id = int(segment["right_face_id"]) if sx0 < sx1 else int(segment["left_face_id"])
        best_y = xsect_y
        best = {
            **segment,
            "scaled": {
                "point": [sx, sy],
                "sx0": sx0,
                "sy0": sy0,
                "sx1": sx1,
                "sy1": sy1,
                "xsect_y": xsect_y,
                "slope": slope,
            },
            "face_id": face_id,
            "slope": slope,
            "xsect_y": xsect_y,
        }

    return {
        "point": [float(point.x), float(point.y)],
        "query_map_id": query_map_id,
        "tie_policy": tie_policy,
        "face_id": 0 if best is None else int(best["face_id"]),
        "segment_id": None if best is None else int(best["segment_id"]),
        "edge_id": None if best is None else int(best["eid"]),
        "best": best,
        "accepted_equal_ties": accepted_equal_ties,
        "skipped_equal_ties": skipped_equal_ties,
    }


def _compute_overlay_state(left: CdbDataset, right: CdbDataset):
    left_inputs = r.load_cdb_overlay_packed_inputs(LEFT)
    right_inputs = r.load_cdb_overlay_packed_inputs(RIGHT)

    rows, _ = r._run_lsi_rows(
        "optix",
        left_inputs.segments,
        right_inputs.segments,
        left,
        right,
        left_coords=left_inputs.segment_coords,
        right_coords=right_inputs.segment_coords,
    )
    xsects = r._intersections_from_lsi_rows(rows)
    xsects_sorted = (
        r._sort_xsects_for_map(xsects, left_inputs.edge_starts, 0),
        r._sort_xsects_for_map(xsects, right_inputs.edge_starts, 1),
    )
    scale_bounds = r._shared_rayjoin_bounds(left_inputs, right_inputs)
    with r._prepared_point_location_pair(
        "optix",
        right_inputs.cdb_segments,
        left_inputs.cdb_segments,
        scale_bounds,
        point_counts=(int(left_inputs.point_count), int(right_inputs.point_count)),
    ) as (map0_in_map1, map1_in_map0, _):
        vertex0_faces, _ = map0_in_map1.faces(left_inputs.points, int(left_inputs.point_count))
        vertex1_faces, _ = map1_in_map0.faces(right_inputs.points, int(right_inputs.point_count))
        for map_index, runner in ((0, map0_in_map1), (1, map1_in_map0)):
            midpoints, owners = r._midpoints_for_sorted_xsects(xsects_sorted[map_index], map_index)
            if midpoints:
                midpoint_points = r._packed_points_from_xy(midpoints)
                midpoint_faces, _ = runner.faces(midpoint_points, len(midpoints))
                r._assign_midpoint_faces(owners, midpoint_faces, map_index=map_index)
    return left_inputs, right_inputs, xsects_sorted, scale_bounds, (vertex0_faces, vertex1_faces)


def _raw_chains_with_sources(
    datasets: tuple[CdbDataset, CdbDataset],
    xsect_edges_sorted,
    point_in_polygon,
    *,
    start: int,
    end: int,
) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    raw_index = 0
    for map_index, dataset in enumerate(datasets):
        edge_attr = "eid0" if map_index == 0 else "eid1"
        grouped: dict[int, list[object]] = {}
        for xsect in xsect_edges_sorted[map_index]:
            grouped.setdefault(int(getattr(xsect, edge_attr)), []).append(xsect)

        point_offset = 0
        edge_id = 0
        for chain in dataset.chains:
            output_chain = {
                "points": [],
                "events": [],
                "left": int(chain.left_face_id),
                "right": int(chain.right_face_id),
                "other": 0,
                "other_source": None,
                "map": map_index,
                "source_chain": int(chain.chain_id),
                "edge_ids": [],
            }

            def flush(reason: str) -> None:
                nonlocal raw_index
                if not output_chain["points"]:
                    return
                keep = (
                    int(output_chain["left"]) * int(output_chain["other"]) != 0
                    or int(output_chain["right"]) * int(output_chain["other"]) != 0
                )
                if keep:
                    raw_index += 1
                    if start <= raw_index <= end:
                        out.append(
                            {
                                "raw_index": raw_index,
                                "reason": reason,
                                "map": output_chain["map"],
                                "source_chain": output_chain["source_chain"],
                                "left": output_chain["left"],
                                "right": output_chain["right"],
                                "other": output_chain["other"],
                                "other_source": output_chain["other_source"],
                                "points": list(output_chain["points"]),
                                "events": list(output_chain["events"]),
                                "edge_ids": list(output_chain["edge_ids"]),
                            }
                        )
                output_chain["points"].clear()
                output_chain["events"].clear()
                output_chain["edge_ids"].clear()

            for local_point_index, point in enumerate(chain.points):
                point_index = point_offset + local_point_index
                output_chain["other"] = int(point_in_polygon[map_index][point_index])
                output_chain["other_source"] = {
                    "kind": "vertex",
                    "map": map_index,
                    "chain_id": int(chain.chain_id),
                    "local_point_index": local_point_index,
                    "point_index": point_index,
                    "point": [float(point.x), float(point.y)],
                }
                output_chain["points"].append([float(point.x), float(point.y)])
                output_chain["events"].append(
                    {
                        "kind": "vertex",
                        "point_index": point_index,
                        "local_point_index": local_point_index,
                        "point": [float(point.x), float(point.y)],
                    }
                )
                if local_point_index == len(chain.points) - 1:
                    continue
                xsects = grouped.get(edge_id)
                if xsects:
                    output_chain["points"].append([float(xsects[0].x), float(xsects[0].y)])
                    output_chain["events"].append(
                        {"kind": "xsect", "edge_id": edge_id, "x": float(xsects[0].x), "y": float(xsects[0].y)}
                    )
                    output_chain["edge_ids"].append(edge_id)
                    for xsect, next_xsect in zip(xsects, xsects[1:]):
                        flush("between_xsects")
                        output_chain["other"] = r._midpoint_face_for_map(xsect, map_index)
                        output_chain["other_source"] = {
                            "kind": "midpoint",
                            "map": map_index,
                            "edge_id": edge_id,
                            "owner_left_eid": int(xsect.eid0),
                            "owner_right_eid": int(xsect.eid1),
                            "midpoint_face": r._midpoint_face_for_map(xsect, map_index),
                        }
                        output_chain["points"].append([float(xsect.x), float(xsect.y)])
                        output_chain["points"].append([float(next_xsect.x), float(next_xsect.y)])
                        output_chain["events"].append(
                            {"kind": "xsect", "edge_id": edge_id, "x": float(xsect.x), "y": float(xsect.y)}
                        )
                        output_chain["events"].append(
                            {"kind": "xsect", "edge_id": edge_id, "x": float(next_xsect.x), "y": float(next_xsect.y)}
                        )
                        output_chain["edge_ids"].append(edge_id)
                    flush("after_xsects")
                    output_chain["points"].append([float(xsects[-1].x), float(xsects[-1].y)])
                    output_chain["events"].append(
                        {"kind": "xsect", "edge_id": edge_id, "x": float(xsects[-1].x), "y": float(xsects[-1].y)}
                    )
                    output_chain["edge_ids"].append(edge_id)
                edge_id += 1
            flush("chain_end")
            point_offset += len(chain.points)
    return out


def _native_single_point_face(base_segments, scale_bounds, *, query_map_id: int, point_xy: tuple[float, float]):
    packed = r._packed_points_from_xy([point_xy])
    with r._PreparedPointLocationRunner(
        "optix",
        base_segments,
        query_map_id=query_map_id,
        scale_bounds=scale_bounds,
    ) as runner:
        rows = None
        try:
            rows = runner.prepared.run_raw(packed)
            columns = rows.to_numpy_columns(copy=True)
        finally:
            if rows is not None:
                rows.close()
    return {
        "face_id": int(columns["face_id"][0]) if len(columns["face_id"]) else 0,
        "segment_id": int(columns["segment_id"][0]) if len(columns["segment_id"]) else None,
        "hit_t": float(columns["hit_t"][0]) if len(columns["hit_t"]) else None,
    }


def main() -> None:
    left = load_cdb(LEFT)
    right = load_cdb(RIGHT)
    left_inputs, right_inputs, xsects_sorted, scale_bounds, faces = _compute_overlay_state(left, right)
    scale = RayjoinScale.from_bounds(scale_bounds)
    window = _raw_chains_with_sources((left, right), xsects_sorted, faces, start=245, end=260)
    target = next((row for row in window if int(row["raw_index"]) == TARGET_RAW_INDEX), None)
    if target is None:
        raise RuntimeError(f"raw chain {TARGET_RAW_INDEX} not found in diagnostic window")
    other_source = target["other_source"]
    if not isinstance(other_source, dict) or other_source.get("kind") not in {"vertex", "midpoint"}:
        raise RuntimeError(f"target raw chain {TARGET_RAW_INDEX} has unsupported source: {other_source}")
    map_index = int(other_source["map"])
    base_dataset = right if map_index == 0 else left
    base_segments = right_inputs.cdb_segments if map_index == 0 else left_inputs.cdb_segments
    if other_source["kind"] == "vertex":
        point_index = int(other_source["point_index"])
        source_dataset = left if map_index == 0 else right
        point = [point for chain in source_dataset.chains for point in chain.points][point_index]
        point_kind = "vertex"
    else:
        points = target["points"]
        if len(points) < 2:
            raise RuntimeError(f"midpoint-sourced target does not contain two endpoints: {target}")
        point = CdbPoint(
            x=(float(points[0][0]) + float(points[1][0])) * 0.5,
            y=(float(points[0][1]) + float(points[1][1])) * 0.5,
        )
        point_kind = "midpoint"
    query_map_id = map_index
    native = _native_single_point_face(
        base_segments,
        scale_bounds,
        query_map_id=query_map_id,
        point_xy=(float(point.x), float(point.y)),
    )
    payload = {
        "target_raw_index": TARGET_RAW_INDEX,
        "target_raw_chain": target,
        "query_map_id": query_map_id,
        "point_kind": point_kind,
        "point": [float(point.x), float(point.y)],
        "native_single_point": native,
        "scalar_author_reply": _author_scalar_point_location(
            point,
            base_dataset,
            scale,
            query_map_id=query_map_id,
            tie_policy="author_reply",
        ),
        "scalar_author_source_literal": _author_scalar_point_location(
            point,
            base_dataset,
            scale,
            query_map_id=query_map_id,
            tie_policy="author_source_literal",
        ),
        "scale_bounds": list(scale_bounds),
        "diagnostic_window": window,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "target_other": int(target["other"]),
                "native_face": payload["native_single_point"]["face_id"],
                "reply_face": payload["scalar_author_reply"]["face_id"],
                "source_literal_face": payload["scalar_author_source_literal"]["face_id"],
                "out": str(OUT),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
