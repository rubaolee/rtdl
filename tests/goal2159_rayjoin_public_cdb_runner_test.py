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


class Goal2159RayjoinPublicCdbRunnerTest(unittest.TestCase):
    def test_dry_run_materializes_slices_and_preserves_boundaries(self) -> None:
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
                    "pip_county512,lsi_county256_soil256_count192",
                    "--backends",
                    "cpu,optix",
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

        self.assertEqual(artifact["goal"], "2159")
        self.assertFalse(artifact["claim_boundary"]["full_rayjoin_reproduction"])
        self.assertFalse(artifact["claim_boundary"]["v2_0_release_authorized"])
        self.assertIn("pip_county512", artifact["cases"])
        self.assertIn("lsi_county256_soil256_count192", artifact["cases"])
        self.assertEqual(artifact["cases"]["pip_county512"]["backends"]["cpu"]["status"], "dry_run")
        self.assertIn("county_256_192", artifact["slices"])

    def test_runner_source_keeps_claim_boundary_flags(self) -> None:
        text = SCRIPT.read_text(encoding="utf-8")

        for phrase in (
            "full_rayjoin_reproduction",
            "paper_scale_perf_claim_authorized",
            "broad_rt_core_speedup_claim_authorized",
            "whole_app_rayjoin_speedup_claim_authorized",
            "v2_0_release_authorized",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
