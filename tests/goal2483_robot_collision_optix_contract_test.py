from __future__ import annotations

import math
import pathlib
import re
import unittest

from rtdsl import PreparedOptixStaticTriangleScene3D
from rtdsl import prepare_optix_static_triangle_scene_3d
from rtdsl import run_optix_grouped_segment_any_hit_flags_3d
from rtdsl.reference import Triangle3D


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2483_robot_collision_optix_contract_2026-05-21.md"
POD_SUMMARY = ROOT / "docs" / "reports" / "goal2483_optix_contract_pod" / "summary.json"
WIP_REPORT = ROOT / "docs" / "reports" / "goal2483_optix_contract_wip_2026-05-21.md"
GEMINI_REVIEW = ROOT / "docs" / "reviews" / "goal2483_gemini_review_robot_collision_optix_contract_2026-05-21.md"
CLAUDE_REVIEW = ROOT / "docs" / "reviews" / "goal2483_claude_review_robot_collision_optix_contract_2026-05-21.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2483_codex_gemini_claude_consensus_robot_collision_optix_contract_2026-05-21.md"
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


def _segment_hits_triangle(
    start: tuple[float, float, float],
    end: tuple[float, float, float],
    triangle: Triangle3D,
) -> bool:
    v0 = (triangle.x0, triangle.y0, triangle.z0)
    v1 = (triangle.x1, triangle.y1, triangle.z1)
    v2 = (triangle.x2, triangle.y2, triangle.z2)
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


def _cpu_grouped_segment_any_hit_flags() -> list[int]:
    flags: list[int] = []
    for group_index in range(len(GROUP_OFFSETS) - 1):
        flag = 0
        for segment_index in range(GROUP_OFFSETS[group_index], GROUP_OFFSETS[group_index + 1]):
            if any(
                _segment_hits_triangle(SEGMENT_STARTS[segment_index], SEGMENT_ENDS[segment_index], triangle)
                for triangle in TRIANGLES
            ):
                flag = 1
                break
        flags.append(flag)
    return flags


def _optix_backend_ready() -> bool:
    try:
        from rtdsl.optix_runtime import _load_optix_library

        _load_optix_library()
    except Exception:
        return False
    return True


class Goal2483RobotCollisionOptixContractTest(unittest.TestCase):
    def test_goal2483_reuses_goal2481_cpu_contract_fixture(self) -> None:
        self.assertEqual(_cpu_grouped_segment_any_hit_flags(), EXPECTED_FLAGS)

    def test_python_api_exports_goal2481_contract(self) -> None:
        self.assertEqual(PreparedOptixStaticTriangleScene3D.contract, CONTRACT)
        self.assertTrue(callable(prepare_optix_static_triangle_scene_3d))
        self.assertTrue(callable(run_optix_grouped_segment_any_hit_flags_3d))

    def test_optix_native_declares_app_agnostic_contract_symbols(self) -> None:
        prelude = (ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp").read_text(encoding="utf-8")

        self.assertIn("struct RtdlSegment3D", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_create", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_destroy", prelude)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_create", api)
        self.assertIn("rtdl_optix_static_triangle_scene_3d_grouped_segment_any_hit_flags", api)
        self.assertIn("PreparedStaticTriangleScene3D", workloads)
        self.assertIn("uint8_t* flags_out", workloads)

    def test_pod_runner_records_required_goal2483_evidence(self) -> None:
        script = (ROOT / "scripts" / "goal2483_optix_contract_pod_runner.py").read_text(encoding="utf-8")

        self.assertIn("make", script)
        self.assertIn("build-optix", script)
        self.assertIn("nvidia-smi", script)
        self.assertIn("nvcc", script)
        self.assertIn("optix_header_candidates", script)
        self.assertIn("run_optix_grouped_segment_any_hit_flags_3d", script)
        self.assertIn("summary.json", script)

    def test_report_records_pod_evidence_and_claim_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        pod_summary = POD_SUMMARY.read_text(encoding="utf-8")

        self.assertIn(CONTRACT, report)
        self.assertIn("NVIDIA RTX A5000", report)
        self.assertIn("69.30.85.236", report)
        self.assertIn("[1, 0, 1, 0, 1]", report)
        self.assertIn("Goal2483 is complete", report)
        self.assertIn('"ok": true', pod_summary)
        self.assertIn('"flags": [', pod_summary)
        self.assertIn('"public_speedup_claim": false', pod_summary)
        self.assertIn('"row_witnesses": false', pod_summary)
        self.assertIn("pure RT-core", report)

    def test_reviews_and_consensus_record_goal2483_closure(self) -> None:
        gemini = GEMINI_REVIEW.read_text(encoding="utf-8")
        claude = CLAUDE_REVIEW.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Verdict: Approved", claude)
        self.assertIn("Consensus: Approved", consensus)
        self.assertIn("Goal2483 is complete", consensus)
        self.assertFalse(WIP_REPORT.exists())

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

    @unittest.skipUnless(_optix_backend_ready(), "OptiX runtime validation requires an NVIDIA pod")
    def test_optix_runtime_matches_cpu_contract_fixture_on_nvidia(self) -> None:
        result = run_optix_grouped_segment_any_hit_flags_3d(
            TRIANGLES,
            SEGMENT_STARTS,
            SEGMENT_ENDS,
            GROUP_OFFSETS,
        )

        self.assertEqual(result["backend"], "optix")
        self.assertEqual(result["contract"], CONTRACT)
        self.assertEqual(result["flags"], EXPECTED_FLAGS)
        self.assertEqual(result["flag_format"], "uint8_byte_per_query_group")
        self.assertEqual(result["precision_metadata"]["host_input"], "float64")
        self.assertTrue(result["precision_metadata"]["coordinate_narrowing_recorded"])
        for value in result["claim_boundary"].values():
            self.assertFalse(value)


if __name__ == "__main__":
    unittest.main()
