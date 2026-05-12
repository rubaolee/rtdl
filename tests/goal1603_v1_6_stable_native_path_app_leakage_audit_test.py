from pathlib import Path
import unittest

from src.rtdsl.v1_6_python_rtdl_readiness import (
    V1_6_PYTHON_RTDL_PENDING_PRIMITIVES,
    V1_6_PYTHON_RTDL_STABLE_PRIMITIVES,
)


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal1603_v1_6_stable_native_path_app_leakage_audit_2026-05-09.md"
GOAL1601_REPORT = ROOT / "docs" / "reports" / "goal1601_v1_6_release_surface_proposal_2026-05-09.md"
EMBREE_API = ROOT / "src" / "native" / "embree" / "rtdl_embree_api.cpp"
OPTIX_API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class Goal1603V16StableNativePathAppLeakageAuditTest(unittest.TestCase):
    def test_readiness_gate_keeps_collect_k_pending(self):
        self.assertIn("COLLECT_K_BOUNDED", V1_6_PYTHON_RTDL_PENDING_PRIMITIVES)
        self.assertNotIn("COLLECT_K_BOUNDED", V1_6_PYTHON_RTDL_STABLE_PRIMITIVES)

    def test_stable_primitive_exports_exist_for_embree_and_optix(self):
        embree = _text(EMBREE_API)
        optix = _text(OPTIX_API)
        for symbol in [
            "rtdl_embree_run_ray_anyhit",
            "rtdl_embree_run_ray_hitcount",
            "rtdl_embree_run_grouped_count",
            "rtdl_embree_run_grouped_sum",
            "rtdl_embree_run_fixed_radius_count_threshold",
        ]:
            self.assertIn(symbol, embree)
        for symbol in [
            "rtdl_optix_run_ray_anyhit",
            "rtdl_optix_run_ray_hitcount",
            "rtdl_optix_run_grouped_count",
            "rtdl_optix_run_grouped_sum",
            "rtdl_optix_run_fixed_radius_count_threshold",
        ]:
            self.assertIn(symbol, optix)

    def test_app_shaped_native_paths_are_still_present_and_excluded(self):
        # "Excluded" here means excluded from the public v1.6 claim boundary,
        # not removed from historical/proof native compatibility code.
        embree = _text(EMBREE_API)
        optix = _text(OPTIX_API)
        for symbol in [
            "rtdl_embree_run_shape_pair_relation_flags",
            "rtdl_embree_run_segment_shape_hitcount",
            "rtdl_embree_collect_shape_pair_candidates_bounded",
        ]:
            self.assertIn(symbol, embree)
        for symbol in [
            "rtdl_optix_run_shape_pair_relation_flags",
            "rtdl_optix_run_segment_shape_hitcount",
            "rtdl_optix_columnar_payload_compact_summary_batch",
        ]:
            self.assertIn(symbol, optix)
        # Goal1681: pip-family native exports were migrated to generic
        # point/primitive any-hit packet symbols. The pose-shaped OptiX
        # exports were similarly migrated to generic group-shaped exports
        # in Goal1673. Goal1682: the directed-Hausdorff Embree export was
        # migrated to a generic max-distance nearest-candidate export with
        # Hausdorff semantics retained at the Python layer.
        self.assertNotIn("rtdl_embree_run_pip", embree)
        self.assertNotIn("rtdl_optix_run_pip", optix)
        self.assertIn("rtdl_embree_run_point_primitive_anyhit_packet", embree)
        self.assertIn("rtdl_optix_run_point_primitive_anyhit_packet", optix)
        self.assertNotIn("rtdl_optix_prepare_pose_indices_2d", optix)
        self.assertIn("rtdl_optix_prepare_group_indices_2d", optix)
        self.assertNotIn("rtdl_embree_run_directed_hausdorff_2d", embree)
        self.assertIn("rtdl_embree_run_max_distance_nearest_candidate_2d", embree)
        # Goal1688: BFS-shaped native exports were migrated to generic
        # frontier/edge traversal packet symbols across Embree, HIPRT, OptiX,
        # Oracle, and Vulkan (Apple RT discover symbols deferred).
        self.assertNotIn("rtdl_embree_run_bfs_expand", embree)
        self.assertNotIn("rtdl_optix_run_bfs_expand", optix)
        self.assertIn("rtdl_embree_run_frontier_edge_traversal_packet", embree)
        self.assertIn("rtdl_optix_run_frontier_edge_traversal_packet", optix)

    def test_goal1601_and_goal1603_block_full_native_app_agnostic_claims(self):
        goal1601 = " ".join(_text(GOAL1601_REPORT).split())
        goal1603 = " ".join(_text(REPORT).split())
        self.assertIn(
            "Claims that native internals are fully app-agnostic if compatibility/proof "
            "paths with app-shaped names or semantics remain.",
            goal1601,
        )
        for phrase in [
            "native engine tree is not fully app-agnostic internally",
            "does block any claim that native internals are fully app-agnostic",
            "Stable public surface: primitive-named Python+RTDL contracts",
            "Excluded/internal surface: app-shaped compatibility and proof exports",
            "Pending surface: `COLLECT_K_BOUNDED`",
        ]:
            self.assertIn(phrase, goal1603)

    def test_goal1603_does_not_authorize_release_or_blocked_claims(self):
        text = " ".join(_text(REPORT).split())
        for phrase in [
            "`v1.6` remains unpublished",
            "does not authorize release/tag action",
            "public speedup wording",
            "true zero-copy wording",
            "partner tensor handoff claims",
            "stable `COLLECT_K_BOUNDED` promotion",
        ]:
            self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
