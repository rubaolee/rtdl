from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts import goal2636_strengthen_benchmark_rows as runner


class Goal3582RayjoinPromotedStrengthenedRunnerTest(unittest.TestCase):
    def test_rayjoin_optix_rows_use_promoted_routes_and_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = runner.build_cases("standard", Path(tmp))

        rayjoin_optix = {
            case.case_id: case
            for case in cases
            if case.app_id == "spatial_rayjoin" and case.backend == "optix"
        }
        self.assertEqual(
            set(rayjoin_optix),
            {
                "rayjoin_optix_promoted_pip_tiled_x512",
                "rayjoin_optix_promoted_lsi_tiled_x512",
                "rayjoin_optix_promoted_overlay_seed_tiled_x512",
            },
        )
        expected = {
            "rayjoin_optix_promoted_pip_tiled_x512": (
                "prepared_optix_cupy_refined_pip",
                ("phases_sec", "prepared_cupy_refine_sec"),
            ),
            "rayjoin_optix_promoted_lsi_tiled_x512": (
                "prepared_optix_left_id_dense_count",
                ("phases_sec", "left_id_count_device_columns_sec"),
            ),
            "rayjoin_optix_promoted_overlay_seed_tiled_x512": (
                "prepared_optix_shape_pair_active_count",
                ("phases_sec", "active_count_device_continuation_sec"),
            ),
        }
        for case_id, (route, metric_path) in expected.items():
            with self.subTest(case_id=case_id):
                case = rayjoin_optix[case_id]
                self.assertIn(route, " ".join(case.command or ()))
                self.assertEqual(case.primary_metric_path, metric_path)
                self.assertIn("Promoted", case.notes)
                self.assertIn("RayJoin paper reproduction", case.notes)

    def test_smoke_dry_run_contains_promoted_rayjoin_case_ids(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifacts"
            self.assertEqual(
                runner.main(["--tier", "smoke", "--dry-run", "--artifact-dir", str(artifact_dir)]),
                0,
            )
            text = (artifact_dir / "summary.md").read_text(encoding="utf-8")
        self.assertIn("rayjoin_optix_promoted_pip_tiled_x64", text)
        self.assertIn("rayjoin_optix_promoted_lsi_tiled_x64", text)
        self.assertIn("rayjoin_optix_promoted_overlay_seed_tiled_x64", text)


if __name__ == "__main__":
    unittest.main()
