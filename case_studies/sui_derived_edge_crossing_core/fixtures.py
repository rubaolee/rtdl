"""Exact adapter from the frozen Goal5834-B1 bytes to Goal5835 concepts."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

from .bounded_piecewise_linear_core import (
    BoundedEdgeCrossingProblem,
    ObstacleEdge,
    ObstacleTriangle,
    SweptSphereSegment,
    deduplicate_triangle_edges,
)


FIXTURE_AUTHORITY_SHA256 = \
    "0f13ab8a7408c253114c56a51645c015d0e5e36ca96a4290c9dd1a2ba700adad"
WORKER_INPUTS_SHA256 = \
    "55eeff377c93c32fed8cc326ad975cb9d2437df85812e30b9d916b3e7cc581a4"


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load(path: Path):
    return json.loads(path.read_text(
        encoding="utf-8", errors="strict"),
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-standard JSON constant {value}")))


@dataclass(frozen=True)
class RegisteredMappedCase:
    family_id: str
    execution_id: str
    problem: BoundedEdgeCrossingProblem
    frozen_static_input: dict[str, object]
    frozen_queries: tuple[tuple[tuple[float, ...], tuple[float, ...]], ...]
    public_static_input_commitment_sha256: str
    public_query_commitment_sha256: str


def _problem_from_worker_row(row):
    static = row["static_input"]
    points = tuple(tuple(value) for value in static["control_points"])
    widths = tuple(static["widths"])
    segments = []
    for primitive_index, (point_index, application_id) in enumerate(zip(
            static["segment_indices"], static["application_ids"])):
        radius = widths[point_index]
        if widths[point_index + 1] != radius:
            raise RuntimeError("Goal5835 requires constant-radius path segments")
        segments.append(SweptSphereSegment(
            sphere_id=primitive_index,
            path_segment_id=application_id,
            start=points[point_index],
            end=points[point_index + 1],
            radius=radius,
        ))
    queries = tuple((tuple(start), tuple(end)) for start, end in row["queries"])
    edges = tuple(ObstacleEdge(
        f"{row['execution_id']}:edge:{index}", start, end,
        ("face_boundary_triangle",)
        if row["execution_id"] == "face_interior_only_boundary" else (),
    ) for index, (start, end) in enumerate(queries))
    problem = BoundedEdgeCrossingProblem(
        row["execution_id"], tuple(segments), edges)
    return RegisteredMappedCase(
        row["family_id"], row["execution_id"], problem,
        static, queries,
        row["public_static_input_commitment_sha256"],
        row["public_query_commitment_sha256"],
    )


def _verify_face_triangle(case):
    queries = case.frozen_queries
    triangle = ObstacleTriangle(
        "face_boundary_triangle", ("a", "b", "c"),
        (queries[0][0], queries[0][1], queries[1][1]))
    edges = deduplicate_triangle_edges((triangle,))
    observed = tuple((row.start, row.end) for row in edges)
    # Dedup output is key-sorted; compare as directed-segment sets because the
    # Boolean finite query is invariant under reversal on this frozen domain.
    canonical = lambda edge: tuple(sorted(edge))
    if {canonical(row) for row in observed} != \
            {canonical(row) for row in queries}:
        raise RuntimeError("face-boundary triangle does not reconstruct queries")


def load_registered_cases(fixture_authority_path, worker_inputs_path):
    authority_path = Path(fixture_authority_path).resolve(strict=True)
    worker_path = Path(worker_inputs_path).resolve(strict=True)
    if _sha(authority_path) != FIXTURE_AUTHORITY_SHA256 \
            or _sha(worker_path) != WORKER_INPUTS_SHA256:
        raise RuntimeError("Goal5835 requires exact Goal5834-B1 frozen bytes")
    authority = _load(authority_path)
    worker = _load(worker_path)
    if authority["worker_inputs"]["sha256"] != WORKER_INPUTS_SHA256 \
            or authority["goal5835_authorized"] is not False \
            or worker["contains_expected_output"] is not False \
            or worker["contains_pairwise_geometry_result"] is not False:
        raise RuntimeError("frozen prerequisite authority differs")
    cases = tuple(_problem_from_worker_row(row) for row in worker["rows"])
    if len(cases) != 11 or len({row.family_id for row in cases}) != 10:
        raise RuntimeError("Goal5835 registered denominator differs")
    face = next(row for row in cases
                if row.execution_id == "face_interior_only_boundary")
    _verify_face_triangle(face)
    return cases


__all__ = [
    "FIXTURE_AUTHORITY_SHA256", "RegisteredMappedCase",
    "WORKER_INPUTS_SHA256", "load_registered_cases",
]
