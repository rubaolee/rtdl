from __future__ import annotations

import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal2428_rt_dbscan_generic_continuation_problem_closure_2026-05-19.md"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
TODO = ROOT / "docs" / "research" / "future_version_to_do_list.md"
NATIVE = ROOT / "src" / "native"


class Goal2428RtDbscanGenericContinuationProblemClosureTest(unittest.TestCase):
    def test_report_separates_closed_planning_from_open_runtime_work(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("planning problem", report)
        self.assertIn("runtime continuation problem", report)
        self.assertIn("Counts and core flags are useful, but they are not enough", report)
        self.assertIn("prepared fixed-radius edge/adjacency stream", report)
        self.assertIn("device-resident grouped union/find continuation", report)
        self.assertIn("not a DBSCAN shortcut", report)

    def test_learner_readme_uses_only_goal2425_goal2427_policy(self) -> None:
        readme = README.read_text(encoding="utf-8")

        self.assertIn("Goal2425 prepared-baseline fairness pass and the Goal2427 pod smoke", readme)
        self.assertIn("measured 524k crossover", readme)
        self.assertIn("measured 65k crossover", readme)
        self.assertNotIn("measured 262k crossover", readme)
        self.assertNotIn("After the Goal2425 prepared-baseline fairness pass, the policy is:", readme)

    def test_future_todo_and_native_tree_keep_app_agnostic_boundary(self) -> None:
        todo = TODO.read_text(encoding="utf-8")
        native_text = "\n".join(
            path.read_text(encoding="utf-8", errors="ignore")
            for path in NATIVE.rglob("*")
            if path.is_file()
        ).lower()

        self.assertIn("remaining performance issue is the generic continuation itself", todo)
        self.assertIn("Do not add\n  DBSCAN-specific native ABI", todo)
        self.assertNotIn("rtdl_optix_dbscan", native_text)


if __name__ == "__main__":
    unittest.main()
