from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = ROOT / "docs" / "rtx_cloud_single_session_runbook.md"
OPTIX_WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"


class Goal829RtxCloudSingleSessionRunbookTest(unittest.TestCase):
    def test_prepared_db_optix_launch_has_traversal_start_timer(self) -> None:
        text = OPTIX_WORKLOADS.read_text(encoding="utf-8")
        start = text.index("static std::vector<size_t> db_collect_candidate_row_indices_optix_prepared(")
        end = text.index("static void run_db_conjunctive_scan_optix(", start)
        body = text[start:end]

        self.assertIn("auto t_start_trav = std::chrono::steady_clock::now();", body)
        self.assertIn("auto t_end_trav = std::chrono::steady_clock::now();", body)
        self.assertLess(body.index("auto t_start_trav"), body.index("OPTIX_CHECK(optixLaunch("))
        self.assertLess(body.index("OPTIX_CHECK(optixLaunch("), body.index("auto t_end_trav"))

    def test_runbook_enforces_local_readiness_before_pod(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("goal824_pre_cloud_rtx_readiness_gate.py", text)
        self.assertIn('"valid": true', text)
        self.assertIn("Do not start a pod for one app at a time.", text)

    def test_runbook_uses_bootstrap_and_artifact_audit(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("goal763_rtx_cloud_bootstrap_check.py", text)
        self.assertIn("Unsupported ABI version", text)
        self.assertIn("OptiX SDK headers `v8.0.0`", text)
        self.assertIn("OptiX SDK headers `v9.0.0` worked", text)
        self.assertIn("Do not patch `OPTIX_ABI_VERSION` manually", text)
        self.assertIn("RTDL_OPTIX_PTX_COMPILER=nvcc", text)
        self.assertIn("gnu/stubs-32.h", text)
        self.assertIn("cloud_claim_contract", text)
        self.assertIn("required_phase_groups", text)
        self.assertIn("needs_attention", text)

    def test_runbook_has_deferred_batch_controls_and_shutdown_rule(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("--include-deferred", text)
        for app in (
            "graph_analytics",
            "road_hazard_screening",
            "segment_polygon_hitcount",
            "segment_polygon_anyhit_rows",
            "hausdorff_distance",
            "ann_candidate_search",
            "barnes_hut_force_app",
            "polygon_pair_overlap_area_rows",
            "polygon_set_jaccard",
        ):
            with self.subTest(app=app):
                self.assertIn(app, text)
        self.assertIn("--only graph_visibility_edges_gate", text)
        self.assertIn("After copying artifacts back, stop or terminate the pod.", text)
        self.assertIn("does not authorize public RTX speedup claims", text)

    def test_runbook_prefers_oom_safe_groups_and_targeted_retry(self) -> None:
        text = RUNBOOK.read_text(encoding="utf-8")

        self.assertIn("OOM-Safe Small Batches", text)
        self.assertIn("Run one group at a time.", text)
        self.assertIn("After every group, copy back that group's summary JSON", text)
        self.assertIn("do not run the\nentire active+deferred manifest blindly", text)
        self.assertNotIn("One Full-Batch Command On The Pod", text)
        self.assertIn("Optional Targeted Deferred Retry", text)
        self.assertIn("Do not\nrestart the pod per app.", text)
        self.assertIn("The deferred batch is allowed to expose failures", text)
        self.assertIn("goal761_rtx_cloud_run_all.py", text)
        for group in (
            "Group A: Robot Flagship",
            "Group B: Fixed-Radius Summaries",
            "Group C: Database Analytics",
            "Group D: Spatial Prepared Summaries",
            "Group E: Segment/Polygon And Road Gates",
            "Group F: Graph Gate",
            "Group G: Prepared Decision Apps",
            "Group H: Polygon Apps",
        ):
            with self.subTest(group=group):
                self.assertIn(group, text)


if __name__ == "__main__":
    unittest.main()
