#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import time
from pathlib import Path
from typing import Any
from urllib.request import Request
from urllib.request import urlopen

import rtdsl as rt


USER_AGENT = "RTDL Goal35 ArcGIS BBox Stager/1.0"


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response:
        return json.load(response)


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=120) as response:
        return response.read()


def write_bytes(destination: Path, payload: bytes, *, use_gzip: bool) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if use_gzip:
        gz_path = destination.with_suffix(destination.suffix + ".gz")
        with gzip.open(gz_path, "wb") as handle:
            handle.write(payload)
        return gz_path
    destination.write_bytes(payload)
    return destination


def stage_asset(
    asset: rt.RayJoinFeatureServiceLayer,
    *,
    output_dir: Path,
    bbox: str,
    page_size: int,
    use_gzip: bool,
    response_format: str,
    sleep_sec: float,
) -> dict[str, Any]:
    asset_root = output_dir / asset.asset_id
    asset_root.mkdir(parents=True, exist_ok=True)

    meta_url = f"{rt.build_arcgis_layer_url(asset.service_url, asset.layer_id)}?f=json"
    count_url = rt.build_arcgis_query_url(
        asset.service_url,
        asset.layer_id,
        offset=0,
        record_count=1,
        response_format="json",
        geometry=bbox,
        geometry_type="esriGeometryEnvelope",
        in_sr=4326,
        spatial_rel="esriSpatialRelIntersects",
        return_count_only=True,
    )

    meta = fetch_json(meta_url)
    count_payload = fetch_json(count_url)
    total = int(count_payload["count"])

    (asset_root / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    (asset_root / "count.json").write_text(json.dumps(count_payload, indent=2, sort_keys=True), encoding="utf-8")

    pages = []
    downloaded = 0
    for offset in range(0, total, page_size):
        suffix = "geojson" if response_format == "geojson" else "json"
        raw_path = asset_root / f"page_{offset:06d}.{suffix}"
        query_url = rt.build_arcgis_query_url(
            asset.service_url,
            asset.layer_id,
            offset=offset,
            record_count=min(page_size, total - offset),
            response_format=response_format,
            geometry=bbox,
            geometry_type="esriGeometryEnvelope",
            in_sr=4326,
            spatial_rel="esriSpatialRelIntersects",
        )
        payload = fetch_bytes(query_url)
        page_path = write_bytes(raw_path, payload, use_gzip=use_gzip)
        decoded = json.loads(payload.decode("utf-8"))
        feature_count = len(decoded.get("features", ()))
        downloaded += feature_count
        pages.append(
            {
                "offset": offset,
                "requested": min(page_size, total - offset),
                "downloaded": feature_count,
                "path": str(page_path),
            }
        )
        print(
            f"[goal35] {asset.asset_id} bbox={bbox} offset={offset} requested={min(page_size, total - offset)} downloaded={feature_count}",
            flush=True,
        )
        if sleep_sec > 0:
            time.sleep(sleep_sec)

    manifest = {
        "asset_id": asset.asset_id,
        "title": asset.title,
        "service_url": asset.service_url,
        "layer_id": asset.layer_id,
        "bbox": bbox,
        "expected_feature_count": total,
        "downloaded_feature_count": downloaded,
        "pages": pages,
        "status": "complete" if downloaded == total else "partial",
        "output_root": str(asset_root),
    }
    (asset_root / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def render_summary(manifest: dict[str, Any]) -> str:
    lines = [
        "# Goal 35 BlockGroup/WaterBodies BBox Staging Summary",
        "",
        f"Host label: `{manifest['host_label']}`",
        f"BBox label: `{manifest['bbox_label']}`",
        f"BBox: `{manifest['bbox']}`",
        "",
        "| Asset | Expected Features | Downloaded Features | Pages | Status |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for asset in manifest["assets"]:
        lines.append(
            f"| `{asset['asset_id']}` | `{asset['expected_feature_count']}` | `{asset['downloaded_feature_count']}` | `{len(asset['pages'])}` | `{asset['status']}` |"
        )
    return "\n".join(lines) + "\n"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage BlockGroup/WaterBodies ArcGIS bbox slices for Goal 35.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bbox", required=True, help="xmin,ymin,xmax,ymax")
    parser.add_argument("--bbox-label", default="custom")
    parser.add_argument("--assets", default="blockgroup_feature_layer,waterbodies_feature_layer")
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--sleep-sec", type=float, default=0.1)
    parser.add_argument("--gzip", action="store_true")
    parser.add_argument("--response-format", choices=("json",), default="json")
    parser.add_argument("--host-label", default="unknown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    assets_by_id = {asset.asset_id: asset for asset in rt.rayjoin_feature_service_layers()}
    assets = []
    for asset_id in [part.strip() for part in args.assets.split(",") if part.strip()]:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise SystemExit(f"unknown asset id: {asset_id}")
        assets.append(asset)

    manifests = [
        stage_asset(
            asset,
            output_dir=output_dir,
            bbox=args.bbox,
            page_size=args.page_size,
            use_gzip=args.gzip,
            response_format=args.response_format,
            sleep_sec=args.sleep_sec,
        )
        for asset in assets
    ]
    top_manifest = {
        "host_label": args.host_label,
        "bbox_label": args.bbox_label,
        "bbox": args.bbox,
        "generated_epoch": int(time.time()),
        "assets": manifests,
    }
    (output_dir / "goal35_staging_manifest.json").write_text(json.dumps(top_manifest, indent=2, sort_keys=True), encoding="utf-8")
    (output_dir / "goal35_staging_summary.md").write_text(render_summary(top_manifest), encoding="utf-8")
    print(json.dumps(top_manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
