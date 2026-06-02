from __future__ import annotations

import json
import unittest
from pathlib import Path

import rtdsl as rt


REPO_ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.md"
)
ARTIFACT = (
    REPO_ROOT
    / "docs"
    / "reports"
    / "goal2994_raydb_numba_neutral_demo_l4_pod_2026-06-01.json"
)


class Goal2994RaydbNumbaNeutralDemoL4PodTest(unittest.TestCase):
    def test_report_records_l4_result_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "first benchmark-app demonstrator",
            "RayDB-style grouped aggregate benchmark",
            "`avg_as_sum_count`",
            "user-selected `partner=\"numba\"`",
            "v2_6_numba_neutral_front_door",
            "Neutral handoff validation: `accept`",
            "does not claim full RayDB paper reproduction",
            "true zero-copy",
            "automatic partner selection",
            "Numba segmented min/max",
        ):
            self.assertIn(phrase, text)

    def test_artifact_records_successful_raydb_style_app_path(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual(data["goal"], "Goal2994")
        self.assertEqual(data["status"], "pass")
        self.assertEqual(data["app"], "raydb_style_columnar_aggregate")
        self.assertEqual(data["mode"], "avg_as_sum_count")
        self.assertEqual(data["partner"], "numba")
        self.assertEqual(data["rows"], 1_000_000)
        self.assertEqual(data["groups"], 4096)
        self.assertIn("NVIDIA L4", data["gpu"])
        self.assertEqual(data["source_commit"], "43f0c63791b1dd078c4a4c66f69fa8e45b709839")
        self.assertEqual(data["operations"], ["segmented_sum_f64", "segmented_count_i64"])
        self.assertEqual(
            data["continuation_paths"],
            ["v2_6_numba_neutral_front_door", "v2_6_numba_neutral_front_door"],
        )
        self.assertTrue(data["counts_match_cpu"])
        self.assertTrue(data["sums_match_cpu"])
        self.assertLess(data["max_sum_abs_error"], 1e-9)

    def test_artifact_records_neutral_handoff_and_toolchain(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        metadata = data["metadata"]
        self.assertEqual(metadata["v2_6_neutral_handoff_validation"]["status"], "accept")
        self.assertEqual(
            metadata["v2_6_neutral_handoff_validation"]["runtime_observed_descriptor_count"],
            2,
        )
        self.assertEqual(metadata["execution_path"], "v2_6_numba_neutral_front_door")
        self.assertFalse(metadata["uses_legacy_torch_carrier"])
        self.assertFalse(metadata["uses_torch_conversion"])
        self.assertFalse(metadata["replaces_rt_traversal"])
        self.assertFalse(metadata["promoted_performance_path"])

        toolchain = data["toolchain"]
        self.assertEqual(toolchain["numba_version"], "0.65.1")
        self.assertIn("numba_cuda/numba/cuda/__init__.py", toolchain["numba_cuda_module"])
        self.assertEqual(toolchain["numba_cuda_use_nvidia_binding"], "1")
        self.assertEqual(toolchain["numba_cuda_enable_minor_version_compatibility"], "1")

    def test_artifact_claim_boundary_authorizes_nothing(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        for field, value in data["claim_boundary"].items():
            self.assertIs(value, False, msg=f"{field} must remain false")

    def test_roadmap_indexes_goal2994_as_first_app_demonstrator(self) -> None:
        roadmap = rt.v2_6_roadmap()
        validation = rt.validate_v2_6_roadmap(roadmap, repo_root=REPO_ROOT)
        self.assertEqual("accept", validation["status"])
        self.assertEqual(roadmap["benchmark_demonstrator_goal"], "Goal2994")
        self.assertIn("raydb_style", roadmap["benchmark_demonstrator_status"])
        self.assertFalse(roadmap["release_authorized"])
        self.assertFalse(roadmap["numba_speedup_claim_authorized"])

    def test_readiness_exposes_next_minmax_action(self) -> None:
        packet = rt.v2_5_internal_readiness_packet(repo_root=REPO_ROOT)
        self.assertIn(
            "begin_goal2995_numba_segmented_min_max_after_raydb_demo",
            packet["allowed_next_actions"],
        )


if __name__ == "__main__":
    unittest.main()
