from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt
from examples.v2_0.research_benchmarks.contact_manifold import (
    rtdl_contact_manifold_benchmark_app as app,
)
from tests._embree_support import embree_available


ROOT = Path(__file__).resolve().parents[1]


def _optix_library_available() -> bool:
    env_path = os.environ.get("RTDL_OPTIX_LIBRARY")
    if env_path and Path(env_path).exists():
        return True
    return any(
        candidate.exists()
        for candidate in (
            ROOT / "build" / "librtdl_optix.so",
            ROOT / "build" / "librtdl_optix.dylib",
        )
    )


class Goal2623OptixAabbPairRowsTest(unittest.TestCase):
    def test_public_contract_exports_generic_optix_pair_row_wrapper(self) -> None:
        self.assertIn("range_intersection_rows", rt.AABB_INDEX_2D_CONTRACT["operations"])
        self.assertIn("collect_aabb_intersection_pair_rows_2d_optix", rt.__all__)
        self.assertIn(
            "range_intersection_rows",
            rt.AABB_INDEX_2D_CONTRACT["backend_status"]["optix"],
        )
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal2623_optix_aabb_intersection_pair_rows_2026-05-25.md"
        ).read_text(encoding="utf-8")
        consensus = (
            ROOT
            / "docs"
            / "reports"
            / "goal2623_optix_aabb_intersection_pair_rows_3ai_consensus_2026-05-25.md"
        ).read_text(encoding="utf-8")
        self.assertIn("failure_mode=fail_closed_overflow", report)
        self.assertIn("without native", report.lower())
        self.assertIn("contact/collision logic", report.lower())
        self.assertIn("3-AI consensus is reached", consensus)
        self.assertIn("No native contact/collision/manifold", consensus)

    def test_optix_pair_row_abi_is_generic_not_contact_specific(self) -> None:
        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(
            encoding="utf-8"
        )
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(
            encoding="utf-8"
        )

        self.assertIn("RtdlAabbPairRow", prelude)
        self.assertIn("static_assert(sizeof(RtdlAabbPairRow) == 8", prelude)
        self.assertIn(
            "rtdl_optix_collect_prepared_aabb_index_2d_range_intersection_rows",
            prelude + api,
        )
        helper_start = workloads.index(
            "static void collect_prepared_aabb_index_2d_range_intersection_rows_optix"
        )
        helper_end = workloads.index(
            "static void ensure_pack_triangle2d_device_columns_kernel",
            helper_start,
        )
        helper_source = workloads[helper_start:helper_end].lower()
        self.assertNotIn("contact", helper_source)
        self.assertNotIn("collision", helper_source)
        self.assertNotIn("triangle", helper_source)

    def test_cpu_row_contract_still_matches_expected_rows(self) -> None:
        payload = rt.aabb_intersection_pair_rows_2d(
            indexed_boxes=((0.0, 0.0, 1.0, 1.0), (2.0, 0.0, 3.0, 1.0)),
            query_boxes=((0.5, 0.0, 0.75, 1.0), (1.5, 0.0, 2.5, 1.0)),
            indexed_ids=(100, 101),
            query_ids=(200, 201),
            resolution=8,
        )

        self.assertEqual(payload["candidate_id_rows"], ((200, 100), (201, 101)))
        self.assertFalse(payload["native_engine_customization"])

    def test_optix_rejects_ids_that_do_not_fit_native_row_layout(self) -> None:
        with self.assertRaisesRegex(ValueError, "uint32"):
            rt.aabb_intersection_pair_rows_2d(
                indexed_boxes=((0.0, 0.0, 1.0, 1.0),),
                query_boxes=((0.0, 0.0, 1.0, 1.0),),
                indexed_ids=(-1,),
                query_ids=(0,),
                backend="optix",
                row_capacity=1,
            )

    def test_optix_requires_explicit_row_capacity(self) -> None:
        with self.assertRaisesRegex(ValueError, "explicit row_capacity"):
            rt.aabb_intersection_pair_rows_2d(
                indexed_boxes=((0.0, 0.0, 1.0, 1.0),),
                query_boxes=((0.0, 0.0, 1.0, 1.0),),
                backend="optix",
            )

    @unittest.skipUnless(embree_available(), "Embree backend library not available locally")
    def test_embree_pair_rows_match_cpu_for_tiny_fixture(self) -> None:
        indexed = ((0.0, 0.0, 1.0, 1.0), (2.0, 0.0, 3.0, 1.0))
        queries = ((0.5, 0.0, 0.75, 1.0), (1.5, 0.0, 2.5, 1.0))
        cpu = rt.aabb_intersection_pair_rows_2d(
            indexed,
            queries,
            indexed_ids=(100, 101),
            query_ids=(200, 201),
            resolution=8,
        )
        embree = rt.aabb_intersection_pair_rows_2d(
            indexed,
            queries,
            indexed_ids=(100, 101),
            query_ids=(200, 201),
            backend="embree",
        )

        self.assertEqual(embree["candidate_id_rows"], cpu["candidate_id_rows"])
        self.assertEqual(embree["backend"], "embree")
        self.assertFalse(embree["native_engine_customization"])

    @unittest.skipUnless(_optix_library_available(), "OptiX backend library not available locally")
    def test_optix_pair_rows_match_cpu_for_tiny_fixture(self) -> None:
        indexed = ((0.0, 0.0, 1.0, 1.0), (2.0, 0.0, 3.0, 1.0))
        queries = ((0.5, 0.0, 0.75, 1.0), (1.5, 0.0, 2.5, 1.0))
        cpu = rt.aabb_intersection_pair_rows_2d(
            indexed,
            queries,
            indexed_ids=(100, 101),
            query_ids=(200, 201),
            resolution=8,
        )
        optix = rt.aabb_intersection_pair_rows_2d(
            indexed,
            queries,
            indexed_ids=(100, 101),
            query_ids=(200, 201),
            backend="optix",
            row_capacity=4,
        )

        self.assertEqual(optix["candidate_id_rows"], cpu["candidate_id_rows"])
        self.assertTrue(optix["rt_core_accelerated"])
        self.assertFalse(optix["native_engine_customization"])

    @unittest.skipUnless(_optix_library_available(), "OptiX backend library not available locally")
    def test_optix_pair_rows_fail_closed_on_capacity_overflow(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "failure_mode=fail_closed_overflow"):
            rt.aabb_intersection_pair_rows_2d(
                indexed_boxes=((0.0, 0.0, 1.0, 1.0), (2.0, 0.0, 3.0, 1.0)),
                query_boxes=((0.5, 0.0, 0.75, 1.0), (1.5, 0.0, 2.5, 1.0)),
                backend="optix",
                row_capacity=1,
            )

    @unittest.skipUnless(_optix_library_available(), "OptiX backend library not available locally")
    def test_contact_app_can_select_optix_discovery_backend(self) -> None:
        payload = app.aabb_broadphase_collect_k_payload(
            dataset="tiny",
            witness_capacity=3,
            discovery_backend="optix",
            discovery_row_capacity=8,
        )

        self.assertTrue(payload["matches_cpu_reference"])
        self.assertEqual(payload["candidate_discovery_backend"], "optix")
        self.assertFalse(payload["engine_boundary"]["native_collision_logic_allowed"])


if __name__ == "__main__":
    unittest.main()
