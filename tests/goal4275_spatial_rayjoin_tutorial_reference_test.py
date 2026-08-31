"""Goal4275: Spatial RayJoin benchmark reference is learner-author useful."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
TUTORIAL = ROOT / "tutorials" / "current" / "08_spatial_join_rayjoin_reference.md"
WALKTHROUGH = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "CODE_WALKTHROUGH.md"
)
README = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "README.md"
)
APP = (
    ROOT
    / "examples"
    / "current"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)
REPORT = ROOT / "docs" / "reports" / "goal4275_spatial_rayjoin_tutorial_reference_2026-06-10.md"


class Goal4275SpatialRayjoinTutorialReferenceTest(unittest.TestCase):
    def test_tutorial_links_spatial_join_reference_material(self) -> None:
        text = TUTORIAL.read_text(encoding="utf-8")

        required = [
            "Spatial Join Benchmark Reference",
            "PYTHONPATH=src:.",
            "all_match_cpu_python_reference: true",
            "CODE_WALKTHROUGH.md",
            "Spatial / RayJoin-Style Study",
            "CuPy and Numba are explicit app choices",
        ]
        missing = [token for token in required if token not in text]
        self.assertEqual([], missing)

    def test_walkthrough_explains_learners_and_rayjoin_authors(self) -> None:
        text = WALKTHROUGH.read_text(encoding="utf-8")

        required_sections = [
            "The Learner Path Through The Code",
            "Language-Level Difference From RayJoin",
            "Optimization-Level Difference From RayJoin",
            "Performance-Level Reading",
            "What Is New For RayJoin Authors",
            "Current Limits",
        ]
        missing = [section for section in required_sections if section not in text]
        self.assertEqual([], missing)

        required_terms = [
            "point_to_polygon_positive_hit_rows",
            "segment_segment_intersection_rows",
            "overlay_pair_dependency",
            "prepared OptiX handles",
            "CuPy dense baselines",
            "Numba reference continuation",
            "38.4x",
            "260x",
            "0.024ms/request",
            "not a universal RayJoin speedup claim",
        ]
        missing_terms = [term for term in required_terms if term not in text]
        self.assertEqual([], missing_terms)

    def test_readme_points_to_walkthrough(self) -> None:
        text = README.read_text(encoding="utf-8")

        self.assertIn("CODE_WALKTHROUGH.md", text)
        self.assertIn("routes, optimizations, and performance boundaries", text)

    def test_cpu_reference_command_still_runs_for_tutorial(self) -> None:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.pathsep.join((str(ROOT / "src"), str(ROOT)))
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--backend",
                "cpu_python_reference",
                "--no-rows",
            ],
            cwd=ROOT,
            env=env,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )

        self.assertIn('"all_match_cpu_python_reference": true', completed.stdout)

    def test_report_records_scope_and_validation(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal4275 Spatial RayJoin Tutorial Reference", text)
        self.assertIn("new learners", text)
        self.assertIn("RayJoin authors", text)
        self.assertIn("not a full RayJoin paper reproduction claim", text)
        self.assertIn("CPU reference suite passed", text)


if __name__ == "__main__":
    unittest.main()
