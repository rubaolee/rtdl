from __future__ import annotations

import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "rtdl_rt_dbscan_benchmark_app.py"
README = ROOT / "examples" / "v2_0" / "research_benchmarks" / "rt_dbscan" / "README.md"
RUNNER = ROOT / "scripts" / "goal2478_rt_dbscan_project_close_pod_runner.py"
REPORT = ROOT / "docs" / "reports" / "goal2478_rt_dbscan_project_completion_2026-05-21.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal2478_rt_dbscan_project_close_pod" / "summary.json"
GEMINI = ROOT / "docs" / "reviews" / "goal2478_gemini_review_rt_dbscan_project_completion_2026-05-21.md"
CLAUDE = ROOT / "docs" / "reviews" / "goal2478_claude_review_rt_dbscan_project_completion_2026-05-21.md"
CONSENSUS = (
    ROOT
    / "docs"
    / "reviews"
    / "goal2478_codex_gemini_claude_consensus_rt_dbscan_project_completion_2026-05-21.md"
)


class Goal2478RtDbscanProjectCompletionTest(unittest.TestCase):
    def test_project_close_runner_records_fair_baselines_and_environment_boundary(self) -> None:
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("PREPARED_CUPY_GRID_MODE", runner)
        self.assertIn("PREPARED_GRID_MODE", runner)
        self.assertIn("_run_grouped_stream_repeats", runner)
        self.assertIn("plan_rt_dbscan_execution", runner)
        self.assertIn("plan_rt_dbscan_continuation_execution", runner)
        self.assertIn("stderr=subprocess.DEVNULL", runner)
        self.assertIn("\"source_tree_is_git_checkout\"", runner)
        self.assertIn("\"paper_speedup_claim_authorized\": False", runner)
        self.assertIn("\"whole_app_speedup_claim_authorized\": False", runner)

    def test_planner_policy_uses_grouped_stream_for_over_budget_dense_continuation(self) -> None:
        app = APP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")

        self.assertIn("optix_rt_core_grouped_stream_cupy_components_3d", app)
        self.assertIn("Goal2457/2461/2463/2465/2475/2476", app)
        self.assertIn("Goal2476", app)
        self.assertIn("if the stream exceeds the budget, use", readme)
        self.assertIn("`optix_rt_core_grouped_stream_cupy_components_3d`", readme)
        self.assertIn("chunked adjacency remains available as a", readme)
        self.assertIn("manual memory-control diagnostic", readme)
        self.assertIn("intersection-direct side-effect experiment", readme)
        self.assertIn("default-off", readme)

    def test_pod_closeout_artifact_records_signatures_and_internal_only_claim_boundary(self) -> None:
        summary = json.loads(ARTIFACT.read_text(encoding="utf-8"))

        self.assertEqual(summary["gpu"], "NVIDIA RTX A5000, 570.211.01")
        self.assertEqual(summary["point_counts"], [32768, 65536, 131072])
        self.assertEqual(summary["repeat_count"], 3)
        self.assertFalse(summary["source_tree_is_git_checkout"])
        self.assertFalse(summary["claim_boundary"]["paper_dataset_reproduction"])
        self.assertFalse(summary["claim_boundary"]["paper_speedup_claim_authorized"])
        self.assertFalse(summary["claim_boundary"]["whole_app_speedup_claim_authorized"])
        rows = {row["point_count"]: row for row in summary["summaries"]}
        self.assertEqual(rows[32768]["planned_continuation_selected_mode"], "optix_rt_core_adjacency_cupy_components_3d")
        self.assertEqual(rows[65536]["planned_continuation_selected_mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertEqual(rows[131072]["planned_continuation_selected_mode"], "optix_rt_core_grouped_stream_cupy_components_3d")
        self.assertGreater(
            rows[131072]["repeat_probe_summary"]["optix_rt_core_flags_cupy_prepared_grid_components_3d"][
                "speedup_vs_prepared_cupy_grid"
            ],
            1.5,
        )
        for point_count, row in rows.items():
            self.assertTrue(
                row["repeat_probe_summary"]["partner_cupy_prepared_grid_components_3d"]["signatures_match_probe"],
                point_count,
            )
            self.assertTrue(
                row["repeat_probe_summary"]["optix_rt_core_flags_cupy_prepared_grid_components_3d"][
                    "signatures_match_probe"
                ],
                point_count,
            )
            self.assertTrue(row["grouped_stream_summary"]["signatures_match_probe"], point_count)
            self.assertGreater(row["grouped_stream_summary"]["speedup_vs_prepared_cupy_grid"], 3.9)
            self.assertFalse(row["grouped_stream_summary"]["materializes_neighbor_rows"])
            self.assertFalse(row["grouped_stream_summary"]["materializes_directed_adjacency_stream"])

    def test_completion_report_closes_project_without_public_speedup_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("complete for the current v2.x scope", report)
        self.assertIn("No DBSCAN-specific native ABI", report)
        self.assertIn("This is not a paper-reproduction claim", report)
        self.assertIn("All recorded probes had matching signatures", report)
        self.assertIn("two post-warmup runs", report)
        self.assertIn("Grouped native kernel, sec", report)
        self.assertIn("1.1179x", report)
        self.assertIn("1.2523x", report)
        self.assertIn("1.5396x", report)
        self.assertIn("3.9108x", report)
        self.assertIn("4.7221x", report)
        self.assertIn("4.8990x", report)
        self.assertIn("Intersection-direct side-effect default promotion", report)
        self.assertIn("not promoted", report)
        self.assertIn("public broad DBSCAN speedup claim", report)

    def test_external_reviews_and_consensus_have_no_project_close_blockers(self) -> None:
        gemini = GEMINI.read_text(encoding="utf-8")
        claude = CLAUDE.read_text(encoding="utf-8")
        consensus = CONSENSUS.read_text(encoding="utf-8")

        self.assertIn("Verdict: Approved", gemini)
        self.assertIn("Blocking Issues", gemini)
        self.assertIn("None", gemini)
        self.assertIn("Verdict: Approved", claude)
        self.assertIn("Blocking Issues", claude)
        self.assertIn("None", claude)
        self.assertIn("Codex, Gemini, and Claude agree", consensus)
        self.assertIn("complete for the current v2.x project scope", consensus)
        self.assertIn("does not authorize public speedup wording", consensus)


if __name__ == "__main__":
    unittest.main()
