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
        print(f"[goal3376] downloading {source}", flush=True)
        rt.download_rayjoin_sample("br_county", source)
    if not sliced_path.exists():
        print(f"[goal3376] materializing {sliced_path}", flush=True)
        county = rt.load_cdb(source)
        sliced = CdbDataset(
            name="br_county_start256_count512",
            chains=tuple(county.chains[256 : 256 + 512]),
        )
        rt.write_cdb(sliced, sliced_path)
    return sliced_path


def _expected_fixture(candidate_artifact: Path) -> dict[str, object]:
    payload = json.loads(candidate_artifact.read_text(encoding="utf-8"))
    exact_by_point: dict[int, tuple[int, ...]] = {}
    for item in payload["per_mismatch_point"]:
        point_id = int(item["point_id"])
        exact_by_point[point_id] = tuple(int(shape_id) for shape_id in item["exact_shape_ids"])
    return {"exact_by_point": exact_by_point}


def _runtime_metadata_columns(county_cdb: Path, selected_points: tuple[int, ...]) -> dict[str, object]:
    county = rt.load_cdb(county_cdb)
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

    topology_rows = rt.chains_to_topology_rows(county)
    topology_by_shape = {int(row["chain_id"]): row for row in topology_rows}
    observed_owner_points = {
        int(row["point_id"])
        for row in incident_rows
        if int(row["face_id"]) == OWNER_FACE_BY_POINT[int(row["point_id"])]
    }
    return {
        "county": county,
        "topology_by_shape": topology_by_shape,
        "cdb_chain_count": len(county.chains),
        "cdb_topology_row_count": len(topology_rows),
        "incident_point_ids": tuple(incident_point_ids),
        "incident_face_ids": tuple(incident_face_ids),
        "incident_counts": tuple(incident_counts),
        "rank_columns": {"rank0": tuple(rank0)},
        "owner_face_present_for_all_points": observed_owner_points == set(selected_points),
    }


def _host_tuple(cp_module, array) -> tuple[int, ...]:
    return tuple(int(value) for value in cp_module.asnumpy(array).tolist())


def _shape_ids_by_point(point_ids: tuple[int, ...], shape_ids: tuple[int, ...]) -> dict[str, list[int]]:
    grouped: dict[str, list[int]] = {}
    for point_id, shape_id in zip(point_ids, shape_ids):
        grouped.setdefault(str(point_id), []).append(int(shape_id))
    return {
        point_id: sorted(set(shape_ids))
        for point_id, shape_ids in sorted(grouped.items(), key=lambda item: int(item[0]))
    }


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    import cupy as cp  # type: ignore
    from rtdsl.optix_runtime import prepare_point_closed_shape_membership_2d_optix

    county_cdb = args.county_cdb
    if county_cdb is None:
        county_cdb = _materialize_county_slice(args.data_dir, download=args.download)

    selected_points = tuple(sorted(OWNER_FACE_BY_POINT))
    expected = _expected_fixture(args.expected_artifact)
    metadata = _runtime_metadata_columns(county_cdb, selected_points)
    county = metadata["county"]
    points = rt.chains_to_probe_points(county)
    shapes = rt.chains_to_polygons(county)

    prepared = prepare_point_closed_shape_membership_2d_optix(shapes)
    candidate_columns = None
    try:
        candidate_columns = prepared.candidate_device_columns(points)
        cupy_candidates = candidate_columns.as_cupy_columns()
        candidate_point_ids = cupy_candidates["point_id"]
        candidate_shape_ids = cupy_candidates["shape_id"]
        selected_point_array = cp.asarray(selected_points, dtype=cp.int64)
        selected_mask = cp.isin(candidate_point_ids, selected_point_array)
        selected_candidate_point_ids = candidate_point_ids[selected_mask]
        selected_candidate_shape_ids = candidate_shape_ids[selected_mask]
        selected_candidate_shape_ids_host = _host_tuple(cp, selected_candidate_shape_ids)
        selected_candidate_point_ids_host = _host_tuple(cp, selected_candidate_point_ids)

        needed_shape_ids = tuple(sorted(set(selected_candidate_shape_ids_host)))
        topology_rows = []
        for shape_id in needed_shape_ids:
            try:
                topology_rows.append(metadata["topology_by_shape"][shape_id])
            except KeyError as exc:
                raise ValueError(f"live candidate shape missing from runtime CDB topology: {shape_id}") from exc

        priority_columns = rt.derive_owner_face_priority_columns_from_rank_signals(
            point_ids=metadata["incident_point_ids"],
            face_ids=metadata["incident_face_ids"],
            rank_columns=metadata["rank_columns"],
            rank_fields=("rank0",),
        )
        result = rt.run_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=cp.asarray(metadata["incident_point_ids"], dtype=cp.int64),
            incident_face_ids=cp.asarray(metadata["incident_face_ids"], dtype=cp.int64),
            incident_face_counts=cp.asarray(metadata["incident_counts"], dtype=cp.int64),
            priority_point_ids=cp.asarray(priority_columns["point_id"], dtype=cp.int64),
            priority_face_ids=cp.asarray(priority_columns["face_id"], dtype=cp.int64),
            priorities=cp.asarray(priority_columns["priority"], dtype=cp.int64),
            candidate_point_ids=selected_candidate_point_ids,
            candidate_shape_ids=selected_candidate_shape_ids,
            topology_shape_ids=cp.asarray(tuple(int(row["chain_id"]) for row in topology_rows), dtype=cp.int64),
            topology_left_face_ids=cp.asarray(tuple(int(row["left_face_id"]) for row in topology_rows), dtype=cp.int64),
            topology_right_face_ids=cp.asarray(tuple(int(row["right_face_id"]) for row in topology_rows), dtype=cp.int64),
            topology_has_left_faces=cp.asarray(tuple(int(row["has_left_face"]) for row in topology_rows), dtype=cp.int8),
            topology_has_right_faces=cp.asarray(tuple(int(row["has_right_face"]) for row in topology_rows), dtype=cp.int8),
        )

        recovered_point_ids = _host_tuple(cp, result["point_id"])
        recovered_shape_ids = _host_tuple(cp, result["shape_id"])
        recovered_by_point = _shape_ids_by_point(recovered_point_ids, recovered_shape_ids)
        exact_by_point = {
            str(point_id): list(shape_ids)
            for point_id, shape_ids in sorted(expected["exact_by_point"].items())
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
        live_candidate_shape_ids_by_point = _shape_ids_by_point(
            selected_candidate_point_ids_host,
            selected_candidate_shape_ids_host,
        )

        return {
            "schema": "rtdl.goal3376.owner_face_cupy_optix_candidate_route_probe.v1",
            "goal": 3376,
            "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
            "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
            "cupy_version": cp.__version__,
            "county_cdb": str(county_cdb),
            "expected_artifact": str(args.expected_artifact),
            "candidate_rows_from_optix_device_columns": True,
            "stored_candidate_artifact_used_as_input": False,
            "stored_topology_artifact_used_as_input": False,
            "stored_incident_artifact_used_as_input": False,
            "stored_exact_oracle_artifact_used_as_input": True,
            "topology_rows_derived_from_cdb": True,
            "incident_rows_derived_from_cdb": True,
            "point_count": len(selected_points),
            "cdb_chain_count": metadata["cdb_chain_count"],
            "cdb_topology_row_count": metadata["cdb_topology_row_count"],
            "optix_candidate_row_count": int(candidate_columns.row_count),
            "optix_candidate_capacity": int(candidate_columns.capacity),
            "optix_candidate_overflow": bool(candidate_columns.overflow),
            "optix_candidate_device_resident": bool(candidate_columns.device_resident),
            "optix_candidate_traversal_seconds": float(candidate_columns.traversal_seconds),
            "selected_candidate_row_count": int(selected_candidate_point_ids.size),
            "pipeline_topology_row_count": len(topology_rows),
            "incident_row_count": len(metadata["incident_point_ids"]),
            "owner_face_present_for_all_points": metadata["owner_face_present_for_all_points"],
            "live_candidate_shape_ids_by_point": live_candidate_shape_ids_by_point,
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
                "Live-candidate route probe only: OptiX produces generic point/shape candidate device columns, "
                "the app masks the seven fixture points, and the composed CuPy owner-face continuation filters "
                "those candidates against CDB-derived topology/incident metadata. The stored artifact supplies "
                "only expected exact answers. This is not release, default-route, speedup, true-zero-copy, or "
                "RayJoin paper reproduction evidence."
            ),
        }
    finally:
        if candidate_columns is not None:
            candidate_columns.close()
        prepared.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3376 owner-face CuPy live OptiX candidate route probe.")
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
        "--expected-artifact",
        type=Path,
        default=ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json",
        help="Stored expected-answer oracle. Candidate rows, topology rows, and incident rows are not read from this artifact.",
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
