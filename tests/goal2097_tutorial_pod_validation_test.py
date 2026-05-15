from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT = (
    ROOT
    / "docs/reports/goal2097_tutorial_pod_validation/goal2097_tutorial_matrix_results.json"
)
REPORT = ROOT / "docs/reports/goal2097_tutorial_pod_validation_2026-05-15.md"


class Goal2097TutorialPodValidationTest(unittest.TestCase):
    def test_pod_tutorial_matrix_all_passed(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        self.assertEqual("6f2219d2febcf24538fbc448771f330813e6199c", data["commit"])
        self.assertEqual({"pass": 41, "fail": 0, "timeout": 0}, data["counts"])
        self.assertEqual(41, len(data["results"]))
        self.assertTrue(all(row["status"] == "pass" for row in data["results"]))

    def test_matrix_covers_embree_and_optix_tutorial_paths(self) -> None:
        data = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        pairs = {(row["name"], row["backend"]) for row in data["results"]}
        required = {
            ("partner_anyhit_numpy", "embree"),
            ("partner_anyhit_numpy", "optix"),
            ("partner_anyhit_cupy", "optix"),
            ("fixed_radius_neighbors", "embree"),
            ("fixed_radius_neighbors", "optix"),
            ("knn_rows", "embree"),
            ("knn_rows", "optix"),
            ("segment_polygon_anyhit_rows", "optix"),
            ("hausdorff_threshold", "optix_rt"),
            ("graph_analytics_visibility", "optix_rt"),
            ("database_analytics_compact", "optix_rt"),
            ("visual_lit_ball", "embree"),
            ("visual_lit_ball", "optix"),
        }
        self.assertTrue(required.issubset(pairs))

    def test_report_documents_environment_and_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "NVIDIA RTX 2000 Ada Generation",
            "570.195.03",
            "libnvrtc.so.12",
            "41",
            "strict 3-AI consensus gate",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
