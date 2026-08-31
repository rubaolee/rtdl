from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
REPORT = ROOT / "docs" / "reports" / "goal3308_prepared_point_workspace_reuse_2026-06-04.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3308_workspace_reuse_prepared_points_rayjoin_same_slice_pod_2026-06-04.json"
GOAL3306_PREPARED = ROOT / "docs" / "reports" / "goal3306_prepared_points_rayjoin_same_slice_pod_2026-06-04.json"
GOAL3306_BASELINE = ROOT / "docs" / "reports" / "goal3306_baseline_device_filtered_same_slice_pod_2026-06-04.json"


class Goal3308PreparedPointWorkspaceReuseTest(unittest.TestCase):
    def test_native_prepared_point_handle_owns_reusable_workspace(self) -> None:
        text = WORKLOADS.read_text(encoding="utf-8")
        struct_start = text.index("struct PreparedPointProbeColumns2D")
        struct_end = text.index("static PreparedShapePairRelationBuild*", struct_start)
        struct_body = text[struct_start:struct_end]
        self.assertIn("DevPtr d_count", struct_body)
        self.assertIn("DevPtr d_params", struct_body)

        count_start = text.index(
            "static void count_prepared_point_closed_shape_membership_device_filtered_prepared_points_2d_optix"
        )
        count_end = text.index(
            "static void run_prepared_point_closed_shape_membership_candidate_device_columns_2d_optix",
            count_start,
        )
        count_body = text[count_start:count_end]
        self.assertIn("prepared_points->d_count.ptr", count_body)
        self.assertIn("prepared_points->d_params.ptr", count_body)
        self.assertNotIn("DevPtr d_count(sizeof(uint32_t));", count_body)
        self.assertNotIn("DevPtr d_params(sizeof(PipLaunchParams));", count_body)
        self.assertNotIn("rayjoin", count_body.lower())

    def test_report_and_artifact_record_current_best_but_block_claims(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))
        goal3306_prepared = json.loads(GOAL3306_PREPARED.read_text(encoding="utf-8"))
        goal3306_baseline = json.loads(GOAL3306_BASELINE.read_text(encoding="utf-8"))

        for phrase in (
            "small additional repeated-query",
            "current best RTDL RayJoin PIP route",
            "does not beat RayJoin",
            "batched/replayed scalar-count launches",
        ):
            self.assertIn(phrase, report)

        self.assertEqual(artifact["rtdl_commit"], "8d8e7c02986df235f5b0719ade521465bbcb0a05")
        self.assertEqual(artifact["status"], "pass_with_optimization_gap")
        self.assertFalse(any(artifact["claim_boundary"].values()))

        pip = artifact["rtdl"]["pip"]
        self.assertEqual(pip["count_mode"], "device_filtered_prepared_points_validated")
        self.assertEqual(pip["counts"]["last"], 1430)
        self.assertEqual(pip["native_phase_samples"][0]["mode"], "prepared_points_device_filtered_count")
        self.assertEqual(pip["native_phase_samples"][0]["point_upload"], 0.0)

        self.assertLess(
            pip["prepared_query_ms"]["median"],
            goal3306_prepared["rtdl"]["pip"]["prepared_query_ms"]["median"],
        )
        self.assertLess(
            pip["prepared_query_ms"]["median"],
            goal3306_baseline["rtdl"]["pip"]["prepared_query_ms"]["median"],
        )
        comparisons = {row["workload"]: row for row in artifact["comparisons"]}
        self.assertGreater(comparisons["pip"]["rtdl_over_rayjoin_query_ratio"], 1.0)
        self.assertLess(comparisons["pip"]["rtdl_over_rayjoin_query_ratio"], 1.4)


if __name__ == "__main__":
    unittest.main()
