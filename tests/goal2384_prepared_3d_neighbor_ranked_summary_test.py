import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "src" / "native" / "optix" / "rtdl_optix_core.cpp"
WORKLOADS = ROOT / "src" / "native" / "optix" / "rtdl_optix_workloads.cpp"
API = ROOT / "src" / "native" / "optix" / "rtdl_optix_api.cpp"
PRELUDE = ROOT / "src" / "native" / "optix" / "rtdl_optix_prelude.h"
RUNTIME = ROOT / "src" / "rtdsl" / "optix_runtime.py"
RUNNER = ROOT / "scripts" / "goal2348_rtnn_v2_2_external_runner.py"
POD_RUNNER = ROOT / "scripts" / "goal2384_native_prepared_frn3d_ranked_summary_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2384_prepared_3d_neighbor_ranked_summary_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2384_native_prepared_frn3d_ranked_summary_pod"
GOAL2371_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2371_native_prepared_frn3d_pod"
GOAL2381_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2381_native_prepared_frn3d_ranked_rows_pod"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2384Prepared3DNeighborRankedSummaryTest(unittest.TestCase):
    def test_generic_ranked_summary_surface_is_wired(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_summary", core)
        self.assertIn("FrnRankedSummary", core)
        self.assertIn("g_frn3d_grid_ranked_summary", workloads)
        self.assertIn("run_prepared_ranked_fixed_radius_neighbor_summaries_grid_3d_optix", workloads)
        self.assertIn("rtdl_optix_run_prepared_ranked_fixed_radius_neighbor_summaries_3d", api)
        self.assertIn("RtdlFixedRadiusRankedNeighborSummary", prelude)
        self.assertIn("static_assert(sizeof(RtdlFixedRadiusRankedNeighborSummary) == 40", prelude)
        self.assertIn("class _RtdlFixedRadiusRankedNeighborSummary", runtime)
        self.assertIn("def run_ranked_summary_raw(self, query_points, *, radius: float, k_max: int)", runtime)
        self.assertIn('"prepared_uniform_cell_ranked_summary_rows"', runtime)
        self.assertIn('"ranked-summary-raw"', runner)
        self.assertIn("device_ranked_summary_rows", runner)

    def test_report_and_runner_preserve_boundaries(self) -> None:
        report = REPORT.read_text(encoding="utf-8")
        pod_runner = POD_RUNNER.read_text(encoding="utf-8")

        self.assertIn("--result-mode ranked-summary-raw", pod_runner)
        self.assertIn("ranked-summary continuation", report)
        self.assertIn("RTNN paper-equivalence", report)
        self.assertIn("RT-core nearest-neighbor", report)
        self.assertIn("k_max <= 64", report)

    def test_pod_artifacts_show_device_summary_gain(self) -> None:
        correctness = _load(ARTIFACT_DIR / "ranked_summary_correctness_small.json")
        summary_65 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_ranked_summary_65536_r002_k50.json")
        summary_262 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_ranked_summary_262144_r002_k50.json")
        ranked_262 = _load(GOAL2381_ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_ranked_rows_262144_r002_k50.json")
        old_262 = _load(GOAL2371_ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_262144_r002_k50.json")

        self.assertTrue(correctness["ok"])
        self.assertEqual(correctness["phase_timings"]["mode"], "prepared_uniform_cell_ranked_summary_rows")
        for payload in (summary_65, summary_262):
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["result_mode"], "ranked-summary-raw")
            self.assertEqual(payload["execution_mode"], "native-prepared-optix")
            self.assertTrue(payload["claim_boundary"]["device_ranked_summary_rows"])
            self.assertFalse(payload["claim_boundary"]["rt_core_neighbor_search_claim_authorized"])
            self.assertEqual(payload["phase_timings"]["mode"], "prepared_uniform_cell_ranked_summary_rows")
            self.assertEqual(payload["phase_timings"]["exact_refine"], 0.0)
            self.assertEqual(payload["row_count"], payload["query_count"])

        self.assertGreater(ranked_262["elapsed_sec"] / summary_262["elapsed_sec"], 5.0)
        self.assertGreater(old_262["elapsed_sec"] / summary_262["elapsed_sec"], 10.0)
        self.assertLess(summary_262["phase_timings"]["row_download"], ranked_262["phase_timings"]["row_download"])


if __name__ == "__main__":
    unittest.main()
