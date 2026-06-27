from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs/reports/goal4383_barnes_hut_fixed_depth_node_coverage_2026-06-14.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal4383_barnes_hut_fixed_depth_node_coverage_2026-06-14"
APP = ROOT / "examples/current/apps/simulation/rtdl_barnes_hut_force_app.py"
BENCH = ROOT / "examples/benchmark_apps/barnes_hut/rtdl_barnes_hut_benchmark_app.py"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal4383BarnesHutFixedDepthNodeCoverageTest(unittest.TestCase):
    def test_fixed_depth_node_topology_is_exposed_without_replacing_default(self) -> None:
        app_source = APP.read_text(encoding="utf-8")
        bench_source = BENCH.read_text(encoding="utf-8")

        self.assertIn('NODE_TOPOLOGIES = ("one_level", "fixed_depth_cells")', app_source)
        self.assertIn('node_topology: str = "one_level"', app_source)
        self.assertIn('build_fixed_depth_quadtree_cells(bodies, depth=node_depth)', app_source)
        self.assertIn("--node-topology", bench_source)
        self.assertIn("node_depth=max_depth", bench_source)

    def test_correctness_smoke_matches_cpu_oracle(self) -> None:
        for name in (
            "embree_depth6_4096_r3_validation.json",
            "optix_depth6_4096_r3_validation.json",
        ):
            payload = _load(name)
            self.assertEqual(payload["body_count"], 4096)
            self.assertEqual(payload["node_count"], 4096)
            self.assertEqual(payload["node_topology"], "fixed_depth_cells")
            self.assertEqual(payload["node_depth"], 6)
            self.assertTrue(payload["matches_oracle"])
            self.assertEqual(payload["node_coverage"]["covered_body_count"], 4096)

    def test_large_row_uses_one_million_bodies_and_many_nodes(self) -> None:
        embree = _load("embree_depth8_1m_r3_no_validation.json")
        optix = _load("optix_depth8_1m_r3_no_validation.json")

        for payload in (embree, optix):
            self.assertEqual(payload["body_count"], 1_000_000)
            self.assertEqual(payload["node_count"], 65_536)
            self.assertEqual(payload["node_topology"], "fixed_depth_cells")
            self.assertEqual(payload["node_depth"], 8)
            self.assertTrue(payload["validation_skipped"])
            self.assertEqual(payload["node_coverage"]["covered_body_count"], 1_000_000)
            self.assertEqual(payload["node_coverage"]["query_repeat_protocol"]["repeat"], 3)

        embree_query = embree["node_coverage"]["run_phases"][
            "query_fixed_radius_threshold_reached_count_sec"
        ]
        optix_query = optix["node_coverage"]["run_phases"][
            "query_fixed_radius_threshold_reached_count_sec"
        ]
        self.assertGreater(embree_query / optix_query, 2.0)

    def test_report_keeps_claim_boundary_narrow(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("closes the previous \"4-node toy\" weakness", text)
        self.assertIn("1,000,000 bodies against 65,536 fixed-depth quadtree nodes", text)
        self.assertIn("2.06x faster", text)
        self.assertIn("not Barnes-Hut opening-rule evaluation", text)
        self.assertIn("not force-vector reduction", text)
        self.assertIn("not an authors-code comparison", text)


if __name__ == "__main__":
    unittest.main()
