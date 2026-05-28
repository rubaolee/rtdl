from __future__ import annotations

import os
from pathlib import Path
import unittest

import rtdsl as rt
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


class Goal2640ExpandedAabbPointMembershipTest(unittest.TestCase):
    def test_cpu_reference_emits_expanded_point_membership_rows(self) -> None:
        payload = rt.expanded_aabb_point_membership_rows_2d(
            indexed_boxes=((0.0, 0.0, 1.0, 1.0), (3.0, 0.0, 4.0, 1.0)),
            source_points=((0.5, 0.5), (2.75, 0.5), (10.0, 10.0)),
            expansions=(0.0, 0.3),
            indexed_ids=(100, 101),
            source_ids=(200, 201, 202),
            resolution=8,
        )

        self.assertEqual(payload["primitive"], "EXPANDED_AABB_POINT_MEMBERSHIP_2D")
        self.assertEqual(payload["contract"], "generic_expanded_aabb_point_membership_rows_2d_v1")
        self.assertEqual(payload["row_schema"], ("source_id", "box_id", "metadata_flags"))
        self.assertEqual(payload["candidate_id_rows"], ((200, 100, 0), (201, 101, 0)))
        self.assertEqual(payload["source_ids"], (200, 201, 202))
        self.assertEqual(payload["row_offsets"], (0, 1, 2, 2))
        self.assertFalse(payload["native_engine_customization"])
        self.assertFalse(payload["rt_core_accelerated"])

    def test_fail_closed_total_capacity_overflow(self) -> None:
        with self.assertRaisesRegex(
            rt.ExpandedAabbPointMembershipOverflowError,
            "failure_mode=fail_closed_overflow",
        ):
            rt.expanded_aabb_point_membership_rows_2d(
                indexed_boxes=((0.0, 0.0, 2.0, 2.0), (0.0, 0.0, 2.0, 2.0)),
                source_points=((1.0, 1.0),),
                indexed_ids=(10, 11),
                source_ids=(20,),
                row_capacity=1,
            )

    def test_fail_closed_per_source_capacity_overflow(self) -> None:
        with self.assertRaisesRegex(
            rt.ExpandedAabbPointMembershipOverflowError,
            "partial_result_returned=False",
        ):
            rt.expanded_aabb_point_membership_rows_2d(
                indexed_boxes=((0.0, 0.0, 2.0, 2.0), (0.0, 0.0, 2.0, 2.0)),
                source_points=((1.0, 1.0),),
                indexed_ids=(10, 11),
                source_ids=(20,),
                max_rows_per_source=1,
            )

    def test_contract_exports_and_native_symbols_are_app_agnostic(self) -> None:
        self.assertIn("expanded_aabb_point_membership_rows_2d", rt.__all__)
        self.assertIn("collect_aabb_point_membership_pair_rows_2d_optix", rt.__all__)
        self.assertIn("point_contains_rows", rt.AABB_INDEX_2D_CONTRACT["operations"])
        self.assertIn(
            "point_contains_rows",
            rt.AABB_INDEX_2D_CONTRACT["backend_status"]["optix"],
        )

        prelude = (ROOT / "src/native/optix/rtdl_optix_prelude.h").read_text(encoding="utf-8")
        api = (ROOT / "src/native/optix/rtdl_optix_api.cpp").read_text(encoding="utf-8")
        workloads = (ROOT / "src/native/optix/rtdl_optix_workloads.cpp").read_text(encoding="utf-8")
        wrapper = (ROOT / "src/rtdsl/optix_runtime.py").read_text(encoding="utf-8")
        symbol = "rtdl_optix_collect_prepared_aabb_index_2d_point_contains_rows"
        self.assertIn(symbol, prelude + api + wrapper)
        helper_start = workloads.index(
            "static void collect_prepared_aabb_index_2d_point_contains_rows_optix"
        )
        helper_end = workloads.index(
            "static void ensure_pack_triangle2d_device_columns_kernel",
            helper_start,
        )
        helper_source = workloads[helper_start:helper_end].lower()
        for forbidden in ("barnes", "force", "mass", "nbody", "contact", "collision"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, helper_source)

    @unittest.skipUnless(embree_available(), "Embree backend library not available locally")
    def test_embree_rows_match_cpu_for_tiny_fixture(self) -> None:
        args = {
            "indexed_boxes": ((0.0, 0.0, 1.0, 1.0), (3.0, 0.0, 4.0, 1.0)),
            "source_points": ((0.5, 0.5), (2.75, 0.5), (10.0, 10.0)),
            "expansions": (0.0, 0.3),
            "indexed_ids": (100, 101),
            "source_ids": (200, 201, 202),
        }
        cpu = rt.expanded_aabb_point_membership_rows_2d(**args)
        embree = rt.expanded_aabb_point_membership_rows_2d(**args, backend="embree")

        self.assertEqual(embree["candidate_id_rows"], cpu["candidate_id_rows"])
        self.assertEqual(embree["row_offsets"], cpu["row_offsets"])
        self.assertEqual(embree["backend"], "embree")

    @unittest.skipUnless(_optix_library_available(), "OptiX backend library not available locally")
    def test_optix_rows_match_cpu_for_tiny_fixture(self) -> None:
        args = {
            "indexed_boxes": ((0.0, 0.0, 1.0, 1.0), (3.0, 0.0, 4.0, 1.0)),
            "source_points": ((0.5, 0.5), (2.75, 0.5), (10.0, 10.0)),
            "expansions": (0.0, 0.3),
            "indexed_ids": (100, 101),
            "source_ids": (200, 201, 202),
            "row_capacity": 6,
        }
        cpu = rt.expanded_aabb_point_membership_rows_2d(**args)
        optix = rt.expanded_aabb_point_membership_rows_2d(**args, backend="optix")

        self.assertEqual(optix["candidate_id_rows"], cpu["candidate_id_rows"])
        self.assertEqual(optix["row_offsets"], cpu["row_offsets"])
        self.assertTrue(optix["rt_core_accelerated"])


if __name__ == "__main__":
    unittest.main()
