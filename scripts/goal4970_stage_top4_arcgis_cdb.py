#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import json
import time
from pathlib import Path
from urllib.request import Request
from urllib.request import urlopen

import rtdsl as rt


TOP4_STATES = ("TX", "CA", "NY", "PA")
USER_AGENT = "RTDL Goal4970 Section57 Top4/1.0"


def _fetch_json(url: str) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=240) as response:
        return json.load(response)


def _fetch_bytes_retry(url: str, *, attempts: int = 5) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            request = Request(url, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=240) as response:
                return response.read()
        except (http.client.IncompleteRead, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(2.0 * attempt)
    assert last_error is not None
    raise last_error


def _render_state_where(field_name: str, states: tuple[str, ...]) -> str:
    quoted = ", ".join(f"'{state}'" for state in states)
    return f"{field_name} IN ({quoted})"


def _manifest_complete(output_dir: Path, *, asset_id: str, where: str) -> dict[str, object] | None:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if manifest.get("asset_id") != asset_id:
        return None
    if manifest.get("where") != where:
        return None
    if int(manifest.get("downloaded_feature_count", -1)) != int(
        manifest.get("expected_feature_count", -2)
    ):
        return None
    for raw_path in manifest.get("page_paths", ()):
        if not Path(raw_path).exists():
            return None
    return manifest


def _stage_asset(
    asset: rt.RayJoinFeatureServiceLayer,
    *,
    output_dir: Path,
    where: str,
    page_size: int,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing = _manifest_complete(output_dir, asset_id=asset.asset_id, where=where)
    if existing is not None:
        print(f"[stage] reuse {asset.asset_id}: {existing['downloaded_feature_count']}", flush=True)
        return existing

    meta_url = f"{rt.build_arcgis_layer_url(asset.service_url, asset.layer_id)}?f=json"
    (output_dir / "meta.json").write_text(
        json.dumps(_fetch_json(meta_url), indent=2, sort_keys=True),
        encoding="utf-8",
    )

    count_url = rt.build_arcgis_query_url(
        asset.service_url,
        asset.layer_id,
        offset=0,
        record_count=1,
        response_format="json",
        where=where,
        return_count_only=True,
    )
    count_payload = _fetch_json(count_url)
    total = int(count_payload["count"])
    (output_dir / "count.json").write_text(
        json.dumps(count_payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    print(f"[stage] start {asset.asset_id}: total={total} where={where}", flush=True)
    page_paths: list[str] = []
    downloaded = 0
    for offset in range(0, total, page_size):
        page_path = output_dir / f"page_{offset:06d}.json"
        if page_path.exists():
            payload = page_path.read_bytes()
        else:
            url = rt.build_arcgis_query_url(
                asset.service_url,
                asset.layer_id,
                offset=offset,
                record_count=min(page_size, total - offset),
                response_format="json",
                where=where,
            )
            payload = _fetch_bytes_retry(url)
            page_path.write_bytes(payload)
        decoded = json.loads(payload.decode("utf-8"))
        count = len(decoded.get("features", ()))
        downloaded += count
        page_paths.append(str(page_path.resolve()))
        print(
            f"[stage] {asset.asset_id} offset={offset} rows={count} "
            f"downloaded={downloaded}/{total}",
            flush=True,
        )

    manifest = {
        "asset_id": asset.asset_id,
        "where": where,
        "expected_feature_count": total,
        "downloaded_feature_count": downloaded,
        "page_count": len(page_paths),
        "page_paths": page_paths,
    }
    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return manifest


def _edge_count(dataset: rt.CdbDataset) -> int:
    return sum(max(0, chain.point_count - 1) for chain in dataset.chains)


def _point_count(dataset: rt.CdbDataset) -> int:
    return sum(chain.point_count for chain in dataset.chains)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--page-size", type=int, default=1000)
    parser.add_argument("--host-label", default="unknown")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    county_layer = next(
        asset for asset in rt.rayjoin_feature_service_layers() if asset.asset_id == "uscounty_feature_layer"
    )
    zipcode_layer = next(
        asset for asset in rt.rayjoin_feature_service_layers() if asset.asset_id == "zipcode_feature_layer"
    )

    county_stage = _stage_asset(
        county_layer,
        output_dir=output_dir / "county",
        where=_render_state_where("STATE_ABBR", TOP4_STATES),
        page_size=args.page_size,
    )
    zipcode_stage = _stage_asset(
        zipcode_layer,
        output_dir=output_dir / "zipcode",
        where=_render_state_where("STATE", TOP4_STATES),
        page_size=args.page_size,
    )

    print("[convert] county", flush=True)
    county = rt.arcgis_pages_to_cdb(output_dir / "county", name="top4_county", ignore_invalid_tail=True)
    county_path = rt.write_cdb(county, output_dir / "top4_county.cdb")

    print("[convert] zipcode", flush=True)
    zipcode = rt.arcgis_pages_to_cdb(output_dir / "zipcode", name="top4_zipcode", ignore_invalid_tail=True)
    zipcode_path = rt.write_cdb(zipcode, output_dir / "top4_zipcode.cdb")

    summary = {
        "schema": "rtdl.paper_reproduction.rayjoin.goal4970_top4_arcgis_cdb.v1",
        "host_label": args.host_label,
        "states": list(TOP4_STATES),
        "county_stage": county_stage,
        "zipcode_stage": zipcode_stage,
        "county": {
            "path": str(Path(county_path).resolve()),
            "features": len(county.face_ids()),
            "chains": len(county.chains),
            "points": _point_count(county),
            "edges": _edge_count(county),
            "bytes": Path(county_path).stat().st_size,
        },
        "zipcode": {
            "path": str(Path(zipcode_path).resolve()),
            "features": len(zipcode.face_ids()),
            "chains": len(zipcode.chains),
            "points": _point_count(zipcode),
            "edges": _edge_count(zipcode),
            "bytes": Path(zipcode_path).stat().st_size,
        },
    }
    (output_dir / "goal4970_top4_cdb_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
