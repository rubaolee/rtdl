#!/usr/bin/env python3
"""Exact Goal5776 input mapping from one extracted real-scale data root."""

from __future__ import annotations

import hashlib
from pathlib import Path

from goal5776_real_scale_formal_contract import UNITS


def _sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_real_scale_inputs(
    data_root: str | Path,
    *, refinement_evidence_path: str | Path | None = None,
) -> dict[str, dict[str, object]]:
    data = Path(data_root).resolve()
    common = data / "common"
    result: dict[str, dict[str, object]] = {
        "particle__microfluidics_5000": {
            "input_root": str(data / "particle"),
        },
        "rtnn__kitti12m_q4096_k4": {
            "input_root": str(data / "rtnn"),
        },
        "xhd__dragon_to_happy": {
            "input_root": str(data / "xhd"),
        },
        "raydb__ssb_sf10_q11": {
            "packet_path": str(common / "raydb/q11/packet.json"),
            "partition_rows": 5_000_000,
        },
        "rayjoin__top4_six_batch": {
            "left": str(common / "rayjoin/top4_county.cdb"),
            "right": str(common / "rayjoin/top4_zipcode.cdb"),
            "lsi_capacity": 1_000_000,
            "expected_output_sha256": (
                "977c93718af22eb6cb887948304f2a9c56cf33aa57e05f5872bf6b2bf271ec3d"
            ),
        },
    }
    prepared_arrays = common / "rt_barneshut/prepared_arrays.json"
    expected_forces = common / "rt_barneshut/expected_forces.txt"
    result["rtbh__author_32768"] = {
        "prepared_arrays": str(prepared_arrays),
        "expected_forces": str(expected_forces),
        "expected_prepared_sha256": _sha(prepared_arrays),
        "expected_forces_sha256": _sha(expected_forces),
    }
    for dataset, filename, count in (
        ("com_dblp", "com-dblp.edge", 2_224_385),
        ("cit_patents", "cit-Patents.edge", 7_515_023),
        ("soc_livejournal1", "soc-LiveJournal1.edge", 285_730_264),
    ):
        for algorithm in ("rt_1a2", "rt_2a1"):
            result[f"triangle__{dataset}__{algorithm}"] = {
                "edge_file": str(data / "triangle" / filename),
                "expected_triangle_count": count,
                "max_relation_rows": 1_000_000,
            }
    evidence = (
        Path(refinement_evidence_path).resolve()
        if refinement_evidence_path is not None
        else data / "FIXED_RADIUS_REFINEMENT_EVIDENCE.json"
    )
    for unit in UNITS:
        if unit.app == "rt_dbscan":
            result[unit.unit_id] = (
                {"input_root": str(data / "rtdbscan")}
                if unit.unit_id.endswith("goal5776_clustered3d_4096")
                else {"refinement_evidence_path": str(evidence)}
            )
    librts = common / "librts/parks"
    for operation, expected in (
        ("point_contains", 112_729),
        ("range_contains", 105_826),
    ):
        result[f"librts__parks_{operation}"] = {
            "cache_npz": str(librts / "cache/parks_bz2.npz"),
            "cache_json": str(librts / "cache/parks_bz2.json"),
            "point_queries" if operation == "point_contains" else "range_queries": str(
                librts / f"queries/{operation}_100000.wkt"
            ),
            "expected_count": expected,
        }
    expected_units = {unit.unit_id for unit in UNITS}
    if set(result) != expected_units:
        raise RuntimeError(
            f"Goal5776 input map mismatch: missing={sorted(expected_units-set(result))}, "
            f"extra={sorted(set(result)-expected_units)}"
        )
    path_keys = {
        "input_root", "packet_path", "left", "right", "prepared_arrays",
        "expected_forces", "edge_file", "refinement_evidence_path",
        "cache_npz", "cache_json", "point_queries", "range_queries",
    }
    for identity in result.values():
        for key, value in identity.items():
            if key in path_keys:
                path = Path(str(value))
                if not path.exists() or path.is_symlink():
                    raise FileNotFoundError(path)
    return result


__all__ = ["build_real_scale_inputs"]
