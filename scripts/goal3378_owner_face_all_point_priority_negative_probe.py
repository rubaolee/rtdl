from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import sys
from typing import Any


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

import rtdsl as rt  # noqa: E402
from rtdsl.datasets import CdbDataset  # noqa: E402


def _command_output(args: list[str]) -> str:
    try:
        return subprocess.check_output(args, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def _materialize_county_slice(data_dir: Path, *, download: bool) -> Path:
    data_dir.mkdir(parents=True, exist_ok=True)
    source = data_dir / "br_county.cdb"
    sliced_path = data_dir / "br_county_start256_count512.cdb"
    if not source.exists():
        if not download:
            raise FileNotFoundError(f"{source} is missing; rerun with --download")
        print(f"[goal3378] downloading {source}", flush=True)
        rt.download_rayjoin_sample("br_county", source)
    if not sliced_path.exists():
        print(f"[goal3378] materializing {sliced_path}", flush=True)
        county = rt.load_cdb(source)
        sliced = CdbDataset(
            name="br_county_start256_count512",
            chains=tuple(county.chains[256 : 256 + 512]),
        )
        rt.write_cdb(sliced, sliced_path)
    return sliced_path


def _coordinate_key(point, precision: int) -> tuple[float, float]:
    return (round(float(point.x), precision), round(float(point.y), precision))


def _build_incident_chain_length_priority_columns(county, *, coordinate_precision: int) -> dict[str, tuple[int, ...]]:
    """Build a deliberately experimental all-point rank signal.

    The policy prefers incident faces that are supported by fewer short chains,
    then by larger minimum incident-chain length, then by face id. Goal3378 is
    a negative probe: this generic-looking signal is not sufficient for
    route-scale correctness on the county slice.
    """

    chains_by_coordinate: dict[tuple[float, float], list[object]] = defaultdict(list)
    for chain in county.chains:
        if not chain.points:
            continue
        for index in (0, len(chain.points) - 1):
            chains_by_coordinate[_coordinate_key(chain.points[index], coordinate_precision)].append(chain)

    incident_point_ids: list[int] = []
    incident_face_ids: list[int] = []
    incident_counts: list[int] = []
    rank_short_chain_count: list[int] = []
    rank_negative_min_chain_length: list[int] = []
    rank_face_id: list[int] = []

    for chain in county.chains:
        if not chain.points:
            continue
        incident_chains = chains_by_coordinate[_coordinate_key(chain.points[0], coordinate_precision)]
        face_to_lengths: dict[int, list[int]] = defaultdict(list)
        for incident in incident_chains:
            if incident.left_face_id != 0:
                face_to_lengths[int(incident.left_face_id)].append(int(incident.point_count))
            if incident.right_face_id != 0:
                face_to_lengths[int(incident.right_face_id)].append(int(incident.point_count))
        for face_id, lengths in sorted(face_to_lengths.items()):
            incident_point_ids.append(int(chain.chain_id))
            incident_face_ids.append(int(face_id))
            incident_counts.append(len(lengths))
            rank_short_chain_count.append(sum(1 for length in lengths if length <= 2))
            rank_negative_min_chain_length.append(-min(lengths))
            rank_face_id.append(int(face_id))

    priority = rt.derive_owner_face_priority_columns_from_rank_signals(
        point_ids=incident_point_ids,
        face_ids=incident_face_ids,
        rank_columns={
            "short_chain_count": tuple(rank_short_chain_count),
            "negative_min_chain_length": tuple(rank_negative_min_chain_length),
            "face_id": tuple(rank_face_id),
        },
        rank_fields=("short_chain_count", "negative_min_chain_length", "face_id"),
    )
    return {
        "incident_point_ids": tuple(incident_point_ids),
        "incident_face_ids": tuple(incident_face_ids),
        "incident_counts": tuple(incident_counts),
        "priority_point_ids": priority["point_id"],
        "priority_face_ids": priority["face_id"],
        "priorities": priority["priority"],
    }


def _pair_set(rows: tuple[dict[str, Any], ...]) -> set[tuple[int, int]]:
    return {(int(row["point_id"]), int(row["shape_id"])) for row in rows}


def run_probe(args: argparse.Namespace) -> dict[str, object]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county_cdb = args.county_cdb
    if county_cdb is None:
        county_cdb = _materialize_county_slice(args.data_dir, download=args.download)
    county = rt.load_cdb(county_cdb)
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)
    priority_columns = _build_incident_chain_length_priority_columns(
        county,
        coordinate_precision=args.coordinate_precision,
    )
    topology_rows = rt.chains_to_topology_rows(county)

    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    candidate_columns = None
    try:
        exact_rows = tuple(prepared.run(points))
        exact_pairs = _pair_set(exact_rows)
        candidate_columns = prepared.candidate_device_columns(points)
        candidates = candidate_columns.as_cupy_columns()
        filtered = rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray(priority_columns["incident_point_ids"], dtype=cp.int64),
            incident_face_ids=cp.asarray(priority_columns["incident_face_ids"], dtype=cp.int64),
            incident_face_counts=cp.asarray(priority_columns["incident_counts"], dtype=cp.int64),
            priority_point_ids=cp.asarray(priority_columns["priority_point_ids"], dtype=cp.int64),
            priority_face_ids=cp.asarray(priority_columns["priority_face_ids"], dtype=cp.int64),
            priorities=cp.asarray(priority_columns["priorities"], dtype=cp.int64),
            candidate_point_ids=candidates["point_id"],
            candidate_shape_ids=candidates["shape_id"],
            topology_shape_ids=cp.asarray([int(row["chain_id"]) for row in topology_rows], dtype=cp.int64),
            topology_left_face_ids=cp.asarray([int(row["left_face_id"]) for row in topology_rows], dtype=cp.int64),
            topology_right_face_ids=cp.asarray([int(row["right_face_id"]) for row in topology_rows], dtype=cp.int64),
            topology_has_left_faces=cp.asarray([int(row["has_left_face"]) for row in topology_rows], dtype=cp.int8),
            topology_has_right_faces=cp.asarray([int(row["has_right_face"]) for row in topology_rows], dtype=cp.int8),
        )
        filtered_pairs = set(
            zip(
                (int(value) for value in cp.asnumpy(filtered["point_id"]).tolist()),
                (int(value) for value in cp.asnumpy(filtered["shape_id"]).tolist()),
            )
        )
        missing = sorted(exact_pairs - filtered_pairs)
        extra = sorted(filtered_pairs - exact_pairs)
        return {
            "schema": "rtdl.goal3378.owner_face_all_point_priority_negative_probe.v1",
            "goal": 3378,
            "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "cupy_version": cp.__version__,
            "county_cdb": str(county_cdb),
            "coordinate_precision": args.coordinate_precision,
            "policy_under_test": "incident_chain_length_rank",
            "policy_result": "reject_for_default_route",
            "cdb_chain_count": len(county.chains),
            "point_count": len(points),
            "shape_count": len(shapes),
            "incident_row_count": len(priority_columns["incident_point_ids"]),
            "priority_row_count": len(priority_columns["priority_point_ids"]),
            "optix_candidate_row_count": int(candidate_columns.row_count),
            "optix_candidate_overflow": bool(candidate_columns.overflow),
            "exact_row_count": len(exact_pairs),
            "filtered_row_count": len(filtered_pairs),
            "matches_exact": filtered_pairs == exact_pairs,
            "missing_exact_row_count": len(missing),
            "extra_row_count": len(extra),
            "missing_sample": [list(pair) for pair in missing[:20]],
            "extra_sample": [list(pair) for pair in extra[:20]],
            "claim_boundary": {
                "release_authorized": False,
                "public_speedup_claim_authorized": False,
                "rayjoin_paper_reproduction_claim_authorized": False,
                "rtdl_beats_rayjoin_claim_authorized": False,
                "rt_core_speedup_claim_authorized": False,
                "true_zero_copy_claim_authorized": False,
                "native_default_route_authorized": False,
            },
            "interpretation": (
                "Negative all-point policy probe: a generic incident-chain-length priority removes extras but "
                "drops true exact rows, so it must not be promoted as a default owner-face route policy."
            ),
        }
    finally:
        if candidate_columns is not None:
            candidate_columns.close()
        prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3378 all-point owner-face priority negative probe.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb",
    )
    parser.add_argument("--county-cdb", type=Path, default=None)
    parser.add_argument("--coordinate-precision", type=int, default=12)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
