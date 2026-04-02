#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import json
import time
from pathlib import Path
from typing import Any
from urllib.request import Request
from urllib.request import urlopen

import rtdsl as rt
from examples.rtdl_language_reference import county_zip_join_reference
from examples.rtdl_language_reference import point_in_counties_reference


USER_AGENT = "RTDL Goal38 State Feasibility/1.0"
COUNTY_LAYER = next(
    asset for asset in rt.rayjoin_feature_service_layers() if asset.asset_id == "uscounty_feature_layer"
)
ZIPCODE_LAYER = next(
    asset for asset in rt.rayjoin_feature_service_layers() if asset.asset_id == "zipcode_feature_layer"
)

FROZEN_STATE_GROUPS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("top1_tx", ("TX",)),
    ("top2_tx_ca", ("TX", "CA")),
    ("top4_tx_ca_ny_pa", ("TX", "CA", "NY", "PA")),
    ("top8_tx_ca_ny_pa_il_oh_mo_ia", ("TX", "CA", "NY", "PA", "IL", "OH", "MO", "IA")),
    (
        "nationwide",
        (
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
            "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
            "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
            "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC",
        ),
    ),
)


def fetch_json(url: str) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=180) as response:
        return json.load(response)


def fetch_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=180) as response:
        return response.read()


def fetch_bytes_with_retry(url: str, *, attempts: int = 4, sleep_sec: float = 2.0) -> bytes:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return fetch_bytes(url)
        except (http.client.IncompleteRead, TimeoutError, OSError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == attempts:
                break
            time.sleep(sleep_sec * attempt)
    assert last_error is not None
    raise last_error


def render_state_where(field_name: str, states: tuple[str, ...]) -> str:
    quoted = ", ".join(f"'{state}'" for state in states)
    return f"{field_name} IN ({quoted})"


def load_manifest_if_complete(
    output_dir: Path,
    *,
    asset_id: str,
    where: str,
) -> dict[str, object] | None:
    manifest_path = output_dir / "manifest.json"
    if not manifest_path.exists():
        return None
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    expected = int(manifest.get("expected_feature_count", -1))
    downloaded = int(manifest.get("downloaded_feature_count", -2))
    if expected < 0 or downloaded != expected:
        return None
    if manifest.get("asset_id") != asset_id:
        return None
    if manifest.get("where") != where:
        return None
    for raw_path in manifest.get("page_paths", ()):
        if not Path(raw_path).exists():
            return None
    return manifest


def stage_asset_for_states(
    asset: rt.RayJoinFeatureServiceLayer,
    *,
    output_dir: Path,
    where: str,
    page_size: int,
) -> dict[str, object]:
    output_dir.mkdir(parents=True, exist_ok=True)
    existing_manifest = load_manifest_if_complete(output_dir, asset_id=asset.asset_id, where=where)
    if existing_manifest is not None:
        return existing_manifest

    meta_url = f"{rt.build_arcgis_layer_url(asset.service_url, asset.layer_id)}?f=json"
    meta = fetch_json(meta_url)
    (output_dir / "meta.json").write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")

    count_url = rt.build_arcgis_query_url(
        asset.service_url,
        asset.layer_id,
        offset=0,
        record_count=1,
        response_format="json",
        where=where,
        return_count_only=True,
    )
    count_payload = fetch_json(count_url)
    total = int(count_payload["count"])
    (output_dir / "count.json").write_text(json.dumps(count_payload, indent=2, sort_keys=True), encoding="utf-8")

    page_paths: list[str] = []
    downloaded = 0
    for offset in range(0, total, page_size):
        page_url = rt.build_arcgis_query_url(
            asset.service_url,
            asset.layer_id,
            offset=offset,
            record_count=min(page_size, total - offset),
            response_format="json",
            where=where,
        )
        payload = fetch_bytes_with_retry(page_url)
        page_path = output_dir / f"page_{offset:06d}.json"
        page_path.write_bytes(payload)
        decoded = json.loads(payload.decode("utf-8"))
        downloaded += len(decoded.get("features", ()))
        page_paths.append(str(page_path))

    manifest = {
        "asset_id": asset.asset_id,
        "where": where,
        "expected_feature_count": total,
        "downloaded_feature_count": downloaded,
        "page_count": len(page_paths),
        "page_paths": page_paths,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


def chain_segment_count(dataset: rt.CdbDataset) -> int:
    return sum(max(0, chain.point_count - 1) for chain in dataset.chains)


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    end = time.perf_counter()
    return result, end - start


def summarize_lsi(cpu_rows, embree_rows, cpu_sec: float | None, embree_sec: float) -> dict[str, object]:
    embree_pairs = sorted((int(row["left_id"]), int(row["right_id"])) for row in embree_rows)
    payload = {
        "embree_row_count": len(embree_rows),
        "embree_sec": embree_sec,
        "sample_embree_pairs": embree_pairs[:10],
        "cpu_row_count": None if cpu_rows is None else len(cpu_rows),
        "cpu_sec": cpu_sec,
        "pair_parity": None if cpu_rows is None else (
            sorted((int(row["left_id"]), int(row["right_id"])) for row in cpu_rows) == embree_pairs
        ),
        "sample_cpu_pairs": [] if cpu_rows is None else sorted(
            (int(row["left_id"]), int(row["right_id"])) for row in cpu_rows
        )[:10],
    }
    return payload


def summarize_pip(cpu_rows, embree_rows, cpu_sec: float | None, embree_sec: float) -> dict[str, object]:
    embree_triplets = sorted(
        (int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in embree_rows
    )
    payload = {
        "embree_row_count": len(embree_rows),
        "embree_sec": embree_sec,
        "sample_embree_rows": embree_triplets[:10],
        "cpu_row_count": None if cpu_rows is None else len(cpu_rows),
        "cpu_sec": cpu_sec,
        "row_parity": None if cpu_rows is None else (
            sorted((int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in cpu_rows) == embree_triplets
        ),
        "sample_cpu_rows": [] if cpu_rows is None else sorted(
            (int(row["point_id"]), int(row["polygon_id"]), int(row["contains"])) for row in cpu_rows
        )[:10],
    }
    return payload


def render_markdown(summary: dict[str, object]) -> str:
    lines = [
        "# Goal 38 Large-Scale Embree Feasibility",
        "",
        f"Host label: `{summary['host_label']}`",
        f"Validation mode: `{summary['validation_mode']}`",
        "",
        "| Label | States | County Features | Zipcode Features | County Chains | Zipcode Chains | County Segments | Zipcode Segments | Validation | LSI Embree (s) | PIP Embree (s) |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: | ---: |",
    ]
    for point in summary["points"]:
        lines.append(
            "| `{label}` | `{states}` | `{county_features}` | `{zipcode_features}` | `{county_chains}` | `{zipcode_chains}` | `{county_segments}` | `{zipcode_segments}` | `{validation_mode}` | `{lsi_embree:.6f}` | `{pip_embree:.6f}` |".format(
                label=point["label"],
                states=",".join(point["states"]),
                county_features=point["county"]["feature_count"],
                zipcode_features=point["zipcode"]["feature_count"],
                county_chains=point["county"]["chain_count"],
                zipcode_chains=point["zipcode"]["chain_count"],
                county_segments=point["county"]["segment_count"],
                zipcode_segments=point["zipcode"]["segment_count"],
                validation_mode=point["validation_mode"],
                lsi_embree=point["lsi"]["embree_sec"],
                pip_embree=point["pip"]["embree_sec"],
            )
        )

    lines.extend(
        [
            "",
            "## Boundary",
            "",
            "- this is a state-filtered exact-source feasibility ladder, not yet a final nationwide reproduction claim",
            "- the main large-scale benchmark path is Embree-only",
            "- Python simulator timings are intentionally excluded from the primary large-scale results",
            "- if larger-scale correctness validation is needed later, it should come from a separate native checker or a bounded validation slice",
            "",
        ]
    )
    return "\n".join(lines)


def write_summary(output_dir: Path, summary: dict[str, object]) -> None:
    (output_dir / "goal38_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    (output_dir / "goal38_summary.md").write_text(render_markdown(summary), encoding="utf-8")


def load_existing_summary(output_dir: Path, *, host_label: str, validation_mode: str) -> dict[str, Any]:
    summary_path = output_dir / "goal38_summary.json"
    if not summary_path.exists():
        return {
            "host_label": host_label,
            "validation_mode": validation_mode,
            "points": [],
        }
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if summary.get("host_label") != host_label or summary.get("validation_mode") != validation_mode:
        raise ValueError("existing Goal 38 summary does not match current host/validation mode")
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Goal 38 large-scale County/Zipcode Embree feasibility ladder.")
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--host-label", default="unknown")
    parser.add_argument("--page-size", type=int, default=500)
    parser.add_argument("--validation-mode", choices=("embree-only",), default="embree-only")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = load_existing_summary(
        output_dir,
        host_label=args.host_label,
        validation_mode=args.validation_mode,
    )
    points: list[dict[str, object]] = list(summary["points"])
    completed_labels = {point["label"] for point in points}
    for label, states in FROZEN_STATE_GROUPS:
        if label in completed_labels:
            continue
        state_dir = output_dir / label
        county_where = render_state_where("STATE_ABBR", states)
        zipcode_where = render_state_where("STATE", states)

        county_stage = stage_asset_for_states(
            COUNTY_LAYER,
            output_dir=state_dir / "county",
            where=county_where,
            page_size=args.page_size,
        )
        zipcode_stage = stage_asset_for_states(
            ZIPCODE_LAYER,
            output_dir=state_dir / "zipcode",
            where=zipcode_where,
            page_size=args.page_size,
        )

        county, county_convert_sec = time_call(
            rt.arcgis_pages_to_cdb,
            state_dir / "county",
            name=f"{label}_county",
            ignore_invalid_tail=True,
        )
        zipcode, zipcode_convert_sec = time_call(
            rt.arcgis_pages_to_cdb,
            state_dir / "zipcode",
            name=f"{label}_zipcode",
            ignore_invalid_tail=True,
        )

        county_segments = rt.chains_to_segments(county)
        zipcode_segments = rt.chains_to_segments(zipcode)
        county_polygons = rt.chains_to_polygons(county)
        zipcode_points = rt.chains_to_probe_points(zipcode)

        lsi_cpu_rows = None
        lsi_cpu_sec = None
        pip_cpu_rows = None
        pip_cpu_sec = None

        lsi_embree_rows, lsi_embree_sec = time_call(
            rt.run_embree,
            county_zip_join_reference,
            left=zipcode_segments,
            right=county_segments,
        )
        pip_embree_rows, pip_embree_sec = time_call(
            rt.run_embree,
            point_in_counties_reference,
            points=zipcode_points,
            polygons=county_polygons,
        )

        point = {
            "label": label,
            "states": states,
            "validation_mode": args.validation_mode,
            "county_stage": county_stage,
            "zipcode_stage": zipcode_stage,
            "county": {
                "feature_count": len(county.face_ids()),
                "chain_count": len(county.chains),
                "segment_count": chain_segment_count(county),
                "convert_sec": county_convert_sec,
            },
            "zipcode": {
                "feature_count": len(zipcode.face_ids()),
                "chain_count": len(zipcode.chains),
                "segment_count": chain_segment_count(zipcode),
                "convert_sec": zipcode_convert_sec,
            },
            "lsi": summarize_lsi(lsi_cpu_rows, lsi_embree_rows, lsi_cpu_sec, lsi_embree_sec),
            "pip": summarize_pip(pip_cpu_rows, pip_embree_rows, pip_cpu_sec, pip_embree_sec),
        }
        points.append(point)
        summary["points"] = points
        write_summary(output_dir, summary)

        if point["lsi"]["pair_parity"] is False or point["pip"]["row_parity"] is False:
            break

    summary = {
        "host_label": args.host_label,
        "validation_mode": args.validation_mode,
        "points": points,
    }
    write_summary(output_dir, summary)
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
