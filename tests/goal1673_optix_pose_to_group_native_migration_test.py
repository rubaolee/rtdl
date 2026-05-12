from __future__ import annotations

from pathlib import Path
import unittest

import rtdsl as rt


ROOT = Path(__file__).resolve().parents[1]
NATIVE_OPTIX = (
    ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h",
    ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp",
)
REPORT = ROOT / "docs" / "reports" / "goal1673_optix_pose_to_group_native_migration_2026-05-10.md"
GOAL1672 = ROOT / "docs" / "reports" / "goal1672_native_app_leakage_migration_classification_2026-05-10.md"


class Goal1673OptixPoseToGroupNativeMigrationTest(unittest.TestCase):
    def test_optix_native_files_no_longer_use_pose_term(self) -> None:
        for path in NATIVE_OPTIX:
            with self.subTest(path=path.name):
                self.assertNotIn("pose", path.read_text(encoding="utf-8").lower())

    def test_optix_native_exports_group_named_symbols(self) -> None:
        combined = "\n".join(path.read_text(encoding="utf-8") for path in NATIVE_OPTIX)
        for phrase in (
            "rtdl_optix_group_flags_prepared_ray_anyhit_2d_packed",
            "rtdl_optix_prepare_group_indices_2d",
            "rtdl_optix_group_flags_prepared_ray_anyhit_2d_prepared_indices",
            "rtdl_optix_count_groups_prepared_ray_anyhit_2d_prepared_indices",
            "rtdl_optix_destroy_prepared_group_indices_2d",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, combined)

    def test_python_keeps_compatibility_aliases_outside_native_engine(self) -> None:
        self.assertIs(rt.OptixPoseIndexBuffer, rt.OptixGroupIndexBuffer)
        with rt.prepare_optix_group_indices_2d(()) as group_indices:
            self.assertEqual(group_indices.count, 0)
        with rt.prepare_optix_pose_indices_2d(()) as pose_indices:
            self.assertIsInstance(pose_indices, rt.OptixGroupIndexBuffer)

        with rt.prepare_optix_rays_2d(()) as rays:
            with rt.prepare_optix_ray_triangle_any_hit_2d(()) as prepared:
                self.assertEqual(prepared.group_flags_packed(rays, (), group_count=2), (False, False))
                self.assertEqual(prepared.pose_flags_packed(rays, (), pose_count=2), (False, False))

    def test_reports_record_boundary_and_no_pod_claim(self) -> None:
        report_text = REPORT.read_text(encoding="utf-8")
        goal1672_text = GOAL1672.read_text(encoding="utf-8")
        for phrase in (
            "no longer exports\npose-shaped native symbols",
            "This is a local source migration only",
            "No pod validation was run",
            "full native app-agnostic claim",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, report_text)
        self.assertIn("Goal1673 completed the first local source migration", goal1672_text)


if __name__ == "__main__":
    unittest.main()
