"""Bounded Sui-derived sphere-trajectory/obstacle-edge case study."""

from .bounded_piecewise_linear_core import (
    BoundedEdgeCrossingProblem,
    ObstacleEdge,
    ObstacleTriangle,
    RTCCDBooleanResult,
    SweptSphereSegment,
    deduplicate_triangle_edges,
    execute_registered_problem,
    trajectory_to_swept_segments,
)

__all__ = [
    "BoundedEdgeCrossingProblem", "ObstacleEdge", "ObstacleTriangle",
    "RTCCDBooleanResult", "SweptSphereSegment",
    "deduplicate_triangle_edges", "execute_registered_problem",
    "trajectory_to_swept_segments",
]
