import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOSSIER = ROOT / "docs" / "rebuild" / "v3" / "phoenix_v3_user_facing_performance_dossier_2026-06-22.md"
PUBLIC_MAP = ROOT / "docs" / "public_documentation_map.md"
README = ROOT / "docs" / "rebuild" / "v3" / "README.md"
WORDING_GATE = ROOT / "scripts" / "v3_release_wording_gate.py"
READINESS_GATE = ROOT / "scripts" / "v3_phoenix_release_readiness_gate.py"


ROW_IDS = (
    "grouped_reduction_sum_scalar_broadcast_repeat100_262144",
    "grouped_reduction_sum_cupy_device_columns_repeat100_262144_rows_1024_groups",
    "grouped_reduction_sum_cupy_device_columns_repeat100_524288_rows_2048_groups",
    "aabb_candidate_stream_all_count_only_float32_32768",
    "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_32768_repeat50",
    "aabb_candidate_stream_range_intersection_rows_native_query_handle_jittered_grid_65536_repeat50",
    "component_union_clustered3d_65536_524288_repeat5_row_scoped",
    "prepared_graph_chunk_rt_graph_2a1_cliques_80000_non_graph_stream",
    "rtnn_prepared_ranked_summary_npz_cubin_repeat50_1048576_points_k50_radius_0_02",
    "aggregate_tree_fused_weighted_vector_sum_numba_cuda_131072_repeat11_row_scoped",
    "hausdorff_threshold_summary_1048576_threshold_0_4_stability_row_scoped",
    "collision_flag_stream_8192poses_no_probe_paired_validation_separated_row_scoped",
    "point_location_topology_stream_relation_status_guarded_squared_boundary_prefilter_zero_county_repeat50_sample7",
)


APP_IDS = (
    "raydb_style",
    "librts_spatial_index",
    "rt_dbscan",
    "triangle_counting",
    "rtnn",
    "barnes_hut",
    "hausdorff_xhd",
    "robot_collision",
    "contact_manifold",
    "spatial_rayjoin",
)


class V3PhoenixUserFacingPerformanceDossierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = DOSSIER.read_text(encoding="utf-8")

    def test_dossier_keeps_release_blocked_and_scoped(self):
        for phrase in (
            "Status: `redo_required`",
            "release_authorized: false",
            "public_speedup_claim_authorized: false",
            "broad_v3_faster_than_v2_claim_authorized: false",
            "broad_v2x_performance_not_proven",
            "serious_all_app_paired_evidence_failed_release_bar",
            "current_scoped_13_row_surface_not_v3_major_release",
            "same_metric_comparison_count: 52",
            "Geomean V3 speedup vs V2.14: 1.012x",
            "release_consideration_eligible: false",
            "app_geomeans_gt_1.05x: 1 of 10",
            "app_geomeans_lt_0.95x: 2 of 10",
            "not a major broad speedup claim",
            "benchmark apps are not the product",
            "reusable RTRDL language/runtime improvement over V2.x",
            "Rows outside this list are internal, blocked, no-go, historical, or future work",
        ):
            self.assertIn(phrase, self.text)

    def test_dossier_lists_exact_thirteen_current_rows(self):
        for row_id in ROW_IDS:
            self.assertIn(row_id, self.text)
        self.assertIn("13 exact current rows", self.text)
        self.assertIn("all 13 rows are row-scoped or supplemental", self.text)

    def test_dossier_explains_all_app_boundaries_and_no_go_numbers(self):
        for app_id in APP_IDS:
            self.assertIn(f"`{app_id}`", self.text)
        for phrase in (
            "wall timing is 0.803x",
            "30489.613x",
            "1483.603x",
            "13.591x",
            "not true zero-copy",
            "not release authorization",
            "Do not claim V3 released or complete.",
            "Do not claim C ABI, embedding, public SDK/package, or multi-language host support.",
        ):
            self.assertIn(phrase, self.text)

    def test_dossier_is_front_door_linked(self):
        public_map = PUBLIC_MAP.read_text(encoding="utf-8")
        readme = README.read_text(encoding="utf-8")
        self.assertIn("Phoenix V3 Performance Dossier", public_map)
        self.assertIn("phoenix_v3_user_facing_performance_dossier_2026-06-22.md", public_map)
        self.assertIn("Phoenix V3 User-Facing Performance Dossier", readme)
        self.assertIn("phoenix_v3_user_facing_performance_dossier_2026-06-22.md", readme)

    def test_wording_and_readiness_gates_reference_dossier(self):
        wording = subprocess.run(
            [sys.executable, str(WORDING_GATE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(wording.returncode, 0, wording.stdout + wording.stderr)
        wording_payload = json.loads(wording.stdout)
        self.assertEqual(wording_payload["status"], "pass")
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_user_facing_performance_dossier_2026-06-22.md",
            wording_payload["scanned_files"],
        )

        readiness = subprocess.run(
            [sys.executable, str(READINESS_GATE)],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(readiness.returncode, 0, readiness.stdout + readiness.stderr)
        readiness_payload = json.loads(readiness.stdout)
        self.assertEqual(readiness_payload["status"], "redo_required")
        self.assertFalse(readiness_payload["release_authorized"])
        self.assertFalse(readiness_payload["public_speedup_claim_authorized"])
        self.assertFalse(readiness_payload["broad_v3_faster_than_v2_claim_authorized"])
        self.assertEqual(
            readiness_payload["blocking_reasons"],
            [
                "broad_v2x_performance_not_proven",
                "serious_all_app_paired_evidence_failed_release_bar",
                "current_scoped_13_row_surface_not_v3_major_release",
                "current_core_gap_external_review_blocks_release",
            ],
        )
        self.assertEqual(readiness_payload["failed_checks"], [])
        self.assertEqual(
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_file_count"],
            24,
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_user_facing_performance_dossier_2026-06-22.md",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_objective_conformance_gate_2026-06-22.json",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_external_verdict_intake_2026-06-22.json",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\phoenix_v3_external_verdict_response_template_2026-06-22.md",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\claude_phoenix_v3_external_review_2026-06-22.md",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\rebuild\\v3\\phoenix_v3_core_gaps_external_verdict_status_2026-06-22.md",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reviews\\phoenix_v3_set_a_set_b_release_bar_proposal_2026-06-22.md",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )
        self.assertIn(
            "docs\\reports\\phoenix_v3_aabb_native_query_handle_runner_route_m2_2026-06-22.md",
            readiness_payload["evidence"]["aggregate_13_row_review_packet_reference_files"],
        )


if __name__ == "__main__":
    unittest.main()
