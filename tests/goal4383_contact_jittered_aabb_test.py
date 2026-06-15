from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "examples/current/research_benchmarks/contact_manifold/rtdl_contact_manifold_benchmark_app.py"
REPORT = ROOT / "docs/reports/goal4383_contact_jittered_aabb_2026-06-14.md"
ARTIFACT_DIR = ROOT / "docs/reports/goal4383_contact_jittered_aabb_2026-06-14"


def _load(name: str) -> dict[str, object]:
    return json.loads((ARTIFACT_DIR / name).read_text(encoding="utf-8"))


class Goal4383ContactJitteredAabbTest(unittest.TestCase):
    def test_app_exposes_jittered_grid_fixture(self) -> None:
        text = APP.read_text(encoding="utf-8")
        self.assertIn("def jittered_grid_fixture", text)
        self.assertIn('"jittered_grid"', text)
        self.assertIn("known exact witness per cell", text)

    def test_large_jittered_rows_match_cpu_reference(self) -> None:
        for name in (
            "embree_jittered_grid65536_r5.json",
            "optix_jittered_grid65536_r5.json",
        ):
            payload = _load(name)
            self.assertEqual(payload["dataset"], "jittered_grid_65536")
            self.assertEqual(payload["candidate_discovery_primitive"], "AABB_INDEX_QUERY_2D")
            self.assertEqual(payload["candidate_discovery_contract"], "generic_aabb_intersection_pair_rows_2d")
            self.assertEqual(payload["primitive_under_test"], "COLLECT_K_BOUNDED")
            self.assertEqual(payload["all_pairs_count"], 4_294_967_296)
            self.assertEqual(payload["aabb_candidate_pair_count"], 65_536)
            self.assertEqual(payload["valid_count"], 65_536)
            self.assertTrue(payload["matches_cpu_reference"])
            self.assertTrue(payload["complete_candidate_coverage"])
            self.assertFalse(payload["overflowed"])

    def test_optix_query_is_faster_but_claim_stays_modest(self) -> None:
        embree = _load("embree_jittered_grid65536_r5.json")
        optix = _load("optix_jittered_grid65536_r5.json")

        embree_query = embree["run_phases"]["emit_aabb_intersection_pair_rows_2d_median_sec"]
        optix_query = optix["run_phases"]["emit_aabb_intersection_pair_rows_2d_median_sec"]
        self.assertGreater(embree_query / optix_query, 1.2)

        embree_hot = (
            embree_query
            + embree["run_phases"]["collect_k_bounded_rows_sec"]
            + embree["run_phases"]["python_exact_refinement_sec"]
        )
        optix_hot = (
            optix_query
            + optix["run_phases"]["collect_k_bounded_rows_sec"]
            + optix["run_phases"]["python_exact_refinement_sec"]
        )
        self.assertGreater(embree_hot / optix_hot, 1.1)

    def test_report_records_boundary_and_fail_closed_behavior(self) -> None:
        text = REPORT.read_text(encoding="utf-8")
        self.assertIn("4,294,967,296` possible pairs", text)
        self.assertIn("OptiX is 1.23x faster than Embree", text)
        self.assertIn("failed closed", text)
        self.assertIn("not a full contact manifold solver", text)
        self.assertIn("not continuous collision detection", text)
        self.assertIn("not physics contact generation", text)


if __name__ == "__main__":
    unittest.main()
