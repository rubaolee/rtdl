from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest import mock

from examples.benchmark_apps.hausdorff_xhd import rtdl_hausdorff_distance_app as hd
from examples.benchmark_apps.librts_spatial_index import (
    rtdl_librts_spatial_index_benchmark_app as librts,
)
from examples.benchmark_apps.triangle_counting import (
    rtdl_triangle_counting_benchmark_app as triangles,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = (
    ROOT
    / "docs"
    / "reports"
    / "goal3882_prepared_session_residency_metadata_remaining_profiled_apps_2026-06-08.md"
)
POD_ARTIFACT = ROOT / "docs" / "reports" / "goal3882_profiled_apps_residency_metadata_a5000" / "summary.json"


class _FakePreparedAabb:
    def count_prepared_query_set(self, *, point_queries, box_queries):
        return {"point_contains": 1, "range_contains": 2, "range_intersects": 3}

    def close(self) -> None:
        pass


class _FakePreparedQuery:
    def close(self) -> None:
        pass


class _FakeTriangleScene:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def ray_any_hit_weighted_sum(self, rays, ray_weights):
        return {"weighted_hit_sum": 0, "contract": "fake_weighted_sum"}


class Goal3882PreparedSessionResidencyMetadataRemainingProfiledAppsTest(unittest.TestCase):
    def _assert_metadata(self, payload: dict, *, primitive: str) -> None:
        metadata = payload["prepared_session_residency"]
        self.assertEqual(metadata["explicit_reuse_helper"], "get_or_prepare_explicit_session")
        self.assertFalse(metadata["cache_enabled_by_default"])
        self.assertTrue(metadata["cold_hot_phase_split_required"])
        self.assertTrue(metadata["prepare_once_query_many_pattern"])
        self.assertFalse(metadata["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["true_zero_copy_claim_authorized"])
        self.assertFalse(metadata["public_speedup_claim_authorized"])
        self.assertEqual(metadata["cache_key"]["primitive"], primitive)
        self.assertFalse(metadata["policy"]["automatic_partner_selection_authorized"])
        self.assertFalse(metadata["policy"]["true_zero_copy_claim_authorized"])

    def test_hausdorff_prepared_threshold_payload_has_residency_metadata(self) -> None:
        directed = {
            "within_threshold": True,
            "identity_parity_available": True,
            "run_phases": {
                "scene_prepare_sec": 0.1,
                "query_fixed_radius_threshold_reached_count_sec": 0.01,
                "query_fixed_radius_threshold_reached_count_total_sec": 0.02,
            },
        }
        oracle = {"hausdorff_distance": 0.1}
        with mock.patch.object(hd, "_run_prepared_directed_threshold", return_value=directed), mock.patch.object(
            hd,
            "expected_tiled_hausdorff",
            return_value=oracle,
        ):
            payload = hd.run_app(
                backend="optix",
                copies=2,
                optix_summary_mode="directed_threshold_prepared",
                hausdorff_threshold=0.25,
                query_repeat=2,
                warmup=1,
            )

        self._assert_metadata(payload, primitive="fixed_radius_threshold_2d")
        self.assertFalse(payload["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_librts_prepared_aabb_payload_has_residency_metadata(self) -> None:
        fixture = librts.LibRTSFixture(
            dataset="tiny",
            boxes=(librts.Box2D(0.0, 0.0, 1.0, 1.0),),
            point_queries=(librts.Point2D(0.5, 0.5),),
            box_queries=(librts.Box2D(0.25, 0.25, 0.75, 0.75),),
            seed=1,
        )
        with mock.patch.object(librts.rt, "prepare_optix_aabb_index_2d", return_value=_FakePreparedAabb()), mock.patch.object(
            librts.rt,
            "prepare_optix_aabb_point_queries_2d",
            return_value=_FakePreparedQuery(),
        ), mock.patch.object(
            librts.rt,
            "prepare_optix_aabb_box_queries_2d",
            return_value=_FakePreparedQuery(),
        ):
            payload = librts.run_optix_aabb_counts(
                fixture,
                "all",
                prepared_queries=True,
                query_repeat=2,
                warmup=1,
            )

        self._assert_metadata(payload, primitive="aabb_index_query_2d")
        self.assertFalse(payload["automatic_partner_selection_authorized"])
        self.assertFalse(payload["true_zero_copy_claim_authorized"])

    def test_triangle_counting_rt_graph_payload_has_residency_metadata(self) -> None:
        with mock.patch.object(
            triangles.rt,
            "prepare_optix_static_triangle_scene_3d",
            return_value=_FakeTriangleScene(),
        ):
            payload = triangles.rt_graph_2a1_generic_rt_payload(
                fixture="degree_oriented_two_triangles",
                edge_file=None,
                edge_format="text",
                backend="optix",
                detail="summary",
                partner="none",
                warmup=1,
                repeat=2,
                rt_graph_copies=2,
            )

        self._assert_metadata(payload, primitive="ray_triangle_weighted_any_hit_sum_3d")
        self.assertFalse(payload["claim_boundary"]["automatic_partner_selection_authorized"])
        self.assertFalse(payload["claim_boundary"]["true_zero_copy_claim_authorized"])

    def test_report_documents_remaining_profiled_apps(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        for phrase in (
            "Goal3882",
            "Hausdorff/X-HD",
            "LibRTS",
            "triangle-counting",
            "fixed_radius_threshold_2d",
            "aabb_index_query_2d",
            "ray_triangle_weighted_any_hit_sum_3d",
            "not a true-zero-copy or public speedup claim",
            "A5000 Evidence",
        ):
            self.assertIn(phrase, text)

    def test_a5000_artifact_confirms_all_profiled_apps_emit_metadata(self) -> None:
        payload = json.loads(POD_ARTIFACT.read_text(encoding="utf-8"))
        self.assertTrue(payload["all_pass"])
        self.assertEqual(payload["selected_prepared_session_residency_profile_count"], 4)
        expected_primitives = {
            "hausdorff_xhd_scale_default_optix_threshold": "fixed_radius_threshold_2d",
            "librts_spatial_index_optix_scale_default_32768": "aabb_index_query_2d",
            "rtnn_prepared_optix_scale_default_65536": "fixed_radius_neighbors_3d_ranked_summary",
            "triangle_counting_optix_rt_graph_2a1_scale_default_2048": "ray_triangle_weighted_any_hit_sum_3d",
        }
        self.assertEqual({row["row_id"] for row in payload["rows"]}, set(expected_primitives))
        for row in payload["rows"]:
            self.assertTrue(row["prepared_session_residency_profiled"], row["row_id"])
            stdout_path = POD_ARTIFACT.parent / "outputs" / f"{row['row_id']}.stdout.json"
            app_payload = json.loads(stdout_path.read_text(encoding="utf-8"))
            metadata = app_payload["prepared_session_residency"]
            self.assertEqual(metadata["cache_key"]["primitive"], expected_primitives[row["row_id"]])
            self.assertEqual(metadata["explicit_reuse_helper"], "get_or_prepare_explicit_session")
            self.assertFalse(metadata["automatic_partner_selection_authorized"])
            self.assertFalse(metadata["true_zero_copy_claim_authorized"])
            self.assertFalse(metadata["public_speedup_claim_authorized"])


if __name__ == "__main__":
    unittest.main()
