from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.error import URLError
from urllib.request import Request
from urllib.request import urlopen


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from rtdsl.datasets import build_arcgis_layer_url
from rtdsl.datasets import build_arcgis_query_url
from rtdsl.datasets import rayjoin_feature_service_layers
from rtdsl.rayjoin_paper_suite import RAYJOIN_PREPROCESSED_SHARE_URL
from rtdsl.rayjoin_paper_suite import availability_matrix
from rtdsl.rayjoin_paper_suite import paper_pairs
from rtdsl.rayjoin_paper_suite import same_source_arcgis_targets


SCHEMA = "rtdl.goal4806.rayjoin_section57_data_acquisition_audit.v1"


def _fetch_json(url: str, *, timeout: int) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": "RTDL-Goal4806-Audit/1.0"})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
            status = getattr(response, "status", None)
            final_url = response.geturl()
    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "final_url": exc.geturl(),
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - started,
        }
    except (OSError, URLError) as exc:
        return {
            "ok": False,
            "status": None,
            "final_url": url,
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - started,
        }
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {
            "ok": False,
            "status": status,
            "final_url": final_url,
            "error": f"non_json_response: {exc}",
            "elapsed_sec": time.perf_counter() - started,
        }
    if isinstance(payload, dict) and "error" in payload:
        return {
            "ok": False,
            "status": status,
            "final_url": final_url,
            "payload": payload,
            "elapsed_sec": time.perf_counter() - started,
        }
    return {
        "ok": True,
        "status": status,
        "final_url": final_url,
        "payload": payload,
        "elapsed_sec": time.perf_counter() - started,
    }


def _fetch_url_status(url: str, *, timeout: int) -> dict[str, object]:
    request = Request(url, headers={"User-Agent": "RTDL-Goal4806-Audit/1.0"})
    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            status = getattr(response, "status", None)
            final_url = response.geturl()
            content_type = response.headers.get("content-type")
            response.read(256)
    except HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "final_url": exc.geturl(),
            "content_type": exc.headers.get("content-type") if exc.headers else None,
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - started,
        }
    except (OSError, URLError) as exc:
        return {
            "ok": False,
            "status": None,
            "final_url": url,
            "content_type": None,
            "error": str(exc),
            "elapsed_sec": time.perf_counter() - started,
        }
    return {
        "ok": True,
        "status": status,
        "final_url": final_url,
        "content_type": content_type,
        "elapsed_sec": time.perf_counter() - started,
    }


def _arcgis_probe(*, timeout: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for layer in rayjoin_feature_service_layers():
        layer_url = f"{build_arcgis_layer_url(layer.service_url, layer.layer_id)}?f=json"
        count_url = build_arcgis_query_url(
            layer.service_url,
            layer.layer_id,
            offset=0,
            record_count=1,
            response_format="json",
            return_count_only=True,
        )
        meta = _fetch_json(layer_url, timeout=timeout)
        count = _fetch_json(count_url, timeout=timeout)
        observed_count = None
        if count.get("ok") and isinstance(count.get("payload"), dict):
            observed_count = count["payload"].get("count")  # type: ignore[index]
        metadata_payload = meta.get("payload") if isinstance(meta.get("payload"), dict) else {}
        metadata_summary = {
            "name": metadata_payload.get("name") if isinstance(metadata_payload, dict) else None,
            "type": metadata_payload.get("type") if isinstance(metadata_payload, dict) else None,
            "geometryType": metadata_payload.get("geometryType") if isinstance(metadata_payload, dict) else None,
            "maxRecordCount": metadata_payload.get("maxRecordCount") if isinstance(metadata_payload, dict) else None,
            "objectIdField": metadata_payload.get("objectIdField") if isinstance(metadata_payload, dict) else None,
        }
        compact_meta = {
            key: value
            for key, value in meta.items()
            if key not in {"payload"}
        }
        compact_count = {
            key: value
            for key, value in count.items()
            if key not in {"payload"}
        }
        rows.append(
            {
                "asset_id": layer.asset_id,
                "title": layer.title,
                "source_url": layer.source_url,
                "service_url": layer.service_url,
                "layer_id": layer.layer_id,
                "expected_feature_count": layer.feature_count,
                "metadata_ok": bool(meta.get("ok")),
                "count_ok": bool(count.get("ok")),
                "observed_count": observed_count,
                "count_matches_registry": observed_count == layer.feature_count,
                "metadata_summary": metadata_summary,
                "metadata_probe": compact_meta,
                "count_probe": compact_count,
            }
        )
    return rows


def build_payload(args: argparse.Namespace) -> dict[str, object]:
    dataset_root = Path(args.dataset_root)
    exact_rows = availability_matrix(dataset_root, program_ids=("overlay",))
    exact_ready = sum(1 for row in exact_rows if row.exact_input_ready)

    same_source_targets = same_source_arcgis_targets()
    same_source_target_ids = {target.target_id for target in same_source_targets}
    same_source_pair_coverage = {
        "county_zipcode": {"required_targets": ("county", "zipcode"), "same_source_generation_supported": True},
        "block_water": {"required_targets": ("blockgroup", "waterbodies"), "same_source_generation_supported": True},
        "lkaf_pkaf": {"required_targets": ("lakes_africa", "parks_africa"), "same_source_generation_supported": False},
        "lkas_pkas": {"required_targets": ("lakes_asia", "parks_asia"), "same_source_generation_supported": False},
        "lkau_pkau": {"required_targets": ("lakes_australia", "parks_australia"), "same_source_generation_supported": False},
        "lkeu_pkeu": {"required_targets": ("lakes_europe", "parks_europe"), "same_source_generation_supported": False},
        "lkna_pkna": {"required_targets": ("lakes_north_america", "parks_north_america"), "same_source_generation_supported": False},
        "lksa_pksa": {"required_targets": ("lakes_south_america", "parks_south_america"), "same_source_generation_supported": False},
    }
    pair_rows = []
    for pair in paper_pairs():
        exact = next(row for row in exact_rows if row.pair_id == pair.pair_id)
        same_source = same_source_pair_coverage[pair.pair_id]
        required_targets = tuple(same_source["required_targets"])
        pair_rows.append(
            {
                "pair_id": pair.pair_id,
                "paper_label": pair.paper_label,
                "exact_input_ready": exact.exact_input_ready,
                "exact_blocker": exact.blocker,
                "same_source_generation_supported": bool(same_source["same_source_generation_supported"]),
                "same_source_required_targets": required_targets,
                "same_source_registered_targets_present": all(target in same_source_target_ids for target in required_targets),
            }
        )

    blockers = []
    if exact_ready != len(exact_rows):
        blockers.append("missing_exact_section57_cdb_inputs")
    unsupported_same_source_pairs = [
        row["pair_id"] for row in pair_rows if not row["same_source_generation_supported"]
    ]
    if unsupported_same_source_pairs:
        blockers.append("same_source_generation_missing_lakes_parks_targets")

    network: dict[str, object] = {"checked": False}
    if args.check_network:
        network = {
            "checked": True,
            "timeout_sec": args.timeout,
            "preprocessed_share": _fetch_url_status(RAYJOIN_PREPROCESSED_SHARE_URL, timeout=args.timeout),
            "arcgis_layers": _arcgis_probe(timeout=args.timeout),
        }
        if not network["preprocessed_share"]["ok"]:  # type: ignore[index]
            blockers.append("preprocessed_share_not_live")
        if not all(row["metadata_ok"] and row["count_ok"] for row in network["arcgis_layers"]):  # type: ignore[index]
            blockers.append("arcgis_source_probe_failed")

    return {
        "schema": SCHEMA,
        "dataset_root": str(dataset_root),
        "exact_overlay_pairs_ready": exact_ready,
        "exact_overlay_pairs_total": len(exact_rows),
        "pair_rows": pair_rows,
        "same_source_arcgis_targets": [
            {
                "target_id": target.target_id,
                "source_asset_id": target.source_asset_id,
                "output_relative_path": target.output_relative_path,
                "cdb_name": target.cdb_name,
                "feature_id_field": target.feature_id_field,
                "topology_contract": target.topology_contract,
            }
            for target in same_source_targets
        ],
        "same_source_generation_scope": {
            "supported_pairs": [
                row["pair_id"] for row in pair_rows if row["same_source_generation_supported"]
            ],
            "unsupported_pairs": unsupported_same_source_pairs,
            "claim_boundary": (
                "same_source_regenerated_cdb can exercise the RTDL/RayJoin route, "
                "but it is not a recovered paper_preprocessed_cdb input unless "
                "the generated CDB is separately proven equivalent."
            ),
        },
        "network": network,
        "blockers": sorted(set(blockers)),
        "next_actions": [
            "Recover exact paper_preprocessed_cdb files, or regenerate CDBs through an audited topology-preserving preprocessing path.",
            "For the two U.S. pairs, use the registered ArcGIS FeatureServer targets as the same-source route.",
            "For the six Lakes/Parks pairs, add source targets and a converter before claiming 8/8 coverage.",
            "Do not use same_source_regenerated_cdb rows as paper_preprocessed_cdb performance claims without equivalence evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Goal4806 Section 5.7 data acquisition readiness.")
    parser.add_argument("--dataset-root", default="data/rayjoin_section57_cdb")
    parser.add_argument("--output-json", type=Path)
    parser.add_argument("--check-network", action="store_true")
    parser.add_argument("--timeout", type=int, default=20)
    args = parser.parse_args()

    payload = build_payload(args)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output_json:
        args.output_json.parent.mkdir(parents=True, exist_ok=True)
        args.output_json.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
