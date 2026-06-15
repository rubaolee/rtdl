import json
import pathlib
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE_DIR = (
    ROOT
    / "docs"
    / "reports"
    / "goal4389_rtdbscan_partner_dual_implementation_2026-06-15"
)


RT_CUPY = "optix_rt_core_flags_cupy_prepared_grid_components_3d"
RT_NUMBA = "optix_rt_core_flags_numba_prepared_grid_components_3d"
PURE_CUPY = "partner_cupy_prepared_grid_components_3d"
PURE_NUMBA = "partner_numba_prepared_grid_components_3d"


def _load(mode: str, points: int) -> dict:
    suffix = "r4w1_validation" if points == 4096 else "r4w1_no_validation"
    path = EVIDENCE_DIR / f"{mode}_clustered3d_{points}_{suffix}.json"
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class Goal4389RTDBSCANPartnerDualImplementationTest(unittest.TestCase):
    def test_evidence_files_cover_cupy_and_numba_same_contract(self) -> None:
        for points in (4096, 65536, 262144, 524288):
            with self.subTest(points=points):
                rt_cupy = _load(RT_CUPY, points)
                rt_numba = _load(RT_NUMBA, points)
                pure_cupy = _load(PURE_CUPY, points)
                pure_numba = _load(PURE_NUMBA, points)

                self.assertEqual(rt_cupy["signature"], rt_numba["signature"])
                self.assertEqual(pure_cupy["signature"], pure_numba["signature"])

                for payload in (rt_cupy, rt_numba, pure_cupy, pure_numba):
                    self.assertEqual(payload["dataset"], "clustered3d")
                    self.assertEqual(payload["point_count"], points)
                    protocol = payload["metadata"]["prepared_query_repeat_protocol"]
                    self.assertEqual(protocol["repeat"], 4)
                    self.assertEqual(protocol["warmup"], 1)
                    self.assertEqual(protocol["measured_iterations"], 3)
                    self.assertIs(protocol["signatures_stable"], True)

                self.assertIs(rt_cupy["metadata"]["rt_core_accelerated"], True)
                self.assertIs(rt_numba["metadata"]["rt_core_accelerated"], True)
                self.assertIs(pure_cupy["metadata"]["rt_core_accelerated"], False)
                self.assertIs(pure_numba["metadata"]["rt_core_accelerated"], False)

    def test_4096_smoke_matches_cpu_reference(self) -> None:
        for mode in (RT_CUPY, RT_NUMBA, PURE_CUPY, PURE_NUMBA):
            with self.subTest(mode=mode):
                self.assertIs(_load(mode, 4096)["matches_reference"], True)

    def test_524k_current_winner_is_numba_for_this_contract(self) -> None:
        rt_cupy = _load(RT_CUPY, 524288)
        rt_numba = _load(RT_NUMBA, 524288)
        pure_cupy = _load(PURE_CUPY, 524288)
        pure_numba = _load(PURE_NUMBA, 524288)

        self.assertLess(rt_numba["elapsed_sec"], rt_cupy["elapsed_sec"])
        self.assertLess(pure_numba["elapsed_sec"], pure_cupy["elapsed_sec"])
        self.assertAlmostEqual(rt_numba["elapsed_sec"], 8.899863, places=3)
        self.assertAlmostEqual(rt_cupy["elapsed_sec"], 10.661565, places=3)

    def test_docs_do_not_defer_current_rtdbscan_partner_gap_to_v3(self) -> None:
        report = (
            ROOT
            / "docs"
            / "reports"
            / "goal4389_rtdbscan_partner_dual_implementation_2026-06-15.md"
        ).read_text(encoding="utf-8")
        policy = (
            ROOT
            / "docs"
            / "reports"
            / "goal4388_partner_dual_implementation_policy_and_app_perf_2026-06-15.md"
        ).read_text(encoding="utf-8")
        public_matrix = (
            ROOT / "docs" / "release_reports" / "v2_14" / "public_rt_vs_embree_comparison.md"
        ).read_text(encoding="utf-8")
        partner_matrix = (
            ROOT / "docs" / "learn" / "benchmark_partner_reference_matrix.md"
        ).read_text(encoding="utf-8")
        joined = "\n".join([report, policy, public_matrix, partner_matrix])

        self.assertIn("No claim here depends on V3.0", report)
        self.assertIn("current best measured partner for this contract is Numba", policy)
        self.assertIn("Goal4389", public_matrix)
        self.assertIn("RT+Numba is 8.900s", partner_matrix)
        self.assertNotIn("best-vs-Numba fresh large sweep is still needed", joined)
        self.assertNotIn("still a V3.0/M1 planning item", joined)

    def test_benchmark_app_has_cupy_prepared_repeat_protocol(self) -> None:
        app = (
            ROOT
            / "examples"
            / "current"
            / "research_benchmarks"
            / "rt_dbscan"
            / "rtdl_rt_dbscan_benchmark_app.py"
        ).read_text(encoding="utf-8")

        self.assertIn("RT-DBSCAN OptiX+CuPy repeat produced no measured rows", app)
        self.assertIn("CuPy prepared-grid repeat produced no measured rows", app)
        self.assertIn('"cupy_component_continuation_sec": timing_breakdown_sec', app)


if __name__ == "__main__":
    unittest.main()
