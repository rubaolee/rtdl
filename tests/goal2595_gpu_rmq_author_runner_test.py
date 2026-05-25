from __future__ import annotations

import argparse
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from scripts import goal2595_gpu_rmq_author_runner as runner


class Goal2595GpuRmqAuthorRunnerTest(unittest.TestCase):
    def test_author_run_command_contains_expected_cli_shape(self) -> None:
        command = runner.author_run_command(
            Path("/tmp/GPU-RMQ"),
            n=1 << 20,
            q=1 << 16,
            lr=-3,
            alg=16,
            log_bs=6,
            reps=3,
            seed=27722,
            dev=0,
            nt=1,
            csv_path=Path("/tmp/out.csv"),
            check_mode="rand",
            save_input_data=True,
        )
        self.assertEqual(command[:5], ["/tmp/GPU-RMQ/build/rtxrmq", "1048576", "65536", "-3", "16"])
        self.assertIn("--randTrivialCheck", command)
        self.assertIn("--save-input-data", command)
        self.assertIn("--save-time=/tmp/out.csv", command)

    def test_plan_payload_has_default_author_algorithms_and_workloads(self) -> None:
        args = argparse.Namespace(
            repo_dir="/tmp/GPU-RMQ",
            optix_home="/opt/OptiX",
            is_long=0,
            cg_size_log=3,
            cg_amount_log=2,
            n=1 << 20,
            q=1 << 16,
            lr=[-3, -6],
            alg=[16, 20],
            log_bs=6,
            reps=3,
            seed=27722,
            dev=0,
            nt=1,
            csv_path="/tmp/out.csv",
            check_mode="rand",
            save_input_data=False,
        )
        payload = runner.plan_payload(args)
        self.assertEqual(payload["author_repo"], runner.AUTHOR_REPO)
        self.assertEqual(len(payload["smoke_matrix"]), 4)
        self.assertIn(-6, payload["paper_workloads"]["range_distributions"])


if __name__ == "__main__":
    unittest.main()
