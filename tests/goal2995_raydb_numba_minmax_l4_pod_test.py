from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = REPO_ROOT / "docs" / "reports" / "goal2995_raydb_numba_minmax_l4_pod_2026-06-01.md"
ARTIFACT = REPO_ROOT / "docs" / "reports" / "goal2995_raydb_numba_minmax_l4_pod_2026-06-01.json"


class Goal2995RaydbNumbaMinmaxL4PodTest(unittest.TestCase):
    def test_report_records_l4_runtime_conformance_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Status: passed on NVIDIA L4 pod",
            "segmented_min_f64",
            "segmented_max_f64",
            "All five modes matched the CPU NumPy reference",
            "v2_6_numba_neutral_front_door",
            "does not authorize",
            "RayDB paper reproduction claims",
            "here-doc had a quoting typo",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_all_five_modes_and_cpu_parity(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal2995")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["app"], "raydb_style_columnar_aggregate")
        self.assertEqual(data["partner"], "numba")
        self.assertEqual(data["rows"], 1_000_000)
        self.assertEqual(data["groups"], 4096)
        self.assertIn("NVIDIA L4", data["gpu"])
        self.assertEqual(data["source_commit"], "b41369e4b4becb3534e729658db41642c643abe2")
        self.assertEqual(tuple(data["modes"]), ("count", "sum", "min", "max", "avg_as_sum_count"))
        expected_ops = {
            "count": ("segmented_count_i64",),
            "sum": ("segmented_sum_f64",),
            "min": ("segmented_min_f64",),
            "max": ("segmented_max_f64",),
            "avg_as_sum_count": ("segmented_sum_f64", "segmented_count_i64"),
        }
        for mode, operations in expected_ops.items():
            result = data["mode_results"][mode]
            self.assertTrue(result["match_cpu"], msg=mode)
            self.assertEqual(tuple(result["operations"]), operations)
            self.assertEqual(result["neutral_handoff_status"], "accept")
            self.assertFalse(result["uses_legacy_torch_carrier"])
            self.assertFalse(result["uses_torch_conversion"])
            self.assertFalse(result["promoted_performance_path"])

    def test_artifact_claim_boundary_authorizes_nothing(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for field, value in data["claim_boundary"].items():
            self.assertIs(value, False, msg=f"{field} must remain false")

    def test_roadmap_and_readiness_index_goal2995(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(roadmap, repo_root=REPO_ROOT)
        self.assertEqual(validation["status"], "accept", validation["errors"])
        self.assertEqual(roadmap["benchmark_minmax_goal"], "Goal2995")
        self.assertIn("all_five_scalar_modes", roadmap["benchmark_minmax_status"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])

        packet = rt.v2_5_internal_readiness_packet(repo_root=REPO_ROOT)
        self.assertIn(
            "request_external_review_for_goal2995_raydb_numba_minmax",
            packet["allowed_next_actions"],
        )
        self.assertIn(
            "begin_next_v2_6_benchmark_app_numba_path_after_goal2995_review",
            packet["allowed_next_actions"],
        )


if __name__ == "__main__":
    unittest.main()
