from __future__ import annotations

import math
import pathlib
import re
import unittest

from rtdsl import prepare_embree_static_triangle_scene_3d
from rtdsl import run_embree_grouped_segment_any_hit_flags_3d
from rtdsl.reference import Triangle3D


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2482_robot_collision_embree_contract_2026-05-21.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2482_gemini_review_robot_collision_embree_contract_2026-05-21.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2482_claude_review_robot_collision_embree_contract_2026-05-21.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2482_codex_gemini_claude_consensus_robot_collision_embree_contract_2026-05-21.md"
)
ACTIVE_NATIVE_DIRS = (
    ROOT / "src" / "native" / "embree",
    ROOT / "src" / "native" / "optix",
)
FORBIDDEN_NATIVE_WORDS = re.compile(
    r"\b(robot|collision|link|pose|joint|kinematic|kinematics|planner)\b",
    re.IGNORECASE,
)
CONTRACT = "PREPARED_TRIANGLE_SCENE_GROUPED_SEGMENT_ANY_HIT_FLAGS_V1"


TRIANGLES = (
    Triangle3D(1, 0.0, 0.0, 0.0, 2.0, 0.0, 0.0, 0.0, 2.0, 0.0),
)
SEGMENT_STARTS = (
    (0.25, 0.25, 1.0),
    (2.5, 2.5, 1.0),
    (2.5, 0.25, 1.0),
    (0.75, 0.25, 1.0),
    (0.3333333333333333, 0.3333333333333333, 2.0),
)
SEGMENT_ENDS = (
    (0.25, 0.25, -1.0),
    (2.5, 2.5, -1.0),
    (2.5, 0.25, -1.0),
    (0.75, 0.25, -1.0),
    (0.3333333333333333, 0.3333333333333333, -2.0),
)
GROUP_OFFSETS = (0, 1, 2, 4, 4, 5)
EXPECTED_FLAGS = [1, 0, 1, 0, 1]


def _sub(left: tuple[float, float, float], right: tuple[float, float, float]) -> tuple[float, float, float]:
    return (left[0] - right[0], left[1] - right[1], left[2] - right[2])


def _dot(left: tuple[float, float, float], right: tuple[float, float, float]) -> float:
    return left[0] * right[0] + left[1] * right[1] + left[2] * right[2]


def _cross(left: tuple[float, float, float], right: tuple[float, float, float]) -> tuple[float, float, float]:
    return (
        left[1] * right[2] - left[2] * right[1],
        left[2] * right[0] - left[0] * right[2],
        left[0] * right[1] - left[1] * right[0],
    )


def _triangle_points(triangle: Triangle3D) -> tuple[tuple[float, float, float], ...]:
    return (
        (triangle.x0, triangle.y0, triangle.z0),
        (triangle.x1, triangle.y1, triangle.z1),
        (triangle.x2, triangle.y2, triangle.z2),
    )


def _segment_hits_triangle(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    triangle: Triangle3D,
) -> bool:
    v0, v1, v2 = _triangle_points(triangle)
    direction = _sub(end, start)
    edge1 = _sub(v1, v0)
    edge2 = _sub(v2, v0)
    pvec = _cross(direction, edge2)
    det = _dot(edge1, pvec)
    if math.isclose(det, 0.0, abs_tol=1e-12):
        return False
    inv_det = 1.0 / det
    tvec = _sub(start, v0)
    u = _dot(tvec, pvec) * inv_det
    if u < -1e-12 or u > 1.0 + 1e-12:
        return False
    qvec = _cross(tvec, edge1)
    v = _dot(direction, qvec) * inv_det
    if v < -1e-12 or u + v > 1.0 + 1e-12:
        return False
    t = _dot(edge2, qvec) * inv_det
    return -1e-12 <= t <= 1.0 + 1e-12


def _cpu_grouped_segment_any_hit_flags(
    triangles: tuple[Triangle3D, ...],
    starts: tuple[tuple[float, float, float], ...],
    ends: tuple[tuple[float, float, float], ...],
    offsets: tuple[int, ...],
) -> list[int]:
    flags: list[int] = []
    for group_index in range(len(offsets) - 1):
        flag = 0
        for segment_index in range(offsets[group_index], offsets[group_index + 1]):
            if any(_segment_hits_triangle(starts[segment_index], ends[segment_index], triangle) for triangle in triangles):
                flag = 1
                break
        flags.append(flag)
    return flags


class Goal2482RobotCollisionEmbreeContractTest(unittest.TestCase):
    def test_cpu_oracle_fixture_locks_goal2481_contract(self) -> None:
        self.assertEqual(
            _cpu_grouped_segment_any_hit_flags(TRIANGLES, SEGMENT_STARTS, SEGMENT_ENDS, GROUP_OFFSETS),
            EXPECTED_FLAGS,
        )

    def test_embree_matches_3d_cpu_oracle_and_returns_contract_metadata(self) -> None:
        result = run_embree_grouped_segment_any_hit_flags_3d(
            TRIANGLES,
            SEGMENT_STARTS,
            SEGMENT_ENDS,
            GROUP_OFFSETS,
        )

        self.assertEqual(result["contract"], CONTRACT)
        self.assertEqual(result["backend"], "embree")
        self.assertEqual(result["flags"], EXPECTED_FLAGS)
        self.assertEqual(result["flag_format"], "uint8_byte_per_query_group")
        self.assertEqual(result["segment_count"], len(SEGMENT_STARTS))
        self.assertEqual(result["group_count"], len(GROUP_OFFSETS) - 1)
        self.assertEqual(result["triangle_count"], len(TRIANGLES))
        self.assertTrue(result["prepared_reused"])
        self.assertEqual(result["precision_metadata"]["host_input"], "float64")
        self.assertTrue(result["precision_metadata"]["coordinate_narrowing_recorded"])
        for key in ("prepare_build", "query_pack", "traversal", "output_postprocess"):
            self.assertIn(key, result["phase_timing_seconds"])
            self.assertGreaterEqual(result["phase_timing_seconds"][key], 0.0)
        for value in result["claim_boundary"].values():
            self.assertFalse(value)

    def test_prepared_embree_scene_reuses_handle_across_runs(self) -> None:
        with prepare_embree_static_triangle_scene_3d(TRIANGLES) as prepared:
            first = prepared.run_grouped_segment_any_hit_flags(SEGMENT_STARTS, SEGMENT_ENDS, GROUP_OFFSETS)
            second = prepared.run_grouped_segment_any_hit_flags(SEGMENT_STARTS, SEGMENT_ENDS, GROUP_OFFSETS)

        self.assertEqual(first["flags"], EXPECTED_FLAGS)
        self.assertEqual(second["flags"], EXPECTED_FLAGS)
        self.assertEqual(first["prepared_run_index"], 1)
        self.assertEqual(second["prepared_run_index"], 2)
        self.assertEqual(first["phase_timing_seconds"]["prepare_build"], second["phase_timing_seconds"]["prepare_build"])

    def test_python_packer_rejects_invalid_segments_before_native_traversal(self) -> None:
        with prepare_embree_static_triangle_scene_3d(TRIANGLES) as prepared:
            with self.assertRaisesRegex(ValueError, "non-zero length"):
                prepared.run_grouped_segment_any_hit_flags(
                    ((0.0, 0.0, 0.0),),
                    ((0.0, 0.0, 0.0),),
                    (0, 1),
                )

    def test_active_native_targets_remain_free_of_app_vocabulary(self) -> None:
        hits: list[str] = []
        for directory in ACTIVE_NATIVE_DIRS:
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if FORBIDDEN_NATIVE_WORDS.search(text):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])

    def test_report_reviews_and_consensus_record_goal2482_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn(CONTRACT, report)
        self.assertIn("3D CPU probe oracle", report)
        self.assertIn("prepared scene reuse", report)
        self.assertIn("byte-per-query-group `uint8` flags", report)
        self.assertIn("No pod was used", report)
        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Verdict: Approved", claude)
        self.assertIn("Consensus: Approved", consensus)
        self.assertIn("Goal2482 is complete", consensus)


if __name__ == "__main__":
    unittest.main()
