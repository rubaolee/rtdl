from __future__ import annotations

import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2486_robot_collision_continuous_feasibility_2026-05-21.md"
ACTIVE_NATIVE_DIRS = (
    ROOT / "src" / "native" / "embree",
    ROOT / "src" / "native" / "optix",
)
FORBIDDEN_NATIVE_WORDS = re.compile(
    r"\b(robot|collision|link|pose|joint|kinematic|kinematics|planner)\b",
    re.IGNORECASE,
)


class Goal2486RobotCollisionContinuousFeasibilityTest(unittest.TestCase):
    def test_report_defers_continuous_collision_to_later_scope(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("Goal2486 is complete", report)
        self.assertIn("Decision: defer implementation", report)
        self.assertIn("sampled transforms over time", report)
        self.assertIn("swept spheres/capsules", report)
        self.assertIn("conservative interval/bounds primitive", report)
        self.assertIn("app-level continuation over discrete RTDL queries", report)
        self.assertIn("not part of Goal2484/2485 performance claims", report)
        self.assertIn("v3.0-or-later candidate", report)

    def test_report_preserves_app_agnostic_boundary(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("No native ABI is added", report)
        self.assertIn("Python owns continuous-collision policy", report)
        self.assertIn("paper reproduction remains blocked", report)
        self.assertIn("exact swept contact remains blocked", report)

    def test_native_sources_still_have_no_app_vocabulary(self) -> None:
        hits: list[str] = []
        for directory in ACTIVE_NATIVE_DIRS:
            for path in directory.rglob("*"):
                if not path.is_file():
                    continue
                text = path.read_text(encoding="utf-8", errors="ignore")
                if FORBIDDEN_NATIVE_WORDS.search(text):
                    hits.append(str(path.relative_to(ROOT)))
        self.assertEqual(hits, [])


if __name__ == "__main__":
    unittest.main()
