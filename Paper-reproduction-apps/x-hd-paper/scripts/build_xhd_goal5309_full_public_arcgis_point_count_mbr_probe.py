#!/usr/bin/env python3
"""Probe full public ArcGIS geo sources for X-HD Figure-5 reconstruction.

This app-owned helper streams ArcGIS FeatureServer pages and computes only the
author-loader point-count / MBR contract. It intentionally does not write full
WKT, does not run author `hd_exec`, and does not run RTDL. The purpose is to
decide whether a full-public reconstruction is even close enough to the paper
logs to justify the much heavier Figure-5 execution work.
"""

from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


@dataclass(frozen=True)
class ServiceSpec:
    key: str
    paper_basename: str
    service_url: str
    max_record_count: int
    paper_point_count: int
    paper_mbr: tuple[tuple[float, float], tuple[float, float]]


SERVICES: tuple[ServiceSpec, ...] = (
    ServiceSpec(
        key="county",
        paper_basename="dtl_cnty.wkt",
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_Counties/FeatureServer",
        max_record_count=2000,
        paper_point_count=9_438_045,
        paper_mbr=((-179.14891052246094, -66.9496078491211), (18.91069221496582, 71.36516571044922)),
    ),
    ServiceSpec(
        key="zcta",
        paper_basename="uszipcode.wkt",
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_ZIP_Code_Areas_anaylsis/FeatureServer",
        max_record_count=2000,
        paper_point_count=43_952_878,
        paper_mbr=((-179.1473388671875, 179.77845764160156), (-14.548691749572754, 71.3904800415039)),
    ),
    ServiceSpec(
        key="waterbodies",
        paper_basename="USADetailedWaterBodies.wkt",
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Detailed_Water_Bodies/FeatureServer",
        max_record_count=1000,
        paper_point_count=22_818_694,
        paper_mbr=((-160.23110961914062, -66.99786376953125), (19.203998565673828, 49.384334564208984)),
    ),
    ServiceSpec(
        key="blockgroups",
        paper_basename="USACensusBlockGroupBoundaries.wkt",
        service_url="https://services.arcgis.com/P3ePLMYs2RVChkJx/arcgis/rest/services/USA_Census_BlockGroups/FeatureServer",
        max_record_count=2000,
        paper_point_count=52_271_340,
        paper_mbr=((-179.14891052246094, -66.9496078491211), (18.91069221496582, 71.36516571044922)),
    ),
)


def _query(service_url: str, params: dict[str, object], *, timeout: int) -> dict[str, Any]:
    url = f"{service_url.rstrip('/')}/0/query?{urlencode(params)}"
    last_error: BaseException | None = None
    for attempt in range(5):
        try:
            with urlopen(url, timeout=timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            last_error = exc
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 4:
                raise
        except (TimeoutError, URLError) as exc:
            last_error = exc
            if attempt == 4:
                raise
        time.sleep(min(30.0, 2.0 ** attempt))
    raise RuntimeError(f"ArcGIS query failed after retries: {last_error!r}")


def _feature_count(spec: ServiceSpec, *, timeout: int) -> int:
    payload = _query(
        spec.service_url,
        {
            "where": "1=1",
            "returnCountOnly": "true",
            "f": "json",
        },
        timeout=timeout,
    )
    count = payload.get("count")
    if not isinstance(count, int):
        raise RuntimeError(f"count query failed for {spec.key}: {payload!r}")
    return count


def _geometry_author_sequences(geometry: dict[str, Any]) -> Iterable[tuple[list[list[float]], bool]]:
    """Yield coordinate sequences with the author WKT-loader closure contract.

    Polygon outer rings are closed by WKT semantics when not already closed.
    Lines and points are not closed. The Figure-5 geo services under test are
    polygonal, but keeping this distinction explicit prevents a silent count
    error if a future full-public source contains linear features.
    """

    geom_type = geometry.get("type")
    coords = geometry.get("coordinates")
    if geom_type == "Polygon":
        if coords:
            yield coords[0], True
    elif geom_type == "MultiPolygon":
        for polygon in coords or ():
            if polygon:
                yield polygon[0], True
    elif geom_type == "LineString":
        yield coords or [], False
    elif geom_type == "MultiLineString":
        for line in coords or ():
            yield line, False
    elif geom_type == "Point":
        if coords:
            yield [coords], False
    else:
        raise ValueError(f"unsupported geometry type for full-public probe: {geom_type!r}")


def _author_sequence_point_count(sequence: list[list[float]], *, close: bool) -> int:
    if not sequence:
        return 0
    if close and sequence[0] != sequence[-1]:
        return len(sequence) + 1
    return len(sequence)


def _iter_author_points_from_sequence(
    sequence: list[list[float]],
    *,
    close: bool,
) -> Iterable[tuple[float, float]]:
    if not sequence:
        return
    for coord in sequence:
        yield float(coord[0]), float(coord[1])
    if close and sequence[0] != sequence[-1]:
        coord = sequence[0]
        yield float(coord[0]), float(coord[1])


def _empty_accumulator(spec: ServiceSpec, service_count: int) -> dict[str, Any]:
    return {
        "key": spec.key,
        "paper_basename": spec.paper_basename,
        "service_url": spec.service_url,
        "service_feature_count": service_count,
        "features_seen": 0,
        "pages_seen": 0,
        "author_loader_point_count": 0,
        "geometry_types": {},
        "object_id_min": None,
        "object_id_max": None,
        "mbr": None,
        "sample_labels": [],
        "complete": False,
        "resumed_from_checkpoint": False,
        "checkpoint_features_seen_at_start": 0,
    }


def _load_checkpoint_accumulator(
    checkpoint_path: Path,
    spec: ServiceSpec,
    service_count: int,
) -> dict[str, Any] | None:
    if not checkpoint_path.exists():
        return None
    payload = json.loads(checkpoint_path.read_text(encoding="utf-8"))
    if payload.get("key") != spec.key:
        raise RuntimeError(f"checkpoint key mismatch for {spec.key}: {checkpoint_path}")
    features_seen = int(payload.get("features_seen", 0))
    payload["service_feature_count"] = service_count
    payload["features_seen"] = features_seen
    payload["pages_seen"] = int(payload.get("pages_seen", 0))
    payload["author_loader_point_count"] = int(payload.get("author_loader_point_count", 0))
    payload["geometry_types"] = dict(payload.get("geometry_types") or {})
    payload["sample_labels"] = list(payload.get("sample_labels") or [])
    payload["complete"] = features_seen >= service_count
    payload["resumed_from_checkpoint"] = True
    payload["checkpoint_features_seen_at_start"] = features_seen
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f"{path.name}.tmp")
    temp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def _update_mbr(mbr: list[float] | None, x: float, y: float) -> list[float]:
    if mbr is None:
        return [x, x, y, y]
    return [min(mbr[0], x), max(mbr[1], x), min(mbr[2], y), max(mbr[3], y)]


def _label(properties: dict[str, Any]) -> str:
    for key in ("NAME", "ZIP_CODE", "FIPS", "FCODE_DESC", "STATE_ABBR"):
        value = properties.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def _process_feature(acc: dict[str, Any], feature: dict[str, Any]) -> None:
    geometry = feature.get("geometry")
    if not isinstance(geometry, dict):
        raise ValueError("feature has no geometry mapping")
    geom_type = str(geometry.get("type"))
    geometry_types = acc["geometry_types"]
    geometry_types[geom_type] = int(geometry_types.get(geom_type, 0)) + 1
    for sequence, close in _geometry_author_sequences(geometry):
        acc["author_loader_point_count"] += _author_sequence_point_count(sequence, close=close)
        for x, y in _iter_author_points_from_sequence(sequence, close=close):
            acc["mbr"] = _update_mbr(acc["mbr"], x, y)

    properties = feature.get("properties") or {}
    object_id = properties.get("OBJECTID")
    if object_id is not None:
        object_id_i = int(object_id)
        acc["object_id_min"] = object_id_i if acc["object_id_min"] is None else min(acc["object_id_min"], object_id_i)
        acc["object_id_max"] = object_id_i if acc["object_id_max"] is None else max(acc["object_id_max"], object_id_i)
    if len(acc["sample_labels"]) < 8:
        label = _label(properties)
        if label:
            acc["sample_labels"].append(label)


def _mbr_delta(observed: list[float] | None, paper: tuple[tuple[float, float], tuple[float, float]]) -> dict[str, float | None]:
    if observed is None:
        return {"x_lower": None, "x_upper": None, "y_lower": None, "y_upper": None}
    return {
        "x_lower": float(observed[0] - paper[0][0]),
        "x_upper": float(observed[1] - paper[0][1]),
        "y_lower": float(observed[2] - paper[1][0]),
        "y_upper": float(observed[3] - paper[1][1]),
    }


def _finalize_service(acc: dict[str, Any], spec: ServiceSpec) -> dict[str, Any]:
    point_count = int(acc["author_loader_point_count"])
    abs_delta = point_count - int(spec.paper_point_count)
    rel_delta = None if spec.paper_point_count == 0 else abs_delta / float(spec.paper_point_count)
    return {
        **acc,
        "paper_point_count": int(spec.paper_point_count),
        "point_count_delta": int(abs_delta),
        "point_count_relative_delta": rel_delta,
        "paper_mbr": {
            "x": [spec.paper_mbr[0][0], spec.paper_mbr[0][1]],
            "y": [spec.paper_mbr[1][0], spec.paper_mbr[1][1]],
        },
        "mbr_delta": _mbr_delta(acc["mbr"], spec.paper_mbr),
    }


def probe_service(
    spec: ServiceSpec,
    *,
    page_size: int,
    timeout: int,
    max_pages: int | None,
    checkpoint_path: Path | None,
) -> dict[str, Any]:
    service_count = _feature_count(spec, timeout=timeout)
    acc = None
    if checkpoint_path is not None:
        acc = _load_checkpoint_accumulator(checkpoint_path, spec, service_count)
    if acc is None:
        acc = _empty_accumulator(spec, service_count)
    if bool(acc["complete"]):
        return _finalize_service(acc, spec)
    offset = int(acc["features_seen"])
    pages = int(acc["pages_seen"])
    pages_at_start = pages
    while offset < service_count:
        if max_pages is not None and (pages - pages_at_start) >= max_pages:
            break
        params = {
            "where": "1=1",
            "outFields": "*",
            "returnGeometry": "true",
            "resultOffset": offset,
            "resultRecordCount": page_size,
            "orderByFields": "OBJECTID",
            "outSR": 4326,
            "f": "geojson",
        }
        payload = _query(spec.service_url, params, timeout=timeout)
        features = payload.get("features")
        if not isinstance(features, list):
            raise RuntimeError(f"feature query failed for {spec.key} offset {offset}: {payload!r}")
        if not features:
            break
        for feature in features:
            _process_feature(acc, feature)
        offset += len(features)
        pages += 1
        acc["features_seen"] = int(acc["features_seen"]) + len(features)
        acc["pages_seen"] = pages
        acc["complete"] = int(acc["features_seen"]) >= service_count
        if checkpoint_path is not None:
            _write_json_atomic(checkpoint_path, _finalize_service(acc, spec))
        if len(features) < page_size:
            break
    acc["complete"] = int(acc["features_seen"]) >= service_count
    return _finalize_service(acc, spec)


def build_probe(args: argparse.Namespace) -> dict[str, Any]:
    requested = set(args.services)
    specs = [spec for spec in SERVICES if "all" in requested or spec.key in requested]
    started = time.perf_counter()
    results: dict[str, Any] = {}
    for spec in specs:
        service_started = time.perf_counter()
        checkpoint = None
        if args.checkpoint_dir:
            checkpoint = Path(args.checkpoint_dir) / f"{spec.key}.json"
        result = probe_service(
            spec,
            page_size=min(int(args.page_size), spec.max_record_count),
            timeout=int(args.timeout),
            max_pages=args.max_pages,
            checkpoint_path=checkpoint,
        )
        result["elapsed_sec"] = time.perf_counter() - service_started
        results[spec.key] = result
    complete = all(bool(item["complete"]) for item in results.values())
    return {
        "schema": "rtdl.paper_reproduction.xhd.goal5309.full_public_arcgis_point_count_mbr_probe.v1",
        "goal": "Goal5309",
        "status": "full_public_probe_complete" if complete else "full_public_probe_partial",
        "elapsed_sec": time.perf_counter() - started,
        "page_size_requested": int(args.page_size),
        "max_pages": args.max_pages,
        "services": results,
        "claim_boundary": {
            "exact_paper_dataset_reproduction_claimed": False,
            "geo_figure5_reproduction_claimed": False,
            "author_rtdl_correctness_claimed": False,
            "performance_ratio_claimed": False,
            "full_paper_reproduction_claimed": False,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--checkpoint-dir")
    parser.add_argument("--services", nargs="+", default=["all"], choices=[*(spec.key for spec in SERVICES), "all"])
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--max-pages", type=int)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    payload = build_probe(args)
    out = Path(args.output)
    _write_json_atomic(out, payload)
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
