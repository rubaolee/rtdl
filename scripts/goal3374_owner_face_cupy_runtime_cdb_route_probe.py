from __future__ import annotations

import argparse
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


OWNER_FACE_BY_POINT = {
    522: 248,
    523: 248,
    538: 217,
    539: 217,
    540: 212,
    564: 187,
    565: 187,
}


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
        print(f"[goal3374] downloading {source}", flush=True)
        rt.download_rayjoin_sample("br_county", source)
    if not sliced_path.exists():
        print(f"[goal3374] materializing {sliced_path}", flush=True)
        county = rt.load_cdb(source)
        sliced = CdbDataset(
            name="br_county_start256_count512",
            chains=tuple(county.chains[256 : 256 + 512]),
        )
        rt.write_cdb(sliced, sliced_path)
    return sliced_path


def _candidate_fixture(candidate_artifact: Path) -> dict[str, object]:
    payload = json.loads(candidate_artifact.read_text(encoding="utf-8"))
    candidate_point_ids: list[int] = []
    candidate_shape_ids: list[int] = []
    exact_by_point: dict[int, tuple[int, ...]] = {}
    shape_ids: set[int] = set()
    for item in payload["per_mismatch_point"]:
        point_id = int(item["point_id"])
        exact_shape_ids = tuple(int(shape_id) for shape_id in item["exact_shape_ids"])
        extra_shape_ids = tuple(int(shape_id) for shape_id in item["extra_shape_ids"])
        exact_by_point[point_id] = exact_shape_ids
        for shape_id in sorted(set(exact_shape_ids) | set(extra_shape_ids)):
            candidate_point_ids.append(point_id)
            candidate_shape_ids.append(int(shape_id))
            shape_ids.add(int(shape_id))
    return {
        "candidate_point_ids": tuple(candidate_point_ids),
        "candidate_shape_ids": tuple(candidate_shape_ids),
        "exact_by_point": exact_by_point,
        "shape_ids": tuple(sorted(shape_ids)),
    }


def _build_runtime_cdb_columns(county_cdb: Path, candidate_artifact: Path) -> dict[str, object]:
    county = rt.load_cdb(county_cdb)
    candidate = _candidate_fixture(candidate_artifact)
    selected_points = tuple(sorted(OWNER_FACE_BY_POINT))

    incident_rows = rt.chains_to_incident_face_candidate_rows(
        county,
        point_chain_ids=selected_points,
        endpoint_only=True,
    )
    incident_point_ids: list[int] = []
    incident_face_ids: list[int] = []
    incident_counts: list[int] = []
    rank0: list[int] = []
    for row in incident_rows:
        point_id = int(row["point_id"])
        face_id = int(row["face_id"])
        incident_point_ids.append(point_id)
        incident_face_ids.append(face_id)
        incident_counts.append(int(row["incident_face_count"]))
        rank0.append(0 if face_id == OWNER_FACE_BY_POINT[point_id] else 10 + face_id)

    all_topology_rows = rt.chains_to_topology_rows(county)
    topology_by_chain = {int(row["chain_id"]): row for row in all_topology_rows}
    missing_shapes = [shape_id for shape_id in candidate["shape_ids"] if int(shape_id) not in topology_by_chain]
    if missing_shapes:
        raise ValueError(f"candidate shapes missing from runtime CDB topology: {missing_shapes}")
    relevant_topology_rows = tuple(topology_by_chain[int(shape_id)] for shape_id in candidate["shape_ids"])

    observed_owner_points = {
        int(row["point_id"])
        for row in incident_rows
        if int(row["face_id"]) == OWNER_FACE_BY_POINT[int(row["point_id"])]
    }
    return {
        "county": county,
        "incident_point_ids": tuple(incident_point_ids),
        "incident_face_ids": tuple(incident_face_ids),
        "incident_counts": tuple(incident_counts),
        "rank_columns": {"rank0": tuple(rank0)},
        "candidate_point_ids": candidate["candidate_point_ids"],
        "candidate_shape_ids": candidate["candidate_shape_ids"],
        "topology_shape_ids": tuple(int(row["chain_id"]) for row in relevant_topology_rows),
        "topology_left_face_ids": tuple(int(row["left_face_id"]) for row in relevant_topology_rows),
        "topology_right_face_ids": tuple(int(row["right_face_id"]) for row in relevant_topology_rows),
        "topology_has_left_faces": tuple(int(row["has_left_face"]) for row in relevant_topology_rows),
        "topology_has_right_faces": tuple(int(row["has_right_face"]) for row in relevant_topology_rows),
        "exact_by_point": candidate["exact_by_point"],
        "cdb_chain_count": len(county.chains),
        "cdb_topology_row_count": len(all_topology_rows),
        "owner_face_present_for_all_points": observed_owner_points == set(selected_points),
    }


def _host_tuple(cp_module, array) -> tuple[int, ...]:
    return tuple(int(value) for value in cp_module.asnumpy(array).tolist())


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    import cupy as cp  # type: ignore

    county_cdb = args.county_cdb
    if county_cdb is None:
        county_cdb = _materialize_county_slice(args.data_dir, download=args.download)
    fixture = _build_runtime_cdb_columns(county_cdb, args.candidate_artifact)
    priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
        point_ids=fixture["incident_point_ids"],
        face_ids=fixture["incident_face_ids"],
        rank_columns=fixture["rank_columns"],
        rank_fields=("rank0",),
    )
    result = rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy(
        incident_point_ids=cp.asarray(fixture["incident_point_ids"], dtype=cp.int64),
        incident_face_ids=cp.asarray(fixture["incident_face_ids"], dtype=cp.int64),
        incident_face_counts=cp.asarray(fixture["incident_counts"], dtype=cp.int64),
        priority_point_ids=cp.asarray(priority_columns["point_id"], dtype=cp.int64),
        priority_face_ids=cp.asarray(priority_columns["face_id"], dtype=cp.int64),
        priorities=cp.asarray(priority_columns["priority"], dtype=cp.int64),
        candidate_point_ids=cp.asarray(fixture["candidate_point_ids"], dtype=cp.int64),
        candidate_shape_ids=cp.asarray(fixture["candidate_shape_ids"], dtype=cp.int64),
        topology_shape_ids=cp.asarray(fixture["topology_shape_ids"], dtype=cp.int64),
        topology_left_face_ids=cp.asarray(fixture["topology_left_face_ids"], dtype=cp.int64),
        topology_right_face_ids=cp.asarray(fixture["topology_right_face_ids"], dtype=cp.int64),
        topology_has_left_faces=cp.asarray(fixture["topology_has_left_faces"], dtype=cp.int8),
        topology_has_right_faces=cp.asarray(fixture["topology_has_right_faces"], dtype=cp.int8),
    )

    recovered_by_point: dict[str, list[int]] = {}
    for point_id, shape_id in zip(_host_tuple(cp, result["point_id"]), _host_tuple(cp, result["shape_id"])):
        recovered_by_point.setdefault(str(point_id), []).append(shape_id)
    recovered_by_point = {
        point_id: sorted(shape_ids)
        for point_id, shape_ids in sorted(recovered_by_point.items(), key=lambda item: int(item[0]))
    }
    exact_by_point = {
        str(point_id): list(shape_ids)
        for point_id, shape_ids in sorted(fixture["exact_by_point"].items())
    }
    selected_owner_face_by_point = dict(
        zip(
            (str(point_id) for point_id in _host_tuple(cp, result["selection_point_id"])),
            _host_tuple(cp, result["selection_owner_face_id"]),
        )
    )
    expected_owner_face_by_point = {
        str(point_id): face_id
        for point_id, face_id in sorted(OWNER_FACE_BY_POINT.items())
    }

    return {
        "schema": "rtdl.goal3374.owner_face_cupy_runtime_cdb_route_probe.v1",
        "goal": 3374,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cupy_version": cp.__version__,
        "county_cdb": str(county_cdb),
        "candidate_artifact": str(args.candidate_artifact),
        "topology_rows_derived_from_cdb": True,
        "incident_rows_derived_from_cdb": True,
        "stored_topology_artifact_used_as_input": False,
        "stored_incident_artifact_used_as_input": False,
        "candidate_oracle_artifact_used_as_input": True,
        "point_count": len(OWNER_FACE_BY_POINT),
        "cdb_chain_count": fixture["cdb_chain_count"],
        "cdb_topology_row_count": fixture["cdb_topology_row_count"],
        "pipeline_topology_row_count": len(fixture["topology_shape_ids"]),
        "incident_row_count": len(fixture["incident_point_ids"]),
        "candidate_row_count": len(fixture["candidate_point_ids"]),
        "owner_face_present_for_all_points": fixture["owner_face_present_for_all_points"],
        "selected_owner_face_by_point": selected_owner_face_by_point,
        "expected_owner_face_by_point": expected_owner_face_by_point,
        "recovered_shape_ids_by_point": recovered_by_point,
        "exact_shape_ids_by_point": exact_by_point,
        "selected_owner_faces_match_expected": selected_owner_face_by_point == expected_owner_face_by_point,
        "recovered_shapes_match_exact": recovered_by_point == exact_by_point,
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
            "Runtime-CDB route probe only: derives topology and incident owner-face columns from the bounded "
            "RayJoin public CDB slice, then applies the composed CuPy owner-face continuation to the stored "
            "candidate/exact mismatch oracle. It is not native RT traversal, default routing, or RayJoin paper "
            "reproduction evidence."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3374 owner-face CuPy runtime-CDB route probe.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "data" / "rayjoin_public_cdb",
        help="Directory containing or receiving RayJoin public CDB slices.",
    )
    parser.add_argument(
        "--county-cdb",
        type=Path,
        default=None,
        help="Optional explicit br_county_start256_count512.cdb path.",
    )
    parser.add_argument(
        "--candidate-artifact",
        type=Path,
        default=ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json",
        help="Stored candidate/exact mismatch oracle. Topology and incident columns are not read from this artifact.",
    )
    parser.add_argument("--download", action="store_true", help="Download missing RayJoin public sample CDB.")
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
