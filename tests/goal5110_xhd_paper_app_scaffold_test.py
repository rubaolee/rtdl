from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "Paper-reproduction-apps" / "x-hd-paper"


class Goal5110XhdPaperAppScaffoldTest(unittest.TestCase):
    def test_manifest_records_pinned_author_source_and_no_reproduction_claim(self) -> None:
        manifest = json.loads((APP_DIR / "data" / "manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(manifest["paper"]["title"], "X-HD: Fast Hausdorff Distance Computation with Ray Tracing")
        self.assertEqual(manifest["paper"]["doi"], "10.1145/3797905.3800509")
        self.assertEqual(manifest["author_artifact"]["repository"], "https://github.com/pwrliang/X-HD.git")
        self.assertEqual(
            manifest["author_artifact"]["commit"],
            "7bf41c8442d059c94f4178355c6d5a10571d9658",
        )
        self.assertEqual(manifest["author_artifact"]["main_variant"], "rt")
        self.assertIn(
            manifest["reproduction_scope"]["status"],
            {
                "not_started__requirements_and_provenance_scaffold",
                "bounded_same_input_author_json_gate_packet_ready__author_execution_pending",
                "bounded_same_input_author_json_gate_complete__matched_on_tiny_wkt_fixture",
                "bounded_same_input_author_json_gates_complete__tiny_and_bounded2d_matched",
                "bounded_same_input_author_json_gates_complete__tiny_bounded2d_bounded3d_matched",
                "bounded_same_input_author_json_gates_complete__bounded2d_rtdl_route_matched",
                "bounded_same_input_author_json_gates_complete__bounded2d_bounded3d_rtdl_routes_matched",
                "xhd_bounded_same_input_reproduction_complete__pending_external_review",
                "xhd_bounded_same_input_reproduction_complete",
                "xhd_public_modelnet40_all400_hd_exec_entrypoint_complete__full_paper_incomplete",
            },
        )
        self.assertFalse(manifest["boundaries"]["full_paper_reproduction_claimed"])
        self.assertFalse(manifest["boundaries"]["exact_paper_dataset_reproduction_claimed"])
        self.assertFalse(manifest["boundaries"]["whole_program_speedup_claimed"])
        self.assertFalse(manifest["boundaries"]["existing_hausdorff_xhd_benchmark_reclassified_as_paper_reproduction"])

    def test_readme_keeps_existing_benchmark_assets_separate_from_paper_reproduction(self) -> None:
        readme = (APP_DIR / "README.md").read_text(encoding="utf-8")

        self.assertIn("examples/current/research_benchmarks/hausdorff_xhd/", readme)
        self.assertIn("These are not yet a paper app", readme)
        self.assertIn("bounded_same_input_author_json_gate", readme)
        self.assertIn("matched = true", readme)
        self.assertIn("full X-HD paper reproduction", readme)
        self.assertIn("author performance parity", readme)

    def test_data_readme_tracks_author_json_schema_sources(self) -> None:
        data_readme = (APP_DIR / "data" / "README.md").read_text(encoding="utf-8")

        self.assertIn("src/flags.cc", data_readme)
        self.assertIn("src/main.cpp", data_readme)
        self.assertIn("src/run_hausdorff_distance.cu", data_readme)
        self.assertIn("HDResult", data_readme)
        self.assertIn("Running.AvgTime", data_readme)
        self.assertIn("paper inputs not pinned", data_readme)


if __name__ == "__main__":
    unittest.main()
