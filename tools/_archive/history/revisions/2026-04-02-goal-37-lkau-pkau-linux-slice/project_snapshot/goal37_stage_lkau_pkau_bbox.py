#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request
from urllib.request import urlopen


DEFAULT_ENDPOINT = "https://overpass.kumi.systems/api/interpreter"
USER_AGENT = "RTDL Goal37 Overpass Stager/1.0"


def fetch_overpass_json(endpoint: str, query: str) -> dict[str, Any]:
    data = urlencode({"data": query}).encode()
    request = Request(endpoint, data=data, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=180) as response:
        return json.load(response)


def parks_query(bbox: str) -> str:
    return (
        "[out:json][timeout:120];"
        f"(way[\"leisure\"=\"park\"]({bbox});way[\"boundary\"=\"national_park\"]({bbox}););"
        "out geom;"
    )


def lakes_query(bbox: str) -> str:
    return f"[out:json][timeout:120];(way[\"natural\"=\"water\"]({bbox}););out geom;"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stage bounded Australia lakes/parks Overpass data for Goal 37.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--bbox", required=True, help="south,west,north,east")
    parser.add_argument("--bbox-label", default="custom")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--host-label", default="unknown")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    payloads = {}
    for asset_id, query_fn in {
        "parks": parks_query,
        "lakes": lakes_query,
    }.items():
        payload = fetch_overpass_json(args.endpoint, query_fn(args.bbox))
        payloads[asset_id] = payload
        (output_dir / f"{asset_id}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )

    manifest = {
        "host_label": args.host_label,
        "bbox_label": args.bbox_label,
        "bbox": args.bbox,
        "endpoint": args.endpoint,
        "generated_epoch": int(time.time()),
        "parks_element_count": len(payloads["parks"].get("elements", ())),
        "lakes_element_count": len(payloads["lakes"].get("elements", ())),
        "parks_path": str(output_dir / "parks.json"),
        "lakes_path": str(output_dir / "lakes.json"),
    }
    (output_dir / "goal37_staging_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
