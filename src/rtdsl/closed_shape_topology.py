from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from typing import Any


OWNER_FACE_MEMBERSHIP_CONTRACT = "rtdl.closed_shape.owner_face_membership.v1"
OWNER_FACE_PRIORITY_PIPELINE_CONTRACT = "rtdl.closed_shape.owner_face_priority_pipeline.v1"
OWNER_FACE_SELECTION_STATUS_CODES = {
    "unique_max_incident_face": 1,
    "priority_tie_break": 2,
    "missing_priority": 3,
    "ambiguous_priority_tie": 4,
}

_CUPY_EXACT_CLOSED_SHAPE_CANDIDATE_REFINE_KERNEL = None


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


def _record_value(record: object, name: str) -> object:
    if isinstance(record, Mapping):
        return record[name]
    return getattr(record, name)


def _cupy_exact_closed_shape_candidate_refine_kernel(cupy):
    global _CUPY_EXACT_CLOSED_SHAPE_CANDIDATE_REFINE_KERNEL
    if _CUPY_EXACT_CLOSED_SHAPE_CANDIDATE_REFINE_KERNEL is None:
        _CUPY_EXACT_CLOSED_SHAPE_CANDIDATE_REFINE_KERNEL = cupy.RawKernel(
            r'''
extern "C" __global__
void exact_closed_shape_candidate_refine(
    const long long* candidate_point_ids,
    const long long* candidate_shape_ids,
    const long long candidate_count,
    const double* point_x_by_id,
    const double* point_y_by_id,
    const int* shape_offset_by_id,
    const int* shape_count_by_id,
    const double* vertices_x,
    const double* vertices_y,
    const double point_eps,
    long long* output_point_ids,
    long long* output_shape_ids,
    unsigned int* output_count)
{
    const long long row = (long long)blockDim.x * (long long)blockIdx.x + (long long)threadIdx.x;
    if (row >= candidate_count) return;
    const long long point_id = candidate_point_ids[row];
    const long long shape_id = candidate_shape_ids[row];
    if (point_id < 0 || shape_id < 0) return;
    const double px = point_x_by_id[point_id];
    const double py = point_y_by_id[point_id];
    const int off = shape_offset_by_id[shape_id];
    const int n = shape_count_by_id[shape_id];
    if (off < 0 || n < 3) return;

    const double eps = point_eps;
    for (int i = 0; i < n; ++i) {
        const int j = (i + 1) % n;
        const double ax = vertices_x[off + i];
        const double ay = vertices_y[off + i];
        const double bx = vertices_x[off + j];
        const double by = vertices_y[off + j];
        const double dx = bx - ax;
        const double dy = by - ay;
        const double len2 = dx * dx + dy * dy;
        bool on_segment = false;
        if (len2 <= eps * eps) {
            on_segment = fabs(px - ax) <= eps && fabs(py - ay) <= eps;
        } else {
            const double len = sqrt(len2);
            const double cross = (px - ax) * dy - (py - ay) * dx;
            const double dot = (px - ax) * dx + (py - ay) * dy;
            const double along_eps = eps * len;
            on_segment = fabs(cross) <= eps * len && dot >= -along_eps && dot <= len2 + along_eps;
        }
        if (on_segment) {
            const unsigned int slot = atomicAdd(output_count, 1u);
            output_point_ids[slot] = point_id;
            output_shape_ids[slot] = shape_id;
            return;
        }
    }

    bool inside = false;
    for (int i = 0, j = n - 1; i < n; j = i++) {
        const double xi = vertices_x[off + i];
        const double yi = vertices_y[off + i];
        const double xj = vertices_x[off + j];
        const double yj = vertices_y[off + j];
        if ((yi > py) != (yj > py)) {
            const double denom = (yj - yi) != 0.0 ? (yj - yi) : 1.0e-20;
            const double x_cross = (xj - xi) * (py - yi) / denom + xi;
            if (px <= x_cross) {
                inside = !inside;
            }
        }
    }
    if (inside) {
        const unsigned int slot = atomicAdd(output_count, 1u);
        output_point_ids[slot] = point_id;
        output_shape_ids[slot] = shape_id;
    }
}
''',
            "exact_closed_shape_candidate_refine",
        )
    return _CUPY_EXACT_CLOSED_SHAPE_CANDIDATE_REFINE_KERNEL


def refine_closed_shape_membership_candidate_columns_exact_cupy(
    candidate_columns: object,
    points: Sequence[object],
    shapes: Sequence[object],
    *,
    point_eps: float = 1.0e-9,
    sort_output: bool = True,
) -> dict[str, object]:
    """Filter generic point/closed-shape candidate columns with a CuPy simple-ring predicate.

    This helper is a partner proof for a future native device refinement stage.
    RTDL still treats the native candidate stream as a broad-phase/superset
    producer. The helper keeps the refinement on the CUDA device, but it matches
    the simple point-in-ring fallback semantics, not the full GEOS/topology
    closed-boundary oracle observed in Goal3421. It does not authorize a native
    exact-device predicate, default route, or release claim.
    """

    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("CuPy is required for exact closed-shape candidate refinement") from exc

    if hasattr(candidate_columns, "as_cupy_columns"):
        column_map = candidate_columns.as_cupy_columns()
        field_names = getattr(candidate_columns, "field_names", ("point_id", "shape_id"))
        raw_point_ids = column_map[field_names[0]]
        raw_shape_ids = column_map[field_names[1]]
    elif isinstance(candidate_columns, Mapping):
        raw_point_ids = candidate_columns.get("point_id", candidate_columns.get("left_id"))
        raw_shape_ids = candidate_columns.get("shape_id", candidate_columns.get("right_id"))
        if raw_point_ids is None or raw_shape_ids is None:
            raise KeyError("candidate column mapping must expose point_id/shape_id or left_id/right_id")
    else:
        raise TypeError("candidate_columns must be an OptixNativeDevicePairColumnOutput or a column mapping")

    candidate_point_ids = cp.asarray(raw_point_ids, dtype=cp.int64)
    candidate_shape_ids = cp.asarray(raw_shape_ids, dtype=cp.int64)
    if int(candidate_point_ids.size) != int(candidate_shape_ids.size):
        raise ValueError("candidate point and shape columns must have equal length")
    eps = float(point_eps)
    if eps < 0.0:
        raise ValueError("point_eps must be non-negative")

    point_records = tuple(points)
    shape_records = tuple(shapes)
    max_point_id = max((int(_record_value(point, "id")) for point in point_records), default=-1)
    max_shape_id = max((int(_record_value(shape, "id")) for shape in shape_records), default=-1)
    if int(candidate_point_ids.size):
        max_point_id = max(max_point_id, int(cp.max(candidate_point_ids).item()))
        max_shape_id = max(max_shape_id, int(cp.max(candidate_shape_ids).item()))

    point_x_by_id = [0.0] * (max_point_id + 1)
    point_y_by_id = [0.0] * (max_point_id + 1)
    for point in point_records:
        point_id = int(_record_value(point, "id"))
        point_x_by_id[point_id] = float(_record_value(point, "x"))
        point_y_by_id[point_id] = float(_record_value(point, "y"))

    shape_offset_by_id = [-1] * (max_shape_id + 1)
    shape_count_by_id = [0] * (max_shape_id + 1)
    vertices_x: list[float] = []
    vertices_y: list[float] = []
    for shape in shape_records:
        shape_id = int(_record_value(shape, "id"))
        vertices = tuple(_record_value(shape, "vertices"))
        shape_offset_by_id[shape_id] = len(vertices_x)
        shape_count_by_id[shape_id] = len(vertices)
        for x, y in vertices:
            vertices_x.append(float(x))
            vertices_y.append(float(y))

    candidate_count = int(candidate_point_ids.size)
    output_point_ids = cp.empty((candidate_count,), dtype=cp.int64)
    output_shape_ids = cp.empty((candidate_count,), dtype=cp.int64)
    output_count = cp.zeros((1,), dtype=cp.uint32)
    if candidate_count:
        kernel = _cupy_exact_closed_shape_candidate_refine_kernel(cp)
        block = 256
        grid = (candidate_count + block - 1) // block
        kernel(
            (grid,),
            (block,),
            (
                candidate_point_ids,
                candidate_shape_ids,
                candidate_count,
                cp.asarray(point_x_by_id, dtype=cp.float64),
                cp.asarray(point_y_by_id, dtype=cp.float64),
                cp.asarray(shape_offset_by_id, dtype=cp.int32),
                cp.asarray(shape_count_by_id, dtype=cp.int32),
                cp.asarray(vertices_x, dtype=cp.float64),
                cp.asarray(vertices_y, dtype=cp.float64),
                eps,
                output_point_ids,
                output_shape_ids,
                output_count,
            ),
        )
    row_count = int(output_count[0].item())
    point_out = output_point_ids[:row_count]
    shape_out = output_shape_ids[:row_count]
    if sort_output and row_count > 1:
        order = cp.lexsort(cp.stack((shape_out, point_out)))
        point_out = point_out[order]
        shape_out = shape_out[order]

    return {
        "point_id": point_out,
        "shape_id": shape_out,
        "membership": cp.ones((row_count,), dtype=cp.int64),
        "row_count": row_count,
        "candidate_row_count": candidate_count,
        "dropped_candidate_row_count": candidate_count - row_count,
        "point_eps": eps,
        "partner": "cupy",
        "predicate": "double_simple_ring_closed_shape_membership",
        "matches_geos_topology_oracle": False,
        "output_residency": "partner_device_refined_columns",
        "host_refined_rows_materialized": False,
        "native_exact_device_row_stream_produced": False,
        "true_zero_copy_claim_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
    }


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


def derive_owner_face_priority_columns_from_rank_signals(
    point_ids: Sequence[int],
    face_ids: Sequence[int],
    rank_columns: Mapping[str, Sequence[Any]],
    *,
    rank_fields: Iterable[str],
    tie_policy: str = "raise",
) -> dict[str, tuple[Any, ...]]:
    """Columnar front door for deterministic owner-face priority derivation."""

    fields = tuple(str(field) for field in rank_fields)
    if len(point_ids) != len(face_ids):
        raise ValueError("point_ids and face_ids must have the same length")
    row_count = len(point_ids)
    missing_columns = tuple(field for field in fields if field not in rank_columns)
    if missing_columns:
        raise KeyError(f"missing owner-face priority rank columns: {missing_columns}")
    bad_lengths = tuple(
        field for field in fields if len(rank_columns[field]) != row_count
    )
    if bad_lengths:
        raise ValueError(
            f"owner-face priority rank columns have wrong length: {bad_lengths}"
        )

    rows = []
    for index, (point_id, face_id) in enumerate(zip(point_ids, face_ids)):
        row: dict[str, Any] = {"point_id": int(point_id), "face_id": int(face_id)}
        for field in fields:
            row[field] = rank_columns[field][index]
        rows.append(row)

    priority_rows = derive_owner_face_priority_rows_from_rank_signals(
        rows,
        rank_fields=fields,
        tie_policy=tie_policy,
    )
    return {
        "point_id": tuple(row["point_id"] for row in priority_rows),
        "face_id": tuple(row["face_id"] for row in priority_rows),
        "priority": tuple(row["priority"] for row in priority_rows),
        "priority_rank_key": tuple(row["priority_rank_key"] for row in priority_rows),
    }


def select_owner_faces_from_incident_candidate_columns_with_priority_columns(
    incident_point_ids: Sequence[int],
    incident_face_ids: Sequence[int],
    incident_face_counts: Sequence[int],
    priority_point_ids: Sequence[int],
    priority_face_ids: Sequence[int],
    priorities: Sequence[int],
    *,
    ambiguity_policy: str = "raise",
) -> dict[str, tuple[Any, ...]]:
    """Columnar front door for explicit-priority owner-face selection."""

    incident_count = len(incident_point_ids)
    if (
        len(incident_face_ids) != incident_count
        or len(incident_face_counts) != incident_count
    ):
        raise ValueError("incident point, face, and count columns must have the same length")
    priority_count = len(priority_point_ids)
    priority_lengths_match = (
        len(priority_face_ids) == priority_count
        and len(priorities) == priority_count
    )
    if not priority_lengths_match:
        raise ValueError("priority point, face, and priority columns must have the same length")

    incident_rows = tuple(
        {
            "point_id": int(point_id),
            "face_id": int(face_id),
            "incident_face_count": int(face_count),
        }
        for point_id, face_id, face_count in zip(
            incident_point_ids,
            incident_face_ids,
            incident_face_counts,
        )
    )
    priority_rows = tuple(
        {
            "point_id": int(point_id),
            "face_id": int(face_id),
            "priority": int(priority),
        }
        for point_id, face_id, priority in zip(
            priority_point_ids,
            priority_face_ids,
            priorities,
        )
    )
    selected_rows = select_owner_faces_from_incident_candidates_with_priority(
        incident_rows,
        priority_rows,
        ambiguity_policy=ambiguity_policy,
    )
    return {
        "point_id": tuple(row["point_id"] for row in selected_rows),
        "owner_face_id": tuple(row["owner_face_id"] for row in selected_rows),
        "incident_face_count": tuple(row["incident_face_count"] for row in selected_rows),
        "candidate_count": tuple(row["candidate_count"] for row in selected_rows),
        "selection_status": tuple(row["selection_status"] for row in selected_rows),
    }


def select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
    incident_point_ids,
    incident_face_ids,
    incident_face_counts,
    priority_point_ids,
    priority_face_ids,
    priorities,
    *,
    ambiguity_policy: str = "raise",
    require_unique_incident_pair: bool = True,
    require_unique_priority_pair: bool = True,
) -> dict[str, object]:
    """CuPy device-column continuation for explicit-priority owner-face selection.

    The device continuation emits numeric ``selection_status_code`` values
    instead of the Python reference's ``selection_status`` strings and returns
    ``selection_status_code_labels`` so callers can translate explicitly. It
    fails closed on duplicate incident or priority ``(point_id, face_id)`` pairs
    by default so each row has one deterministic role in the grouped selection.
    """

    if ambiguity_policy not in {"raise", "drop", "emit_ambiguous"}:
        raise ValueError("ambiguity_policy must be 'raise', 'drop', or 'emit_ambiguous'")
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised on CUDA hosts.
        raise RuntimeError("owner-face CuPy selector requires cupy") from exc

    incident_point_ids = cp.asarray(incident_point_ids, dtype=cp.int64)
    incident_face_ids = cp.asarray(incident_face_ids, dtype=cp.int64)
    incident_face_counts = cp.asarray(incident_face_counts, dtype=cp.int64)
    priority_point_ids = cp.asarray(priority_point_ids, dtype=cp.int64)
    priority_face_ids = cp.asarray(priority_face_ids, dtype=cp.int64)
    priorities = cp.asarray(priorities, dtype=cp.int64)

    incident_count = int(incident_point_ids.size)
    if (
        int(incident_face_ids.size) != incident_count
        or int(incident_face_counts.size) != incident_count
    ):
        raise ValueError("incident point, face, and count columns must have the same length")
    priority_count = int(priority_point_ids.size)
    if int(priority_face_ids.size) != priority_count or int(priorities.size) != priority_count:
        raise ValueError("priority point, face, and priority columns must have the same length")

    empty = cp.asarray([], dtype=cp.int64)
    if incident_count == 0:
        return {
            "point_id": empty,
            "owner_face_id": empty,
            "incident_face_count": empty,
            "candidate_count": empty,
            "selection_status_code": empty,
            "selection_status_code_labels": dict(OWNER_FACE_SELECTION_STATUS_CODES),
        }

    int64_max = 9223372036854775807
    all_points = (
        cp.concatenate((incident_point_ids, priority_point_ids))
        if priority_count
        else incident_point_ids
    )
    all_faces = (
        cp.concatenate((incident_face_ids, priority_face_ids))
        if priority_count
        else incident_face_ids
    )
    min_point = int(cp.min(all_points).item())
    max_point = int(cp.max(all_points).item())
    min_face = int(cp.min(all_faces).item())
    max_face = int(cp.max(all_faces).item())
    point_offset = -min_point if min_point < 0 else 0
    face_offset = -min_face if min_face < 0 else 0
    max_point_key = max_point + point_offset
    max_face_key = max_face + face_offset
    base = max_face_key + 1
    if base <= 0 or max_point_key > (int64_max - max_face_key) // base:
        raise OverflowError("point/face ids are too large for the CuPy pair-key selector")

    def pair_keys(point_ids, face_ids):
        return (point_ids + point_offset) * base + (face_ids + face_offset)

    incident_keys = pair_keys(incident_point_ids, incident_face_ids)
    if require_unique_incident_pair and incident_count > 1:
        sorted_incident_keys = cp.sort(incident_keys)
        duplicate_incident = bool(
            cp.any(sorted_incident_keys[1:] == sorted_incident_keys[:-1]).item()
        )
        if duplicate_incident:
            raise ValueError("incident point/face pairs must be unique for the CuPy selector")

    if priority_count:
        priority_keys = pair_keys(priority_point_ids, priority_face_ids)
        priority_order = cp.argsort(priority_keys, kind="stable")
        sorted_priority_keys = priority_keys[priority_order]
        sorted_priorities = priorities[priority_order]
        if require_unique_priority_pair and priority_count > 1:
            duplicate_priority = bool(
                cp.any(sorted_priority_keys[1:] == sorted_priority_keys[:-1]).item()
            )
            if duplicate_priority:
                raise ValueError("priority point/face pairs must be unique for the CuPy selector")
    else:
        sorted_priority_keys = empty
        sorted_priorities = empty

    unique_points, inverse = cp.unique(incident_point_ids, return_inverse=True)
    point_count = int(unique_points.size)
    max_counts = cp.full((point_count,), -9223372036854775808, dtype=cp.int64)
    cp.maximum.at(max_counts, inverse, incident_face_counts)

    winner_mask = incident_face_counts == max_counts[inverse]
    winner_counts = cp.bincount(inverse[winner_mask], minlength=point_count).astype(
        cp.int64, copy=False
    )
    unique_groups = winner_counts == 1
    tied_winner_mask = winner_mask & (winner_counts[inverse] > 1)

    def grouped_mask_count(mask):
        if bool(cp.any(mask).item()):
            return cp.bincount(inverse[mask], minlength=point_count).astype(
                cp.int64, copy=False
            )
        return cp.zeros((point_count,), dtype=cp.int64)

    if priority_count:
        priority_pos = cp.searchsorted(sorted_priority_keys, incident_keys)
        priority_safe_pos = cp.minimum(priority_pos, priority_count - 1)
        priority_found = (
            (priority_pos < priority_count)
            & (sorted_priority_keys[priority_safe_pos] == incident_keys)
        )
        incident_priorities = sorted_priorities[priority_safe_pos]
    else:
        priority_found = cp.zeros((incident_count,), dtype=cp.bool_)
        incident_priorities = cp.zeros((incident_count,), dtype=cp.int64)

    missing_priority_rows = tied_winner_mask & ~priority_found
    missing_priority_counts = grouped_mask_count(missing_priority_rows)
    missing_priority_groups = missing_priority_counts > 0

    if bool(cp.any(missing_priority_groups).item()):
        if ambiguity_policy == "raise":
            raise ValueError("missing owner-face priority for one or more tied points")

    priority_inf = cp.asarray(int64_max, dtype=cp.int64)
    priority_for_min = cp.where(tied_winner_mask & priority_found, incident_priorities, priority_inf)
    min_priorities = cp.full((point_count,), priority_inf, dtype=cp.int64)
    cp.minimum.at(min_priorities, inverse, priority_for_min)
    priority_winner_mask = (
        tied_winner_mask
        & priority_found
        & (incident_priorities == min_priorities[inverse])
    )
    priority_winner_counts = grouped_mask_count(priority_winner_mask)
    ambiguous_priority_groups = (
        (winner_counts > 1)
        & ~missing_priority_groups
        & (priority_winner_counts != 1)
    )
    if bool(cp.any(ambiguous_priority_groups).item()):
        if ambiguity_policy == "raise":
            raise ValueError("ambiguous owner-face priority for one or more tied points")

    owner_face_by_group = cp.full((point_count,), -1, dtype=cp.int64)
    unique_winner_rows = winner_mask & unique_groups[inverse]
    owner_face_by_group[inverse[unique_winner_rows]] = incident_face_ids[unique_winner_rows]
    priority_resolved_groups = (
        (winner_counts > 1)
        & ~missing_priority_groups
        & (priority_winner_counts == 1)
    )
    priority_winner_rows = priority_winner_mask & priority_resolved_groups[inverse]
    owner_face_by_group[inverse[priority_winner_rows]] = incident_face_ids[priority_winner_rows]

    status_by_group = cp.zeros((point_count,), dtype=cp.int64)
    status_by_group[unique_groups] = OWNER_FACE_SELECTION_STATUS_CODES[
        "unique_max_incident_face"
    ]
    status_by_group[priority_resolved_groups] = OWNER_FACE_SELECTION_STATUS_CODES[
        "priority_tie_break"
    ]
    status_by_group[missing_priority_groups] = OWNER_FACE_SELECTION_STATUS_CODES[
        "missing_priority"
    ]
    status_by_group[ambiguous_priority_groups] = OWNER_FACE_SELECTION_STATUS_CODES[
        "ambiguous_priority_tie"
    ]

    candidate_count_by_group = cp.where(
        unique_groups,
        cp.ones((point_count,), dtype=cp.int64),
        winner_counts,
    )
    candidate_count_by_group = cp.where(
        ambiguous_priority_groups,
        priority_winner_counts,
        candidate_count_by_group,
    )

    selected_groups = unique_groups | priority_resolved_groups
    if ambiguity_policy == "emit_ambiguous":
        selected_groups = selected_groups | missing_priority_groups | ambiguous_priority_groups
    elif ambiguity_policy == "drop":
        selected_groups = selected_groups

    return {
        "point_id": unique_points[selected_groups],
        "owner_face_id": owner_face_by_group[selected_groups],
        "incident_face_count": max_counts[selected_groups],
        "candidate_count": candidate_count_by_group[selected_groups],
        "selection_status_code": status_by_group[selected_groups],
        "selection_status_code_labels": dict(OWNER_FACE_SELECTION_STATUS_CODES),
    }


def filter_closed_shape_membership_candidate_columns_by_owner_face_columns(
    candidate_point_ids: Sequence[int],
    candidate_shape_ids: Sequence[int],
    topology_shape_ids: Sequence[int],
    topology_left_face_ids: Sequence[int],
    topology_right_face_ids: Sequence[int],
    owner_point_ids: Sequence[int],
    owner_face_ids: Sequence[int],
    *,
    topology_has_left_faces: Sequence[int] | None = None,
    topology_has_right_faces: Sequence[int] | None = None,
    missing_owner_policy: str = "raise",
) -> dict[str, tuple[int, ...]]:
    """Columnar front door for owner-face membership candidate filtering."""

    candidate_count = len(candidate_point_ids)
    if len(candidate_shape_ids) != candidate_count:
        raise ValueError("candidate point and shape columns must have the same length")

    topology_count = len(topology_shape_ids)
    topology_lengths_match = (
        len(topology_left_face_ids) == topology_count
        and len(topology_right_face_ids) == topology_count
    )
    if not topology_lengths_match:
        raise ValueError("topology shape and face columns must have the same length")
    if (
        topology_has_left_faces is not None
        and len(topology_has_left_faces) != topology_count
    ):
        raise ValueError("topology_has_left_faces must match topology length")
    if (
        topology_has_right_faces is not None
        and len(topology_has_right_faces) != topology_count
    ):
        raise ValueError("topology_has_right_faces must match topology length")

    owner_count = len(owner_point_ids)
    if len(owner_face_ids) != owner_count:
        raise ValueError("owner point and face columns must have the same length")

    candidate_rows = tuple(
        {"point_id": int(point_id), "shape_id": int(shape_id)}
        for point_id, shape_id in zip(candidate_point_ids, candidate_shape_ids)
    )
    topology_rows = []
    for index, shape_id in enumerate(topology_shape_ids):
        row = {
            "shape_id": int(shape_id),
            "left_face_id": int(topology_left_face_ids[index]),
            "right_face_id": int(topology_right_face_ids[index]),
        }
        if topology_has_left_faces is not None:
            row["has_left_face"] = int(topology_has_left_faces[index])
        if topology_has_right_faces is not None:
            row["has_right_face"] = int(topology_has_right_faces[index])
        topology_rows.append(row)

    owner_faces: dict[int, set[int]] = {}
    for point_id, face_id in zip(owner_point_ids, owner_face_ids):
        owner_faces.setdefault(int(point_id), set()).add(int(face_id))

    filtered_rows = filter_closed_shape_membership_candidates_by_owner_face(
        candidate_rows,
        topology_rows,
        owner_faces,
        missing_owner_policy=missing_owner_policy,
    )
    return {
        "point_id": tuple(int(row["point_id"]) for row in filtered_rows),
        "shape_id": tuple(int(row["shape_id"]) for row in filtered_rows),
        "membership": tuple(int(row["membership"]) for row in filtered_rows),
        "owner_face_id": tuple(int(row["owner_face_id"]) for row in filtered_rows),
    }


def filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
    candidate_point_ids,
    candidate_shape_ids,
    topology_shape_ids,
    topology_left_face_ids,
    topology_right_face_ids,
    owner_point_ids,
    owner_face_ids,
    *,
    topology_has_left_faces=None,
    topology_has_right_faces=None,
    missing_owner_policy: str = "raise",
    require_unique_owner_point: bool = True,
    require_unique_candidate_pair: bool = True,
) -> dict[str, object]:
    """CuPy device-column continuation for owner-face membership filtering.

    This helper is a single-owner-face-per-point device continuation. Duplicate
    candidate ``(point_id, shape_id)`` pairs fail closed by default because the
    Python row reference deduplicates them while this device path preserves row
    shape. Use the Python/columnar reference when multiple owner faces per point
    are required.
    """

    if missing_owner_policy not in {"raise", "drop"}:
        raise ValueError("missing_owner_policy must be 'raise' or 'drop'")
    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover - exercised on CUDA hosts.
        raise RuntimeError("owner-face CuPy filter requires cupy") from exc

    candidate_point_ids = cp.asarray(candidate_point_ids, dtype=cp.int64)
    candidate_shape_ids = cp.asarray(candidate_shape_ids, dtype=cp.int64)
    topology_shape_ids = cp.asarray(topology_shape_ids, dtype=cp.int64)
    topology_left_face_ids = cp.asarray(topology_left_face_ids, dtype=cp.int64)
    topology_right_face_ids = cp.asarray(topology_right_face_ids, dtype=cp.int64)
    owner_point_ids = cp.asarray(owner_point_ids, dtype=cp.int64)
    owner_face_ids = cp.asarray(owner_face_ids, dtype=cp.int64)

    candidate_count = int(candidate_point_ids.size)
    if int(candidate_shape_ids.size) != candidate_count:
        raise ValueError("candidate point and shape columns must have the same length")
    topology_count = int(topology_shape_ids.size)
    if (
        int(topology_left_face_ids.size) != topology_count
        or int(topology_right_face_ids.size) != topology_count
    ):
        raise ValueError("topology shape and face columns must have the same length")
    owner_count = int(owner_point_ids.size)
    if int(owner_face_ids.size) != owner_count:
        raise ValueError("owner point and face columns must have the same length")

    if topology_has_left_faces is None:
        topology_has_left_faces = cp.ones((topology_count,), dtype=cp.int8)
    else:
        topology_has_left_faces = cp.asarray(topology_has_left_faces, dtype=cp.int8)
    if topology_has_right_faces is None:
        topology_has_right_faces = cp.ones((topology_count,), dtype=cp.int8)
    else:
        topology_has_right_faces = cp.asarray(topology_has_right_faces, dtype=cp.int8)
    if int(topology_has_left_faces.size) != topology_count:
        raise ValueError("topology_has_left_faces must match topology length")
    if int(topology_has_right_faces.size) != topology_count:
        raise ValueError("topology_has_right_faces must match topology length")

    if candidate_count == 0:
        empty = cp.asarray([], dtype=cp.int64)
        return {
            "point_id": empty,
            "shape_id": empty,
            "membership": empty,
            "owner_face_id": empty,
        }

    if require_unique_candidate_pair and candidate_count > 1:
        candidate_order = cp.lexsort(cp.stack((candidate_shape_ids, candidate_point_ids)))
        sorted_candidate_points = candidate_point_ids[candidate_order]
        sorted_candidate_shapes = candidate_shape_ids[candidate_order]
        duplicate_candidate = bool(
            cp.any(
                (sorted_candidate_points[1:] == sorted_candidate_points[:-1])
                & (sorted_candidate_shapes[1:] == sorted_candidate_shapes[:-1])
            ).item()
        )
        if duplicate_candidate:
            raise ValueError("candidate point/shape pairs must be unique for the CuPy filter")

    if owner_count == 0:
        owner_found = cp.zeros((candidate_count,), dtype=cp.bool_)
        owner_faces = cp.zeros((candidate_count,), dtype=cp.int64)
    else:
        owner_order = cp.argsort(owner_point_ids, kind="stable")
        sorted_owner_points = owner_point_ids[owner_order]
        sorted_owner_faces = owner_face_ids[owner_order]
        if owner_count > 1:
            duplicate_owner = bool(
                cp.any(sorted_owner_points[1:] == sorted_owner_points[:-1]).item()
            )
            if duplicate_owner:
                if require_unique_owner_point:
                    raise ValueError("owner point ids must be unique for the CuPy filter")
                raise ValueError(
                    "multiple owner faces per point are not supported by the CuPy filter"
                )
        owner_pos = cp.searchsorted(sorted_owner_points, candidate_point_ids)
        owner_safe_pos = cp.minimum(owner_pos, owner_count - 1)
        owner_found = (
            (owner_pos < owner_count)
            & (sorted_owner_points[owner_safe_pos] == candidate_point_ids)
        )
        owner_faces = sorted_owner_faces[owner_safe_pos]

    if missing_owner_policy == "raise" and bool(cp.any(~owner_found).item()):
        raise KeyError("missing owner face id for one or more point ids")

    if topology_count == 0:
        topology_found = cp.zeros((candidate_count,), dtype=cp.bool_)
        left_faces = cp.zeros((candidate_count,), dtype=cp.int64)
        right_faces = cp.zeros((candidate_count,), dtype=cp.int64)
        has_left = cp.zeros((candidate_count,), dtype=cp.bool_)
        has_right = cp.zeros((candidate_count,), dtype=cp.bool_)
    else:
        topology_order = cp.argsort(topology_shape_ids, kind="stable")
        sorted_shape_ids = topology_shape_ids[topology_order]
        sorted_left_faces = topology_left_face_ids[topology_order]
        sorted_right_faces = topology_right_face_ids[topology_order]
        sorted_has_left = topology_has_left_faces[topology_order].astype(cp.bool_, copy=False)
        sorted_has_right = topology_has_right_faces[topology_order].astype(cp.bool_, copy=False)
        topology_pos = cp.searchsorted(sorted_shape_ids, candidate_shape_ids)
        topology_safe_pos = cp.minimum(topology_pos, topology_count - 1)
        topology_found = (
            (topology_pos < topology_count)
            & (sorted_shape_ids[topology_safe_pos] == candidate_shape_ids)
        )
        left_faces = sorted_left_faces[topology_safe_pos]
        right_faces = sorted_right_faces[topology_safe_pos]
        has_left = sorted_has_left[topology_safe_pos]
        has_right = sorted_has_right[topology_safe_pos]

    matches_left = has_left & (left_faces >= 0) & (left_faces == owner_faces)
    matches_right = has_right & (right_faces >= 0) & (right_faces == owner_faces)
    keep = owner_found & topology_found & (matches_left | matches_right)
    unmatched_face = cp.full((candidate_count,), 9223372036854775807, dtype=cp.int64)
    matched_left_faces = cp.where(matches_left, left_faces, unmatched_face)
    matched_right_faces = cp.where(matches_right, right_faces, unmatched_face)
    kept_owner_faces = cp.minimum(matched_left_faces, matched_right_faces)[keep]
    return {
        "point_id": candidate_point_ids[keep],
        "shape_id": candidate_shape_ids[keep],
        "membership": cp.ones((int(cp.count_nonzero(keep).item()),), dtype=cp.int64),
        "owner_face_id": kept_owner_faces.astype(cp.int64, copy=False),
    }


def run_closed_shape_owner_face_priority_membership_pipeline_cupy(
    incident_point_ids,
    incident_face_ids,
    incident_face_counts,
    priority_point_ids,
    priority_face_ids,
    priorities,
    candidate_point_ids,
    candidate_shape_ids,
    topology_shape_ids,
    topology_left_face_ids,
    topology_right_face_ids,
    *,
    topology_has_left_faces=None,
    topology_has_right_faces=None,
    ambiguity_policy: str = "raise",
    missing_owner_policy: str = "raise",
) -> dict[str, object]:
    """Compose CuPy owner-face selection and membership filtering on columns."""

    selected = select_owner_faces_from_incident_candidate_columns_with_priority_cupy(
        incident_point_ids=incident_point_ids,
        incident_face_ids=incident_face_ids,
        incident_face_counts=incident_face_counts,
        priority_point_ids=priority_point_ids,
        priority_face_ids=priority_face_ids,
        priorities=priorities,
        ambiguity_policy=ambiguity_policy,
    )
    filtered = filter_closed_shape_membership_candidate_columns_by_owner_face_cupy(
        candidate_point_ids=candidate_point_ids,
        candidate_shape_ids=candidate_shape_ids,
        topology_shape_ids=topology_shape_ids,
        topology_left_face_ids=topology_left_face_ids,
        topology_right_face_ids=topology_right_face_ids,
        topology_has_left_faces=topology_has_left_faces,
        topology_has_right_faces=topology_has_right_faces,
        owner_point_ids=selected["point_id"],
        owner_face_ids=selected["owner_face_id"],
        missing_owner_policy=missing_owner_policy,
    )
    return {
        "point_id": filtered["point_id"],
        "shape_id": filtered["shape_id"],
        "membership": filtered["membership"],
        "owner_face_id": filtered["owner_face_id"],
        "selection_point_id": selected["point_id"],
        "selection_owner_face_id": selected["owner_face_id"],
        "selection_incident_face_count": selected["incident_face_count"],
        "selection_candidate_count": selected["candidate_count"],
        "selection_status_code": selected["selection_status_code"],
        "selection_status_code_labels": selected["selection_status_code_labels"],
    }


def run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy(
    incident_point_ids,
    incident_face_ids,
    incident_face_counts,
    priority_point_ids,
    priority_face_ids,
    priorities,
    candidate_point_ids,
    candidate_shape_ids,
    topology_shape_ids,
    topology_left_face_ids,
    topology_right_face_ids,
    *,
    selected_point_ids,
    topology_has_left_faces=None,
    topology_has_right_faces=None,
    ambiguity_policy: str = "raise",
    missing_owner_policy: str = "raise",
) -> dict[str, object]:
    """Filter only caller-selected ambiguous point candidates, pass others through.

    The caller supplies ``selected_point_ids`` as the explicit ambiguity set.
    RTDL does not infer which points need owner-face reconciliation.
    """

    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("CuPy is required for owner-face selective pipeline continuation") from exc

    candidate_point_ids = cp.asarray(candidate_point_ids, dtype=cp.int64)
    candidate_shape_ids = cp.asarray(candidate_shape_ids, dtype=cp.int64)
    selected_point_ids = cp.asarray(selected_point_ids, dtype=cp.int64)
    if int(candidate_point_ids.size) != int(candidate_shape_ids.size):
        raise ValueError("candidate point and shape columns must have the same length")

    candidate_count = int(candidate_point_ids.size)
    selected_mask = cp.isin(candidate_point_ids, selected_point_ids) if selected_point_ids.size else cp.zeros(
        candidate_count,
        dtype=cp.bool_,
    )
    passthrough_mask = ~selected_mask
    passthrough_point_ids = candidate_point_ids[passthrough_mask]
    passthrough_shape_ids = candidate_shape_ids[passthrough_mask]
    passthrough_count = int(passthrough_point_ids.size)
    passthrough_membership = cp.ones((passthrough_count,), dtype=cp.int64)
    passthrough_owner_face_ids = cp.full((passthrough_count,), -1, dtype=cp.int64)

    selected_candidate_count = int(cp.count_nonzero(selected_mask).item())
    if selected_candidate_count:
        selected_result = run_closed_shape_owner_face_priority_membership_pipeline_cupy(
            incident_point_ids=incident_point_ids,
            incident_face_ids=incident_face_ids,
            incident_face_counts=incident_face_counts,
            priority_point_ids=priority_point_ids,
            priority_face_ids=priority_face_ids,
            priorities=priorities,
            candidate_point_ids=candidate_point_ids[selected_mask],
            candidate_shape_ids=candidate_shape_ids[selected_mask],
            topology_shape_ids=topology_shape_ids,
            topology_left_face_ids=topology_left_face_ids,
            topology_right_face_ids=topology_right_face_ids,
            topology_has_left_faces=topology_has_left_faces,
            topology_has_right_faces=topology_has_right_faces,
            ambiguity_policy=ambiguity_policy,
            missing_owner_policy=missing_owner_policy,
        )
        selected_point_out = selected_result["point_id"]
        selected_shape_out = selected_result["shape_id"]
        selected_membership = selected_result["membership"]
        selected_owner_face_ids = selected_result["owner_face_id"]
    else:
        empty = cp.asarray((), dtype=cp.int64)
        selected_result = {
            "selection_point_id": empty,
            "selection_owner_face_id": empty,
            "selection_incident_face_count": empty,
            "selection_candidate_count": empty,
            "selection_status_code": empty,
            "selection_status_code_labels": OWNER_FACE_SELECTION_STATUS_CODES,
        }
        selected_point_out = empty
        selected_shape_out = empty
        selected_membership = empty
        selected_owner_face_ids = empty

    point_out = cp.concatenate((passthrough_point_ids, selected_point_out))
    shape_out = cp.concatenate((passthrough_shape_ids, selected_shape_out))
    membership_out = cp.concatenate((passthrough_membership, selected_membership))
    owner_face_out = cp.concatenate((passthrough_owner_face_ids, selected_owner_face_ids))
    if int(point_out.size) > 1:
        order = cp.lexsort(cp.stack((shape_out, point_out)))
        point_out = point_out[order]
        shape_out = shape_out[order]
        membership_out = membership_out[order]
        owner_face_out = owner_face_out[order]

    return {
        "point_id": point_out,
        "shape_id": shape_out,
        "membership": membership_out,
        "owner_face_id": owner_face_out,
        "selection_point_id": selected_result["selection_point_id"],
        "selection_owner_face_id": selected_result["selection_owner_face_id"],
        "selection_incident_face_count": selected_result["selection_incident_face_count"],
        "selection_candidate_count": selected_result["selection_candidate_count"],
        "selection_status_code": selected_result["selection_status_code"],
        "selection_status_code_labels": selected_result["selection_status_code_labels"],
        "selected_candidate_row_count": selected_candidate_count,
        "passthrough_candidate_row_count": passthrough_count,
        "selected_point_filter_mode": "caller_supplied_ambiguity_set",
    }


def run_selective_closed_shape_boundary_event_membership_pipeline_cupy(
    candidate_point_ids,
    candidate_shape_ids,
    boundary_point_ids,
    boundary_shape_ids,
    boundary_crossing_t,
    *,
    selected_point_ids,
    crossing_tolerance: float = 0.0,
) -> dict[str, object]:
    """Filter selected candidates through generic zero-boundary event pairs.

    The caller supplies ``selected_point_ids``. RTDL does not infer which points
    need boundary-event reconciliation. Non-selected candidate rows pass through
    unchanged.
    """

    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("CuPy is required for boundary-event selective continuation") from exc

    candidate_point_ids = cp.asarray(candidate_point_ids, dtype=cp.int64)
    candidate_shape_ids = cp.asarray(candidate_shape_ids, dtype=cp.int64)
    boundary_point_ids = cp.asarray(boundary_point_ids, dtype=cp.int64)
    boundary_shape_ids = cp.asarray(boundary_shape_ids, dtype=cp.int64)
    boundary_crossing_t = cp.asarray(boundary_crossing_t, dtype=cp.float64)
    selected_point_ids = cp.asarray(selected_point_ids, dtype=cp.int64)
    if int(candidate_point_ids.size) != int(candidate_shape_ids.size):
        raise ValueError("candidate point and shape columns must have the same length")
    if (
        int(boundary_point_ids.size) != int(boundary_shape_ids.size)
        or int(boundary_point_ids.size) != int(boundary_crossing_t.size)
    ):
        raise ValueError("boundary point, shape, and crossing_t columns must have the same length")
    if crossing_tolerance < 0.0:
        raise ValueError("crossing_tolerance must be non-negative")

    candidate_count = int(candidate_point_ids.size)
    selected_mask = cp.isin(candidate_point_ids, selected_point_ids) if selected_point_ids.size else cp.zeros(
        candidate_count,
        dtype=cp.bool_,
    )
    selected_candidate_count = int(cp.count_nonzero(selected_mask).item())
    passthrough_mask = ~selected_mask
    passthrough_count = int(cp.count_nonzero(passthrough_mask).item())

    if candidate_count == 0:
        empty = cp.asarray((), dtype=cp.int64)
        return {
            "point_id": empty,
            "shape_id": empty,
            "membership": empty,
            "boundary_event_filter_status": empty,
            "selected_candidate_row_count": 0,
            "passthrough_candidate_row_count": 0,
            "selected_kept_row_count": 0,
            "selected_dropped_row_count": 0,
            "selected_point_filter_mode": "caller_supplied_ambiguity_set",
            "boundary_event_filter": "candidate_pair_has_zero_crossing_t",
            "crossing_tolerance": float(crossing_tolerance),
        }

    zero_boundary_mask = cp.abs(boundary_crossing_t) <= float(crossing_tolerance)
    zero_boundary_count = int(cp.count_nonzero(zero_boundary_mask).item())
    if zero_boundary_count:
        key_points = cp.concatenate((candidate_point_ids, boundary_point_ids[zero_boundary_mask]))
        key_shapes = cp.concatenate((candidate_shape_ids, boundary_shape_ids[zero_boundary_mask]))
    else:
        key_points = candidate_point_ids
        key_shapes = candidate_shape_ids

    int64_max = 9223372036854775807
    min_point = int(cp.min(key_points).item())
    max_point = int(cp.max(key_points).item())
    min_shape = int(cp.min(key_shapes).item())
    max_shape = int(cp.max(key_shapes).item())
    point_offset = -min_point if min_point < 0 else 0
    shape_offset = -min_shape if min_shape < 0 else 0
    max_point_key = max_point + point_offset
    max_shape_key = max_shape + shape_offset
    base = max_shape_key + 1
    if base <= 0 or max_point_key > (int64_max - max_shape_key) // base:
        raise OverflowError("point/shape ids are too large for the CuPy boundary-event pair-key filter")

    def pair_keys(point_ids, shape_ids):
        return (point_ids + point_offset) * base + (shape_ids + shape_offset)

    candidate_keys = pair_keys(candidate_point_ids, candidate_shape_ids)
    selected_keep = cp.zeros((candidate_count,), dtype=cp.bool_)
    if zero_boundary_count and selected_candidate_count:
        zero_keys = cp.sort(
            cp.unique(pair_keys(boundary_point_ids[zero_boundary_mask], boundary_shape_ids[zero_boundary_mask]))
        )
        candidate_pos = cp.searchsorted(zero_keys, candidate_keys)
        safe_pos = cp.minimum(candidate_pos, int(zero_keys.size) - 1)
        found = (candidate_pos < int(zero_keys.size)) & (zero_keys[safe_pos] == candidate_keys)
        selected_keep = selected_mask & found

    keep = passthrough_mask | selected_keep
    point_out = candidate_point_ids[keep]
    shape_out = candidate_shape_ids[keep]
    membership_out = cp.ones((int(point_out.size),), dtype=cp.int64)
    status = cp.where(selected_mask[keep], cp.asarray(1, dtype=cp.int64), cp.asarray(0, dtype=cp.int64))
    if int(point_out.size) > 1:
        order = cp.lexsort(cp.stack((shape_out, point_out)))
        point_out = point_out[order]
        shape_out = shape_out[order]
        membership_out = membership_out[order]
        status = status[order]

    selected_kept_count = int(cp.count_nonzero(selected_keep).item())
    return {
        "point_id": point_out,
        "shape_id": shape_out,
        "membership": membership_out,
        "boundary_event_filter_status": status,
        "selected_candidate_row_count": selected_candidate_count,
        "passthrough_candidate_row_count": passthrough_count,
        "selected_kept_row_count": selected_kept_count,
        "selected_dropped_row_count": selected_candidate_count - selected_kept_count,
        "selected_point_filter_mode": "caller_supplied_ambiguity_set",
        "boundary_event_filter": "candidate_pair_has_zero_crossing_t",
        "crossing_tolerance": float(crossing_tolerance),
    }


def materialize_closed_shape_membership_rows_as_cupy_columns(
    rows: Iterable[Mapping[str, Any]],
    *,
    source_protocol: str = "host_refined_exact_rows",
    sort_output: bool = True,
) -> dict[str, object]:
    """Upload exact closed-shape membership rows into CuPy columns.

    This is a bounded bridge for partner continuations that need exact
    membership rows today. It does not claim true zero-copy or a native exact
    device-row producer: callers have already materialized exact rows on the
    host, typically through an RTDL backend's exact prepared run path.
    """

    try:
        import cupy as cp  # type: ignore
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("CuPy is required to materialize exact membership rows as partner columns") from exc

    point_values: list[int] = []
    shape_values: list[int] = []
    membership_values: list[int] = []
    for row in rows:
        if "point_id" in row:
            point_id = row["point_id"]
        elif "left_id" in row:
            point_id = row["left_id"]
        else:
            raise KeyError("membership row must expose point_id or left_id")
        if "shape_id" in row:
            shape_id = row["shape_id"]
        elif "right_id" in row:
            shape_id = row["right_id"]
        else:
            raise KeyError("membership row must expose shape_id or right_id")
        point_values.append(int(point_id))
        shape_values.append(int(shape_id))
        membership_values.append(int(row.get("membership", 1)))

    point_out = cp.asarray(point_values, dtype=cp.int64)
    shape_out = cp.asarray(shape_values, dtype=cp.int64)
    membership_out = cp.asarray(membership_values, dtype=cp.int64)
    if sort_output and int(point_out.size) > 1:
        order = cp.lexsort(cp.stack((shape_out, point_out)))
        point_out = point_out[order]
        shape_out = shape_out[order]
        membership_out = membership_out[order]

    return {
        "point_id": point_out,
        "shape_id": shape_out,
        "membership": membership_out,
        "row_count": int(point_out.size),
        "source_protocol": str(source_protocol),
        "output_residency": "partner_device_after_host_refine_upload",
        "host_refined_rows_materialized": True,
        "native_exact_device_row_stream_produced": False,
        "true_zero_copy_claim_authorized": False,
        "release_authorized": False,
        "public_speedup_claim_authorized": False,
        "rt_core_speedup_claim_authorized": False,
    }


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
            "derive_owner_face_priority_columns_from_rank_signals",
        ),
        "optional_columnar_pipeline_helpers": (
            "select_owner_faces_from_incident_candidate_columns_with_priority_columns",
            "select_owner_faces_from_incident_candidate_columns_with_priority_cupy",
            "filter_closed_shape_membership_candidate_columns_by_owner_face_columns",
            "filter_closed_shape_membership_candidate_columns_by_owner_face_cupy",
            "run_closed_shape_owner_face_priority_membership_pipeline_cupy",
            "run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy",
            "run_selective_closed_shape_boundary_event_membership_pipeline_cupy",
        ),
        "selection_rule": {
            "primary": "higher incident_face_count wins",
            "tie_break": "lower caller_supplied_priority wins",
            "missing_priority": "fail_closed",
            "tied_priority": "fail_closed",
            "native_engine_may_invent_priority": False,
        },
        "filter_policy": {
            "missing_owner": "fail_closed_by_default",
            "missing_topology": "drop_candidate",
            "topology_face_presence_columns": "gate_left_and_right_face_ids_when_present",
            "device_cupy_filter_candidate_duplicates": "fail_closed_by_default",
            "device_cupy_filter_face_ids": "non_negative_matches_only",
            "device_cupy_filter_owner_multiplicity": "single_owner_face_per_point_only",
        },
        "outputs": ("point_id", "shape_id", "membership", "owner_face_id"),
        "app_agnostic": True,
        "caller_policy_required": True,
        "native_engine_may_infer_app_ownership": False,
        "native_lowering_status": "blocked_until_contract_stable_and_validated",
        "promotion_requirements": (
            "deterministic priority derivation contract or explicit caller priority columns",
            "same-contract tests against the Python reference",
            "explicit selection_status_code to selection_status translation at path boundaries",
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
    filter_policy = contract["filter_policy"]
    if (
        not isinstance(filter_policy, Mapping)
        or filter_policy.get("missing_topology") != "drop_candidate"
        or filter_policy.get("missing_owner") != "fail_closed_by_default"
        or filter_policy.get("topology_face_presence_columns")
        != "gate_left_and_right_face_ids_when_present"
        or filter_policy.get("device_cupy_filter_candidate_duplicates")
        != "fail_closed_by_default"
        or filter_policy.get("device_cupy_filter_face_ids") != "non_negative_matches_only"
        or filter_policy.get("device_cupy_filter_owner_multiplicity")
        != "single_owner_face_per_point_only"
    ):
        raise ValueError("owner-face priority pipeline filter policy must stay explicit")
    inputs = contract["inputs"]
    if not isinstance(inputs, tuple) or not any("priority_rows" in item for item in inputs):
        raise ValueError("owner-face priority pipeline must require explicit priority rows")
    promotion_requirements = contract["promotion_requirements"]
    if (
        not isinstance(promotion_requirements, tuple)
        or not any("selection_status_code" in item for item in promotion_requirements)
    ):
        raise ValueError("owner-face priority pipeline must document status-code translation")
    helpers = contract["optional_priority_derivation_helpers"]
    if (
        not isinstance(helpers, tuple)
        or "derive_owner_face_priority_rows_from_rank_signals" not in helpers
        or "derive_owner_face_priority_columns_from_rank_signals" not in helpers
    ):
        raise ValueError("owner-face priority pipeline must expose rank-signal derivation helpers")
    columnar_helpers = contract["optional_columnar_pipeline_helpers"]
    if (
        not isinstance(columnar_helpers, tuple)
        or "select_owner_faces_from_incident_candidate_columns_with_priority_columns"
        not in columnar_helpers
        or "select_owner_faces_from_incident_candidate_columns_with_priority_cupy"
        not in columnar_helpers
        or "filter_closed_shape_membership_candidate_columns_by_owner_face_columns"
        not in columnar_helpers
        or "filter_closed_shape_membership_candidate_columns_by_owner_face_cupy"
        not in columnar_helpers
        or "run_closed_shape_owner_face_priority_membership_pipeline_cupy"
        not in columnar_helpers
        or "run_selective_closed_shape_owner_face_priority_membership_pipeline_cupy"
        not in columnar_helpers
        or "run_selective_closed_shape_boundary_event_membership_pipeline_cupy"
        not in columnar_helpers
    ):
        raise ValueError("owner-face priority pipeline must expose columnar selection helpers")
    boundary = contract["claim_boundary"]
    if not isinstance(boundary, Mapping) or any(bool(value) for value in boundary.values()):
        raise ValueError("owner-face priority pipeline claim boundary must stay blocked")
    return contract
