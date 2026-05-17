from __future__ import annotations

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "goal2159_rayjoin_public_cdb_runner.py"
FIXTURES = ROOT / "tests" / "fixtures" / "rayjoin"


class Goal2175RayjoinOverlayRunnerDirectReferenceTest(unittest.TestCase):
    def test_dry_run_exposes_larger_overlay_case_and_prepared_backend(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = pathlib.Path(temp_dir)
            data_dir = temp / "data"
            data_dir.mkdir()
            (data_dir / "br_county.cdb").write_text(
                (FIXTURES / "br_county_subset.cdb").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (data_dir / "br_soil.cdb").write_text(
                (FIXTURES / "br_soil_subset.cdb").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            output = temp / "dry_run.json"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--data-dir",
                    str(data_dir),
                    "--output",
                    str(output),
                    "--cases",
                    "overlay_county256_soil256",
                    "--backends",
                    "cpu,embree,optix,optix_prepared_overlay_seed",
                    "--dry-run",
                ],
                cwd=ROOT,
                check=True,
                env={
                    **os.environ,
                    "PYTHONPATH": f"{ROOT / 'src'}{';' if sys.platform == 'win32' else ':'}{ROOT}",
                },
            )
            artifact = json.loads(output.read_text(encoding="utf-8"))

        case = artifact["cases"]["overlay_county256_soil256"]
        self.assertEqual(case["workload"], "overlay_seed")
        self.assertIn("optix_prepared_overlay_seed", case["backends"])
        self.assertIn("county_0_256", artifact["slices"])
        self.assertIn("soil_0_256", artifact["slices"])
        self.assertFalse(artifact["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])

    def test_runner_source_reuses_reference_for_direct_overlay_timings(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        self.assertIn("_run_overlay_seed_direct_backend", text)
        self.assertIn("_run_lsi_direct_backend", text)
        self.assertIn("_run_pip_direct_backend", text)
        self.assertIn("county_soil_overlay_reference", text)
        self.assertIn("county_zip_join_reference", text)
        self.assertIn("rayjoin_point_location_positive_hits_reference", text)
        self.assertIn("direct_overlay_seed_runner", text)
        self.assertIn("direct_lsi_runner", text)
        self.assertIn("direct_pip_runner", text)
        self.assertIn("reference_reused_per_backend", text)
        self.assertIn("shared_pip_reference_rows", text)
        self.assertIn("shared_lsi_reference_rows", text)
        self.assertIn("shared_overlay_reference_rows", text)
        self.assertIn("prepare shared", text)
        self.assertIn("reused_by_backends", text)
        self.assertIn("overlay_county256_soil256", text)
        self.assertIn("overlay_county384_soil384", text)
        self.assertIn("overlay_county512_soil512", text)

    def test_pip_input_loader_reads_probe_points_and_polygons(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location("goal2159_runner", SCRIPT)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        points, polygons = module._load_pip_inputs(str(FIXTURES / "br_county_subset.cdb"))

        self.assertGreater(len(points), 0)
        self.assertGreater(len(polygons), 0)
        self.assertTrue(hasattr(points[0], "x"))
        self.assertTrue(hasattr(polygons[0], "vertices"))


if __name__ == "__main__":
    unittest.main()
