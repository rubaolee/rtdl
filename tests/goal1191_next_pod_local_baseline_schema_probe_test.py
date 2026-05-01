from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts import goal1191_next_pod_local_baseline_schema_probe as goal1191


ROOT = Path(__file__).resolve().parents[1]


class Goal1191NextPodLocalBaselineSchemaProbeTest(unittest.TestCase):
    def test_probe_definitions_cover_six_apps(self) -> None:
        apps = {probe["app"] for probe in goal1191.PROBES}
        self.assertEqual(
            apps,
            {
                "database_analytics",
                "graph_analytics",
                "road_hazard_screening",
                "polygon_pair_overlap_area_rows",
                "polygon_set_jaccard",
                "hausdorff_distance",
            },
        )

    def test_probe_definitions_include_required_phase_paths(self) -> None:
        probes = {probe["app"]: probe for probe in goal1191.PROBES}
        self.assertIn(("graph_phase_totals_sec", "query_visibility_pair_rows_sec"), probes["graph_analytics"]["required_paths"])
        self.assertIn(("run_phases", "rt_candidate_discovery_sec"), probes["polygon_pair_overlap_area_rows"]["required_paths"])
        self.assertIn(("run_phases", "rt_candidate_discovery_sec"), probes["polygon_set_jaccard"]["required_paths"])
        self.assertIn(("run_phases", "native_directed_summary_sec"), probes["hausdorff_distance"]["required_paths"])

    def test_cli_probe_passes_in_current_environment(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            output_dir = tmp_path / "probe_outputs"
            output_json = tmp_path / "probe.json"
            output_md = tmp_path / "probe.md"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/goal1191_next_pod_local_baseline_schema_probe.py",
                    "--output-dir",
                    str(output_dir),
                    "--output-json",
                    str(output_json),
                    "--output-md",
                    str(output_md),
                ],
                cwd=ROOT,
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            )
            payload = json.loads(output_json.read_text(encoding="utf-8"))
            markdown = output_md.read_text(encoding="utf-8")
            self.assertTrue(payload["valid"], payload)
            self.assertEqual(payload["probe_count"], 6)
            self.assertEqual(payload["failing_probe_count"], 0)
            self.assertIn("does not authorize pod execution", markdown)


if __name__ == "__main__":
    unittest.main()
