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
POD_RUNNER = ROOT / "scripts" / "goal2381_native_prepared_frn3d_ranked_rows_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2381_prepared_3d_neighbor_ranked_rows_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2381_native_prepared_frn3d_ranked_rows_pod"
GOAL2371_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2371_native_prepared_frn3d_pod"
GOAL2379_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2379_native_prepared_frn3d_exact_rows_pod"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2381Prepared3DNeighborRankedRowsTest(unittest.TestCase):
    def test_generic_ranked_row_surface_is_wired(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_count", core)
        self.assertIn("fixed_radius_neighbors_3d_grid_ranked_rows", core)
        self.assertIn("frn_ranked_insert", core)
        self.assertIn("g_frn3d_grid_ranked_rows", workloads)
        self.assertIn("run_prepared_ranked_fixed_radius_neighbors_grid_3d_optix", workloads)
        self.assertIn("rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d", api)
        self.assertIn("rtdl_optix_run_prepared_ranked_fixed_radius_neighbors_3d", prelude)
        self.assertIn("static_assert(sizeof(RtdlKnnNeighborRow) == 24", prelude)
        self.assertIn("def run_ranked_raw(self, query_points, *, radius: float, k_max: int)", runtime)
        self.assertIn('"prepared_uniform_cell_ranked_rows"', runtime)
        self.assertIn('"ranked-raw"', runner)
        self.assertIn("device_ranked_witness_rows", runner)

    def test_pod_runner_and_report_preserve_claim_boundaries(self) -> None:
        pod_runner = POD_RUNNER.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("--result-mode ranked-raw", pod_runner)
        self.assertIn("ranked-rows", pod_runner)
        self.assertIn("bounded ranked fixed-radius contract", report)
        self.assertIn("RTNN paper-equivalence", report)
        self.assertIn("RT-core speedup", report)
        self.assertIn("k_max <= 64", report)

    def test_small_correctness_oracle_and_pod_artifacts(self) -> None:
        correctness = _load(ARTIFACT_DIR / "ranked_correctness_small.json")
        ranked_65 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_ranked_rows_65536_r002_k50.json")
        ranked_262 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_ranked_rows_262144_r002_k50.json")
        old_262 = _load(GOAL2371_ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_262144_r002_k50.json")
        exact_262 = _load(GOAL2379_ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_exact_rows_262144_r002_k50.json")

        self.assertTrue(correctness["ok"])
        self.assertEqual(correctness["phase_timings"]["mode"], "prepared_uniform_cell_ranked_rows")
        for payload in (ranked_65, ranked_262):
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["result_mode"], "ranked-raw")
            self.assertEqual(payload["execution_mode"], "native-prepared-optix")
            self.assertTrue(payload["claim_boundary"]["device_ranked_witness_rows"])
            self.assertFalse(payload["claim_boundary"]["rt_core_neighbor_search_claim_authorized"])
            self.assertEqual(payload["phase_timings"]["mode"], "prepared_uniform_cell_ranked_rows")
            self.assertEqual(payload["phase_timings"]["exact_refine"], 0.0)
            self.assertGreater(payload["phase_timings"]["row_download"], 0.0)

        self.assertGreater(old_262["elapsed_sec"] / ranked_262["elapsed_sec"], 1.5)
        self.assertGreater(ranked_262["elapsed_sec"] / exact_262["elapsed_sec"], 1.2)


if __name__ == "__main__":
    unittest.main()
