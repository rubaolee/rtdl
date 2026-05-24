from __future__ import annotations

import importlib
import json
import tempfile
import unittest
from pathlib import Path


APP = importlib.import_module(
    "examples.v2_0.research_benchmarks.librts_spatial_index.rtdl_librts_spatial_index_benchmark_app"
)
RUNNER = importlib.import_module("scripts.goal2574_librts_external_runner")
ROOT = Path(__file__).resolve().parents[1]


class LibRTSSpatialIndexBenchmarkAppTest(unittest.TestCase):
    def test_tiny_fixture_matches_authors_predicate_orientation(self) -> None:
        fixture = APP.make_tiny_fixture()
        self.assertEqual(APP.count_point_contains(fixture.boxes[:2], fixture.point_queries), 5)
        self.assertEqual(APP.count_range_intersects(fixture.boxes[:2], fixture.box_queries[:1]), 2)
        self.assertEqual(APP.count_range_contains(fixture.boxes[:2], fixture.box_queries[1:2]), 2)
        payload = APP.run_counts(fixture, "all")
        self.assertEqual(payload["semantics"]["range_contains"], "indexed_box_contains_query_box")
        self.assertFalse(payload["paper_reproduction"])
        self.assertFalse(payload["authors_code_comparison"])
        self.assertFalse(payload["native_engine_customization"])

    def test_uniform_fixture_is_deterministic_and_wkt_compatible(self) -> None:
        first = APP.make_uniform_fixture(box_count=8, query_count=4, seed=17)
        second = APP.make_uniform_fixture(box_count=8, query_count=4, seed=17)
        self.assertEqual(first, second)
        self.assertTrue(first.boxes[0].to_wkt().startswith("POLYGON(("))
        self.assertTrue(first.point_queries[0].to_wkt().startswith("POINT("))

    def test_partner_grid_reference_matches_cpu_reference(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=64, query_count=32, seed=41)
        cpu = APP.run_counts(fixture, "all")
        grid = APP.run_grid_counts(fixture, "all", resolution=16)
        self.assertEqual(grid["counts"], cpu["counts"])
        self.assertTrue(grid["matches_cpu_reference"])
        self.assertFalse(grid["rt_core_accelerated"])
        self.assertFalse(grid["native_engine_customization"])
        self.assertGreater(grid["grid"]["occupied_cells"], 0)

    def test_emit_wkt_manifest_and_external_commands(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=4, query_count=3, seed=9)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = APP.write_wkt_fixture(fixture, Path(tmp), include_counts=True)
            manifest_path = Path(manifest["manifest"])
            self.assertTrue(manifest_path.exists())
            loaded = json.loads(manifest_path.read_text(encoding="utf-8"))
            commands = RUNNER.build_rtspatial_commands(
                loaded,
                rtspatial_exec="/opt/rtspatial_exec",
                load_factor=0.25,
            )
            self.assertIn("--point_query=", " ".join(commands["point_contains"]))
            self.assertIn("--predicate=contains", commands["range_contains"])
            self.assertIn("--predicate=intersects", commands["range_intersects"])
            self.assertEqual(loaded["cpu_reference"]["counts"], APP.run_counts(fixture, "all")["counts"])

    def test_wkt_fixture_roundtrip_feeds_cpu_oracle(self) -> None:
        fixture = APP.make_uniform_fixture(box_count=12, query_count=6, seed=2574)
        with tempfile.TemporaryDirectory() as tmp:
            manifest = APP.write_wkt_fixture(fixture, Path(tmp), include_counts=True)
            files = manifest["files"]
            loaded = APP.load_wkt_fixture(
                boxes_path=Path(files["boxes"]),
                point_queries_path=Path(files["point_queries"]),
                box_queries_path=Path(files["box_queries"]),
                seed=fixture.seed,
            )
            self.assertEqual(APP.run_counts(loaded, "all")["counts"], APP.run_counts(fixture, "all")["counts"])
            self.assertEqual(APP.parse_point_wkt("POINT(0.25 0.75)"), APP.Point2D(0.25, 0.75))
            self.assertEqual(
                APP.parse_box_wkt("POLYGON((0 0,1 0,1 1,0 1,0 0))"),
                APP.Box2D(0.0, 0.0, 1.0, 1.0),
            )

    def test_runner_parses_authors_output(self) -> None:
        parsed = RUNNER.parse_rtspatial_output(
            "Loaded boxes 100\nLoaded point queries 10\nRT, load 1.25 ms, query 2.5 ms, results: 42\n"
        )
        self.assertEqual(parsed["loaded_boxes"], 100)
        self.assertEqual(parsed["loaded_point_queries"], 10)
        self.assertIsNone(parsed["loaded_box_queries"])
        self.assertEqual(parsed["load_ms"], 1.25)
        self.assertEqual(parsed["query_ms"], 2.5)
        self.assertEqual(parsed["results"], 42)

    def test_readme_and_intake_keep_claim_boundary(self) -> None:
        readme = (ROOT / "examples/v2_0/research_benchmarks/librts_spatial_index/README.md").read_text(
            encoding="utf-8"
        )
        report = (ROOT / "docs/reports/goal2574_librts_spatial_index_benchmark_intake_2026-05-24.md").read_text(
            encoding="utf-8"
        )
        for text in (readme, report):
            self.assertIn("LibRTS: A Spatial Indexing Library by Ray Tracing", text)
            self.assertIn("10.1145/3710848.3710850", text)
            self.assertIn("RTSpatial/RTSpatial", text)
            self.assertIn("does not authorize public speedup wording", text)


if __name__ == "__main__":
    unittest.main()
