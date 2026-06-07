import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "docs" / "reports" / "goal3723_rayjoin_lsi_direct_intersection_route_probe_2026-06-07.md"
ARTIFACT = ROOT / "docs" / "reports" / "goal3722_rayjoin_lsi_direct_intersection_route_a5000" / "summary.json"


class Goal3723RayJoinLsiDirectIntersectionRouteProbeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = REPORT.read_text(encoding="utf-8")
        cls.artifact = json.loads(ARTIFACT.read_text(encoding="utf-8"))

    def test_artifact_counts_match_but_direct_route_is_slower(self):
        comparison = self.artifact["comparison"]
        self.assertTrue(comparison["counts_match"])
        self.assertEqual(20860, int(comparison["rayjoin_lsi_intersections"]))
        self.assertEqual(20860, int(comparison["rtdl_count"]))
        self.assertLess(float(comparison["direct_intersection_speedup_vs_existing_anyhit"]), 1.0)
        self.assertLess(float(comparison["direct_intersection_speedup_vs_rayjoin"]), 1.0)

    def test_phase_modes_are_machine_readable(self):
        existing = self.artifact["rtdl_existing_anyhit_exact_count"]["runs"][-1]["native_phase_timings"]
        direct = self.artifact["rtdl_direct_intersection_exact_count"]["runs"][-1]["native_phase_timings"]
        self.assertEqual("count_prepared_left", existing["mode"])
        self.assertEqual("count_prepared_left_direct_intersection", direct["mode"])
        self.assertEqual(20860, int(existing["emitted_count"]))
        self.assertEqual(20860, int(direct["emitted_count"]))

    def test_report_closes_simple_anyhit_hypothesis(self):
        self.assertIn("closes the simple \"remove any-hit\" hypothesis", self.report)
        self.assertIn("slower than the existing RTDL any-hit exact-count route", self.report)
        self.assertIn("Do not promote the direct-intersection route", self.report)
        self.assertIn("generic grouped/ranged primitive representation", self.report)
        self.assertIn("fixed-point or integer-coordinate exact predicate option", self.report)

    def test_claim_boundaries_remain_false(self):
        boundary = self.artifact["claim_boundary"]
        for key in (
            "release_authorized",
            "public_speedup_claim_authorized",
            "rayjoin_paper_reproduction_claim_authorized",
            "rtdl_beats_rayjoin_claim_authorized",
            "rt_core_speedup_claim_authorized",
            "true_zero_copy_claim_authorized",
            "native_default_route_authorized",
        ):
            self.assertFalse(boundary[key], key)
        self.assertIn("does not authorize", self.report)
        self.assertIn("RTDL-beats-RayJoin claims", self.report)


if __name__ == "__main__":
    unittest.main()
