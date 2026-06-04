from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


OWNER_FACE_MEMBERSHIP_CONTRACT = "rtdl.closed_shape.owner_face_membership.v1"
OWNER_FACE_PRIORITY_PIPELINE_CONTRACT = "rtdl.closed_shape.owner_face_priority_pipeline.v1"


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


def select_owner_faces_from_incident_candidates_with_priority(
    incident_face_candidate_rows: Iterable[Mapping[str, Any]],
    priority_rows: Iterable[Mapping[str, Any]],
    *,
    ambiguity_policy: str = "raise",
) -> tuple[dict[str, int | str], ...]:
    """Select owner faces using incident counts plus caller-supplied priorities.

    Higher incident-face count wins first. If counts tie, lower priority value
    wins. Missing or tied priorities fail closed by default. The priority rows
    are explicit caller/data policy; this helper does not infer those priorities
    from application names or native-engine behavior.
    """

    if ambiguity_policy not in {"raise", "drop", "emit_ambiguous"}:
        raise ValueError("ambiguity_policy must be 'raise', 'drop', or 'emit_ambiguous'")

    priority_by_key: dict[tuple[int, int], int] = {}
    for row in priority_rows:
        priority_by_key[(int(row["point_id"]), int(row["face_id"]))] = int(row["priority"])

    grouped: dict[int, list[Mapping[str, Any]]] = {}
    for row in incident_face_candidate_rows:
        grouped.setdefault(int(row["point_id"]), []).append(row)

    selected_rows: list[dict[str, int | str]] = []
    for point_id in sorted(grouped):
        rows = grouped[point_id]
        max_count = max(int(row["incident_face_count"]) for row in rows)
        count_winners = sorted(
            (row for row in rows if int(row["incident_face_count"]) == max_count),
            key=lambda row: int(row["face_id"]),
        )
        if len(count_winners) == 1:
            winner = count_winners[0]
            selected_rows.append(
                {
                    "point_id": point_id,
                    "owner_face_id": int(winner["face_id"]),
                    "incident_face_count": max_count,
                    "candidate_count": 1,
                    "selection_status": "unique_max_incident_face",
                }
            )
            continue

        missing_priority_faces = tuple(
            int(row["face_id"])
            for row in count_winners
            if (point_id, int(row["face_id"])) not in priority_by_key
        )
        if missing_priority_faces:
            if ambiguity_policy == "raise":
                raise ValueError(
                    f"missing owner-face priority for point_id={point_id}: {missing_priority_faces}"
                )
            if ambiguity_policy == "drop":
                continue
            selected_rows.append(
                {
                    "point_id": point_id,
                    "owner_face_id": -1,
                    "incident_face_count": max_count,
                    "candidate_count": len(count_winners),
                    "selection_status": "missing_priority",
                }
            )
            continue

        min_priority = min(priority_by_key[(point_id, int(row["face_id"]))] for row in count_winners)
        priority_winners = [
            row
            for row in count_winners
            if priority_by_key[(point_id, int(row["face_id"]))] == min_priority
        ]
        if len(priority_winners) != 1:
            if ambiguity_policy == "raise":
                faces = tuple(int(row["face_id"]) for row in priority_winners)
                raise ValueError(f"ambiguous owner-face priority for point_id={point_id}: {faces}")
            if ambiguity_policy == "drop":
                continue
            selected_rows.append(
                {
                    "point_id": point_id,
                    "owner_face_id": -1,
                    "incident_face_count": max_count,
                    "candidate_count": len(priority_winners),
                    "selection_status": "ambiguous_priority_tie",
                }
            )
            continue
        winner = priority_winners[0]
        selected_rows.append(
            {
                "point_id": point_id,
                "owner_face_id": int(winner["face_id"]),
                "incident_face_count": max_count,
                "candidate_count": len(count_winners),
                "selection_status": "priority_tie_break",
            }
        )
    return tuple(selected_rows)


def derive_owner_face_priority_rows_from_rank_signals(
    priority_signal_rows: Iterable[Mapping[str, Any]],
    *,
    rank_fields: Iterable[str],
    tie_policy: str = "raise",
) -> tuple[dict[str, object], ...]:
    """Build deterministic priority rows from caller-supplied rank signals.

    This helper does not infer ownership. The caller supplies generic rank
    columns and declares their ordering. Lower rank tuples receive lower
    priority values. Missing rank fields, duplicate point/face rows, and tied
    rank tuples fail closed by default.
    """

    fields = tuple(str(field) for field in rank_fields)
    if not fields:
        raise ValueError("rank_fields must not be empty")
    if tie_policy not in {"raise", "drop"}:
        raise ValueError("tie_policy must be 'raise' or 'drop'")

    grouped: dict[int, list[tuple[int, tuple[Any, ...]]]] = {}
    seen_pairs: set[tuple[int, int]] = set()
    for row in priority_signal_rows:
        point_id = int(row["point_id"])
        face_id = int(row["face_id"])
        pair = (point_id, face_id)
        if pair in seen_pairs:
            raise ValueError(
                f"duplicate owner-face priority signal for point_id={point_id}, face_id={face_id}"
            )
        seen_pairs.add(pair)
        missing_fields = tuple(field for field in fields if field not in row)
        if missing_fields:
            raise KeyError(f"missing owner-face priority rank fields: {missing_fields}")
        grouped.setdefault(point_id, []).append((face_id, tuple(row[field] for field in fields)))

    priority_rows: list[dict[str, object]] = []
    for point_id in sorted(grouped):
        rows = grouped[point_id]
        key_counts: dict[tuple[Any, ...], int] = {}
        for _, rank_key in rows:
            key_counts[rank_key] = key_counts.get(rank_key, 0) + 1
        tied_keys = tuple(rank_key for rank_key, count in key_counts.items() if count > 1)
        if tied_keys:
            if tie_policy == "raise":
                raise ValueError(f"ambiguous owner-face priority rank for point_id={point_id}: {tied_keys}")
            rows = [(face_id, rank_key) for face_id, rank_key in rows if rank_key not in tied_keys]

        try:
            sorted_rows = sorted(rows, key=lambda item: (item[1], item[0]))
        except TypeError as exc:
            raise TypeError("owner-face priority rank values must be mutually sortable") from exc
        for priority, (face_id, rank_key) in enumerate(sorted_rows):
            priority_rows.append(
                {
                    "point_id": point_id,
                    "face_id": face_id,
                    "priority": priority,
                    "priority_rank_key": rank_key,
                }
            )
    return tuple(priority_rows)


def owner_face_ids_by_point_from_selection_rows(
    selection_rows: Iterable[Mapping[str, Any]],
    *,
    require_selected: bool = True,
) -> dict[int, int]:
    """Convert owner-face selection rows into a point-id mapping.

    Ambiguous rows carry ``owner_face_id=-1`` and are rejected by default. This
    keeps downstream membership filtering from accidentally treating ambiguous
    topology as an accepted ownership decision.
    """

    mapping: dict[int, int] = {}
    for row in selection_rows:
        point_id = int(row["point_id"])
        owner_face_id = int(row["owner_face_id"])
        if owner_face_id < 0:
            if require_selected:
                raise ValueError(f"owner face is not selected for point_id={point_id}")
            continue
        if point_id in mapping and mapping[point_id] != owner_face_id:
            raise ValueError(f"conflicting owner face selection for point_id={point_id}")
        mapping[point_id] = owner_face_id
    return mapping


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
        "optional_reference_helpers": (
            "select_unique_owner_faces_from_incident_candidates",
            "select_owner_faces_from_incident_candidates_with_priority",
            "owner_face_ids_by_point_from_selection_rows",
        ),
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


def owner_face_priority_pipeline_contract() -> dict[str, object]:
    """Return the explicit-priority owner-face pipeline contract.

    This is a stricter, compositional contract over the lower-level
    owner-face helpers. It is intentionally only a Python reference contract:
    callers may provide deterministic priority columns, but the native engine
    must not derive application ownership policy by itself.
    """

    return {
        "contract": OWNER_FACE_PRIORITY_PIPELINE_CONTRACT,
        "status": "python_reference_contract_only",
        "inputs": (
            "incident_face_candidate_rows(point_id,face_id,incident_face_count)",
            "priority_rows(point_id,face_id,priority)",
            "candidate_rows(point_id,shape_id)",
            "topology_rows(shape_id|chain_id,left_face_id,right_face_id)",
        ),
        "pipeline_steps": (
            "select_owner_faces_from_incident_candidates_with_priority",
            "owner_face_ids_by_point_from_selection_rows",
            "filter_closed_shape_membership_candidates_by_owner_face",
        ),
        "optional_priority_derivation_helpers": (
            "derive_owner_face_priority_rows_from_rank_signals",
        ),
        "selection_rule": {
            "primary": "higher incident_face_count wins",
            "tie_break": "lower caller_supplied_priority wins",
            "missing_priority": "fail_closed",
            "tied_priority": "fail_closed",
            "native_engine_may_invent_priority": False,
        },
        "outputs": ("point_id", "shape_id", "membership", "owner_face_id"),
        "app_agnostic": True,
        "caller_policy_required": True,
        "native_engine_may_infer_app_ownership": False,
        "native_lowering_status": "blocked_until_contract_stable_and_validated",
        "promotion_requirements": (
            "deterministic priority derivation contract or explicit caller priority columns",
            "same-contract tests against the Python reference",
            "pod/native evidence before any device-lowered implementation is selected by default",
            "claim-boundary review before public performance or paper-reproduction wording",
        ),
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


def validate_owner_face_priority_pipeline_contract() -> dict[str, object]:
    contract = owner_face_priority_pipeline_contract()
    if contract["contract"] != OWNER_FACE_PRIORITY_PIPELINE_CONTRACT:
        raise ValueError("owner-face priority pipeline contract id mismatch")
    if contract["status"] != "python_reference_contract_only":
        raise ValueError("owner-face priority pipeline must remain Python-reference-only")
    if contract["app_agnostic"] is not True:
        raise ValueError("owner-face priority pipeline contract must be app-agnostic")
    if contract["caller_policy_required"] is not True:
        raise ValueError("owner-face priority pipeline must require caller policy")
    if contract["native_engine_may_infer_app_ownership"] is not False:
        raise ValueError("native engine must not infer app ownership")
    rule = contract["selection_rule"]
    if not isinstance(rule, Mapping) or rule.get("native_engine_may_invent_priority") is not False:
        raise ValueError("native engine must not invent owner-face priority")
    inputs = contract["inputs"]
    if not isinstance(inputs, tuple) or not any("priority_rows" in item for item in inputs):
        raise ValueError("owner-face priority pipeline must require explicit priority rows")
    helpers = contract["optional_priority_derivation_helpers"]
    if (
        not isinstance(helpers, tuple)
        or "derive_owner_face_priority_rows_from_rank_signals" not in helpers
    ):
        raise ValueError("owner-face priority pipeline must expose the rank-signal derivation helper")
    boundary = contract["claim_boundary"]
    if not isinstance(boundary, Mapping) or any(bool(value) for value in boundary.values()):
        raise ValueError("owner-face priority pipeline claim boundary must stay blocked")
    return contract
