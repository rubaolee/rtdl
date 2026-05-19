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
POD_RUNNER = ROOT / "scripts" / "goal2375_native_prepared_frn3d_count_summary_pod_runner.sh"
REPORT = ROOT / "docs" / "reports" / "goal2375_prepared_3d_neighbor_exact_count_summary_2026-05-19.md"
ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2375_native_prepared_frn3d_count_summary_pod"
GOAL2371_ARTIFACT_DIR = ROOT / "docs" / "reports" / "goal2371_native_prepared_frn3d_pod"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class Goal2375Prepared3DNeighborExactCountSummaryTest(unittest.TestCase):
    def test_generic_count_summary_surface_is_wired(self) -> None:
        core = CORE.read_text(encoding="utf-8")
        workloads = WORKLOADS.read_text(encoding="utf-8")
        api = API.read_text(encoding="utf-8")
        prelude = PRELUDE.read_text(encoding="utf-8")
        runtime = RUNTIME.read_text(encoding="utf-8")
        runner = RUNNER.read_text(encoding="utf-8")

        self.assertIn("fixed_radius_neighbors_3d_grid_exact_count", core)
        self.assertIn("floor_to_int_exact", core)
        self.assertIn("g_frn3d_grid_exact_count", workloads)
        self.assertIn("count_prepared_fixed_radius_neighbors_grid_3d_optix", workloads)
        self.assertIn("rtdl_optix_count_prepared_fixed_radius_neighbors_3d", api)
        self.assertIn("rtdl_optix_count_prepared_fixed_radius_neighbors_3d", prelude)
        self.assertIn("def count(self, query_points, *, radius: float, k_max: int) -> int", runtime)
        self.assertIn('"prepared_uniform_cell_exact_count_summary"', runtime)
        self.assertIn('"count"', runner)
        self.assertIn("device_resident_summary", runner)

    def test_pod_runner_and_report_preserve_claim_boundaries(self) -> None:
        pod_runner = POD_RUNNER.read_text(encoding="utf-8")
        report = REPORT.read_text(encoding="utf-8")

        self.assertIn("--result-mode count", pod_runner)
        self.assertIn("count-summary", pod_runner)
        self.assertIn("This is a count-summary contract, not a witness-row contract.", report)
        self.assertIn("It does not authorize an RT-core speedup claim.", report)
        self.assertIn("No native `rtnn` ABI names were added.", report)

    def test_pod_artifacts_show_device_summary_without_witness_materialization(self) -> None:
        summary_65 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_count_summary_65536_r002_k50.json")
        summary_262 = _load(ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_count_summary_262144_r002_k50.json")
        rows_262 = _load(GOAL2371_ARTIFACT_DIR / "rtdl_packed_native_prepared_optix_3d_262144_r002_k50.json")

        for payload in (summary_65, summary_262):
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["result_mode"], "count")
            self.assertEqual(payload["execution_mode"], "native-prepared-optix")
            self.assertTrue(payload["claim_boundary"]["device_resident_summary"])
            self.assertFalse(payload["claim_boundary"]["rt_core_neighbor_search_claim_authorized"])
            self.assertEqual(payload["phase_timings"]["mode"], "prepared_uniform_cell_exact_count_summary")
            self.assertEqual(payload["phase_timings"]["row_download"], 0.0)
            self.assertEqual(payload["phase_timings"]["exact_refine"], 0.0)
            self.assertGreater(payload["row_count"], 0)

        self.assertGreater(rows_262["elapsed_sec"] / summary_262["elapsed_sec"], 10.0)


if __name__ == "__main__":
    unittest.main()
