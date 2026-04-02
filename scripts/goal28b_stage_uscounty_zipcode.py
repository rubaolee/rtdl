#!/usr/bin/env python3
from __future__ import annotations

import argparse
import gzip
import json
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request
from urllib.request import urlopen

import rtdsl as rt


USER_AGENT = "RTDL Goal28B ArcGIS Stager/1.0"


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
    page_size: int,
    sleep_sec: float,
    use_gzip: bool,
    response_format: str,
) -> dict[str, Any]:
    asset_root = output_dir / asset.asset_id
    asset_root.mkdir(parents=True, exist_ok=True)

    meta_url = f"{rt.build_arcgis_layer_url(asset.service_url, asset.layer_id)}?f=json"
    count_url = (
        f"{rt.build_arcgis_layer_url(asset.service_url, asset.layer_id)}"
        "/query?where=1%3D1&returnCountOnly=true&f=json"
    )
    meta = fetch_json(meta_url)
    count_payload = fetch_json(count_url)

    (asset_root / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    (asset_root / "count.json").write_text(json.dumps(count_payload, indent=2, sort_keys=True), encoding="utf-8")

    total = int(count_payload["count"])
    pages: list[dict[str, Any]] = []
    downloaded = 0
    for offset in range(0, total, page_size):
        query_url = rt.build_arcgis_query_url(
            asset.service_url,
            asset.layer_id,
            offset=offset,
            record_count=min(page_size, total - offset),
            response_format=response_format,
        )
        try:
            payload = fetch_bytes(query_url)
        except HTTPError as error:
            raise RuntimeError(f"{asset.asset_id} page fetch failed at offset={offset}: {error}") from error
        suffix = "geojson" if response_format == "geojson" else "json"
        page_name = f"page_{offset:06d}.{suffix}"
        page_path = write_bytes(asset_root / page_name, payload, use_gzip=use_gzip)
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
            f"[goal28b] {asset.asset_id} offset={offset} requested={min(page_size, total - offset)} downloaded={feature_count}",
            flush=True,
        )
        if sleep_sec > 0:
            time.sleep(sleep_sec)

    asset_manifest = {
        "asset_id": asset.asset_id,
        "title": asset.title,
        "service_url": asset.service_url,
        "layer_id": asset.layer_id,
        "geometry_type": meta.get("geometryType", asset.geometry_type),
        "max_record_count": meta.get("maxRecordCount", asset.max_record_count),
        "expected_feature_count": total,
        "downloaded_feature_count": downloaded,
        "pages": pages,
        "status": "complete" if downloaded == total else "partial",
        "response_format": response_format,
        "output_root": str(asset_root),
    }
    (asset_root / "manifest.json").write_text(json.dumps(asset_manifest, indent=2, sort_keys=True), encoding="utf-8")
    return asset_manifest


def render_summary(manifest: dict[str, Any]) -> str:
    lines = [
        "# Goal 28B County/Zipcode Linux Staging Summary",
        "",
        f"Generated UTC epoch: `{manifest['generated_epoch']}`",
        f"Host label: `{manifest['host_label']}`",
        "",
        "| Asset | Expected Features | Downloaded Features | Pages | Status | Output Root |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for asset in manifest["assets"]:
        lines.append(
            f"| `{asset['asset_id']}` | `{asset['expected_feature_count']}` | "
            f"`{asset['downloaded_feature_count']}` | `{len(asset['pages'])}` | "
            f"`{asset['status']}` | `{asset['output_root']}` |"
        )
    lines.extend(
        [
            "",
            "Boundary note:",
            "",
            "- This script stages raw paginated FeatureServer exports from the live ArcGIS layers.",
            "- The current Linux run uses `f=json` because it is materially smaller than `f=geojson` on the host network path.",
            "- It does not yet convert those files into RayJoin-compatible CDB inputs.",
            "- The first exact-input Linux slice therefore closes raw-source acquisition/staging, not full RayJoin-format execution.",
            "",
        ]
    )
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage USCounty/Zipcode ArcGIS FeatureServer data for Goal 28B.")
    parser.add_argument("--output-dir", required=True, help="Directory where staged pages and manifests are written.")
    parser.add_argument(
        "--assets",
        default="uscounty_feature_layer,zipcode_feature_layer",
        help="Comma-separated asset ids from rayjoin_feature_service_layers().",
    )
    parser.add_argument("--page-size", type=int, default=1000, help="Requested page size for paginated queries.")
    parser.add_argument("--sleep-sec", type=float, default=0.1, help="Optional delay between page fetches.")
    parser.add_argument("--gzip", action="store_true", help="Compress downloaded page files with gzip.")
    parser.add_argument("--host-label", default="unknown", help="Label recorded in the top-level manifest.")
    parser.add_argument(
        "--response-format",
        choices=("json", "geojson"),
        default="json",
        help="FeatureServer response format used for paginated page downloads.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    assets_by_id = {asset.asset_id: asset for asset in rt.rayjoin_feature_service_layers()}
    selected_assets: list[rt.RayJoinFeatureServiceLayer] = []
    for asset_id in [part.strip() for part in args.assets.split(",") if part.strip()]:
        asset = assets_by_id.get(asset_id)
        if asset is None:
            raise SystemExit(f"unknown asset id: {asset_id}")
        selected_assets.append(asset)

    manifests = [
        stage_asset(
            asset,
            output_dir=output_dir,
            page_size=args.page_size,
            sleep_sec=args.sleep_sec,
            use_gzip=args.gzip,
            response_format=args.response_format,
        )
        for asset in selected_assets
    ]
    top_manifest = {
        "host_label": args.host_label,
        "generated_epoch": int(time.time()),
        "assets": manifests,
    }
    (output_dir / "goal28b_staging_manifest.json").write_text(
        json.dumps(top_manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "goal28b_staging_summary.md").write_text(render_summary(top_manifest), encoding="utf-8")
    print(json.dumps(top_manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
