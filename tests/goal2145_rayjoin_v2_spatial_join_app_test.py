from __future__ import annotations

import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP = (
    ROOT
    / "examples"
    / "v2_0"
    / "research_benchmarks"
    / "spatial_rayjoin"
    / "rtdl_rayjoin_v2_spatial_join_app.py"
)

sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from examples import rtdl_rayjoin_v2_spatial_join_app as app


class Goal2145RayjoinV2SpatialJoinAppTest(unittest.TestCase):
    def test_suite_runs_three_rayjoin_workloads_with_boundaries(self) -> None:
        payload = app.run_rayjoin_suite(backend="cpu_python_reference", include_rows=False)

        self.assertEqual(payload["app"], "rayjoin_v2_spatial_join")
        self.assertEqual(set(payload["workloads"]), {"pip", "lsi", "overlay_seed"})
        self.assertTrue(payload["all_match_cpu_python_reference"])
        for workload, result in payload["workloads"].items():
            with self.subTest(workload=workload):
                self.assertEqual(result["app"], "rayjoin_v2_spatial_join")
                self.assertTrue(result["parity_vs_cpu_python_reference"])
                self.assertFalse(result["claim_boundary"]["full_rayjoin_reproduction"])
                self.assertFalse(result["claim_boundary"]["paper_scale_perf_claim_authorized"])
                self.assertIn("generic point, segment, polygon", result["native_engine_boundary"])

    def test_pip_positive_assignments_are_user_policy_not_engine_surface(self) -> None:
        payload = app.run_rayjoin_workload("pip", backend="cpu_python_reference", include_rows=True)

        self.assertEqual(
            payload["summary"]["output_contract"],
            "point_to_polygon_positive_hit_rows",
        )
        self.assertEqual(
            payload["summary"]["positive_hit_row_count"],
            payload["summary"]["positive_assignment_count"],
        )
        for row in payload["rows"]:
            self.assertEqual(row["contains"], 1)
        for row in payload["summary"]["positive_assignments"]:
            self.assertEqual(set(row), {"point_id", "polygon_id"})

    def test_lsi_and_overlay_seed_contracts_are_distinct(self) -> None:
        lsi = app.run_rayjoin_workload("lsi", backend="cpu_python_reference", include_rows=False)
        overlay = app.run_rayjoin_workload("overlay_seed", backend="cpu_python_reference", include_rows=False)

        self.assertEqual(lsi["summary"]["output_contract"], "segment_segment_intersection_rows")
        self.assertIn("intersection_count", lsi["summary"])
        self.assertEqual(
            overlay["summary"]["output_contract"],
            "overlay_pair_dependency_rows_with_lsi_pip_flags",
        )
        self.assertIn("pair_dependency_row_count", overlay["summary"])
        self.assertIn("active_seed_count", overlay["summary"])
        self.assertIn("active_seed_pairs", overlay["summary"])

    def test_cli_outputs_json_without_rows(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(APP),
                "--workload",
                "pip",
                "--backend",
                "cpu_python_reference",
                "--no-rows",
            ],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn('"workload": "pip"', completed.stdout)
        self.assertIn('"positive_assignment_count"', completed.stdout)
        self.assertNotIn('"rows"', completed.stdout)

    def test_external_cdb_paths_are_loaded_without_engine_customization(self) -> None:
        fixture_root = ROOT / "tests" / "fixtures" / "rayjoin"
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = pathlib.Path(temp_dir)
            county = temp_root / "county_external.cdb"
            soil = temp_root / "soil_external.cdb"
            shutil.copyfile(fixture_root / "br_county_subset.cdb", county)
            shutil.copyfile(fixture_root / "br_soil_subset.cdb", soil)

            pip = app.run_rayjoin_workload(
                "pip",
                backend="cpu_python_reference",
                dataset=str(county),
                include_rows=False,
            )
            overlay = app.run_rayjoin_workload(
                "overlay_seed",
                backend="cpu_python_reference",
                dataset=f"{county} + {soil}",
                include_rows=False,
            )

        self.assertIn("External CDB point-location", pip["dataset_note"])
        self.assertEqual(pip["summary"]["output_contract"], "point_to_polygon_positive_hit_rows")
        self.assertIn("External CDB overlay", overlay["dataset_note"])
        self.assertEqual(
            overlay["summary"]["output_contract"],
            "overlay_pair_dependency_rows_with_lsi_pip_flags",
        )


if __name__ == "__main__":
    unittest.main()
