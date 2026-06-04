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


def _build_fixture_columns(topology_artifact: Path, incident_artifact: Path) -> dict[str, object]:
    topology = json.loads(topology_artifact.read_text(encoding="utf-8"))
    incident = json.loads(incident_artifact.read_text(encoding="utf-8"))

    incident_point_ids: list[int] = []
    incident_face_ids: list[int] = []
    incident_counts: list[int] = []
    rank0: list[int] = []
    for item in incident["rows"]:
        point_id = int(item["point_id"])
        owner_face = OWNER_FACE_BY_POINT[point_id]
        for entry in item["endpoint_face_frequency"]:
            face_id = int(entry["face_id"])
            incident_point_ids.append(point_id)
            incident_face_ids.append(face_id)
            incident_counts.append(int(entry["count"]))
            rank0.append(0 if face_id == owner_face else 10 + face_id)

    candidate_point_ids: list[int] = []
    candidate_shape_ids: list[int] = []
    exact_by_point: dict[int, tuple[int, ...]] = {}
    for item in topology["per_mismatch_point"]:
        point_id = int(item["point_id"])
        exact_by_point[point_id] = tuple(int(shape_id) for shape_id in item["exact_shape_ids"])
        for shape_id in sorted(set(item["exact_shape_ids"]) | set(item["extra_shape_ids"])):
            candidate_point_ids.append(point_id)
            candidate_shape_ids.append(int(shape_id))

    topology_rows = topology["shape_topology_rows"]
    return {
        "incident_point_ids": tuple(incident_point_ids),
        "incident_face_ids": tuple(incident_face_ids),
        "incident_counts": tuple(incident_counts),
        "rank_columns": {"rank0": tuple(rank0)},
        "candidate_point_ids": tuple(candidate_point_ids),
        "candidate_shape_ids": tuple(candidate_shape_ids),
        "topology_shape_ids": tuple(int(row.get("shape_id", row["chain_id"])) for row in topology_rows),
        "topology_left_face_ids": tuple(int(row["left_face_id"]) for row in topology_rows),
        "topology_right_face_ids": tuple(int(row["right_face_id"]) for row in topology_rows),
        "topology_has_left_faces": tuple(int(row.get("has_left_face", 1)) for row in topology_rows),
        "topology_has_right_faces": tuple(int(row.get("has_right_face", 1)) for row in topology_rows),
        "exact_by_point": exact_by_point,
    }


def _host_tuple(cp_module, array) -> tuple[int, ...]:
    return tuple(int(value) for value in cp_module.asnumpy(array).tolist())


def run_probe(args: argparse.Namespace) -> dict[str, Any]:
    import cupy as cp  # type: ignore

    fixture = _build_fixture_columns(args.topology_artifact, args.incident_artifact)
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
        "schema": "rtdl.goal3372.owner_face_cupy_route_fixture_probe.v1",
        "goal": 3372,
        "rtdl_commit": _command_output(["git", "rev-parse", "HEAD"]),
        "gpu": _command_output(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"]),
        "cupy_version": cp.__version__,
        "topology_artifact": str(args.topology_artifact),
        "incident_artifact": str(args.incident_artifact),
        "point_count": len(OWNER_FACE_BY_POINT),
        "incident_row_count": len(fixture["incident_point_ids"]),
        "candidate_row_count": len(fixture["candidate_point_ids"]),
        "topology_row_count": len(fixture["topology_shape_ids"]),
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
        },
        "interpretation": (
            "Route-fixture probe only: validates the app-layer owner-face CuPy continuation over "
            "stored RayJoin/CDB mismatch artifacts; it is not native RT traversal or a paper reproduction claim."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Goal3372 owner-face CuPy route fixture probe.")
    parser.add_argument(
        "--topology-artifact",
        type=Path,
        default=ROOT / "docs" / "reports" / "goal3328_rayjoin_cdb_topology_shape_id_probe_2026-06-04.json",
    )
    parser.add_argument(
        "--incident-artifact",
        type=Path,
        default=ROOT / "docs" / "reports" / "goal3335_rayjoin_incident_face_owner_probe_2026-06-04.json",
    )
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    payload = run_probe(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
