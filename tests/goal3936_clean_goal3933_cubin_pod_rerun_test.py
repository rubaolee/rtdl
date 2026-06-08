from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal3936_clean_goal3933_cubin_pod_rerun_2026-06-08"


class Goal3936CleanGoal3933CubinPodRerunTest(unittest.TestCase):
    def test_clean_manifest_passes_without_source_dirty(self) -> None:
        manifest = json.loads((ARTIFACT_DIR / "summary_manifest.json").read_text(encoding="utf-8"))
        evaluation = json.loads((ARTIFACT_DIR / "goal3931_evaluation.json").read_text(encoding="utf-8"))

        self.assertEqual("pass", manifest["status"])
        self.assertEqual("cd7fa65f", manifest["source_commit"])
        self.assertEqual("cd7fa65f", manifest["source_commit_label"])
        self.assertEqual([], manifest["source_dirty"])
        self.assertEqual("accept_with_boundary", evaluation["status"])
        self.assertEqual([], evaluation["errors"])
        self.assertEqual("cd7fa65f", evaluation["source_commit"])
        self.assertEqual("cd7fa65f", evaluation["source_commit_label"])

    def test_rayjoin_clean_artifact_keeps_route_decisions_and_counts(self) -> None:
        rayjoin = json.loads((ARTIFACT_DIR / "rayjoin" / "summary.json").read_text(encoding="utf-8"))

        self.assertTrue(rayjoin["all_counts_match"])
        self.assertEqual("", rayjoin["git_status_short"])
        self.assertEqual("cd7fa65f32bdf1f70ebab0fdb6eb897048739fec", rayjoin["git_commit"])
        self.assertFalse(rayjoin["claim_boundary"]["release_authorized"])
        self.assertFalse(rayjoin["claim_boundary"]["public_speedup_claim_authorized"])
        self.assertFalse(rayjoin["claim_boundary"]["automatic_partner_selection_authorized"])

        summary = rayjoin["representative_hot_path_summary"]
        self.assertGreater(summary["lsi_scalar_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertGreater(summary["overlay_active_count"]["rtdl_optix_speedup_vs_numba"], 200.0)
        self.assertLess(summary["pip_one_shot"]["rtdl_optix_speedup_vs_numba"], 1.0)
        self.assertEqual("numba_cuda_jit_scalar_count_no_rawkernel", summary["pip_one_shot"]["recommended_route"])
        self.assertEqual("rtdl_optix_prepared_batch_executor", summary["pip_repeated_requests"]["recommended_route"])
        self.assertGreater(summary["pip_repeated_requests"]["per_request_speedup_vs_single_request"], 1.0)

    def test_rtdbscan_blocked_candidate_stays_unpromoted(self) -> None:
        evaluation = json.loads((ARTIFACT_DIR / "goal3931_evaluation.json").read_text(encoding="utf-8"))
        unblocked = json.loads(
            (
                ARTIFACT_DIR
                / "rtdbscan"
                / "optix_rt_core_grouped_stream_numba_column_signature_3d.json"
            ).read_text(encoding="utf-8")
        )
        blocked = json.loads(
            (
                ARTIFACT_DIR
                / "rtdbscan"
                / "optix_rt_core_grouped_stream_blocked_numba_column_signature_3d.json"
            ).read_text(encoding="utf-8")
        )

        self.assertLess(unblocked["elapsed_sec"], blocked["elapsed_sec"])
        self.assertEqual("numba", unblocked["metadata"]["count_metadata"]["partner"])
        self.assertEqual("numba", blocked["metadata"]["count_metadata"]["partner"])
        self.assertEqual(
            "blocked_candidate_slower_keep_unblocked_default",
            evaluation["rtdbscan"]["recommendation"],
        )
        self.assertTrue(all(value is False for value in evaluation["claim_boundary"].values()))

    def test_report_states_evidence_hygiene_boundary(self) -> None:
        text = REPORT.read_text(encoding="utf-8")

        for phrase in (
            "fresh clean checkout",
            "Source dirty list: empty",
            "accept_with_boundary",
            "Goal3933 repair now has both external review and a clean post-commit pod rerun",
            "does not authorize a release",
        ):
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
