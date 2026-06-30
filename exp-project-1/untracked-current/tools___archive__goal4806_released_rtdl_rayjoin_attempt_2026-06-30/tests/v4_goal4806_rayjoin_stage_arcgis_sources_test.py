from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class V4Goal4806RayJoinStageArcgisSourcesTest(unittest.TestCase):
    def test_stage_arcgis_sources_dry_run_plans_registered_us_targets(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output_json = root / "stage.json"
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/rayjoin_paper_reproduction_suite.py",
                    "stage-arcgis-sources",
                    "--staged-root",
                    str(root / "staged"),
                    "--dataset-root",
                    str(root / "dataset"),
                    "--targets",
                    "county,zipcode,blockgroup,waterbodies",
                    "--max-pages",
                    "1",
                    "--dry-run",
                    "--output-json",
                    str(output_json),
                ],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
            self.assertEqual(completed.stdout, "")
            self.assertEqual(completed.returncode, 0)
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            file_payload = json.loads(output_json.read_text(encoding="utf-8"))

        self.assertEqual(payload["schema"], "rtdl.rayjoin_paper_suite.stage_arcgis_sources.v1")
        self.assertEqual(file_payload["schema"], payload["schema"])
        self.assertTrue(payload["dry_run"])
        self.assertEqual(payload["targets"], ["county", "zipcode", "blockgroup", "waterbodies"])
        self.assertEqual(len(payload["rows"]), 4)
        for row in payload["rows"]:
            self.assertEqual(row["status"], "planned")
            self.assertEqual(len(row["pages"]), 1)
            self.assertEqual(row["pages"][0]["status"], "planned")
        self.assertIn("build-arcgis-cdb-tree", payload["next_command"])
        self.assertIn("same_source_regenerated_cdb", payload["claim_boundary"])


if __name__ == "__main__":
    unittest.main()
