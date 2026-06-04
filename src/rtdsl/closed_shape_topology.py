from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


OWNER_FACE_MEMBERSHIP_CONTRACT = "rtdl.closed_shape.owner_face_membership.v1"


def _int_set(value: int | Iterable[int]) -> frozenset[int]:
    if isinstance(value, bool):
        return frozenset((int(value),))
    if isinstance(value, int):
        return frozenset((int(value),))
    return frozenset(int(item) for item in value)


def _candidate_ids(row: Mapping[str, Any]) -> tuple[int, int]:
    if "point_id" in row:
        point_id = row["point_id"]
    elif "left_id" in row:
        point_id = row["left_id"]
    else:
        raise KeyError("candidate row must expose point_id or left_id")

    if "shape_id" in row:
        shape_id = row["shape_id"]
    elif "right_id" in row:
        shape_id = row["right_id"]
    else:
        raise KeyError("candidate row must expose shape_id or right_id")

    return int(point_id), int(shape_id)


def topology_rows_by_shape_id(
    topology_rows: Iterable[Mapping[str, Any]],
) -> dict[int, Mapping[str, Any]]:
    """Index generic chain/face topology rows by closed-shape id."""

    indexed: dict[int, Mapping[str, Any]] = {}
    for row in topology_rows:
        if "shape_id" in row:
            shape_id = int(row["shape_id"])
        elif "chain_id" in row:
            shape_id = int(row["chain_id"])
        else:
            raise KeyError("topology row must expose shape_id or chain_id")
        indexed[shape_id] = row
    return indexed


def topology_face_ids(row: Mapping[str, Any]) -> frozenset[int]:
    """Return non-negative face ids associated with one generic topology row."""

    faces: set[int] = set()
    if int(row.get("has_left_face", 1)) and "left_face_id" in row:
        left = int(row["left_face_id"])
        if left >= 0:
            faces.add(left)
    if int(row.get("has_right_face", 1)) and "right_face_id" in row:
        right = int(row["right_face_id"])
        if right >= 0:
            faces.add(right)
    return frozenset(faces)


def filter_closed_shape_membership_candidates_by_owner_face(
    candidate_rows: Iterable[Mapping[str, Any]],
    topology_rows: Iterable[Mapping[str, Any]],
    owner_face_ids_by_point: Mapping[int, int | Iterable[int]],
    *,
    missing_owner_policy: str = "raise",
) -> tuple[dict[str, int], ...]:
    """Filter point/closed-shape candidates through caller-supplied owner faces.

    The contract is intentionally app-agnostic: RTDL supplies generic candidate
    ids and topology rows; the caller supplies the ownership face id(s) required
    by its dataset or benchmark semantics. The engine does not infer CDB,
    RayJoin, GIS, or application-specific ownership.
    """

    if missing_owner_policy not in {"raise", "drop"}:
        raise ValueError("missing_owner_policy must be 'raise' or 'drop'")

    topology_by_shape = topology_rows_by_shape_id(topology_rows)
    owner_faces = {int(point_id): _int_set(faces) for point_id, faces in owner_face_ids_by_point.items()}
    output: list[dict[str, int]] = []
    seen: set[tuple[int, int]] = set()
    for row in candidate_rows:
        point_id, shape_id = _candidate_ids(row)
        allowed_faces = owner_faces.get(point_id)
        if allowed_faces is None:
            if missing_owner_policy == "raise":
                raise KeyError(f"missing owner face id for point_id={point_id}")
            continue
        topology = topology_by_shape.get(shape_id)
        if topology is None:
            continue
        matched_faces = topology_face_ids(topology) & allowed_faces
        if not matched_faces:
            continue
        key = (point_id, shape_id)
        if key in seen:
            continue
        seen.add(key)
        output.append(
            {
                "point_id": point_id,
                "shape_id": shape_id,
                "membership": 1,
                "owner_face_id": min(matched_faces),
            }
        )
    return tuple(output)


def count_closed_shape_membership_candidates_by_owner_face(
    candidate_rows: Iterable[Mapping[str, Any]],
    topology_rows: Iterable[Mapping[str, Any]],
    owner_face_ids_by_point: Mapping[int, int | Iterable[int]],
    *,
    missing_owner_policy: str = "raise",
) -> int:
    """Count owner-face-filtered point/closed-shape memberships."""

    return len(
        filter_closed_shape_membership_candidates_by_owner_face(
            candidate_rows,
            topology_rows,
            owner_face_ids_by_point,
            missing_owner_policy=missing_owner_policy,
        )
    )


def select_unique_owner_faces_from_incident_candidates(
    incident_face_candidate_rows: Iterable[Mapping[str, Any]],
    *,
    ambiguity_policy: str = "raise",
) -> tuple[dict[str, int | str], ...]:
    """Select owner faces only when incident-face evidence has a unique maximum.

    This helper is intentionally conservative. It can turn generic incident
    face candidate rows into explicit owner-face rows when the evidence is
    unambiguous, but ties are not silently resolved. Callers that need richer
    semantics must provide an app/data policy outside the native engine.
    """

    if ambiguity_policy not in {"raise", "drop", "emit_ambiguous"}:
        raise ValueError("ambiguity_policy must be 'raise', 'drop', or 'emit_ambiguous'")

    grouped: dict[int, list[Mapping[str, Any]]] = {}
    for row in incident_face_candidate_rows:
        grouped.setdefault(int(row["point_id"]), []).append(row)

    selected_rows: list[dict[str, int | str]] = []
    for point_id in sorted(grouped):
        rows = grouped[point_id]
        if not rows:
            continue
        max_count = max(int(row["incident_face_count"]) for row in rows)
        winners = sorted(
            (row for row in rows if int(row["incident_face_count"]) == max_count),
            key=lambda row: int(row["face_id"]),
        )
        if len(winners) != 1:
            if ambiguity_policy == "raise":
                faces = tuple(int(row["face_id"]) for row in winners)
                raise ValueError(f"ambiguous owner face for point_id={point_id}: {faces}")
            if ambiguity_policy == "drop":
                continue
            selected_rows.append(
                {
                    "point_id": point_id,
                    "owner_face_id": -1,
                    "incident_face_count": max_count,
                    "candidate_count": len(winners),
                    "selection_status": "ambiguous_tie",
                }
            )
            continue
        winner = winners[0]
        selected_rows.append(
            {
                "point_id": point_id,
                "owner_face_id": int(winner["face_id"]),
                "incident_face_count": max_count,
                "candidate_count": 1,
                "selection_status": "unique_max_incident_face",
            }
        )
    return tuple(selected_rows)


def owner_face_membership_contract() -> dict[str, object]:
    """Return the generic reference contract for owner-face membership."""

    return {
        "contract": OWNER_FACE_MEMBERSHIP_CONTRACT,
        "status": "python_reference_contract",
        "inputs": (
            "candidate_rows(point_id,shape_id)",
            "topology_rows(shape_id|chain_id,left_face_id,right_face_id)",
            "owner_face_ids_by_point",
        ),
        "outputs": ("point_id", "shape_id", "membership", "owner_face_id"),
        "optional_reference_helpers": ("select_unique_owner_faces_from_incident_candidates",),
        "app_agnostic": True,
        "native_engine_may_infer_app_ownership": False,
        "claim_boundary": {
            "release_authorized": False,
            "public_speedup_claim_authorized": False,
            "rayjoin_paper_reproduction_claim_authorized": False,
            "rtdl_beats_rayjoin_claim_authorized": False,
            "rt_core_speedup_claim_authorized": False,
            "true_zero_copy_claim_authorized": False,
        },
    }


def validate_owner_face_membership_contract() -> dict[str, object]:
    contract = owner_face_membership_contract()
    if contract["contract"] != OWNER_FACE_MEMBERSHIP_CONTRACT:
        raise ValueError("owner-face membership contract id mismatch")
    if contract["status"] != "python_reference_contract":
        raise ValueError("owner-face membership contract must remain a Python reference contract")
    if contract["app_agnostic"] is not True:
        raise ValueError("owner-face membership contract must be app-agnostic")
    if contract["native_engine_may_infer_app_ownership"] is not False:
        raise ValueError("native engine must not infer app ownership")
    boundary = contract["claim_boundary"]
    if not isinstance(boundary, Mapping) or any(bool(value) for value in boundary.values()):
        raise ValueError("owner-face membership claim boundary must stay blocked")
    return contract
