from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal4354_rayjoin_original_vs_rtdl_same_stream_scalar_count.py"


class Goal4357RayJoinGoal4354ExactPreparedPointsRunnerTest(unittest.TestCase):
    def test_goal4354_runner_can_measure_exact_prepared_points_pip_route(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "--pip-rtdl-count-mode",
            'choices=("exact", "exact_prepared_points")',
            "count_prepared_points_exact(prepared_points)",
            "prepared_exact_closed_shape_membership_prepared_points_scalar_count",
            "rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d",
            "scalar_exact_positive_membership_count_prepared_points",
            '"pip_rtdl_count_mode": args.pip_rtdl_count_mode',
        ):
            self.assertIn(phrase, text)

    def test_original_goal4354_exact_route_remains_default(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('default="exact"', text)
        self.assertIn("prepared_exact_closed_shape_membership_scalar_count", text)
        self.assertIn("rtdl_optix_count_prepared_point_closed_shape_membership_2d", text)


if __name__ == "__main__":
    unittest.main()
