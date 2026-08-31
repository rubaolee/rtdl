from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _load_matrix_runner():
    script = ROOT / "Paper-reproduction-apps" / "x-hd-paper" / "scripts" / "run_xhd_seeded_performance_matrix.py"
    spec = importlib.util.spec_from_file_location("run_xhd_seeded_performance_matrix", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class Goal5156XhdRoutePhaseMedianProfileTest(unittest.TestCase):
    def test_phase_medians_are_computed_from_all_runs(self) -> None:
        matrix = _load_matrix_runner()

        runs = [
            {
                "rtdl_route": {
                    "directed_a_to_b": {
                        "phase_timings_sec": {
                            "initial_state_seed": 3.0,
                            "frontier_rows": 30.0,
                        }
                    }
                }
            },
            {
                "rtdl_route": {
                    "directed_a_to_b": {
                        "phase_timings_sec": {
                            "initial_state_seed": 1.0,
                            "frontier_rows": 10.0,
                        }
                    }
                }
            },
            {
                "rtdl_route": {
                    "directed_a_to_b": {
                        "phase_timings_sec": {
                            "initial_state_seed": 2.0,
                            "frontier_rows": 20.0,
                        }
                    }
                }
            },
        ]

        phase_runs = matrix._direction_phase_runs(runs, "directed_a_to_b")
        self.assertEqual(phase_runs["initial_state_seed"], [3.0, 1.0, 2.0])
        self.assertEqual(phase_runs["frontier_rows"], [30.0, 10.0, 20.0])
        self.assertEqual(matrix._phase_medians(phase_runs), {
            "frontier_rows": 20.0,
            "initial_state_seed": 2.0,
        })

    def test_production_matrix_artifact_has_phase_runs_and_medians_when_present(self) -> None:
        path = (
            ROOT
            / "Paper-reproduction-apps"
            / "x-hd-paper"
            / "results"
            / "xhd_seeded_sample256_1024_production_author_only_median_profile_pod.json"
        )
        if not path.exists():
            self.skipTest("Goal5156 median-profile artifact not generated yet")

        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
        for case in payload["cases"]:
            directed = case["rtdl"]["directed_a_to_b"]
            if "phase_timings_sec_runs" not in directed:
                self.skipTest("Goal5156 median-profile artifact not generated yet")
            runs = directed["phase_timings_sec_runs"]
            medians = directed["phase_timings_sec_median"]
            self.assertIn("initial_state_seed", runs)
            self.assertIn("frontier_rows", runs)
            self.assertIn("nearest_continuation", runs)
            self.assertEqual(len(runs["initial_state_seed"]), len(case["rtdl"]["route_sec_runs"]))
            self.assertGreater(medians["initial_state_seed"], 0.0)
            self.assertGreater(medians["frontier_rows"], 0.0)
            self.assertGreater(medians["nearest_continuation"], 0.0)


if __name__ == "__main__":
    unittest.main()
