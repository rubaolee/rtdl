from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
import statistics
import sys
import time
from pathlib import Path


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))


EPSILON = 1.0e-9
DATASETS = ("tiny", "scaled")
MODES = (
    "cpu_reference",
    "embree_prepared",
    "optix_prepared",
    "embree_prepared_buffers",
    "optix_prepared_buffers",
    "optix_prepared_device_buffers",
    "optix_prepared_device_count",
)
PREPARED_BACKENDS = ("embree", "optix")
DEFAULT_REPEAT_COUNT = 7
DEFAULT_WARMUP_COUNT = 2
PROBE_Z_START = 1.0
PROBE_Z_END = -1.0


@dataclass(frozen=True)
class Point2:
    x: float
    y: float


@dataclass(frozen=True)
class Triangle2:
    id: int
    x0: float
    y0: float
    x1: float
    y1: float
    x2: float
    y2: float

    def points(self) -> tuple[Point2, Point2, Point2]:
        return (
            Point2(self.x0, self.y0),
            Point2(self.x1, self.y1),
            Point2(self.x2, self.y2),
        )


@dataclass(frozen=True)
class LinkMesh2D:
    link_id: int
    name: str
    local_center_x: float
    local_center_y: float
    width: float
    height: float


@dataclass(frozen=True)
class Pose2D:
    pose_id: int
    base_x: float
    base_y: float
    theta_degrees: float
    label: str


@dataclass(frozen=True)
class RobotCollisionCase:
    dataset: str
    obstacle_triangles: tuple[Triangle2, ...]
    links: tuple[LinkMesh2D, ...]
    poses: tuple[Pose2D, ...]
    expected_link_flags: dict[tuple[int, int], bool] | None
    note: str


@dataclass(frozen=True)
class ProbeGroup:
    pose_id: int
    pose_label: str
    link_id: int
    link_name: str


@dataclass(frozen=True)
class SegmentProbeContract:
    static_triangles_3d: tuple[object, ...]
    segment_start_xyz: tuple[tuple[float, float, float], ...]
    segment_end_xyz: tuple[tuple[float, float, float], ...]
    segment_group_offsets: tuple[int, ...]
    groups: tuple[ProbeGroup, ...]
    probe_points_per_group: int
    lowering_policy: str


def _json_ready(value):
    if isinstance(value, tuple):
        return [_json_ready(item) for item in value]
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, bool | int | float | str) or value is None:
        return value
    if hasattr(value, "__dict__"):
        return _json_ready(value.__dict__)
    return value


def _signed_area(a: Point2, b: Point2, c: Point2) -> float:
    return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x)


def _point_on_segment(point: Point2, a: Point2, b: Point2) -> bool:
    if abs(_signed_area(a, b, point)) > EPSILON:
        return False
    return (
        min(a.x, b.x) - EPSILON <= point.x <= max(a.x, b.x) + EPSILON
        and min(a.y, b.y) - EPSILON <= point.y <= max(a.y, b.y) + EPSILON
    )


def _segments_intersect(a: Point2, b: Point2, c: Point2, d: Point2) -> bool:
    ab_c = _signed_area(a, b, c)
    ab_d = _signed_area(a, b, d)
    cd_a = _signed_area(c, d, a)
    cd_b = _signed_area(c, d, b)

    if abs(ab_c) <= EPSILON and _point_on_segment(c, a, b):
        return True
    if abs(ab_d) <= EPSILON and _point_on_segment(d, a, b):
        return True
    if abs(cd_a) <= EPSILON and _point_on_segment(a, c, d):
        return True
    if abs(cd_b) <= EPSILON and _point_on_segment(b, c, d):
        return True
    return (ab_c > 0.0) != (ab_d > 0.0) and (cd_a > 0.0) != (cd_b > 0.0)


def _point_in_triangle(point: Point2, tri: Triangle2) -> bool:
    a, b, c = tri.points()
    areas = (
        _signed_area(a, b, point),
        _signed_area(b, c, point),
        _signed_area(c, a, point),
    )
    has_negative = any(area < -EPSILON for area in areas)
    has_positive = any(area > EPSILON for area in areas)
    return not (has_negative and has_positive)


def triangles_intersect(left: Triangle2, right: Triangle2) -> bool:
    left_points = left.points()
    right_points = right.points()
    left_edges = tuple(zip(left_points, left_points[1:] + left_points[:1]))
    right_edges = tuple(zip(right_points, right_points[1:] + right_points[:1]))
    for a, b in left_edges:
        for c, d in right_edges:
            if _segments_intersect(a, b, c, d):
                return True
    if any(_point_in_triangle(point, right) for point in left_points):
        return True
    return any(_point_in_triangle(point, left) for point in right_points)


def _rect_triangles(rect_id: int, x0: float, y0: float, x1: float, y1: float) -> tuple[Triangle2, Triangle2]:
    return (
        Triangle2(id=rect_id * 2, x0=x0, y0=y0, x1=x1, y1=y0, x2=x1, y2=y1),
        Triangle2(id=rect_id * 2 + 1, x0=x0, y0=y0, x1=x1, y1=y1, x2=x0, y2=y1),
    )


def _transform_point(local_x: float, local_y: float, pose: Pose2D) -> Point2:
    radians = math.radians(pose.theta_degrees)
    cos_t = math.cos(radians)
    sin_t = math.sin(radians)
    return Point2(
        x=pose.base_x + local_x * cos_t - local_y * sin_t,
        y=pose.base_y + local_x * sin_t + local_y * cos_t,
    )


def transformed_link_triangles(link: LinkMesh2D, pose: Pose2D) -> tuple[Triangle2, Triangle2]:
    half_w = link.width / 2.0
    half_h = link.height / 2.0
    vertices = (
        (link.local_center_x - half_w, link.local_center_y - half_h),
        (link.local_center_x + half_w, link.local_center_y - half_h),
        (link.local_center_x + half_w, link.local_center_y + half_h),
        (link.local_center_x - half_w, link.local_center_y + half_h),
    )
    p0, p1, p2, p3 = tuple(_transform_point(x, y, pose) for x, y in vertices)
    base_id = pose.pose_id * 100_000 + link.link_id * 100
    return (
        Triangle2(base_id, p0.x, p0.y, p1.x, p1.y, p2.x, p2.y),
        Triangle2(base_id + 1, p0.x, p0.y, p2.x, p2.y, p3.x, p3.y),
    )


def _default_links(link_count: int = 2) -> tuple[LinkMesh2D, ...]:
    if link_count < 1:
        raise ValueError("link_count must be positive")
    links = []
    for index in range(link_count):
        links.append(
            LinkMesh2D(
                link_id=index + 1,
                name=f"link_{index + 1}",
                local_center_x=0.8 * index,
                local_center_y=0.0,
                width=0.6 if index == 0 else 0.58,
                height=0.30 if index == 0 else 0.25,
            )
        )
    return tuple(links)


def make_tiny_case() -> RobotCollisionCase:
    links = _default_links(2)
    obstacle_triangles = _rect_triangles(100, x0=2.0, y0=-0.6, x1=3.0, y1=0.6)
    poses = (
        Pose2D(1, base_x=0.0, base_y=0.0, theta_degrees=0.0, label="clear_left"),
        Pose2D(2, base_x=1.4, base_y=0.0, theta_degrees=0.0, label="forearm_hits"),
        Pose2D(3, base_x=2.4, base_y=0.0, theta_degrees=0.0, label="both_links_hit"),
        Pose2D(4, base_x=3.7, base_y=0.0, theta_degrees=0.0, label="clear_right"),
        Pose2D(5, base_x=2.5, base_y=1.1, theta_degrees=-90.0, label="rotated_forearm_hits"),
    )
    expected = {
        (1, 1): False,
        (1, 2): False,
        (2, 1): False,
        (2, 2): True,
        (3, 1): True,
        (3, 2): True,
        (4, 1): False,
        (4, 2): False,
        (5, 1): False,
        (5, 2): True,
    }
    return RobotCollisionCase(
        dataset="tiny",
        obstacle_triangles=obstacle_triangles,
        links=links,
        poses=poses,
        expected_link_flags=expected,
        note="Five deterministic two-link poses against one static rectangular obstacle.",
    )


def make_scaled_case(*, pose_count: int, obstacle_count: int, link_count: int) -> RobotCollisionCase:
    if pose_count < 1:
        raise ValueError("pose_count must be positive")
    if obstacle_count < 1:
        raise ValueError("obstacle_count must be positive")
    links = _default_links(link_count)
    grid = int(math.ceil(math.sqrt(obstacle_count)))
    obstacles: list[Triangle2] = []
    for obstacle_index in range(obstacle_count):
        gx = obstacle_index % grid
        gy = obstacle_index // grid
        x0 = gx * 2.2 + 2.0
        y0 = gy * 1.8 - 0.6
        obstacles.extend(_rect_triangles(1_000 + obstacle_index, x0=x0, y0=y0, x1=x0 + 1.0, y1=y0 + 1.2))
    poses: list[Pose2D] = []
    for index in range(pose_count):
        gx = index % grid
        gy = (index // grid) % grid
        near_obstacle = index % 2 == 1
        base_x = gx * 2.2 + (1.35 if near_obstacle else -0.1)
        base_y = gy * 1.8 + (0.0 if near_obstacle else 0.95)
        theta = -30.0 if index % 3 == 2 else 0.0
        poses.append(
            Pose2D(
                pose_id=index + 1,
                base_x=base_x,
                base_y=base_y,
                theta_degrees=theta,
                label="near_static_geometry" if near_obstacle else "clear_offset",
            )
        )
    return RobotCollisionCase(
        dataset="scaled",
        obstacle_triangles=tuple(obstacles),
        links=links,
        poses=tuple(poses),
        expected_link_flags=None,
        note="Deterministic scaled fixture with alternating clear and near-obstacle poses.",
    )


def make_robot_collision_case(
    dataset: str,
    *,
    pose_count: int | None = None,
    obstacle_count: int | None = None,
    link_count: int = 2,
) -> RobotCollisionCase:
    if dataset == "tiny":
        return make_tiny_case()
    if dataset == "scaled":
        return make_scaled_case(
            pose_count=16 if pose_count is None else pose_count,
            obstacle_count=4 if obstacle_count is None else obstacle_count,
            link_count=link_count,
        )
    raise ValueError(f"dataset must be one of: {', '.join(DATASETS)}")


def _expected_pose_flags(expected: dict[tuple[int, int], bool] | None) -> dict[int, bool] | None:
    if expected is None:
        return None
    by_pose: dict[int, bool] = {}
    for (pose_id, _), any_hit in expected.items():
        by_pose[pose_id] = by_pose.get(pose_id, False) or any_hit
    return by_pose


def _evaluate_cpu_reference(case: RobotCollisionCase, *, include_hit_pairs: bool) -> dict[str, object]:
    start = time.perf_counter()
    link_flags = []
    hit_pairs = []
    triangle_pair_tests = 0
    triangle_pair_hit_count = 0
    for pose in case.poses:
        for link in case.links:
            query_triangles = transformed_link_triangles(link, pose)
            link_hit_pairs = []
            for query_triangle in query_triangles:
                for obstacle_triangle in case.obstacle_triangles:
                    triangle_pair_tests += 1
                    if not triangles_intersect(query_triangle, obstacle_triangle):
                        continue
                    triangle_pair_hit_count += 1
                    pair = {
                        "pose_id": pose.pose_id,
                        "link_id": link.link_id,
                        "query_triangle_id": query_triangle.id,
                        "obstacle_triangle_id": obstacle_triangle.id,
                    }
                    link_hit_pairs.append(pair)
                    if include_hit_pairs:
                        hit_pairs.append(pair)
            any_hit = bool(link_hit_pairs)
            link_flags.append(
                {
                    "pose_id": pose.pose_id,
                    "link_id": link.link_id,
                    "link_name": link.name,
                    "any_hit": any_hit,
                    "hit_pair_count": len(link_hit_pairs),
                    "query_triangle_count": len(query_triangles),
                }
            )
    pose_summaries = []
    for pose in case.poses:
        pose_link_flags = [row for row in link_flags if int(row["pose_id"]) == pose.pose_id]
        colliding_link_ids = [int(row["link_id"]) for row in pose_link_flags if bool(row["any_hit"])]
        pose_summaries.append(
            {
                "pose_id": pose.pose_id,
                "label": pose.label,
                "base_x": pose.base_x,
                "base_y": pose.base_y,
                "theta_degrees": pose.theta_degrees,
                "any_hit": bool(colliding_link_ids),
                "colliding_link_ids": colliding_link_ids,
            }
        )
    compact_link_flags = [1 if bool(row["any_hit"]) else 0 for row in link_flags]
    elapsed_sec = time.perf_counter() - start
    expected_link = case.expected_link_flags
    expected_pose = _expected_pose_flags(expected_link)
    matches_expected = None
    if expected_link is not None:
        matches_expected = all(
            bool(row["any_hit"]) == expected_link[(int(row["pose_id"]), int(row["link_id"]))]
            for row in link_flags
        )
    return {
        "elapsed_sec": elapsed_sec,
        "link_flags": link_flags,
        "pose_summaries": pose_summaries,
        "compact_link_flags": compact_link_flags,
        "hit_pairs": hit_pairs if include_hit_pairs else None,
        "triangle_pair_tests": triangle_pair_tests,
        "triangle_pair_hit_count": triangle_pair_hit_count,
        "matches_expected": matches_expected,
        "expected_link_flags": (
            [
                {"pose_id": pose_id, "link_id": link_id, "any_hit": any_hit}
                for (pose_id, link_id), any_hit in sorted(expected_link.items())
            ]
            if expected_link is not None
            else None
        ),
        "expected_pose_flags": (
            [{"pose_id": pose_id, "any_hit": any_hit} for pose_id, any_hit in sorted(expected_pose.items())]
            if expected_pose is not None
            else None
        ),
    }


def _triangle2_to_triangle3(triangle: Triangle2):
    from rtdsl.reference import Triangle3D

    return Triangle3D(
        triangle.id,
        triangle.x0,
        triangle.y0,
        0.0,
        triangle.x1,
        triangle.y1,
        0.0,
        triangle.x2,
        triangle.y2,
        0.0,
    )


def _sample_link_probe_points(link: LinkMesh2D, pose: Pose2D) -> tuple[Point2, ...]:
    half_w = link.width / 2.0
    half_h = link.height / 2.0
    local_points = (
        (link.local_center_x, link.local_center_y),
        (link.local_center_x - half_w, link.local_center_y - half_h),
        (link.local_center_x + half_w, link.local_center_y - half_h),
        (link.local_center_x + half_w, link.local_center_y + half_h),
        (link.local_center_x - half_w, link.local_center_y + half_h),
        (link.local_center_x, link.local_center_y - half_h),
        (link.local_center_x + half_w, link.local_center_y),
        (link.local_center_x, link.local_center_y + half_h),
        (link.local_center_x - half_w, link.local_center_y),
    )
    return tuple(_transform_point(x, y, pose) for x, y in local_points)


def build_segment_probe_contract(case: RobotCollisionCase) -> SegmentProbeContract:
    """Lower app geometry to the Goal2481 app-agnostic segment-probe contract."""
    starts: list[tuple[float, float, float]] = []
    ends: list[tuple[float, float, float]] = []
    offsets = [0]
    groups: list[ProbeGroup] = []
    points_per_group = 0
    for pose in case.poses:
        for link in case.links:
            probe_points = _sample_link_probe_points(link, pose)
            points_per_group = len(probe_points)
            for point in probe_points:
                starts.append((point.x, point.y, PROBE_Z_START))
                ends.append((point.x, point.y, PROBE_Z_END))
            offsets.append(len(starts))
            groups.append(ProbeGroup(pose.pose_id, pose.label, link.link_id, link.name))
    return SegmentProbeContract(
        static_triangles_3d=tuple(_triangle2_to_triangle3(triangle) for triangle in case.obstacle_triangles),
        segment_start_xyz=tuple(starts),
        segment_end_xyz=tuple(ends),
        segment_group_offsets=tuple(offsets),
        groups=tuple(groups),
        probe_points_per_group=points_per_group,
        lowering_policy=(
            "sampled_link_points_to_vertical_finite_segments_3d;"
            "center_corners_and_edge_midpoints_per_pose_link"
        ),
    )


def _probe_reference_flags(contract: SegmentProbeContract) -> list[int]:
    from rtdsl.reference import Ray3D, ray_triangle_any_hit_cpu

    rays = tuple(
        Ray3D(
            index,
            start[0],
            start[1],
            start[2],
            end[0] - start[0],
            end[1] - start[1],
            end[2] - start[2],
            1.0,
        )
        for index, (start, end) in enumerate(zip(contract.segment_start_xyz, contract.segment_end_xyz))
    )
    segment_hits = [int(row["any_hit"]) for row in ray_triangle_any_hit_cpu(rays, contract.static_triangles_3d)]
    flags: list[int] = []
    for group_index in range(len(contract.segment_group_offsets) - 1):
        start = contract.segment_group_offsets[group_index]
        end = contract.segment_group_offsets[group_index + 1]
        flags.append(1 if any(segment_hits[start:end]) else 0)
    return flags


def _flags_to_rows(
    flags: list[int],
    groups: tuple[ProbeGroup, ...],
    *,
    hit_pair_count_by_group: dict[int, int] | None = None,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    link_flags = []
    for index, (flag, group) in enumerate(zip(flags, groups)):
        link_flags.append(
            {
                "pose_id": group.pose_id,
                "link_id": group.link_id,
                "link_name": group.link_name,
                "any_hit": bool(flag),
                "hit_pair_count": int(hit_pair_count_by_group.get(index, 1 if flag else 0))
                if hit_pair_count_by_group is not None
                else int(1 if flag else 0),
                "query_group_index": index,
            }
        )
    pose_summaries = []
    pose_order = []
    for group in groups:
        if group.pose_id not in pose_order:
            pose_order.append(group.pose_id)
    for pose_id in pose_order:
        pose_link_flags = [row for row in link_flags if int(row["pose_id"]) == pose_id]
        pose_label = next(group.pose_label for group in groups if group.pose_id == pose_id)
        colliding_link_ids = [int(row["link_id"]) for row in pose_link_flags if bool(row["any_hit"])]
        pose_summaries.append(
            {
                "pose_id": pose_id,
                "label": pose_label,
                "any_hit": bool(colliding_link_ids),
                "colliding_link_ids": colliding_link_ids,
            }
        )
    return link_flags, pose_summaries


def _claim_boundary(*, mode: str) -> dict[str, object]:
    native_mode = mode != "cpu_reference"
    return {
        "paper_reproduction_claim_authorized": False,
        "authors_code_comparison_claim_authorized": False,
        "public_speedup_claim_authorized": False,
        "native_robot_abi_added": False,
        "native_collision_abi_added": False,
        "native_engine_touched": native_mode,
        "native_engine_touch_kind": "generic_rt_primitive_only" if native_mode else "none",
        "continuous_collision_supported": False,
        "exact_solid_collision_claim_authorized": False,
        "discrete_sampled_probe_contract_only": mode != "cpu_reference",
        "cpu_reference_only": mode == "cpu_reference",
        "source_tree_usage_only": True,
    }


def _paper_status() -> dict[str, object]:
    return {
        "paper_anchor": "Hardware-Accelerated Ray Tracing for Discrete and Continuous Collision Detection on GPUs",
        "paper_anchor_status": "tentative_goal2480_web_checked_2026_05_21",
        "authors": ["Sizhe Sui", "Luis Sentis", "Andrew Bylard"],
        "venue_status": "ICRA 2025 direction; exact citation should be rechecked before paper-facing wording",
        "official_code_verified": False,
        "official_data_verified": False,
        "comparison_policy": "separate_scoping_goal_required_if_authors_code_or_data_becomes_available",
        "sources": [
            "https://arxiv.org/abs/2409.09918",
            "https://ssz990220.github.io/publications/",
        ],
    }


def run_robot_collision_benchmark(
    *,
    mode: str = "cpu_reference",
    dataset: str = "tiny",
    pose_count: int | None = None,
    obstacle_count: int | None = None,
    link_count: int = 2,
    include_rows: bool = False,
) -> dict[str, object]:
    if mode not in MODES:
        raise ValueError(f"mode must be one of: {', '.join(MODES)}")
    case = make_robot_collision_case(
        dataset,
        pose_count=pose_count,
        obstacle_count=obstacle_count,
        link_count=link_count,
    )
    evaluation = _evaluate_cpu_reference(case, include_hit_pairs=include_rows)
    if mode == "cpu_reference":
        compact_link_flags = evaluation["compact_link_flags"]
        link_flags = evaluation["link_flags"]
        pose_summaries = evaluation["pose_summaries"]
        native_result = None
        probe_reference_flags = None
        matches_probe_reference = None
        prepared_metadata = None
    else:
        if mode == "optix_prepared_device_count":
            raise ValueError(
                "optix_prepared_device_count is a count-only repeated benchmark mode; "
                "use run_prepared_reuse_probe(..., reuse_native_device_query_count=True) or the CLI mode"
            )
        reuse_native_device_query_buffers = mode == "optix_prepared_device_buffers"
        reuse_query_buffers = mode.endswith("_prepared_buffers") and not reuse_native_device_query_buffers
        if reuse_native_device_query_buffers:
            backend = "optix"
        else:
            backend = mode.removesuffix("_prepared_buffers") if reuse_query_buffers else mode.removesuffix("_prepared")
        prepared_payload = run_prepared_reuse_probe(
            backend=backend,
            dataset=dataset,
            pose_count=pose_count,
            obstacle_count=obstacle_count,
            link_count=link_count,
            repeats=1,
            warmup=0,
            reuse_query_buffers=reuse_query_buffers,
            reuse_native_device_query_buffers=reuse_native_device_query_buffers,
        )
        native_result = prepared_payload["runs"][0]["backend_result"]
        compact_link_flags = list(native_result["flags"])
        contract = build_segment_probe_contract(case)
        probe_reference_flags = _probe_reference_flags(contract)
        matches_probe_reference = compact_link_flags == probe_reference_flags
        link_flags, pose_summaries = _flags_to_rows(compact_link_flags, contract.groups)
        prepared_metadata = {
            "backend": backend,
            "contract": prepared_payload["contract"],
            "prepared_scene_reused": bool(prepared_payload["reuse_metadata"]["prepared_scene_reused"]),
            "prepared_run_index": int(native_result["prepared_run_index"]),
            "query_input_sequences_reused": bool(prepared_payload["reuse_metadata"]["query_input_sequences_reused"]),
            "host_query_output_buffers_reused": bool(
                prepared_payload["reuse_metadata"]["host_query_output_buffers_reused"]
            ),
            "native_query_output_buffers_reused": bool(
                prepared_payload["reuse_metadata"]["native_query_output_buffers_reused"]
            ),
            "probe_points_per_group": int(contract.probe_points_per_group),
            "lowering_policy": contract.lowering_policy,
        }
    payload = {
        "app": "robot_collision_benchmark",
        "mode": mode,
        "dataset": case.dataset,
        "case_note": case.note,
        "pose_count": len(case.poses),
        "link_count": len(case.links),
        "static_obstacle_triangle_count": len(case.obstacle_triangles),
        "query_triangle_count": len(case.poses) * len(case.links) * 2,
        "output_contract": "batched_transformed_query_mesh_to_static_triangles_compact_any_hit_flags",
        "future_generic_contract_target": (
            "prepared_static_triangles_plus_batched_transformed_query_geometry_to_compact_any_hit_flags"
        ),
        "compact_output_format": "uint8_byte_per_query_group" if mode != "cpu_reference" else (
            "cpu_reference_list_of_0_1_flags_in_pose_major_link_order; "
            "Goal2481_must_choose_native_column_format"
        ),
        "dynamic_transformed_query_geometry": True,
        "prepared_static_scene_target": True,
        "paper_status": _paper_status(),
        "claim_boundary": _claim_boundary(mode=mode),
        "metadata": {
            "goal": (
                "Goal2489"
                if mode == "optix_prepared_device_buffers"
                else (
                    "Goal2488"
                    if mode.endswith("_prepared_buffers")
                    else ("Goal2484" if mode != "cpu_reference" else "Goal2480")
                )
            ),
            "goal_status": (
                "prepared_native_device_query_buffer_reuse_probe"
                if mode == "optix_prepared_device_buffers"
                else (
                    "prepared_query_buffer_reuse_probe"
                    if mode.endswith("_prepared_buffers")
                    else ("prepared_reuse_probe" if mode != "cpu_reference" else "cpu_reference_only")
                )
            ),
            "native_work_deferred_until": None if mode != "cpu_reference" else (
                "Goal2482/Goal2483_after_Goal2481_contract_review"
            ),
            "native_forbidden_vocabulary": [
                "robot",
                "link",
                "pose",
                "joint",
                "kinematics",
                "planner",
                "collision",
            ],
            "allowed_native_vocabulary_examples": ["intersection", "overlap", "hit", "any_hit"],
        },
        "elapsed_sec": evaluation["elapsed_sec"],
        "triangle_pair_tests": evaluation["triangle_pair_tests"],
        "triangle_pair_hit_count": evaluation["triangle_pair_hit_count"],
        "matches_expected": evaluation["matches_expected"],
        "matches_probe_reference": matches_probe_reference,
        "matches_exact_cpu_reference": (
            None if mode == "cpu_reference" else compact_link_flags == evaluation["compact_link_flags"]
        ),
        "pose_summaries": pose_summaries,
        "link_flags": link_flags,
        "compact_link_flags": compact_link_flags,
        "exact_cpu_reference_compact_link_flags": evaluation["compact_link_flags"],
    }
    if probe_reference_flags is not None:
        payload["probe_reference_compact_link_flags"] = probe_reference_flags
    if prepared_metadata is not None:
        payload["prepared_metadata"] = prepared_metadata
    if native_result is not None:
        payload["backend_result"] = native_result
    if include_rows:
        payload["hit_pairs"] = evaluation["hit_pairs"]
    if evaluation["expected_link_flags"] is not None:
        payload["expected_link_flags"] = evaluation["expected_link_flags"]
        payload["expected_pose_flags"] = evaluation["expected_pose_flags"]
    return _json_ready(payload)


def _prepare_backend(backend: str, static_triangles_3d: tuple[object, ...]):
    if backend == "embree":
        from rtdsl import prepare_embree_static_triangle_scene_3d

        return prepare_embree_static_triangle_scene_3d(static_triangles_3d)
    if backend == "optix":
        from rtdsl import prepare_optix_static_triangle_scene_3d

        return prepare_optix_static_triangle_scene_3d(static_triangles_3d)
    raise ValueError(f"backend must be one of: {', '.join(PREPARED_BACKENDS)}")


def _median(values: list[float]) -> float | None:
    return float(statistics.median(values)) if values else None


def _signature(flags: list[int]) -> str:
    return "".join(str(int(value)) for value in flags)


def run_prepared_reuse_probe(
    *,
    backend: str,
    dataset: str = "tiny",
    pose_count: int | None = None,
    obstacle_count: int | None = None,
    link_count: int = 2,
    repeats: int = DEFAULT_REPEAT_COUNT,
    warmup: int = DEFAULT_WARMUP_COUNT,
    reuse_query_buffers: bool = False,
    reuse_native_device_query_buffers: bool = False,
    reuse_native_device_query_count: bool = False,
) -> dict[str, object]:
    if backend not in PREPARED_BACKENDS:
        raise ValueError(f"backend must be one of: {', '.join(PREPARED_BACKENDS)}")
    reuse_choices = [
        bool(reuse_query_buffers),
        bool(reuse_native_device_query_buffers),
        bool(reuse_native_device_query_count),
    ]
    if sum(1 for choice in reuse_choices if choice) > 1:
        raise ValueError("choose only one prepared query/output reuse mode")
    if (reuse_native_device_query_buffers or reuse_native_device_query_count) and backend != "optix":
        raise ValueError("native device query reuse is currently implemented for the OptiX backend")
    if repeats < 1:
        raise ValueError("repeats must be positive")
    if warmup < 0 or warmup >= repeats:
        raise ValueError("warmup must be non-negative and smaller than repeats")

    case = make_robot_collision_case(
        dataset,
        pose_count=pose_count,
        obstacle_count=obstacle_count,
        link_count=link_count,
    )
    lowering_start = time.perf_counter()
    contract = build_segment_probe_contract(case)
    app_lowering_seconds = time.perf_counter() - lowering_start
    probe_reference_flags = _probe_reference_flags(contract)
    probe_reference_flagged_group_count = sum(1 for flag in probe_reference_flags if flag)
    prepared_query = None
    if reuse_native_device_query_buffers or reuse_native_device_query_count:
        from rtdsl import prepare_optix_grouped_segment_query_3d

        prepared_query = prepare_optix_grouped_segment_query_3d(
            contract.segment_start_xyz,
            contract.segment_end_xyz,
            contract.segment_group_offsets,
        )
    elif reuse_query_buffers:
        from rtdsl import prepare_grouped_segment_query_3d

        prepared_query = prepare_grouped_segment_query_3d(
            contract.segment_start_xyz,
            contract.segment_end_xyz,
            contract.segment_group_offsets,
        )

    runs = []
    with _prepare_backend(backend, contract.static_triangles_3d) as prepared:
        for iteration in range(repeats):
            total_start = time.perf_counter()
            if prepared_query is None:
                result = prepared.run_grouped_segment_any_hit_flags(
                    contract.segment_start_xyz,
                    contract.segment_end_xyz,
                    contract.segment_group_offsets,
                )
            elif reuse_native_device_query_buffers:
                result = prepared.run_native_prepared_grouped_segment_any_hit_flags(prepared_query)
            elif reuse_native_device_query_count:
                result = prepared.run_native_prepared_grouped_segment_any_hit_count(prepared_query)
            else:
                result = prepared.run_prepared_grouped_segment_any_hit_flags(prepared_query)
            total_run_seconds = time.perf_counter() - total_start
            if reuse_native_device_query_count:
                flags = []
                flagged_group_count = int(result["flagged_group_count"])
                flags_signature = f"count:{flagged_group_count}"
                matches_probe_reference = flagged_group_count == probe_reference_flagged_group_count
            else:
                flags = list(result["flags"])
                flagged_group_count = sum(1 for flag in flags if flag)
                flags_signature = _signature(flags)
                matches_probe_reference = flags == probe_reference_flags
            runs.append(
                {
                    "iteration": iteration,
                    "is_warmup": iteration < warmup,
                    "total_run_seconds": total_run_seconds,
                    "flags": flags,
                    "flagged_group_count": flagged_group_count,
                    "flags_signature": flags_signature,
                    "matches_probe_reference": matches_probe_reference,
                    "prepared_run_index": int(result["prepared_run_index"]),
                    "phase_timing_seconds": result["phase_timing_seconds"],
                    "backend_result": result,
                }
            )

    measured = [row for row in runs if not bool(row["is_warmup"])]
    phase_names = tuple(
        sorted({name for row in measured for name in row["phase_timing_seconds"]})
    ) or ("prepare_build", "query_pack", "traversal", "output_postprocess")
    tail_phase_medians = {
        name: _median([float(row["phase_timing_seconds"][name]) for row in measured])
        for name in phase_names
    }
    first_prepare = float(runs[0]["phase_timing_seconds"]["prepare_build"])
    reuse_metadata = {
        "warmup_rows_dropped": warmup,
        "repeat_count": repeats,
        "measured_run_count": len(measured),
        "prepared_scene_reused": all(bool(row["backend_result"]["prepared_scene_used"]) for row in runs),
        "prepared_run_indices": [int(row["prepared_run_index"]) for row in runs],
        "prepared_run_indices_strictly_increase": [int(row["prepared_run_index"]) for row in runs]
        == list(range(1, repeats + 1)),
        "prepare_build_seconds_constant": all(
            float(row["phase_timing_seconds"]["prepare_build"]) == first_prepare for row in runs
        ),
        "query_input_sequences_reused": True,
        "host_query_output_buffers_reused": bool(
            reuse_query_buffers or reuse_native_device_query_buffers or reuse_native_device_query_count
        ),
        "native_query_output_buffers_reused": bool(
            reuse_native_device_query_buffers or reuse_native_device_query_count
        ),
        "native_query_output_buffer_reuse_note": (
            (
                "prepared_device_buffers mode reuses native OptiX device query/output buffers; "
                "the current Python API still downloads compact group flags and does not claim true zero-copy"
            )
            if reuse_native_device_query_buffers
            else (
                (
                    "prepared_device_count mode reuses native OptiX device query/output buffers and returns only "
                    "a scalar flagged-group count to Python; native host code still downloads compact group flags "
                    "internally, so no true zero-copy claim is made"
                )
                if reuse_native_device_query_count
                else (
                    (
                        "prepared_buffers mode reuses Python-owned ctypes query/output buffers; "
                        + (
                            "OptiX still uploads query segments per run and no native device buffer reuse is claimed"
                            if backend == "optix"
                            else "the backend consumes reusable host buffers and no native device buffer reuse is claimed"
                        )
                    )
                    if reuse_query_buffers
                    else (
                        "current Python ABI reuses prepared scene and Python input sequences; "
                        "native query/output buffers are repacked per run"
                    )
                )
            )
        ),
        "prepared_query_descriptor": (
            runs[-1]["backend_result"].get("buffer_reuse_metadata")
            if prepared_query is not None and runs
            else None
        ),
        "prepared_query_run_indices": [
            int(row["backend_result"].get("prepared_query_run_index", 0)) for row in runs
        ],
        "prepared_query_run_indices_strictly_increase": (
            [int(row["backend_result"].get("prepared_query_run_index", 0)) for row in runs]
            == list(range(1, repeats + 1))
            if prepared_query is not None
            else False
        ),
        "all_measured_runs_match_probe_reference": all(bool(row["matches_probe_reference"]) for row in measured),
        "probe_reference_flagged_group_count": probe_reference_flagged_group_count,
        "all_measured_counts_match_probe_reference": all(
            int(row["flagged_group_count"]) == probe_reference_flagged_group_count for row in measured
        ),
        "all_run_signatures_identical": len({str(row["flags_signature"]) for row in runs}) == 1,
    }
    if reuse_native_device_query_count:
        mode_name = f"{backend}_prepared_device_count"
    elif reuse_native_device_query_buffers:
        mode_name = f"{backend}_prepared_device_buffers"
    elif reuse_query_buffers:
        mode_name = f"{backend}_prepared_buffers"
    else:
        mode_name = f"{backend}_prepared"
    return _json_ready(
        {
            "app": "robot_collision_benchmark",
            "goal": (
                "Goal2490"
                if reuse_native_device_query_count
                else "Goal2489"
                if reuse_native_device_query_buffers
                else ("Goal2488" if reuse_query_buffers else "Goal2484")
            ),
            "backend": backend,
            "mode": mode_name,
            "dataset": case.dataset,
            "contract": "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1",
            "warmup_protocol": {
                "repeat_count": repeats,
                "warmup_count": warmup,
                "rule": "drop the first warmup_count rows; report medians over remaining tail rows",
                "minimum_default": "7 repeats with 2 warmup rows for local evidence",
            },
            "case_shape": {
                "pose_count": len(case.poses),
                "link_count": len(case.links),
                "group_count": len(contract.groups),
                "static_obstacle_triangle_count": len(contract.static_triangles_3d),
                "segment_count": len(contract.segment_start_xyz),
                "probe_points_per_group": contract.probe_points_per_group,
            },
            "app_lowering_seconds": app_lowering_seconds,
            "probe_reference_compact_link_flags": probe_reference_flags,
            "probe_reference_signature": _signature(probe_reference_flags),
            "lowering_policy": contract.lowering_policy,
            "reuse_metadata": reuse_metadata,
            "tail_medians": {
                "total_run_seconds": _median([float(row["total_run_seconds"]) for row in measured]),
                "phase_timing_seconds": tail_phase_medians,
            },
            "runs": runs,
            "claim_boundary": _claim_boundary(mode=mode_name),
        }
    )


def run_performance_matrix(
    *,
    dataset: str = "scaled",
    pose_count: int = 64,
    obstacle_count: int = 16,
    link_count: int = 3,
    repeats: int = DEFAULT_REPEAT_COUNT,
    warmup: int = DEFAULT_WARMUP_COUNT,
    include_optix: bool = True,
    include_extended_modes: bool = False,
    goal: str = "Goal2485",
) -> dict[str, object]:
    case = make_robot_collision_case(
        dataset,
        pose_count=pose_count,
        obstacle_count=obstacle_count,
        link_count=link_count,
    )
    cpu_runs = []
    for iteration in range(repeats):
        start = time.perf_counter()
        evaluation = _evaluate_cpu_reference(case, include_hit_pairs=False)
        cpu_runs.append(
            {
                "iteration": iteration,
                "is_warmup": iteration < warmup,
                "elapsed_sec": time.perf_counter() - start,
                "flags_signature": _signature(list(evaluation["compact_link_flags"])),
            }
        )
    measured_cpu = [row for row in cpu_runs if not bool(row["is_warmup"])]
    rows: list[dict[str, object]] = [
        {
            "mode": "cpu_reference",
            "backend": "python",
            "status": "ok",
            "tail_median_total_run_seconds": _median([float(row["elapsed_sec"]) for row in measured_cpu]),
            "flags_signature": cpu_runs[-1]["flags_signature"] if cpu_runs else "",
            "parity_reference": "exact_2d_cpu_reference",
            "runs": cpu_runs,
        }
    ]

    mode_specs: list[dict[str, object]] = [
        {"mode": "embree_prepared", "backend": "embree"},
        {"mode": "optix_prepared", "backend": "optix"},
    ]
    if include_extended_modes:
        mode_specs = [
            {"mode": "embree_prepared", "backend": "embree"},
            {"mode": "embree_prepared_buffers", "backend": "embree", "reuse_query_buffers": True},
            {"mode": "optix_prepared", "backend": "optix"},
            {"mode": "optix_prepared_buffers", "backend": "optix", "reuse_query_buffers": True},
            {
                "mode": "optix_prepared_device_buffers",
                "backend": "optix",
                "reuse_native_device_query_buffers": True,
            },
            {
                "mode": "optix_prepared_device_count",
                "backend": "optix",
                "reuse_native_device_query_count": True,
            },
        ]

    for spec in mode_specs:
        backend = str(spec["backend"])
        mode = str(spec["mode"])
        if backend == "optix" and not include_optix:
            rows.append({"mode": mode, "backend": "optix", "status": "skipped", "reason": "optix_disabled"})
            continue
        try:
            prepared = run_prepared_reuse_probe(
                backend=backend,
                dataset=dataset,
                pose_count=pose_count,
                obstacle_count=obstacle_count,
                link_count=link_count,
                repeats=repeats,
                warmup=warmup,
                reuse_query_buffers=bool(spec.get("reuse_query_buffers", False)),
                reuse_native_device_query_buffers=bool(spec.get("reuse_native_device_query_buffers", False)),
                reuse_native_device_query_count=bool(spec.get("reuse_native_device_query_count", False)),
            )
            rows.append(
                {
                    "mode": mode,
                    "backend": backend,
                    "status": "ok",
                    "goal": prepared["goal"],
                    "tail_median_total_run_seconds": prepared["tail_medians"]["total_run_seconds"],
                    "tail_median_phase_timing_seconds": prepared["tail_medians"]["phase_timing_seconds"],
                    "flags_signature": prepared["probe_reference_signature"],
                    "parity_reference": "goal2481_probe_reference",
                    "all_measured_runs_match_probe_reference": prepared["reuse_metadata"][
                        "all_measured_runs_match_probe_reference"
                    ],
                    "all_measured_counts_match_probe_reference": prepared["reuse_metadata"].get(
                        "all_measured_counts_match_probe_reference"
                    ),
                    "reuse_metadata": prepared["reuse_metadata"],
                    "case_shape": prepared["case_shape"],
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "mode": mode,
                    "backend": backend,
                    "status": "error",
                    "error": repr(exc),
                }
            )

    return _json_ready(
        {
            "goal": goal,
            "app": "robot_collision_benchmark",
            "dataset": dataset,
            "case_shape": {
                "pose_count": len(case.poses),
                "link_count": len(case.links),
                "obstacle_count": obstacle_count,
                "static_obstacle_triangle_count": len(case.obstacle_triangles),
            },
            "warmup_protocol": {
                "repeat_count": repeats,
                "warmup_count": warmup,
                "rule": "drop warmup rows and report tail medians",
            },
            "matrix_scope": (
                "final_canonical_robot_collision_modes"
                if include_extended_modes
                else "goal2485_cpu_embree_optix_prepared_modes"
            ),
            "rows": rows,
            "claim_boundary": {
                "internal_evidence_only": True,
                "public_speedup_claim_authorized": False,
                "paper_reproduction_claim_authorized": False,
                "authors_code_comparison_claim_authorized": False,
                "exact_solid_collision_claim_authorized": False,
                "continuous_collision_supported": False,
            },
        }
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the robot-collision CPU, prepared, or matrix benchmark app.")
    parser.add_argument("--mode", choices=MODES, default="cpu_reference")
    parser.add_argument("--dataset", choices=DATASETS, default="tiny")
    parser.add_argument("--pose-count", type=int, default=None)
    parser.add_argument("--obstacle-count", type=int, default=None)
    parser.add_argument("--link-count", type=int, default=2)
    parser.add_argument("--repeats", type=int, default=DEFAULT_REPEAT_COUNT)
    parser.add_argument("--warmup", type=int, default=DEFAULT_WARMUP_COUNT)
    parser.add_argument("--matrix", action="store_true")
    parser.add_argument("--final-matrix", action="store_true")
    parser.add_argument("--skip-optix", action="store_true")
    parser.add_argument("--include-rows", action="store_true")
    parser.add_argument("--json-out", default=None)
    args = parser.parse_args(argv)
    if args.matrix:
        payload = run_performance_matrix(
            dataset=args.dataset,
            pose_count=64 if args.pose_count is None else args.pose_count,
            obstacle_count=16 if args.obstacle_count is None else args.obstacle_count,
            link_count=args.link_count,
            repeats=args.repeats,
            warmup=args.warmup,
            include_optix=not args.skip_optix,
            include_extended_modes=args.final_matrix,
            goal="Goal2491" if args.final_matrix else "Goal2485",
        )
    elif args.mode == "optix_prepared_device_buffers":
        payload = run_prepared_reuse_probe(
            backend="optix",
            dataset=args.dataset,
            pose_count=args.pose_count,
            obstacle_count=args.obstacle_count,
            link_count=args.link_count,
            repeats=args.repeats,
            warmup=args.warmup,
            reuse_native_device_query_buffers=True,
        )
    elif args.mode == "optix_prepared_device_count":
        payload = run_prepared_reuse_probe(
            backend="optix",
            dataset=args.dataset,
            pose_count=args.pose_count,
            obstacle_count=args.obstacle_count,
            link_count=args.link_count,
            repeats=args.repeats,
            warmup=args.warmup,
            reuse_native_device_query_count=True,
        )
    elif args.mode.endswith("_prepared_buffers") or (args.mode.endswith("_prepared") and args.repeats != 1):
        reuse_query_buffers = args.mode.endswith("_prepared_buffers")
        payload = run_prepared_reuse_probe(
            backend=args.mode.removesuffix("_prepared_buffers") if reuse_query_buffers else args.mode.removesuffix("_prepared"),
            dataset=args.dataset,
            pose_count=args.pose_count,
            obstacle_count=args.obstacle_count,
            link_count=args.link_count,
            repeats=args.repeats,
            warmup=args.warmup,
            reuse_query_buffers=reuse_query_buffers,
        )
    else:
        payload = run_robot_collision_benchmark(
            mode=args.mode,
            dataset=args.dataset,
            pose_count=args.pose_count,
            obstacle_count=args.obstacle_count,
            link_count=args.link_count,
            include_rows=args.include_rows,
        )
    text = json.dumps(payload, indent=2, sort_keys=True)
    if args.json_out:
        Path(args.json_out).write_text(text + "\n", encoding="utf-8")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
