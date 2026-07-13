#!/usr/bin/env python3
"""Build full-public WaterBodies->BlockGroups WKT candidates from ArcGIS.

This is an app-owned X-HD reproduction helper. It materializes the strongest
Goal5309 geo candidate into author-readable WKT, but still does not claim exact
paper input recovery. The source is a public ArcGIS reconstruction, not a
file/hash match to the author's `/local/storage/shared/HDDatasets` WKT files.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
GOAL5309_SCRIPT = (
    REPO_ROOT
    / "Paper-reproduction-apps"
    / "x-hd-paper"
    / "scripts"
    / "build_xhd_goal5309_full_public_arcgis_point_count_mbr_probe.py"
)


def _load_goal5309_module():
    spec = importlib.util.spec_from_file_location("xhd_goal5309_probe", GOAL5309_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"could not load {GOAL5309_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


G5309 = _load_goal5309_module()
SERVICE_BY_KEY = {spec.key: spec for spec in G5309.SERVICES}
DEFAULT_SERVICE_KEYS = ("waterbodies", "blockgroups")


def _fmt(value: float) -> str:
    text = f"{float(value):.12g}"
    if text == "-0":
        return "0"
    return text


def _coord_text(coord: list[float]) -> str:
    return f"{_fmt(coord[0])} {_fmt(coord[1])}"


def _ring_text(ring: list[list[float]]) -> str:
    if not ring:
        raise ValueError("empty WKT ring")
    if ring[0] != ring[-1]:
        ring = [*ring, ring[0]]
    return "(" + ", ".join(_coord_text(coord) for coord in ring) + ")"


def _polygon_text(rings: list[list[list[float]]]) -> str:
    if not rings:
        raise ValueError("empty WKT polygon")
    return "(" + ", ".join(_ring_text(ring) for ring in rings) + ")"


def _geometry_to_wkt_and_meta(geometry: dict[str, Any]) -> tuple[str, int, list[float]]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")
    if geom_type == "Polygon":
        polygons = [coords]
        wkt = "POLYGON " + _polygon_text(coords)
    elif geom_type == "MultiPolygon":
        polygons = coords
        wkt = "MULTIPOLYGON (" + ", ".join(_polygon_text(poly) for poly in polygons) + ")"
    else:
        raise ValueError(f"unsupported geometry type for full-public WKT candidate: {geom_type!r}")

    point_count = 0
    bounds: list[float] | None = None
    for polygon in polygons:
        if not polygon:
            continue
        outer = polygon[0]
        if outer and outer[0] != outer[-1]:
            outer = [*outer, outer[0]]
        point_count += len(outer)
        for x, y, *_ in outer:
            xf = float(x)
            yf = float(y)
            if bounds is None:
                bounds = [xf, xf, yf, yf]
            else:
                bounds = [min(bounds[0], xf), max(bounds[1], xf), min(bounds[2], yf), max(bounds[3], yf)]
    if bounds is None:
        raise ValueError("geometry has no outer-ring author points")
    return wkt, point_count, bounds


def _update_bounds(bounds: list[float] | None, feature_bounds: list[float]) -> list[float]:
    if bounds is None:
        return list(feature_bounds)
    return [
        min(bounds[0], feature_bounds[0]),
        max(bounds[1], feature_bounds[1]),
        min(bounds[2], feature_bounds[2]),
        max(bounds[3], feature_bounds[3]),
    ]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f"{path.name}.tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def _empty_checkpoint(key: str, service_count: int, output_wkt: Path) -> dict[str, Any]:
    return {
        "key": key,
        "service_feature_count": service_count,
        "features_seen": 0,
        "pages_seen": 0,
        "author_loader_point_count": 0,
        "geometry_types": {},
        "object_id_min": None,
        "object_id_max": None,
        "mbr": None,
        "output_wkt": str(output_wkt),
        "complete": False,
        "resumed_from_checkpoint": False,
        "checkpoint_features_seen_at_start": 0,
    }


def _load_checkpoint(path: Path, *, key: str, service_count: int, output_wkt: Path) -> dict[str, Any]:
    if not path.exists():
        return _empty_checkpoint(key, service_count, output_wkt)
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("key") != key:
        raise RuntimeError(f"checkpoint key mismatch: expected {key}, got {payload.get('key')!r}")
    if Path(payload.get("output_wkt", "")) != output_wkt:
        raise RuntimeError(f"checkpoint output path mismatch for {key}: {payload.get('output_wkt')!r}")
    if not output_wkt.exists():
        raise RuntimeError(f"checkpoint exists for {key}, but output WKT is missing: {output_wkt}")
    features_seen = int(payload.get("features_seen", 0))
    payload["service_feature_count"] = service_count
    payload["features_seen"] = features_seen
    payload["pages_seen"] = int(payload.get("pages_seen", 0))
    payload["author_loader_point_count"] = int(payload.get("author_loader_point_count", 0))
    payload["geometry_types"] = dict(payload.get("geometry_types") or {})
    payload["complete"] = features_seen >= service_count
    payload["resumed_from_checkpoint"] = True
    payload["checkpoint_features_seen_at_start"] = features_seen
    return payload


def _finalize_service(acc: dict[str, Any], spec: Any, output_wkt: Path) -> dict[str, Any]:
    point_count = int(acc["author_loader_point_count"])
    delta = point_count - int(spec.paper_point_count)
    rel_delta = None if spec.paper_point_count == 0 else delta / float(spec.paper_point_count)
    complete = bool(acc["complete"])
    return {
        **acc,
        "paper_basename": spec.paper_basename,
        "service_url": spec.service_url,
        "paper_point_count": int(spec.paper_point_count),
        "point_count_delta": int(delta),
        "point_count_relative_delta": rel_delta,
        "paper_mbr": {
            "x": [spec.paper_mbr[0][0], spec.paper_mbr[0][1]],
            "y": [spec.paper_mbr[1][0], spec.paper_mbr[1][1]],
        },
        "mbr_delta": G5309._mbr_delta(acc["mbr"], spec.paper_mbr),
        "output_wkt": str(output_wkt),
        "output_bytes": output_wkt.stat().st_size if output_wkt.exists() else 0,
        "sha256": _sha256_file(output_wkt) if complete and output_wkt.exists() else None,
    }


def materialize_service(
    key: str,
    *,
    output_dir: Path,
    checkpoint_dir: Path,
    page_size: int,
    timeout: int,
    max_pages: int | None,
) -> dict[str, Any]:
    spec = SERVICE_BY_KEY[key]
    service_count = G5309._feature_count(spec, timeout=timeout)
    output_wkt = output_dir / f"{spec.paper_basename}.full_public_arcgis_candidate.wkt"
    checkpoint_path = checkpoint_dir / f"{key}.json"
    acc = _load_checkpoint(checkpoint_path, key=key, service_count=service_count, output_wkt=output_wkt)
    started_pages = int(acc["pages_seen"])
    offset = int(acc["features_seen"])
    if bool(acc["complete"]):
        return _finalize_service(acc, spec, output_wkt)

    output_wkt.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if offset > 0 else "w"
    with output_wkt.open(mode, encoding="utf-8", newline="\n") as handle:
        while offset < service_count:
            if max_pages is not None and int(acc["pages_seen"]) - started_pages >= max_pages:
                break
            params = {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "resultOffset": offset,
                "resultRecordCount": min(page_size, spec.max_record_count),
                "orderByFields": "OBJECTID",
                "outSR": 4326,
                "f": "geojson",
            }
            payload = G5309._query(spec.service_url, params, timeout=timeout)
            features = payload.get("features")
            if not isinstance(features, list):
                raise RuntimeError(f"feature query failed for {key} offset {offset}: {payload!r}")
            if not features:
                break
            for feature in features:
                geometry = feature.get("geometry")
                if not isinstance(geometry, dict):
                    raise ValueError(f"feature has no geometry mapping for {key}")
                geom_type = str(geometry.get("type"))
                acc["geometry_types"][geom_type] = int(acc["geometry_types"].get(geom_type, 0)) + 1
                wkt, point_count, bounds = _geometry_to_wkt_and_meta(geometry)
                handle.write(wkt)
                handle.write("\n")
                acc["author_loader_point_count"] = int(acc["author_loader_point_count"]) + point_count
                acc["mbr"] = _update_bounds(acc["mbr"], bounds)
                props = feature.get("properties") or {}
                object_id = props.get("OBJECTID")
                if object_id is not None:
                    object_id_i = int(object_id)
                    acc["object_id_min"] = object_id_i if acc["object_id_min"] is None else min(acc["object_id_min"], object_id_i)
                    acc["object_id_max"] = object_id_i if acc["object_id_max"] is None else max(acc["object_id_max"], object_id_i)
            offset += len(features)
            acc["features_seen"] = offset
            acc["pages_seen"] = int(acc["pages_seen"]) + 1
            acc["complete"] = offset >= service_count
            handle.flush()
            _write_json_atomic(checkpoint_path, _finalize_service(acc, spec, output_wkt))
            if len(features) < min(page_size, spec.max_record_count):
                break
    acc["complete"] = int(acc["features_seen"]) >= service_count
    _write_json_atomic(checkpoint_path, _finalize_service(acc, spec, output_wkt))
    return _finalize_service(acc, spec, output_wkt)


def build(args: argparse.Namespace) -> dict[str, Any]:
    output_dir = Path(args.output_dir)
    checkpoint_dir = Path(args.checkpoint_dir)
    started = time.perf_counter()
    services: dict[str, Any] = {}
    for key in args.services:
        service_started = time.perf_counter()
        result = materialize_service(
            key,
            output_dir=output_dir,
            checkpoint_dir=checkpoint_dir,
            page_size=int(args.page_size),
            timeout=int(args.timeout),
            max_pages=args.max_pages,
        )
        result["elapsed_sec"] = time.perf_counter() - service_started
        services[key] = result
    complete = all(bool(item["complete"]) for item in services.values())
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5310.water_bg_full_public_wkt_candidate.v1",
        "goal": "Goal5310",
        "status": "water_bg_full_public_wkt_candidate_complete" if complete else "water_bg_full_public_wkt_candidate_partial",
        "elapsed_sec": time.perf_counter() - started,
        "page_size_requested": int(args.page_size),
        "max_pages": args.max_pages,
        "services": services,
        "pair": "USADetailedWaterBodies.wkt -> USACensusBlockGroupBoundaries.wkt",
        "source_basis": "Goal5309 strong full-public candidate, not exact paper file/hash provenance",
        "comparison_readiness": {
            "author_hd_exec_ready": complete,
            "rtdl_route_ready": complete,
            "reason": "Full-public WKT materialization only; author/RTDL execution must be a separate reviewed gate.",
        },
        "claim_boundary": {
            "full_public_wkt_candidate_claimed": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "geo_figure5_reproduction_claimed": False,
            "author_rtdl_correctness_claimed": False,
            "performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate",
    )
    parser.add_argument(
        "--checkpoint-dir",
        default="Paper-reproduction-apps/x-hd-paper/results/goal5310_water_bg_full_public_wkt_checkpoints",
    )
    parser.add_argument(
        "--manifest",
        default="Paper-reproduction-apps/x-hd-paper/data/generated/goal5310_water_bg_full_public_wkt_candidate/manifest.json",
    )
    parser.add_argument("--services", nargs="+", default=list(DEFAULT_SERVICE_KEYS), choices=list(DEFAULT_SERVICE_KEYS))
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--max-pages", type=int)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = build(args)
    manifest = Path(args.manifest)
    _write_json_atomic(manifest, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
