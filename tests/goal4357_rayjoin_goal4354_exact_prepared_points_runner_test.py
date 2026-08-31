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
            'choices=("exact", "exact_prepared_points", "exact_prepared_points_executor")',
            "count_prepared_points_exact(prepared_points)",
            "prepared_exact_closed_shape_membership_prepared_points_scalar_count",
            "rtdl_optix_count_prepared_point_closed_shape_membership_prepared_points_2d",
            "scalar_exact_positive_membership_count_prepared_points",
            "native_phase_timings",
            "candidate_count_pass",
            "Native phase ms",
            "Hardware Classification",
            "--rt-core-hardware",
            "_infer_nvidia_rt_core_hardware",
            '"rt_core_detection": reason',
            '"rt_core_accelerated": bool(rt_core_hardware is True)',
            '"pip_rtdl_count_mode": args.pip_rtdl_count_mode',
            "_parse_rayjoin(artifact_dir, workloads)",
            "Status: measured from RayJoin-exported query streams",
        ):
            self.assertIn(phrase, text)

        self.assertNotIn("Status: measured on the pod from RayJoin-exported query streams", text)

    def test_original_goal4354_exact_route_remains_default(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn('default="exact"', text)
        self.assertIn("prepared_exact_closed_shape_membership_scalar_count", text)
        self.assertIn("rtdl_optix_count_prepared_point_closed_shape_membership_2d", text)

    def test_optix_rt_core_claim_is_not_unconditional(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertNotIn('"rt_core_accelerated": True', text)
        self.assertIn('"GPU name contains GTX; this is not NVIDIA RT-core hardware"', text)
        self.assertIn('"GPU name contains RTX"', text)

    def test_workload_filter_applies_to_rayjoin_log_parser(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn(
            "def _parse_rayjoin(artifact_dir: Path, workloads: tuple[str, ...] = WORKLOADS)",
            text,
        )
        self.assertIn("for workload in workloads:", text)


if __name__ == "__main__":
    unittest.main()
