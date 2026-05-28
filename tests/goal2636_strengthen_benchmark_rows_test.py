from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts import goal2636_strengthen_benchmark_rows as runner
from rtdsl.baseline_runner import load_representative_case


class Goal2636StrengthenBenchmarkRowsTest(unittest.TestCase):
    def test_smoke_tier_covers_the_five_weak_apps(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = runner.build_cases("smoke", Path(tmp))

        app_ids = {case.app_id for case in cases}
        self.assertEqual(app_ids, set(runner.WEAK_ROW_APPS))

    def test_standard_tier_contains_expected_strengthening_cases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = runner.build_cases("standard", Path(tmp))

        case_ids = {case.case_id for case in cases}
        expected = {
            "hausdorff_optix_exact_grouped_seeded_pruned_points_8192",
            "rayjoin_optix_prepared_overlay_seed_tiled_x512",
            "rtnn_optix_clustered_65536_ranked_summary",
            "barnes_hut_optix_node_coverage_bodies_32768",
            "triangle_counting_optix_rt_graph_2a1_cliques_20000",
        }
        self.assertTrue(expected.issubset(case_ids))

    def test_rayjoin_uses_derived_tiled_datasets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = runner.build_cases("standard", Path(tmp))

        rayjoin_commands = [
            " ".join(case.command or ())
            for case in cases
            if case.app_id == "spatial_rayjoin"
        ]
        self.assertTrue(any("derived/authored_pip_square_tiled_x512" in command for command in rayjoin_commands))
        self.assertTrue(any("derived/authored_lsi_crossing_tiled_x512" in command for command in rayjoin_commands))
        self.assertTrue(any("derived/authored_overlay_squares_tiled_x512" in command for command in rayjoin_commands))

    def test_rayjoin_stress_uses_larger_derived_tiled_datasets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cases = runner.build_cases("stress", Path(tmp))

        rayjoin_commands = [
            " ".join(case.command or ())
            for case in cases
            if case.app_id == "spatial_rayjoin"
        ]
        self.assertTrue(any("derived/authored_pip_square_tiled_x2048" in command for command in rayjoin_commands))
        self.assertTrue(any("derived/authored_lsi_crossing_tiled_x2048" in command for command in rayjoin_commands))
        self.assertTrue(any("derived/authored_overlay_squares_tiled_x2048" in command for command in rayjoin_commands))

    def test_rayjoin_authored_tiled_fixtures_are_nonzero(self) -> None:
        pip = load_representative_case("pip", "derived/authored_pip_square_tiled_x64")
        lsi = load_representative_case("lsi", "derived/authored_lsi_crossing_tiled_x64")
        overlay = load_representative_case("overlay", "derived/authored_overlay_squares_tiled_x64")

        self.assertEqual(len(pip.inputs["points"]), 128)
        self.assertEqual(len(pip.inputs["polygons"]), 64)
        self.assertEqual(len(lsi.inputs["left"]), 64)
        self.assertEqual(len(lsi.inputs["right"]), 64)
        self.assertEqual(len(overlay.inputs["left"]), 64)
        self.assertEqual(len(overlay.inputs["right"]), 64)

    def test_dry_run_writes_summary(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            artifact_dir = Path(tmp) / "artifacts"
            exit_code = runner.main(["--tier", "smoke", "--dry-run", "--artifact-dir", str(artifact_dir)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((artifact_dir / "summary.json").exists())
            self.assertTrue((artifact_dir / "summary.md").exists())


if __name__ == "__main__":
    unittest.main()
