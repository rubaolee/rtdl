from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from goal3474_shape_pair_exact_overlay_area_shapely_oracle import (  # noqa: E402
    _build_oracle_polygon,
    _build_oracle_polygons,
    _claim_boundary,
    _import_shapely,
)
from examples.v2_0.research_benchmarks.spatial_rayjoin.rtdl_rayjoin_v2_spatial_join_app import (  # noqa: E402
    pack_rayjoin_optix_shape_pair_active_count_left_shapes,
    prepare_rayjoin_optix_shape_pair_active_count,
)
import rtdsl as rt  # noqa: E402
from rtdsl.datasets import chains_to_polygons  # noqa: E402
from rtdsl.datasets import load_cdb  # noqa: E402
from rtdsl.simple_polygon_overlay_area_reference import Triangle2  # noqa: E402
from rtdsl.simple_polygon_overlay_area_reference import triangulate_simple_polygon_ear_clip  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _exterior_vertices(polygon: Any) -> tuple[tuple[float, float], ...]:
    coords = tuple((float(x), float(y)) for x, y in polygon.exterior.coords)
    if len(coords) >= 2 and coords[0] == coords[-1]:
        return coords[:-1]
    return coords


def _component_payload_parts_for_prepared_geometry(
    geometry: Any,
) -> tuple[
    str,
    tuple[tuple[tuple[float, float], ...], ...],
    tuple[tuple[Triangle2, ...], ...],
    tuple[tuple[float, float, float, float], ...],
]:
    geom_type = str(getattr(geometry, "geom_type", "unknown"))
    if getattr(geometry, "is_empty", False):
        return "unsupported_empty", (), (), ()
    if geom_type == "Polygon":
        parts = (geometry,)
    elif geom_type == "MultiPolygon":
        parts = tuple(geometry.geoms)
    else:
        return f"unsupported_geometry_type_{geom_type}", (), (), ()

    component_vertices: list[tuple[tuple[float, float], ...]] = []
    component_triangles: list[tuple[Triangle2, ...]] = []
    component_bounds: list[tuple[float, float, float, float]] = []
    for part in parts:
        if len(part.interiors) != 0:
            return "unsupported_holes", tuple(component_vertices), tuple(component_triangles), tuple(component_bounds)
        vertices = _exterior_vertices(part)
        try:
            triangles = triangulate_simple_polygon_ear_clip(vertices)
        except Exception:
            return "unsupported_triangulation_failed", tuple(component_vertices), tuple(component_triangles), tuple(component_bounds)
        component_vertices.append(vertices)
        component_triangles.append(triangles)
        xs = [float(point[0]) for point in vertices]
        ys = [float(point[1]) for point in vertices]
        component_bounds.append((min(xs), min(ys), max(xs), max(ys)))
    return "prepared_simple_components", tuple(component_vertices), tuple(component_triangles), tuple(component_bounds)


def _add_count(counts: dict[str, int], key: str, value: int = 1) -> None:
    counts[key] = counts.get(key, 0) + int(value)


def _prepare_payload_from_geometries(
    geometries: tuple[Any, ...],
) -> tuple[rt.PreparedSimplePolygonComponentPayload, dict[int, tuple[int, ...]], dict[str, int]]:
    return _prepare_payload_from_geometry_map(dict(enumerate(geometries)))


def _prepare_payload_from_geometry_map(
    geometries: dict[int, Any],
) -> tuple[rt.PreparedSimplePolygonComponentPayload, dict[int, tuple[int, ...]], dict[str, int]]:
    component_triangles: list[tuple[Triangle2, ...]] = []
    component_vertex_counts: list[int] = []
    component_bounds: list[tuple[float, float, float, float]] = []
    source_shape_ids: list[int] = []
    shape_to_components: dict[int, tuple[int, ...]] = {}
    status_counts: dict[str, int] = {}
    for shape_ordinal, geometry in sorted(geometries.items()):
        status, component_vertices, triangles, bounds = _component_payload_parts_for_prepared_geometry(geometry)
        _add_count(status_counts, status)
        component_ordinals: list[int] = []
        if status == "prepared_simple_components":
            for vertices, component_triangle_rows, component_bound in zip(component_vertices, triangles, bounds):
                component_ordinals.append(len(component_triangles))
                component_triangles.append(component_triangle_rows)
                component_vertex_counts.append(len(vertices))
                component_bounds.append(component_bound)
                source_shape_ids.append(shape_ordinal)
        shape_to_components[shape_ordinal] = tuple(component_ordinals)
    payload = rt.prepare_simple_polygon_component_payload_from_triangles(
        component_triangles,
        source_shape_ids=source_shape_ids,
        component_vertex_counts=component_vertex_counts,
        component_bounds=component_bounds,
    )
    return payload, shape_to_components, status_counts


def _geometry_payload_parts_worker(task: tuple[int, Any]) -> dict[str, Any]:
    shape_ordinal, record = task
    ShapelyPolygon, make_valid, _ = _import_shapely()
    geometry, geometry_status = _build_oracle_polygon(record, ShapelyPolygon, make_valid)
    payload_status, component_vertices, triangles, bounds = _component_payload_parts_for_prepared_geometry(geometry)
    try:
        from shapely import wkb as shapely_wkb  # type: ignore
    except Exception:  # pragma: no cover - Shapely 1.x compatibility path
        import shapely.wkb as shapely_wkb  # type: ignore

    return {
        "shape_ordinal": int(shape_ordinal),
        "geometry_wkb": shapely_wkb.dumps(geometry),
        "geometry_status": geometry_status,
        "payload_status": payload_status,
        "component_vertex_counts": tuple(len(vertices) for vertices in component_vertices),
        "component_triangles": triangles,
        "component_bounds": bounds,
    }


def _prepare_geometry_payload_bundle_parallel(
    records: tuple[Any, ...],
    shape_ordinals: set[int],
    *,
    workers: int,
) -> tuple[Any, dict[int, tuple[int, ...]], dict[str, int], dict[int, Any], dict[str, int]]:
    if workers <= 1:
        raise ValueError("parallel payload preparation requires workers > 1")
    tasks = [(int(shape_ordinal), records[int(shape_ordinal)]) for shape_ordinal in sorted(shape_ordinals)]
    try:
        from shapely import wkb as shapely_wkb  # type: ignore
    except Exception:  # pragma: no cover - Shapely 1.x compatibility path
        import shapely.wkb as shapely_wkb  # type: ignore

    geometry_map: dict[int, Any] = {}
    geometry_status_counts: dict[str, int] = {}
    prepared_status_counts: dict[str, int] = {}
    component_triangles: list[tuple[Triangle2, ...]] = []
    component_vertex_counts: list[int] = []
    component_bounds: list[tuple[float, float, float, float]] = []
    source_shape_ids: list[int] = []
    shape_to_components: dict[int, tuple[int, ...]] = {}

    with ProcessPoolExecutor(max_workers=int(workers)) as executor:
        results = executor.map(_geometry_payload_parts_worker, tasks)
        for result in sorted(results, key=lambda item: int(item["shape_ordinal"])):
            shape_ordinal = int(result["shape_ordinal"])
            geometry_map[shape_ordinal] = shapely_wkb.loads(result["geometry_wkb"])
            _add_count(geometry_status_counts, str(result["geometry_status"]))
            payload_status = str(result["payload_status"])
            _add_count(prepared_status_counts, payload_status)
            component_ordinals: list[int] = []
            if payload_status == "prepared_simple_components":
                for triangles, vertex_count, bounds in zip(
                    result["component_triangles"],
                    result["component_vertex_counts"],
                    result["component_bounds"],
                ):
                    component_ordinals.append(len(component_triangles))
                    component_triangles.append(tuple(triangles))
                    component_vertex_counts.append(int(vertex_count))
                    component_bounds.append(tuple(float(value) for value in bounds))
                    source_shape_ids.append(shape_ordinal)
            shape_to_components[shape_ordinal] = tuple(component_ordinals)

    payload = rt.prepare_simple_polygon_component_payload_from_triangles(
        component_triangles,
        source_shape_ids=source_shape_ids,
        component_vertex_counts=component_vertex_counts,
        component_bounds=component_bounds,
    )
    return payload, shape_to_components, prepared_status_counts, geometry_map, geometry_status_counts


def _shape_components_to_jsonable(
    shape_to_components: dict[int, tuple[int, ...]],
) -> dict[str, list[int]]:
    return {
        str(int(shape_ordinal)): [int(component) for component in components]
        for shape_ordinal, components in sorted(shape_to_components.items())
    }


def _shape_components_from_jsonable(data: dict[str, Any]) -> dict[int, tuple[int, ...]]:
    return {
        int(shape_ordinal): tuple(int(component) for component in components)
        for shape_ordinal, components in data.items()
    }


def _json_cache_schema() -> str:
    return "rtdl.goal3507.overlay_area_prepared_payload_cache.v1"


def _binary_cache_schema() -> str:
    return "rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1"


def _cache_path(cache_dir: Path, side: str) -> Path:
    return cache_dir / f"{side}_prepared_simple_polygon_component_payload.json"


def _binary_cache_manifest_path(cache_dir: Path, side: str) -> Path:
    return cache_dir / f"{side}_prepared_simple_polygon_component_payload_binary_manifest.json"


def _binary_payload_npz_path(cache_dir: Path, side: str) -> Path:
    return cache_dir / f"{side}_prepared_simple_polygon_component_payload_columns.npz"


def _binary_shape_components_npz_path(cache_dir: Path, side: str) -> Path:
    return cache_dir / f"{side}_shape_component_columns.npz"


def _binary_geometry_wkb_npz_path(cache_dir: Path, side: str) -> Path:
    return cache_dir / f"{side}_geometry_wkb_columns.npz"


def _write_shape_components_npz(path: Path, shape_to_components: dict[int, tuple[int, ...]]) -> None:
    import numpy as np  # type: ignore

    shape_ordinals: list[int] = []
    offsets: list[int] = [0]
    component_ordinals: list[int] = []
    for shape_ordinal, components in sorted(shape_to_components.items()):
        shape_ordinals.append(int(shape_ordinal))
        component_ordinals.extend(int(component) for component in components)
        offsets.append(len(component_ordinals))
    np.savez(
        path,
        schema=np.asarray([_binary_cache_schema()]),
        shape_ordinals=np.asarray(shape_ordinals, dtype=np.int64),
        offsets=np.asarray(offsets, dtype=np.int64),
        component_ordinals=np.asarray(component_ordinals, dtype=np.int64),
    )


def _read_shape_components_npz(path: Path) -> dict[int, tuple[int, ...]]:
    import numpy as np  # type: ignore

    with np.load(path, allow_pickle=False) as data:
        schema = str(np.asarray(data["schema"]).reshape(-1)[0])
        if schema != _binary_cache_schema():
            raise ValueError("unexpected shape-component cache schema")
        shape_ordinals = np.asarray(data["shape_ordinals"], dtype=np.int64)
        offsets = np.asarray(data["offsets"], dtype=np.int64)
        component_ordinals = np.asarray(data["component_ordinals"], dtype=np.int64)
        return {
            int(shape_ordinal): tuple(
                int(component) for component in component_ordinals[int(offsets[index]) : int(offsets[index + 1])]
            )
            for index, shape_ordinal in enumerate(shape_ordinals)
        }


def _write_geometry_wkb_npz(path: Path, geometry_map: dict[int, Any]) -> None:
    import numpy as np  # type: ignore

    shape_ordinals: list[int] = []
    offsets: list[int] = [0]
    chunks: list[bytes] = []
    for shape_ordinal, geometry in sorted(geometry_map.items()):
        blob = bytes(geometry.wkb)
        shape_ordinals.append(int(shape_ordinal))
        chunks.append(blob)
        offsets.append(offsets[-1] + len(blob))
    combined = b"".join(chunks)
    np.savez(
        path,
        schema=np.asarray([_binary_cache_schema()]),
        shape_ordinals=np.asarray(shape_ordinals, dtype=np.int64),
        offsets=np.asarray(offsets, dtype=np.int64),
        blob=np.frombuffer(combined, dtype=np.uint8),
    )


def _read_geometry_wkb_npz(path: Path) -> dict[int, Any]:
    import numpy as np  # type: ignore

    try:
        from shapely import wkb as shapely_wkb  # type: ignore
    except Exception:  # pragma: no cover - Shapely 1.x compatibility path
        import shapely.wkb as shapely_wkb  # type: ignore

    with np.load(path, allow_pickle=False) as data:
        schema = str(np.asarray(data["schema"]).reshape(-1)[0])
        if schema != _binary_cache_schema():
            raise ValueError("unexpected geometry WKB cache schema")
        shape_ordinals = np.asarray(data["shape_ordinals"], dtype=np.int64)
        offsets = np.asarray(data["offsets"], dtype=np.int64)
        blob = np.asarray(data["blob"], dtype=np.uint8).tobytes()
        return {
            int(shape_ordinal): shapely_wkb.loads(blob[int(offsets[index]) : int(offsets[index + 1])])
            for index, shape_ordinal in enumerate(shape_ordinals)
        }


def _write_prepared_payload_cache(
    cache_dir: Path,
    side: str,
    *,
    source_cdb: Path,
    selected_shape_ordinals: set[int],
    payload: rt.PreparedSimplePolygonComponentPayload,
    shape_to_components: dict[int, tuple[int, ...]],
    prepared_status_counts: dict[str, int],
    geometry_map: dict[int, Any],
    geometry_status_counts: dict[str, int],
    cache_format: str = "json",
) -> Path:
    cache_dir.mkdir(parents=True, exist_ok=True)
    if cache_format == "binary":
        import numpy as np  # type: ignore

        payload_path = _binary_payload_npz_path(cache_dir, side)
        shape_components_path = _binary_shape_components_npz_path(cache_dir, side)
        geometry_wkb_path = _binary_geometry_wkb_npz_path(cache_dir, side)
        np.savez(payload_path, **rt.prepared_simple_polygon_component_payload_to_numpy_columns(payload))
        _write_shape_components_npz(shape_components_path, shape_to_components)
        _write_geometry_wkb_npz(geometry_wkb_path, geometry_map)
        manifest_data = {
            "schema": _binary_cache_schema(),
            "side": side,
            "source_cdb": str(source_cdb),
            "selected_shape_ordinals": [int(value) for value in sorted(selected_shape_ordinals)],
            "payload_columns": payload_path.name,
            "shape_component_columns": shape_components_path.name,
            "geometry_wkb_columns": geometry_wkb_path.name,
            "prepared_status_counts": {str(key): int(value) for key, value in sorted(prepared_status_counts.items())},
            "geometry_status_counts": {str(key): int(value) for key, value in sorted(geometry_status_counts.items())},
            "claim_boundary": _claim_boundary(),
        }
        path = _binary_cache_manifest_path(cache_dir, side)
        path.write_text(json.dumps(manifest_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path
    if cache_format != "json":
        raise ValueError(f"unsupported prepared payload cache format: {cache_format}")
    payload_data = {
        "schema": _json_cache_schema(),
        "side": side,
        "source_cdb": str(source_cdb),
        "selected_shape_ordinals": [int(value) for value in sorted(selected_shape_ordinals)],
        "payload": rt.prepared_simple_polygon_component_payload_to_dict(payload),
        "shape_to_components": _shape_components_to_jsonable(shape_to_components),
        "prepared_status_counts": {str(key): int(value) for key, value in sorted(prepared_status_counts.items())},
        "geometry_status_counts": {str(key): int(value) for key, value in sorted(geometry_status_counts.items())},
        "geometry_wkb_hex": {
            str(int(shape_ordinal)): bytes(geometry.wkb).hex()
            for shape_ordinal, geometry in sorted(geometry_map.items())
        },
        "claim_boundary": _claim_boundary(),
    }
    path = _cache_path(cache_dir, side)
    path.write_text(json.dumps(payload_data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def _read_prepared_payload_cache(
    cache_dir: Path,
    side: str,
    *,
    source_cdb: Path,
    selected_shape_ordinals: set[int],
    cache_format: str = "json",
) -> tuple[rt.PreparedSimplePolygonComponentPayload, dict[int, tuple[int, ...]], dict[str, int], dict[int, Any], dict[str, int], dict[str, Any]]:
    if cache_format == "binary":
        path = _binary_cache_manifest_path(cache_dir, side)
        if not path.exists():
            raise FileNotFoundError(f"missing prepared payload binary cache manifest for {side}: {path}")
        data = json.loads(path.read_text(encoding="utf-8"))
        if data.get("schema") != _binary_cache_schema():
            raise ValueError(f"unexpected prepared payload binary cache schema for {side}")
        if str(data.get("source_cdb")) != str(source_cdb):
            raise ValueError(f"prepared payload binary cache source mismatch for {side}")
        cached_shape_ordinals = {int(value) for value in data.get("selected_shape_ordinals", ())}
        if cached_shape_ordinals != {int(value) for value in selected_shape_ordinals}:
            raise ValueError(f"prepared payload binary cache shape ordinal set mismatch for {side}")
        import numpy as np  # type: ignore

        payload_path = cache_dir / str(data["payload_columns"])
        with np.load(payload_path, allow_pickle=False) as payload_columns:
            payload = rt.prepared_simple_polygon_component_payload_from_numpy_columns(payload_columns)
        shape_components_path = cache_dir / str(data["shape_component_columns"])
        geometry_wkb_path = cache_dir / str(data["geometry_wkb_columns"])
        geometry_map = _read_geometry_wkb_npz(geometry_wkb_path)
        return (
            payload,
            _read_shape_components_npz(shape_components_path),
            {str(key): int(value) for key, value in data["prepared_status_counts"].items()},
            geometry_map,
            {str(key): int(value) for key, value in data["geometry_status_counts"].items()},
            {
                "cache_path": str(path),
                "schema": data.get("schema"),
                "format": cache_format,
                "side": side,
                "selected_shape_count": len(cached_shape_ordinals),
                "payload_triangle_count": payload.triangle_count,
                "component_count": payload.component_count,
                "payload_columns": str(payload_path),
                "shape_component_columns": str(shape_components_path),
                "geometry_wkb_columns": str(geometry_wkb_path),
            },
        )
    if cache_format != "json":
        raise ValueError(f"unsupported prepared payload cache format: {cache_format}")
    path = _cache_path(cache_dir, side)
    if not path.exists():
        raise FileNotFoundError(f"missing prepared payload cache for {side}: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if data.get("schema") != _json_cache_schema():
        raise ValueError(f"unexpected prepared payload cache schema for {side}")
    if str(data.get("source_cdb")) != str(source_cdb):
        raise ValueError(f"prepared payload cache source mismatch for {side}")
    cached_shape_ordinals = {int(value) for value in data.get("selected_shape_ordinals", ())}
    if cached_shape_ordinals != {int(value) for value in selected_shape_ordinals}:
        raise ValueError(f"prepared payload cache shape ordinal set mismatch for {side}")
    try:
        from shapely import wkb as shapely_wkb  # type: ignore
    except Exception:  # pragma: no cover - Shapely 1.x compatibility path
        import shapely.wkb as shapely_wkb  # type: ignore

    geometry_map = {
        int(shape_ordinal): shapely_wkb.loads(bytes.fromhex(wkb_hex))
        for shape_ordinal, wkb_hex in data.get("geometry_wkb_hex", {}).items()
    }
    payload = rt.prepared_simple_polygon_component_payload_from_dict(data["payload"])
    return (
        payload,
        _shape_components_from_jsonable(data["shape_to_components"]),
        {str(key): int(value) for key, value in data["prepared_status_counts"].items()},
        geometry_map,
        {str(key): int(value) for key, value in data["geometry_status_counts"].items()},
        {
            "cache_path": str(path),
            "schema": data.get("schema"),
            "side": side,
            "selected_shape_count": len(cached_shape_ordinals),
            "payload_triangle_count": payload.triangle_count,
            "component_count": payload.component_count,
        },
    )


def _shape_component_table(
    shape_to_components: dict[int, tuple[int, ...]],
    shape_count: int,
) -> tuple[list[int], list[int]]:
    starts = [0] * int(shape_count)
    counts = [0] * int(shape_count)
    for shape_ordinal, components in shape_to_components.items():
        if not components:
            continue
        starts[int(shape_ordinal)] = int(components[0])
        counts[int(shape_ordinal)] = len(components)
    return starts, counts


def _build_oracle_geometry_map(
    records: tuple[Any, ...],
    shape_ordinals: set[int],
    ShapelyPolygon: Any,
    make_valid: Any,
) -> tuple[dict[int, Any], dict[str, int]]:
    geometries: dict[int, Any] = {}
    status_counts: dict[str, int] = {}
    for shape_ordinal in sorted(shape_ordinals):
        geometry, status = _build_oracle_polygon(records[shape_ordinal], ShapelyPolygon, make_valid)
        geometries[shape_ordinal] = geometry
        _add_count(status_counts, status)
    return geometries, status_counts


def _percentile(values: list[float], q: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, round((len(ordered) - 1) * q)))
    return float(ordered[index])


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore

    if args.device_active_shape_ordinals and not args.active_shapes_only:
        raise ValueError("--device-active-shape-ordinals requires --active-shapes-only")

    ShapelyPolygon, make_valid, shapely_version = _import_shapely()
    print("[goal3492] load CDB", flush=True)
    left_shapes = tuple(chains_to_polygons(load_cdb(args.left_cdb)))
    right_shapes = tuple(chains_to_polygons(load_cdb(args.right_cdb)))

    print("[goal3492] discover active relation ordinals with RTDL/OptiX", flush=True)
    discovery_start = time.perf_counter()
    active_shape_ordinals_sec = 0.0
    bounds_positive_filter_sec = 0.0
    relation_ordinal_download_sec = 0.0
    active_relation_device_columns_sec = 0.0
    relation_column_warmup_secs: list[float] = []
    active_shape_ordinal_metadata: dict[str, object] | None = None
    bounds_positive_filter_metadata: dict[str, object] | None = None
    bounds_positive_relation_rows = None
    bounds_positive_mask = None
    bounds_positive_relation_rows_device = None
    left_ordinals_device = None
    right_ordinals_device = None
    candidate_relation_rows_device = None
    device_active_shape_ordinals_used = False
    with prepare_rayjoin_optix_shape_pair_active_count(
        right_shapes,
        dataset=f"{args.left_cdb} + {args.right_cdb}",
        dataset_note="Goal3492 public-CDB prepared tile-task executor over RTDL relation rows.",
    ) as prepared:
        packed_left = pack_rayjoin_optix_shape_pair_active_count_left_shapes(left_shapes)
        for repeat in range(max(0, int(args.relation_column_warmup_repeats))):
            print(
                "[goal3492] warm active relation device columns "
                f"{repeat + 1}/{max(0, int(args.relation_column_warmup_repeats))}",
                flush=True,
            )
            warmup_start = time.perf_counter()
            with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as warm_columns:
                cp.cuda.Stream.null.synchronize()
                _ = int(warm_columns.row_count)
            relation_column_warmup_secs.append(time.perf_counter() - warmup_start)
        relation_column_start = time.perf_counter()
        with prepared.active_relation_device_columns(packed_left, max_rows=int(args.max_rows)) as columns:
            cp.cuda.Stream.null.synchronize()
            active_relation_device_columns_sec = time.perf_counter() - relation_column_start
            cp.cuda.Stream.null.synchronize()
            if args.bounds_positive_filter:
                bounds_filter_start = time.perf_counter()
                bounds = rt.shape_pair_relation_bounds_overlap_area_cupy(columns, group_by=None)
                bounds_positive_mask = bounds.row_areas > 0.0
                bounds_positive_relation_rows_device = cp.nonzero(bounds_positive_mask)[0].astype(cp.uint32, copy=True)
                bounds_positive_relation_rows = cp.asnumpy(bounds_positive_relation_rows_device).astype("uint32", copy=False)
                bounds_positive_filter_metadata = bounds.to_metadata()
                bounds_positive_filter_metadata.update(
                    {
                        "bounds_positive_relation_row_count": int(len(bounds_positive_relation_rows)),
                        "row_filter": "bounds_overlap_area_gt_zero",
                        "exact_area_for_filtered_rows": "known_zero_by_axis_aligned_bounds_disjointness",
                    }
                )
                cp.cuda.Stream.null.synchronize()
                bounds_positive_filter_sec = time.perf_counter() - bounds_filter_start
            if args.active_shapes_only and args.device_active_shape_ordinals:
                active_shape_start = time.perf_counter()
                active_ordinals = rt.shape_pair_relation_active_shape_ordinals_cupy(
                    columns,
                    row_mask=bounds_positive_mask,
                )
                cp.cuda.Stream.null.synchronize()
                left_shapes_to_build = set(
                    map(int, cp.asnumpy(active_ordinals.left_unique_ordinals).tolist())
                )
                right_shapes_to_build = set(
                    map(int, cp.asnumpy(active_ordinals.right_unique_ordinals).tolist())
                )
                active_shape_ordinal_metadata = active_ordinals.to_metadata()
                device_active_shape_ordinals_used = True
                active_shape_ordinals_sec = time.perf_counter() - active_shape_start
            ordinals = columns.as_cupy_ordinal_columns()
            relation_download_start = time.perf_counter()
            left_ordinals = cp.asnumpy(ordinals["left_ordinal"]).astype("uint32", copy=False)
            right_ordinals = cp.asnumpy(ordinals["right_ordinal"]).astype("uint32", copy=False)
            relation_ordinal_download_sec = time.perf_counter() - relation_download_start
            if args.device_tile_task_planner:
                left_ordinals_device = cp.array(ordinals["left_ordinal"], dtype=cp.uint32, copy=True)
                right_ordinals_device = cp.array(ordinals["right_ordinal"], dtype=cp.uint32, copy=True)
                candidate_relation_rows_device = (
                    cp.array(bounds_positive_relation_rows_device, dtype=cp.uint32, copy=True)
                    if bounds_positive_relation_rows_device is not None
                    else cp.arange(int(columns.row_count), dtype=cp.uint32)
                )
                cp.cuda.Stream.null.synchronize()
    relation_discovery_sec = time.perf_counter() - discovery_start

    candidate_relation_rows = (
        tuple(map(int, bounds_positive_relation_rows.tolist()))
        if bounds_positive_relation_rows is not None
        else tuple(range(len(left_ordinals)))
    )

    if args.active_shapes_only and not device_active_shape_ordinals_used:
        left_shapes_to_build = set(map(int, left_ordinals[list(candidate_relation_rows)]))
        right_shapes_to_build = set(map(int, right_ordinals[list(candidate_relation_rows)]))
    elif not args.active_shapes_only:
        left_shapes_to_build = set(range(len(left_shapes)))
        right_shapes_to_build = set(range(len(right_shapes)))

    print(
        "[goal3492] build Shapely oracle geometries "
        f"(left={len(left_shapes_to_build)}/{len(left_shapes)}, right={len(right_shapes_to_build)}/{len(right_shapes)})",
        flush=True,
    )
    payload_workers = max(1, int(args.payload_workers))
    payload_cache_dir = Path(args.payload_cache_dir) if args.payload_cache_dir is not None else None
    payload_cache_mode = str(args.payload_cache_mode)
    payload_cache_format = str(args.payload_cache_format)
    if payload_cache_mode != "off" and payload_cache_dir is None:
        raise ValueError("--payload-cache-mode requires --payload-cache-dir")
    build_start = time.perf_counter()
    parallel_payload_prepare_sec = 0.0
    parallel_payload_prepare_used = payload_workers > 1
    payload_cache_load_sec = 0.0
    payload_cache_write_sec = 0.0
    payload_cache_read_used = payload_cache_mode == "read"
    payload_cache_write_used = payload_cache_mode in {"write", "refresh"}
    payload_cache_metadata: dict[str, object] = {
        "mode": payload_cache_mode,
        "format": payload_cache_format,
        "cache_dir": str(payload_cache_dir) if payload_cache_dir is not None else None,
        "read_used": False,
        "write_used": False,
        "left": None,
        "right": None,
    }
    if payload_cache_read_used:
        if payload_cache_dir is None:
            raise ValueError("payload cache read requires --payload-cache-dir")
        print(f"[goal3492] read prepared payload cache from {payload_cache_dir}", flush=True)
        cache_load_start = time.perf_counter()
        (
            left_payload,
            left_shape_components,
            left_prepared_status,
            left_geometry_map,
            left_geometry_status,
            left_cache_metadata,
        ) = _read_prepared_payload_cache(
            payload_cache_dir,
            "left",
            source_cdb=args.left_cdb,
            selected_shape_ordinals=left_shapes_to_build if args.active_shapes_only else set(range(len(left_shapes))),
            cache_format=payload_cache_format,
        )
        (
            right_payload,
            right_shape_components,
            right_prepared_status,
            right_geometry_map,
            right_geometry_status,
            right_cache_metadata,
        ) = _read_prepared_payload_cache(
            payload_cache_dir,
            "right",
            source_cdb=args.right_cdb,
            selected_shape_ordinals=right_shapes_to_build if args.active_shapes_only else set(range(len(right_shapes))),
            cache_format=payload_cache_format,
        )
        payload_cache_load_sec = time.perf_counter() - cache_load_start
        geometry_build_sec = 0.0
        payload_build_sec = 0.0
        parallel_payload_prepare_used = False
        payload_cache_metadata.update(
            {
                "read_used": True,
                "left": left_cache_metadata,
                "right": right_cache_metadata,
            }
        )
    elif parallel_payload_prepare_used:
        print(f"[goal3492] parallel geometry/payload preparation workers={payload_workers}", flush=True)
        left_payload, left_shape_components, left_prepared_status, left_geometry_map, left_geometry_status = (
            _prepare_geometry_payload_bundle_parallel(
                left_shapes,
                left_shapes_to_build if args.active_shapes_only else set(range(len(left_shapes))),
                workers=payload_workers,
            )
        )
        right_payload, right_shape_components, right_prepared_status, right_geometry_map, right_geometry_status = (
            _prepare_geometry_payload_bundle_parallel(
                right_shapes,
                right_shapes_to_build if args.active_shapes_only else set(range(len(right_shapes))),
                workers=payload_workers,
            )
        )
        parallel_payload_prepare_sec = time.perf_counter() - build_start
        geometry_build_sec = 0.0
        payload_build_sec = 0.0
    else:
        if args.active_shapes_only:
            left_geometry_map, left_geometry_status = _build_oracle_geometry_map(
                left_shapes, left_shapes_to_build, ShapelyPolygon, make_valid
            )
            right_geometry_map, right_geometry_status = _build_oracle_geometry_map(
                right_shapes, right_shapes_to_build, ShapelyPolygon, make_valid
            )
        else:
            left_geometries, left_geometry_status = _build_oracle_polygons(left_shapes, ShapelyPolygon, make_valid)
            right_geometries, right_geometry_status = _build_oracle_polygons(right_shapes, ShapelyPolygon, make_valid)
            left_geometry_map = dict(enumerate(left_geometries))
            right_geometry_map = dict(enumerate(right_geometries))
        geometry_build_sec = time.perf_counter() - build_start

        print("[goal3492] prepare simple-polygon component payloads", flush=True)
        payload_start = time.perf_counter()
        left_payload, left_shape_components, left_prepared_status = _prepare_payload_from_geometry_map(left_geometry_map)
        right_payload, right_shape_components, right_prepared_status = _prepare_payload_from_geometry_map(right_geometry_map)
        payload_build_sec = time.perf_counter() - payload_start

    if payload_cache_write_used:
        if payload_cache_dir is None:
            raise ValueError("payload cache write requires --payload-cache-dir")
        print(f"[goal3492] write prepared payload cache to {payload_cache_dir}", flush=True)
        cache_write_start = time.perf_counter()
        left_cache_path = _write_prepared_payload_cache(
            payload_cache_dir,
            "left",
            source_cdb=args.left_cdb,
            selected_shape_ordinals=left_shapes_to_build if args.active_shapes_only else set(range(len(left_shapes))),
            payload=left_payload,
            shape_to_components=left_shape_components,
            prepared_status_counts=left_prepared_status,
            geometry_map=left_geometry_map,
            geometry_status_counts=left_geometry_status,
            cache_format=payload_cache_format,
        )
        right_cache_path = _write_prepared_payload_cache(
            payload_cache_dir,
            "right",
            source_cdb=args.right_cdb,
            selected_shape_ordinals=right_shapes_to_build if args.active_shapes_only else set(range(len(right_shapes))),
            payload=right_payload,
            shape_to_components=right_shape_components,
            prepared_status_counts=right_prepared_status,
            geometry_map=right_geometry_map,
            geometry_status_counts=right_geometry_status,
            cache_format=payload_cache_format,
        )
        payload_cache_write_sec = time.perf_counter() - cache_write_start
        payload_cache_metadata.update(
            {
                "write_used": True,
                "left": {
                    "cache_path": str(left_cache_path),
                    "format": payload_cache_format,
                    "selected_shape_count": len(left_shapes_to_build),
                },
                "right": {
                    "cache_path": str(right_cache_path),
                    "format": payload_cache_format,
                    "selected_shape_count": len(right_shapes_to_build),
                },
            }
        )

    print(
        f"[goal3492] build exact oracle areas for {len(candidate_relation_rows)}/{len(left_ordinals)} rows",
        flush=True,
    )
    exact_start = time.perf_counter()
    exact_areas: list[float] = [0.0] * len(left_ordinals)
    for index, relation_row in enumerate(candidate_relation_rows):
        if int(args.progress_every) > 0 and index > 0 and index % int(args.progress_every) == 0:
            print(f"[goal3492] exact rows={index}/{len(candidate_relation_rows)}", flush=True)
        left_ordinal = left_ordinals[relation_row]
        right_ordinal = right_ordinals[relation_row]
        exact_areas[relation_row] = float(
            left_geometry_map[int(left_ordinal)].intersection(right_geometry_map[int(right_ordinal)]).area
        )
    exact_oracle_sec = time.perf_counter() - exact_start

    print("[goal3492] expand component pairs and tile tasks", flush=True)
    plan_start = time.perf_counter()
    component_pairs: list[tuple[int, int]] = []
    relation_row_ordinals: list[int] = []
    unsupported_rows = 0
    unsupported_positive_rows = 0
    device_tile_task_planning_sec = 0.0
    device_tile_task_planning_repeat_secs: list[float] = []
    resident_inputs = None
    if args.device_tile_task_planner:
        if left_ordinals_device is None or right_ordinals_device is None or candidate_relation_rows_device is None:
            raise RuntimeError("device tile-task planner requires copied CuPy relation ordinal columns")
        for relation_row in candidate_relation_rows:
            left_ordinal = left_ordinals[relation_row]
            right_ordinal = right_ordinals[relation_row]
            if not left_shape_components.get(int(left_ordinal), ()) or not right_shape_components.get(int(right_ordinal), ()):
                unsupported_rows += 1
                if exact_areas[relation_row] > rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE:
                    unsupported_positive_rows += 1
        left_component_starts, left_component_counts = _shape_component_table(left_shape_components, len(left_shapes))
        right_component_starts, right_component_counts = _shape_component_table(right_shape_components, len(right_shapes))
        for repeat in range(max(1, int(args.device_planner_repeats))):
            print(f"[goal3492] device tile-task planner repeat {repeat + 1}/{max(1, int(args.device_planner_repeats))}", flush=True)
            device_plan_start = time.perf_counter()
            resident_inputs = rt.prepare_overlay_area_tile_task_cupy_inputs_from_relation_ordinals(
                left_payload,
                right_payload,
                relation_row_ordinals=candidate_relation_rows_device,
                left_relation_ordinals=left_ordinals_device,
                right_relation_ordinals=right_ordinals_device,
                left_shape_component_starts=left_component_starts,
                left_shape_component_counts=left_component_counts,
                right_shape_component_starts=right_component_starts,
                right_shape_component_counts=right_component_counts,
                relation_row_count=len(left_ordinals),
                max_triangle_pairs_per_task=int(args.max_triangle_pairs_per_task),
                component_bounds_positive_filter=bool(args.component_bounds_filter),
            )
            cp.cuda.Stream.null.synchronize()
            device_tile_task_planning_repeat_secs.append(time.perf_counter() - device_plan_start)
        device_tile_task_planning_sec = sum(device_tile_task_planning_repeat_secs)
        assert resident_inputs is not None
        task_summary = resident_inputs.to_metadata()["planner_summary"]
        pair_rows = ()
        tasks = ()
        component_pair_row_count = int(task_summary["pair_row_count"])
        tile_task_count = int(task_summary["task_count"])
        planned_triangle_pair_count = int(task_summary["planned_triangle_pair_count"])
        expected_triangle_pair_count = int(task_summary["expected_triangle_pair_count"])
    else:
        for relation_row in candidate_relation_rows:
            left_ordinal = left_ordinals[relation_row]
            right_ordinal = right_ordinals[relation_row]
            left_components = left_shape_components.get(int(left_ordinal), ())
            right_components = right_shape_components.get(int(right_ordinal), ())
            if not left_components or not right_components:
                unsupported_rows += 1
                if exact_areas[relation_row] > rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE:
                    unsupported_positive_rows += 1
                continue
            for left_component in left_components:
                for right_component in right_components:
                    if args.component_bounds_filter and not rt.prepared_overlay_area_component_bounds_overlap_positive(
                        left_payload,
                        right_payload,
                        left_component,
                        right_component,
                    ):
                        continue
                    component_pairs.append((left_component, right_component))
                    relation_row_ordinals.append(relation_row)
        pair_rows = rt.prepare_overlay_area_pair_rows(left_payload, right_payload, component_pairs)
        tasks = rt.plan_prepared_overlay_area_tile_tasks(
            pair_rows,
            max_triangle_pairs_per_task=int(args.max_triangle_pairs_per_task),
            relation_row_ordinals=relation_row_ordinals,
        )
        task_summary = rt.summarize_prepared_overlay_area_tile_tasks(pair_rows, tasks)
        component_pair_row_count = len(pair_rows)
        tile_task_count = len(tasks)
        planned_triangle_pair_count = int(task_summary["planned_triangle_pair_count"])
        expected_triangle_pair_count = int(task_summary["expected_triangle_pair_count"])
    planning_sec = time.perf_counter() - plan_start
    supported_relation_row_count = int(task_summary.get("relation_row_count", len(candidate_relation_rows) - unsupported_rows))
    skipped_candidate_relation_row_count = int(len(candidate_relation_rows) - supported_relation_row_count)
    component_bounds_filtered_relation_row_count = (
        max(0, skipped_candidate_relation_row_count - unsupported_rows)
        if args.component_bounds_filter
        else 0
    )

    print(f"[goal3492] execute {tile_task_count} tile tasks over {component_pair_row_count} component-pair rows", flush=True)
    cp.cuda.Stream.null.synchronize()
    input_prepare_sec = 0.0
    executor_repeats = max(1, int(args.executor_repeats))
    executor_repeat_secs: list[float] = []
    if resident_inputs is not None:
        result = None
        for repeat in range(executor_repeats):
            print(f"[goal3492] device-planned resident executor repeat {repeat + 1}/{executor_repeats}", flush=True)
            execute_start = time.perf_counter()
            result = rt.evaluate_prepared_overlay_area_tile_task_cupy_inputs(
                resident_inputs,
                input_contract="device_planned_prepared_overlay_area_tile_task_cupy_inputs",
            )
            cp.cuda.Stream.null.synchronize()
            executor_repeat_secs.append(time.perf_counter() - execute_start)
        assert result is not None
        executor_sec = sum(executor_repeat_secs)
    elif args.resident_cupy_inputs:
        input_prepare_start = time.perf_counter()
        resident_inputs = rt.prepare_overlay_area_tile_task_cupy_inputs(
            left_payload,
            right_payload,
            tasks,
            relation_row_count=len(left_ordinals),
        )
        cp.cuda.Stream.null.synchronize()
        input_prepare_sec = time.perf_counter() - input_prepare_start
        result = None
        for repeat in range(executor_repeats):
            print(f"[goal3492] resident executor repeat {repeat + 1}/{executor_repeats}", flush=True)
            execute_start = time.perf_counter()
            result = rt.evaluate_prepared_overlay_area_tile_task_cupy_inputs(resident_inputs)
            cp.cuda.Stream.null.synchronize()
            executor_repeat_secs.append(time.perf_counter() - execute_start)
        assert result is not None
        executor_sec = sum(executor_repeat_secs)
    else:
        execute_start = time.perf_counter()
        result = rt.evaluate_prepared_overlay_area_tile_tasks_cupy(
            left_payload,
            right_payload,
            tasks,
            relation_row_count=len(left_ordinals),
        )
        cp.cuda.Stream.null.synchronize()
        executor_sec = time.perf_counter() - execute_start
        executor_repeat_secs.append(executor_sec)
    relation_areas = cp.asnumpy(result.relation_areas).astype("float64", copy=False)
    metadata = result.to_metadata()

    errors = [abs(float(observed) - float(expected)) for observed, expected in zip(relation_areas, exact_areas)]
    max_abs_error = max(errors, default=0.0)
    total_observed_area = float(relation_areas.sum())
    total_exact_area = float(sum(exact_areas))
    positive_threshold = rt.V2_8_OVERLAY_AREA_ROW_ABS_TOLERANCE
    observed_positive_rows = int(sum(1 for area in relation_areas if float(area) > positive_threshold))
    exact_positive_rows = int(sum(1 for area in exact_areas if float(area) > positive_threshold))
    largest_error_rows = sorted(
        (
            {
                "relation_row": int(row),
                "left_ordinal": int(left_ordinals[row]),
                "right_ordinal": int(right_ordinals[row]),
                "observed_area": float(relation_areas[row]),
                "exact_area": float(exact_areas[row]),
                "abs_error": float(errors[row]),
            }
            for row in range(len(errors))
        ),
        key=lambda item: item["abs_error"],
        reverse=True,
    )[:10]

    schema = (
        "rtdl.goal3511.overlay_area_steady_state_relation_stream.v1"
        if args.relation_stream_steady_state_evidence
        else (
            "rtdl.goal3509.overlay_area_binary_prepared_payload_cache.v1"
            if payload_cache_format == "binary"
            else "rtdl.goal3507.overlay_area_prepared_payload_cache.v1"
        )
        if args.payload_cache_evidence
        else (
            "rtdl.goal3504.overlay_area_parallel_payload_prepare.v1"
            if args.parallel_payload_prepare_evidence
            else (
                "rtdl.goal3502.overlay_area_single_triangulation_payload_construction.v1"
                if args.single_triangulation_payload_evidence
                else (
                    "rtdl.goal3497.overlay_area_bounds_positive_filtered_tile_tasks.v1"
                    if args.bounds_positive_filter and not args.device_tile_task_planner
                    else (
                        "rtdl.goal3501.overlay_area_component_bounds_filtered_tile_tasks.v1"
                        if args.component_bounds_filter
                        else (
                            "rtdl.goal3498.overlay_area_device_tile_task_planner.v1"
                            if args.device_tile_task_planner
                            else (
                                "rtdl.goal3495.overlay_area_device_active_shape_ordinals.v1"
                                if device_active_shape_ordinals_used
                                else (
                                    "rtdl.goal3494.overlay_area_resident_cupy_tile_task_inputs.v1"
                                    if args.resident_cupy_inputs
                                    else (
                                        "rtdl.goal3493.overlay_area_active_shape_payload_construction.v1"
                                        if args.active_shapes_only
                                        else "rtdl.goal3492.overlay_area_public_cdb_tile_task_executor.v1"
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )
    )
    goal = 3511 if args.relation_stream_steady_state_evidence else (
        (3509 if payload_cache_format == "binary" else 3507) if args.payload_cache_evidence else (
        3504 if args.parallel_payload_prepare_evidence else (
            3502 if args.single_triangulation_payload_evidence else (
                3501 if args.component_bounds_filter else (3498 if args.device_tile_task_planner else (3497 if args.bounds_positive_filter else (
                    3495 if device_active_shape_ordinals_used else (
                        3494 if args.resident_cupy_inputs else (3493 if args.active_shapes_only else 3492)
                    )
                )))
            )
        )
    ))

    result = {
        "schema": schema,
        "goal": goal,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cupy_version": cp.__version__,
        "shapely_version": shapely_version,
        "left_cdb": str(args.left_cdb),
        "right_cdb": str(args.right_cdb),
        "active_shapes_only": bool(args.active_shapes_only),
        "max_rows": int(args.max_rows),
        "max_triangle_pairs_per_task": int(args.max_triangle_pairs_per_task),
        "resident_cupy_inputs": bool(args.resident_cupy_inputs or args.device_tile_task_planner),
        "device_active_shape_ordinals": bool(args.device_active_shape_ordinals),
        "device_active_shape_ordinals_used": bool(device_active_shape_ordinals_used),
        "bounds_positive_filter": bool(args.bounds_positive_filter),
        "component_bounds_filter": bool(args.component_bounds_filter),
        "device_tile_task_planner": bool(args.device_tile_task_planner),
        "single_triangulation_payload_construction": True,
        "single_triangulation_payload_evidence": bool(args.single_triangulation_payload_evidence),
        "payload_workers": payload_workers,
        "parallel_payload_prepare": bool(parallel_payload_prepare_used),
        "parallel_payload_prepare_evidence": bool(args.parallel_payload_prepare_evidence),
        "payload_cache_mode": payload_cache_mode,
        "payload_cache_format": payload_cache_format,
        "payload_cache_evidence": bool(args.payload_cache_evidence),
        "payload_cache_metadata": payload_cache_metadata,
        "relation_stream_steady_state_evidence": bool(args.relation_stream_steady_state_evidence),
        "relation_column_warmup_repeats": max(0, int(args.relation_column_warmup_repeats)),
        "bounds_positive_relation_row_count": int(len(candidate_relation_rows)),
        "bounds_positive_filter_metadata": bounds_positive_filter_metadata,
        "active_shape_ordinal_metadata": active_shape_ordinal_metadata,
        "executor_repeats": executor_repeats,
        "device_planner_repeats": max(1, int(args.device_planner_repeats)),
        "left_shape_count": len(left_shapes),
        "right_shape_count": len(right_shapes),
        "prepared_left_shape_count": len(left_geometry_map),
        "prepared_right_shape_count": len(right_geometry_map),
        "left_geometry_status_counts": left_geometry_status,
        "right_geometry_status_counts": right_geometry_status,
        "left_prepared_status_counts": left_prepared_status,
        "right_prepared_status_counts": right_prepared_status,
        "left_payload_triangle_count": left_payload.triangle_count,
        "right_payload_triangle_count": right_payload.triangle_count,
        "relation_row_count": int(len(left_ordinals)),
        "candidate_relation_row_count": int(len(candidate_relation_rows)),
        "supported_relation_row_count": supported_relation_row_count,
        "skipped_candidate_relation_row_count": skipped_candidate_relation_row_count,
        "component_bounds_filtered_relation_row_count": component_bounds_filtered_relation_row_count,
        "unsupported_relation_row_count": unsupported_rows,
        "unsupported_positive_relation_row_count": unsupported_positive_rows,
        "component_pair_row_count": component_pair_row_count,
        "tile_task_count": tile_task_count,
        "planned_triangle_pair_count": planned_triangle_pair_count,
        "expected_triangle_pair_count": expected_triangle_pair_count,
        "task_summary": task_summary,
        "executor_metadata": metadata,
        "observed_total_area": total_observed_area,
        "exact_total_area": total_exact_area,
        "total_area_abs_error": abs(total_observed_area - total_exact_area),
        "observed_positive_row_count": observed_positive_rows,
        "exact_positive_row_count": exact_positive_rows,
        "positive_row_count_match": observed_positive_rows == exact_positive_rows,
        "max_relation_abs_error": max_abs_error,
        "relation_abs_error_percentiles": {
            "p50": _percentile(errors, 0.50),
            "p90": _percentile(errors, 0.90),
            "p99": _percentile(errors, 0.99),
        },
        "largest_error_rows": largest_error_rows,
        "timing_sec": {
            "geometry_build": geometry_build_sec,
            "payload_build": payload_build_sec,
            "parallel_geometry_payload_prepare": parallel_payload_prepare_sec,
            "payload_cache_load": payload_cache_load_sec,
            "payload_cache_write": payload_cache_write_sec,
            "geometry_plus_payload_prepare": (
                payload_cache_load_sec
                if payload_cache_read_used
                else (parallel_payload_prepare_sec if parallel_payload_prepare_used else geometry_build_sec + payload_build_sec)
            ),
            "relation_discovery": relation_discovery_sec,
            "active_relation_device_columns": active_relation_device_columns_sec,
            "active_relation_device_columns_warmup_secs": relation_column_warmup_secs,
            "active_relation_device_columns_best_warmup": (
                min(relation_column_warmup_secs) if relation_column_warmup_secs else 0.0
            ),
            "bounds_positive_filter": bounds_positive_filter_sec,
            "device_active_shape_ordinals": active_shape_ordinals_sec,
            "relation_ordinal_download": relation_ordinal_download_sec,
            "exact_oracle": exact_oracle_sec,
            "planning": planning_sec,
            "device_tile_task_planning": device_tile_task_planning_sec,
            "device_tile_task_planning_repeat_secs": device_tile_task_planning_repeat_secs,
            "device_tile_task_planning_best_repeat": (
                min(device_tile_task_planning_repeat_secs) if device_tile_task_planning_repeat_secs else 0.0
            ),
            "cupy_tile_task_input_prepare": input_prepare_sec,
            "cupy_tile_task_executor": executor_sec,
            "cupy_tile_task_executor_repeat_secs": executor_repeat_secs,
            "cupy_tile_task_executor_best_repeat": min(executor_repeat_secs) if executor_repeat_secs else 0.0,
        },
        "claim_boundary": _claim_boundary(),
        "interpretation": (
            "Executes the prepared simple-polygon overlay-area tile-task plan over the public-CDB "
            "active relation stream and compares scalar relation areas with the external Shapely/GEOS oracle."
        ),
    }
    result["prepared_execution_report"] = rt.prepared_execution_report_from_artifact(
        result,
        workflow_name="simple_polygon_overlay_area_prepared_execution",
        backend="optix",
        notes=(
            "Partner choice is explicit in executor_metadata.partner.",
            "Validation oracle time is separated from the steady-state execution path.",
        ),
    ).to_dict()
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3492 public-CDB prepared tile-task overlay-area executor.")
    parser.add_argument("--left-cdb", type=Path, default=ROOT / "data" / "rayjoin_public_cdb" / "br_county.cdb")
    parser.add_argument(
        "--right-cdb",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb" / "br_county_start256_count1024.cdb",
    )
    parser.add_argument("--max-rows", type=int, default=65536)
    parser.add_argument("--max-triangle-pairs-per-task", type=int, default=512)
    parser.add_argument("--progress-every", type=int, default=500)
    parser.add_argument("--resident-cupy-inputs", action="store_true")
    parser.add_argument("--executor-repeats", type=int, default=1)
    parser.add_argument("--device-planner-repeats", type=int, default=1)
    parser.add_argument(
        "--payload-workers",
        type=int,
        default=1,
        help=(
            "Use multiple CPU processes for independent Shapely geometry repair and "
            "prepared component extraction. The default 1 preserves the sequential path."
        ),
    )
    parser.add_argument("--payload-cache-dir", type=Path, default=None)
    parser.add_argument(
        "--relation-column-warmup-repeats",
        type=int,
        default=0,
        help=(
            "Run and discard this many prepared active-relation device-column passes before "
            "the measured pass. This exposes steady-state relation-stream timing without "
            "hiding setup costs in the artifact."
        ),
    )
    parser.add_argument(
        "--relation-stream-steady-state-evidence",
        action="store_true",
        help="Label the output as Goal3511 evidence for steady-state prepared relation-stream timing.",
    )
    parser.add_argument(
        "--payload-cache-mode",
        choices=("off", "read", "write", "refresh"),
        default="off",
        help="Prepared payload cache mode. read requires existing cache; write/refresh write cache after preparation.",
    )
    parser.add_argument(
        "--payload-cache-format",
        choices=("json", "binary"),
        default="json",
        help="Prepared payload cache storage format. json preserves Goal3507; binary labels Goal3509 evidence.",
    )
    parser.add_argument(
        "--payload-cache-evidence",
        action="store_true",
        help="Label the output as Goal3507 evidence for prepared-payload cache reuse.",
    )
    parser.add_argument(
        "--bounds-positive-filter",
        action="store_true",
        help=(
            "Use generic bounds-overlap area > 0 as a device-side zero-area filter before "
            "component-pair and tile-task planning."
        ),
    )
    parser.add_argument(
        "--device-tile-task-planner",
        action="store_true",
        help=(
            "Plan component-pair tile tasks with a generic CuPy continuation from relation ordinal "
            "columns and prepared component tables."
        ),
    )
    parser.add_argument(
        "--component-bounds-filter",
        action="store_true",
        help=(
            "Skip prepared component pairs whose component bounding boxes have non-positive "
            "overlap before exact triangle-pair tile execution."
        ),
    )
    parser.add_argument(
        "--device-active-shape-ordinals",
        action="store_true",
        help=(
            "When active-shapes-only is enabled, compute unique active shape ordinals on device "
            "and materialize only the smaller unique ordinal lists for CPU-owned payload preparation."
        ),
    )
    parser.add_argument(
        "--single-triangulation-payload-evidence",
        action="store_true",
        help=(
            "Label the output as Goal3502 evidence for the generic single-triangulation "
            "prepared-payload construction path."
        ),
    )
    parser.add_argument(
        "--parallel-payload-prepare-evidence",
        action="store_true",
        help="Label the output as Goal3504 evidence for parallel prepared-payload preparation.",
    )
    parser.add_argument(
        "--active-shapes-only",
        action="store_true",
        help="Prepare only shapes referenced by the active relation stream instead of the whole CDB.",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
