"""Build a bounded County->ZCTA WKT fixture from name-matched ArcGIS services.

This is an app-owned X-HD reproduction helper.  It deliberately creates a
Level-B same-source fixture, not an exact-paper dataset.  The produced WKT is
one geometry per line so the author's Boost WKT loader can read it.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


COUNTY_SERVICE = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer"
ZIP_SERVICE = "https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas_anaylsis/FeatureServer"


def _query_url(service_url: str, *, count: int) -> str:
    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "resultOffset": 0,
        "resultRecordCount": count,
        "orderByFields": "OBJECTID",
        "outSR": 4326,
        "f": "geojson",
    }
    return f"{service_url.rstrip('/')}/0/query?{urlencode(params)}"


def _fetch_geojson(service_url: str, *, count: int) -> dict[str, Any]:
    url = _query_url(service_url, count=count)
    with urlopen(url, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if payload.get("type") != "FeatureCollection":
        raise RuntimeError(f"unexpected ArcGIS payload type from {url}: {payload.get('type')!r}")
    features = payload.get("features")
    if not isinstance(features, list) or len(features) != count:
        raise RuntimeError(f"expected {count} features from {url}, got {len(features) if isinstance(features, list) else features!r}")
    return payload


def _fmt(value: float) -> str:
    # Decimal enough for source-coordinate fidelity without huge WKT bloat.
    text = f"{float(value):.12g}"
    if text == "-0":
        return "0"
    return text


def _coord_text(coord: list[float]) -> str:
    return f"{_fmt(coord[0])} {_fmt(coord[1])}"


def _ring_text(ring: list[list[float]]) -> str:
    if not ring:
        raise ValueError("empty ring")
    if ring[0] != ring[-1]:
        ring = [*ring, ring[0]]
    return "(" + ", ".join(_coord_text(coord) for coord in ring) + ")"


def _polygon_text(rings: list[list[list[float]]]) -> str:
    if not rings:
        raise ValueError("empty polygon")
    return "(" + ", ".join(_ring_text(ring) for ring in rings) + ")"


def _geometry_to_wkt(geometry: dict[str, Any]) -> tuple[str, int, list[float]]:
    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")
    if geom_type == "Polygon":
        polygons = [coords]
        wkt = "POLYGON " + _polygon_text(coords)
    elif geom_type == "MultiPolygon":
        polygons = coords
        wkt = "MULTIPOLYGON (" + ", ".join(_polygon_text(poly) for poly in polygons) + ")"
    else:
        raise ValueError(f"unsupported geometry type for bounded County-ZCTA fixture: {geom_type!r}")

    outer_points = 0
    xs: list[float] = []
    ys: list[float] = []
    for polygon in polygons:
        if not polygon:
            continue
        outer = polygon[0]
        if outer and outer[0] != outer[-1]:
            outer = [*outer, outer[0]]
        outer_points += len(outer)
        for x, y, *_ in outer:
            xs.append(float(x))
            ys.append(float(y))
    if not xs or not ys:
        raise ValueError("geometry has no outer-ring points")
    return wkt, outer_points, [min(xs), max(xs), min(ys), max(ys)]


def _write_wkt(features: list[dict[str, Any]], path: pathlib.Path) -> dict[str, Any]:
    lines: list[str] = []
    point_count = 0
    bounds: list[float] | None = None
    geometry_types: dict[str, int] = {}
    object_ids: list[int] = []
    names: list[str] = []
    for feature in features:
        geometry = feature["geometry"]
        geom_type = str(geometry.get("type"))
        geometry_types[geom_type] = geometry_types.get(geom_type, 0) + 1
        wkt, outer_points, feature_bounds = _geometry_to_wkt(geometry)
        lines.append(wkt)
        point_count += outer_points
        if bounds is None:
            bounds = feature_bounds
        else:
            bounds = [
                min(bounds[0], feature_bounds[0]),
                max(bounds[1], feature_bounds[1]),
                min(bounds[2], feature_bounds[2]),
                max(bounds[3], feature_bounds[3]),
            ]
        properties = feature.get("properties") or {}
        object_id = properties.get("OBJECTID")
        if object_id is not None:
            object_ids.append(int(object_id))
        for key in ("NAME", "ZIP_CODE", "PO_NAME"):
            if key in properties:
                names.append(str(properties[key]))
                break

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    data = path.read_bytes()
    return {
        "path": str(path),
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "feature_count": len(features),
        "outer_ring_point_count_author_loader_estimate": point_count,
        "geometry_types": geometry_types,
        "object_ids": object_ids,
        "sample_names": names,
        "bbox": bounds,
        "line_count": len(lines),
    }


def build(output_dir: pathlib.Path, *, county_count: int, zipcode_count: int) -> dict[str, Any]:
    started = time.perf_counter()
    county_payload = _fetch_geojson(COUNTY_SERVICE, count=county_count)
    zip_payload = _fetch_geojson(ZIP_SERVICE, count=zipcode_count)
    county_wkt = output_dir / "dtl_cnty_arcgis_bounded.wkt"
    zip_wkt = output_dir / "uszipcode_arcgis_bounded.wkt"
    county_meta = _write_wkt(county_payload["features"], county_wkt)
    zip_meta = _write_wkt(zip_payload["features"], zip_wkt)
    manifest = {
        "schema": "rtdl.paper_reproduction.xhd.goal5303.arcgis_county_zcta_bounded_fixture.v1",
        "goal": "Goal5303",
        "status": "arcgis_county_zcta_bounded_fixture_ready__level_b_only__not_exact_paper_input",
        "created_sec": time.perf_counter() - started,
        "source_contract": {
            "source_family": "ArcGIS name-matched services already tracked by RTDL RayJoin assets",
            "county_service": COUNTY_SERVICE,
            "zipcode_service": ZIP_SERVICE,
            "query_order": "OBJECTID",
            "out_sr": 4326,
            "county_feature_count_requested": county_count,
            "zipcode_feature_count_requested": zipcode_count,
        },
        "author_loader_contract": {
            "input_type": "wkt",
            "n_dims": 2,
            "normalize": False,
            "one_geometry_per_line": True,
            "polygon_outer_ring_only_for_author_point_count": True,
        },
        "outputs": {
            "county": county_meta,
            "zipcode": zip_meta,
        },
        "comparison_readiness": {
            "author_hd_exec_ready": False,
            "rtdl_route_ready": False,
            "reason": "This goal creates a bounded input fixture and metadata only; author/RTDL execution should be a separate gate.",
            "first_author_command_shape": "./bin/hd_exec -input1 <county_wkt> -input2 <zipcode_wkt> -input_type wkt -n_dims 2 -variant rt -execution gpu -normalize=false -json <summary.json>",
        },
        "claim_boundary": {
            "level_b_same_source_fixture": True,
            "exact_paper_dataset_reproduction_claimed": False,
            "geo_correctness_claimed": False,
            "figure5_reproduction_claimed": False,
            "performance_ratio_claimed": False,
        },
    }
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="Paper-reproduction-apps/x-hd-paper/data/generated/goal5303_arcgis_county_zcta_bounded",
    )
    parser.add_argument("--county-count", type=int, default=3)
    parser.add_argument("--zipcode-count", type=int, default=5)
    args = parser.parse_args()
    if args.county_count <= 0 or args.zipcode_count <= 0:
        raise SystemExit("feature counts must be positive")
    manifest = build(pathlib.Path(args.output_dir), county_count=args.county_count, zipcode_count=args.zipcode_count)
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
