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
POD_RUNNER = ROOT / "scripts" / "goal2377_native_prepared_frn3d_distance_summary_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2377_prepared_3d_neighbor_distance_summary_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2377_native_prepared_frn3d_distance_summary_pod"
GOAL2371_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2371_native_prepared_frn3d_pod"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2377Prepared3DNeighborDistanceSummaryTest(unittest.TestCase):
    def test_generic_distance_summary_surface_is_wired(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_exact_summary", core)
        self.assertIn("struct FrnSummary", core)
        self.assertIn("g_frn3d_grid_exact_summary", workloads)
        self.assertIn("summarize_prepared_fixed_radius_neighbors_grid_3d_optix", workloads)
        self.assertIn("rtdl_optix_summarize_prepared_fixed_radius_neighbors_3d", api)
        self.assertIn("RtdlFixedRadiusNeighborSummary", prelude)
        self.assertIn("static_assert(sizeof(RtdlFixedRadiusNeighborSummary) == 32", prelude)
        self.assertIn("offsetof(RtdlFixedRadiusNeighborSummary, sum_distance) == 24", prelude)
        self.assertIn("def summary(self, query_points, *, radius: float, k_max: int)", runtime)
        self.assertIn('"prepared_uniform_cell_exact_distance_summary"', runtime)
        self.assertIn('"summary"', runner)
        self.assertIn("distance_summary", runner)
        self.assertIn("device_resident_summary", runner)

    def test_pod_runner_and_report_preserve_claim_boundaries(self) -> None:
        pod_runner = POD_RUNNER.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("--result-mode summary", pod_runner)
        self.assertIn("distance-summary", pod_runner)
        self.assertIn("This is a distance-summary contract, not a witness-row contract.", report)
        self.assertIn("It is not a replacement for witness rows", report)
        self.assertIn("RTNN paper-equivalence", report)
        self.assertIn("RT-core speedup", report)

    def test_pod_artifacts_show_distance_summary_without_witness_materialization(self) -> None:
        summary_65 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_distance_summary_65536_r002_k50.json")
        summary_262 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_distance_summary_262144_r002_k50.json")
        rows_262 = _load(GOAL2371_ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_262144_r002_k50.json")

        for payload in (summary_65, summary_262):
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["result_mode"], "summary")
            self.assertEqual(payload["execution_mode"], "native-prepared-optix")
            self.assertTrue(payload["claim_boundary"]["device_resident_summary"])
            self.assertFalse(payload["claim_boundary"]["rt_core_neighbor_search_claim_authorized"])
            self.assertEqual(payload["phase_timings"]["mode"], "prepared_uniform_cell_exact_distance_summary")
            self.assertEqual(payload["phase_timings"]["row_download"], 0.0)
            self.assertEqual(payload["phase_timings"]["exact_refine"], 0.0)
            self.assertEqual(payload["row_count"], payload["distance_summary"]["count"])
            self.assertGreater(payload["distance_summary"]["count"], 0)
            self.assertGreaterEqual(payload["distance_summary"]["min_distance"], 0.0)
            self.assertGreaterEqual(payload["distance_summary"]["max_distance"], payload["distance_summary"]["min_distance"])
            self.assertGreater(payload["distance_summary"]["sum_distance"], 0.0)

        self.assertGreater(rows_262["elapsed_sec"] / summary_262["elapsed_sec"], 5.0)


if __name__ == "__main__":
    unittest.main()
